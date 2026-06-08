"""Harness 全局配置：模型、路径、MongoDB Checkpointer。"""

from datetime import timedelta
from pathlib import Path
from typing import Literal

import httpx
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.store.memory import InMemoryStore
from pymongo import MongoClient

from agent.env_utils import (
    AGENT_API_KEY,
    AGENT_BASE_URL,
    AGENT_MODEL,
    MONGODB_CHECKPOINT_COLLECTION,
    MONGODB_DB_NAME,
    MONGODB_URI,
    SANDBOX_DOMAIN,
)


def _is_gemma_agent_endpoint() -> bool:
    model = (AGENT_MODEL or "").lower()
    base = (AGENT_BASE_URL or "").lower()
    return (
        "gemma" in model
        or "deepinfra.com" in base
        or "generativelanguage.googleapis.com" in base
    )


def build_chat_model(role: Literal["main", "summary"]) -> ChatOpenAI:
    """按角色构建 ChatOpenAI；Gemma 4 Agent 关闭 thinking 并采用推荐采样参数。"""
    if role == "main":
        temperature = 1.0
        max_tokens = 8192
    else:
        temperature = 0.3
        max_tokens = 4096

    kwargs: dict = {
        "model": AGENT_MODEL,
        "temperature": temperature,
        "openai_api_key": AGENT_API_KEY,
        "openai_api_base": AGENT_BASE_URL,
        "max_tokens": max_tokens,
    }
    if _is_gemma_agent_endpoint():
        kwargs["model_kwargs"] = {
            "extra_body": {"chat_template_kwargs": {"enable_thinking": False}}
        }
    return ChatOpenAI(**kwargs)


# ---------- 模型配置 ----------
MAIN_MODEL = build_chat_model("main")
SUMMARY_MODEL = build_chat_model("summary")

# ---------- 沙箱配置（Phase 0 可选） ----------
SANDBOX_CONFIG = None
if SANDBOX_DOMAIN:
    from opensandbox.config import ConnectionConfigSync

    SANDBOX_CONFIG = ConnectionConfigSync(
        domain=SANDBOX_DOMAIN,
        use_server_proxy=True,
        request_timeout=timedelta(seconds=60),
        transport=httpx.HTTPTransport(limits=httpx.Limits(max_connections=20)),
    )

# ---------- 路径常量 ----------
BACKEND_DIR = Path(__file__).resolve().parent.parent
AGENT_DIR = BACKEND_DIR / "agent"
LOCAL_SKILLS_DIR = BACKEND_DIR / "skills"
LOCAL_SUBAGENT_CONFIG_DIR = AGENT_DIR / "subagents" / "configs"
LOCAL_AGENTS_MD = AGENT_DIR / "memory" / "AGENTS.md"
LOCAL_WORKSPACE_DIR = BACKEND_DIR / "agent_workspace"
DOWNLOAD_DIR = BACKEND_DIR / "download"

SANDBOX_SKILLS_ROOT = "/skills"
SANDBOX_MEMORIES_ROOT = "/memories"
AGENTS_MD_FILENAME = "/AGENTS.md"
USER_PREFERENCES_FILENAME = "preferences.md"
PERSISTED_SKILLS_ROOT = "/persisted-skills"
SKILLS_STORE_NAMESPACE = ("skills",)

SCOPE_MAP = {
    "main": "main",
    "clinical-assistant": "clinical",
    "followup-executor": "followup",
}

# ---------- 持久化存储 ----------
STORE = InMemoryStore()

_mongodb_client: MongoClient | None = None
CHECKPOINTER = None

try:
    _mongodb_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
    _mongodb_client.admin.command("ping")
    CHECKPOINTER = MongoDBSaver(
        client=_mongodb_client,
        db_name=MONGODB_DB_NAME,
        checkpoint_collection_name=MONGODB_CHECKPOINT_COLLECTION,
    )
except Exception as exc:
    import logging

    logging.getLogger(__name__).warning(
        "MongoDB 不可用 (%s)，回退到 MemorySaver（HITL 续跑不可用）", exc
    )
    from langgraph.checkpoint.memory import MemorySaver

    CHECKPOINTER = MemorySaver()
