from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, Protocol

MessageContent = str | list[dict[str, Any]]


@dataclass
class ChatMessage:
    role: str
    content: MessageContent


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str | None = None
    used_fallback: bool = False


def build_text_part(text: str) -> dict[str, str]:
    return {"type": "text", "text": text}


def build_image_url_part(url: str, *, detail: str = "auto") -> dict[str, Any]:
    return {"type": "image_url", "image_url": {"url": url, "detail": detail}}


def build_user_message_content(
    text: str,
    attachments: list[dict[str, str]] | None = None,
) -> MessageContent:
    """构建用户消息 content；无附件时返回纯文本，有附件时返回 OpenAI 多模态 parts。"""
    if not attachments:
        return text
    parts: list[dict[str, Any]] = [build_text_part(text)]
    for item in attachments:
        url = item.get("url", "").strip()
        if not url:
            continue
        parts.append(build_image_url_part(url))
    return parts if len(parts) > 1 else text


class LLMProvider(Protocol):
    name: str

    def is_available(self) -> bool: ...

    def chat(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: dict | None = None,
    ) -> LLMResponse: ...

    def chat_stream(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: dict | None = None,
    ) -> Iterator[str]: ...
