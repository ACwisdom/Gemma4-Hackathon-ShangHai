演示视频：https://www.bilibili.com/video/BV1SBEb6yEjM

# DocClaw · 医疗 AI 工作台

DocClaw（目标产品名 **DoctorClaw**）是一个面向医生的医疗 Skills 管理平台：医生可启用、自定义、发布 AI 技能，在问诊过程中获得实时辅助，并管理随访等计划性任务。

> 代码仓库为 **DocClaw** MVP；终局愿景为基于国产算力的 **DoctorClaw 医疗智能体平台**（Skills 引擎 + 患者连续管理 + 科室 SkillsHub）。

---

## 核心能力

| 模块 | 说明 |
|------|------|
| **患者队列** | 今日问诊列表，支持状态 / 类型筛选 |
| **问诊工作台** | Skill 模式 + Agent 模式双轨；门诊病历结构化、检查结果分析 |
| **个人技能** | 管理本地 AI 技能，启用 / 停用 / 发布 |
| **技能广场** | 浏览、获取其他医生分享的技能及 [ClawHub](https://clawhub.ai/) 开放技能 |
| **随访计划** | 创建随访计划，APScheduler 自动 / 手动执行 |
| **通知中心** | 任务提醒与系统通知 |

### 病历结构化（核心 Skill）

问诊页 **Skill 模式** 下，触发「帮我输出病历」等意图时，走 **Skill Runtime 短路**：

```
问诊对话 + 患者上下文
  → 单次 LLM 调用（JSON Schema）
  → Pydantic 校验 + field_diff 事实比对
  → SSE 推送结构化结果
  → 医生 HITL 确认
```

**AI 引擎**：**Gemma 4 31B**（`google/gemma-4-31B-it`）驱动病历结构化；详见 [`病历结构化Skill最小算力与模型配置说明.md`](./病历结构化Skill最小算力与模型配置说明.md)（[Word 版](./病历结构化Skill最小算力与模型配置说明.docx)）。

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React · TypeScript · Vite · React Router |
| 业务 API | FastAPI · SQLAlchemy · SQLite · APScheduler |
| AI / Skill | Gemma 4 · json_schema Structured Output · SSE 流式 |
| Agent Harness | DeepAgents · LangGraph · MCP · HITL |

---

## 架构概览

问诊工作台支持两条 AI 通路：

| 通路 | 触发 | 执行路径 |
|------|------|----------|
| **A. Skill Runtime** | Skill 模式 + 病历意图 | 单次 Structured Output，Schema 质量优先 |
| **B. DeepAgents Harness** | Agent 模式 | 主 Agent → 子 Agent → MCP 工具 → HITL |

### 服务与端口

| 服务 | 端口 | 说明 |
|------|------|------|
| Medical API | 8000 | 患者、问诊、技能、随访等业务 |
| MCP Server | 8001 | Agent 工具层 |
| Agent API | 8090 | SSE 对话 + HITL `/resume` |
| Frontend | 5173 | 医生工作台 UI |

---

## 依赖安装

本项目依赖分三部分，安装路径如下：

| 依赖类型 | 文件路径 | 安装命令 |
|----------|----------|----------|
| **主 Python 依赖**（业务 API） | [`backend/requirements.txt`](./backend/requirements.txt) | `pip install -r backend/requirements.txt` |
| **Agent Harness 依赖**（可选，Agent 模式） | [`backend/requirements-agent.txt`](./backend/requirements-agent.txt) | `pip install -r backend/requirements-agent.txt` |
| **前端依赖** | [`frontend/package.json`](./frontend/package.json) | `cd frontend && npm install` |

**安装方式（二选一）**：

```bash
# 方式 1：在项目根目录安装主 Python 依赖（根目录 requirements.txt 会引用 backend/）
pip install -r requirements.txt

# 方式 2：在 backend 目录安装
cd backend
pip install -r requirements.txt
```

Agent Harness 需在 `backend` 目录额外安装（Python 3.11+）：

```bash
cd backend
pip install -r requirements-agent.txt
```

---

## 快速启动

### 环境要求

- Python 3.11+（Harness 依赖）
- Node.js 18+
- （可选）MongoDB — HITL 跨请求续跑
- （可选）`LLM_API_KEY` — 未配置时使用 mock 降级

### 一键启动（Windows）

```bat
start.bat
```

### 手动启动

```bash
# 1. 业务后端（也可在根目录：pip install -r requirements.txt）
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 2. 前端
cd frontend
npm install
npm run dev

# 3. Agent Harness（可选）
cd backend
pip install -r requirements-agent.txt
py -3.11 start_agent.py
```

访问 **http://localhost:5173**

### LLM 配置（Gemma 4 云端，推荐 DeepInfra）

复制 `backend/.env.example` 为 `backend/.env` 后配置：

```env
# Skill Runtime — 病历结构化
LLM_PROVIDER=gemma
LLM_BASE_URL=https://api.deepinfra.com/v1/openai
LLM_API_KEY=<your-token>
LLM_MODEL=google/gemma-4-31B-it
LLM_TEMPERATURE=0.3
LLM_STRUCTURED_OUTPUT_MODE=json_schema
LLM_ENABLE_THINKING=false
LLM_FALLBACK_TO_MOCK=true

# Agent Harness — 工具调用
AGENT_MODEL=google/gemma-4-26B-A4B-it
AGENT_BASE_URL=https://api.deepinfra.com/v1/openai
AGENT_API_KEY=<your-token>
```

未配置 Key 时自动降级 Mock Provider，演示不中断。

---

## 页面路由

| 路由 | 说明 |
|------|------|
| `/queue` | 患者队列 |
| `/skills` | 个人技能 |
| `/skills/new` | 创建技能 |
| `/store` | 技能广场 |
| `/consult/:slug` | 问诊工作台 |
| `/followup` | 随访计划 |
| `/notifications` | 通知中心 |

API 文档：启动后端后访问 http://localhost:8000/docs

---

## 项目结构

```
DocClaw/
├── README.md                              # 本文件
├── requirements.txt                       # 主 Python 依赖入口（引用 backend/）
├── PROJECT_CONTEXT.md                     # 项目全景与架构说明
├── HARNESS_PLAN.md                        # DeepAgents 分期实施计划
├── DEMO.md                                # 演示与验收步骤
├── 病历结构化Skill最小算力与模型配置说明.md  # 算力 / 模型配置说明
├── start.bat                              # Windows 一键启动
├── run_acceptance.bat                     # Phase 5 验收入口
├── frontend/                              # React 前端
├── backend/
│   ├── app/                               # 业务 API（:8000）
│   │   ├── medical_record/                # 病历 Schema、Prompt、校验
│   │   ├── services/skill_runtime*.py     # Skill 执行与流式
│   │   └── services/llm/                  # Gemma 4 Provider + mock 降级
│   ├── agent/                             # DeepAgents Harness（:8090）
│   ├── skills/                            # 技能手册（clinical / clawhub）
│   └── scripts/                           # 验收、ClawHub 同步等脚本
└── scripts/
    └── md_to_docx.py                      # Markdown → Word 转换工具
```

---

## 文档索引

| 文档 | 用途 |
|------|------|
| [`PROJECT_CONTEXT.md`](./PROJECT_CONTEXT.md) | 目标蓝图、架构缺口、分阶段 Plan、API 清单 |
| [`HARNESS_PLAN.md`](./HARNESS_PLAN.md) | DeepAgents Harness Phase 0–6 实施详表 |
| [`DEMO.md`](./DEMO.md) | 6 步演示闭环与验收 |
| [`病历结构化Skill最小算力与模型配置说明.md`](./病历结构化Skill最小算力与模型配置说明.md) | 病历 Skill 最小算力与模型参数 |
| [`录屏演示指南.md`](./录屏演示指南.md) | 录屏演示操作指引 |
| [`技术报告.docx`](./技术报告.docx) | Gemma 4 模型选型与架构设计 |

---

## 验收与演示

```bat
run_acceptance.bat
```

或：

```bash
cd backend
python scripts/e2e_acceptance.py
python scripts/e2e_acceptance.py --with-llm --with-agent
```

详见 [`DEMO.md`](./DEMO.md)。

---

## ClawHub 技能同步

启动后端时自动从 ClawHub 拉取医疗相关开放技能（幂等）。手动同步：

```bash
cd backend
python scripts/import_clawhub_skills.py
python scripts/import_clawhub_skills.py --slug pubmed-search-skill
```

或在技能广场点击「同步 ClawHub」，或调用 `POST /api/store/sync-clawhub`。

---

## 当前限制（MVP）

- 无登录 / 多租户，固定「李医生」演示账号
- HIS 为 Mock，无真实 EMR 写入
- 知识层 / RAG 未接入
- 默认 DeepInfra 云端 Gemma 4 API，本地 vLLM 可按同端点切换
- MongoDB 未部署时 HITL 跨刷新续跑不稳定

---

## 参赛提交说明

本项目按 Gemma 4 Good Hackathon 上海站 **方式 A：Fork & PR** 提交。

### 提交路径

请将本仓库内容提交至官方仓库以下目录：

```
submissions/2026/track_A/DoctorClaw/
```

目录内应包含：`README.md`（含环境安装步骤）、`requirements.txt`、核心源码（`backend/`、`frontend/` 等）。

### PR 标题格式

```
[赛道A] DoctorClaw - <队伍名>
```

示例：`[赛道A] DoctorClaw - 某某战队`（请将 `<队伍名>` 替换为实际队伍名称）

### 提交流程

1. **Fork** 官方 Gemma4 Hackathon 仓库到你的 GitHub 账号
2. 将本项目放入 `submissions/2026/track_A/DoctorClaw/` 后 **提交 Pull Request**
3. **队长** 在现场赛材料表单中填写 PR 链接等信息（Git/Fork/PR 由参赛者自行完成）

### 提交前检查清单

- [ ] `README.md` 已包含依赖安装与快速启动说明
- [ ] 根目录 `requirements.txt` 可正常引用 `backend/requirements.txt`
- [ ] 核心源码完整（`backend/`、`frontend/` 等）
- [ ] **勿提交** `backend/.env`、`.env` 等密钥文件（参考 `.gitignore`）
- [ ] **勿提交** `frontend/node_modules/`、`frontend/dist/`、`*.db` 等生成物
- [ ] **勿提交** 本地 IDE 配置（如 `.cursor/`）
- [ ] PR 标题符合 `[赛道A] DoctorClaw - <队伍名>` 格式

---

## 相关链接

- ClawHub 技能市场：https://clawhub.ai/

---

**最后更新**：2026-06-08
