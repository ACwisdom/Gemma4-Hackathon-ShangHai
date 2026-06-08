"""Harness 环境变量加载。"""

import os

from dotenv import load_dotenv

load_dotenv(override=True)

# Agent 模型（与 Skill Runtime 共用 Gemma 4 云端端点，可按角色拆分型号）
AGENT_API_KEY = os.getenv("AGENT_API_KEY") or os.getenv("LLM_API_KEY")
AGENT_BASE_URL = os.getenv(
    "AGENT_BASE_URL",
    os.getenv("LLM_BASE_URL", "https://api.deepinfra.com/v1/openai"),
)
AGENT_MODEL = os.getenv(
    "AGENT_MODEL",
    os.getenv("LLM_MODEL", "google/gemma-4-26B-A4B-it"),
)

# 可选：Web 搜索增强（文献检索优先使用 PubMed Skill）
WEB_SEARCH_API_KEY = os.getenv("WEB_SEARCH_API_KEY", "")

# MongoDB
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB", "doctorclaw_agent")
MONGODB_CHECKPOINT_COLLECTION = os.getenv(
    "MONGODB_CHECKPOINT_COLLECTION", "checkpoints"
)

# MCP / 业务 API
MEDICAL_API_BASE_URL = os.getenv(
    "MEDICAL_API_BASE_URL", "http://localhost:8000/api"
)
MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8001"))
MCP_PATH = os.getenv("MCP_PATH", "/mcp")
MCP_URL = os.getenv("MCP_URL", f"http://{MCP_HOST}:{MCP_PORT}{MCP_PATH}")

# Agent API
AGENT_API_PORT = int(os.getenv("AGENT_API_PORT", "8090"))

# Sandbox（Phase 4 前可留空，使用本地 backend 降级）
SANDBOX_DOMAIN = os.getenv("SANDBOX_DOMAIN", "")
