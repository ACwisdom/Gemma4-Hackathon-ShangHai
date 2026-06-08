import json
from collections.abc import Iterator

import httpx

from ...config import Settings
from .base import ChatMessage, LLMResponse


def is_gemma_endpoint(base_url: str, model: str) -> bool:
    base = base_url.lower()
    model_lower = model.lower()
    return (
        "gemma" in model_lower
        or "deepinfra.com" in base
        or "generativelanguage.googleapis.com" in base
    )


def is_structured_output_mode(response_format: dict | None) -> bool:
    if not response_format:
        return False
    fmt_type = response_format.get("type")
    return fmt_type in ("json_object", "json_schema")


class GemmaProvider:
    name = "gemma"

    def __init__(self, settings: Settings):
        self._settings = settings

    def _should_disable_thinking(self) -> bool:
        if self._settings.llm_enable_thinking:
            return False
        return self._settings.llm_disable_thinking

    def is_available(self) -> bool:
        return bool(self._settings.llm_api_key.strip())

    def _build_payload(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: dict | None = None,
        stream: bool = False,
    ) -> dict:
        payload: dict = {
            "model": self._settings.llm_model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature if temperature is not None else self._settings.llm_temperature,
            "max_tokens": max_tokens if max_tokens is not None else self._settings.llm_max_tokens,
        }
        if stream:
            payload["stream"] = True
        if self._should_disable_thinking():
            payload.setdefault("extra_body", {})
            payload["extra_body"].setdefault("chat_template_kwargs", {})
            payload["extra_body"]["chat_template_kwargs"]["enable_thinking"] = False
        if response_format:
            payload["response_format"] = response_format
        return payload

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._settings.llm_api_key}",
            "Content-Type": "application/json",
        }

    def _extract_delta(self, data: dict) -> str:
        choices = data.get("choices") or []
        if not choices:
            return ""
        delta = choices[0].get("delta") or {}
        return delta.get("content") or ""

    def _extract_message_content(self, message: dict) -> str:
        content = message.get("content") or ""
        if content.strip():
            return content
        reasoning = message.get("reasoning") or ""
        return reasoning if isinstance(reasoning, str) else ""

    def chat(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: dict | None = None,
    ) -> LLMResponse:
        if not self.is_available():
            raise RuntimeError("Gemma API key 未配置")

        url = f"{self._settings.llm_base_url.rstrip('/')}/chat/completions"
        payload = self._build_payload(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )

        with httpx.Client(timeout=self._settings.llm_timeout) as client:
            response = client.post(url, json=payload, headers=self._headers())
            response.raise_for_status()
            data = response.json()

        message = data["choices"][0]["message"]
        content = self._extract_message_content(message)
        if not content.strip():
            raise RuntimeError("Gemma 返回内容为空")
        return LLMResponse(
            content=content,
            provider=self.name,
            model=data.get("model") or self._settings.llm_model,
        )

    def chat_stream(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: dict | None = None,
    ) -> Iterator[str]:
        if not self.is_available():
            raise RuntimeError("Gemma API key 未配置")

        url = f"{self._settings.llm_base_url.rstrip('/')}/chat/completions"
        payload = self._build_payload(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
            stream=True,
        )
        structured_mode = is_structured_output_mode(response_format)
        buffer = ""

        with httpx.Client(timeout=self._settings.llm_timeout) as client:
            with client.stream("POST", url, json=payload, headers=self._headers()) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data_str = line[5:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
                    delta = self._extract_delta(data)
                    if not delta:
                        continue
                    buffer += delta
                    if not structured_mode:
                        yield delta

        if structured_mode and buffer.strip():
            yield buffer
