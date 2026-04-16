# Source Code Agent Backend

一个基于 FastAPI 的后端系统，聚焦于模型管理、智能体对话、知识库检索、图谱增强与数据源能力编排。

## 目录
- [项目简介](#项目简介)
- [核心能力](#核心能力)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [运行方式](#运行方式)
- [测试与质量检查](#测试与质量检查)
- [API 文档与测试工作台](#api-文档与测试工作台)
- [扩展指南](#扩展指南)
- [常见问题](#常见问题)
- [相关文档](#相关文档)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 项目简介
本项目提供统一的 AI 后端能力层，主要解决以下问题：
- 统一管理多模型提供商（OpenAI / Anthropic / Ollama / Google / Local / Custom）。
- 为智能体对话提供统一编排流程，支持联网检索、知识库检索、图谱检索增强。
- 提供知识库文件处理、向量检索与知识图谱相关接口。
- 提供数据源连接与 SQL 执行能力，支撑数据问答和结构化检索场景。

## 核心能力
- 模型管理：模型增删改查、连接测试、Provider 动态扫描与热加载。
- 智能体管理：智能体配置、会话历史、API Key 与分享 Token 能力。
- RAG 能力：文件解析、切分、嵌入、检索，以及知识增强注入。
- 图谱能力：图谱实体/关系管理，Neo4j 相关检索与可视化支撑。
- 数据源能力：MySQL / PostgreSQL 连接、结构读取、查询执行。
- 工程能力：异步处理、Pydantic 校验、FastAPI 自动文档。

## 技术栈
- 语言与运行时：Python `3.11 ~ 3.13`
- Web 框架：FastAPI + Uvicorn
- ORM：SQLAlchemy
- 配置管理：Pydantic Settings + `.env`
- 异步网络：aiohttp / httpx
- 存储与中间件：MySQL/PostgreSQL、MinIO、Neo4j（可选）
- 测试：pytest + pytest-asyncio

## 项目结构
```text
source_code_agent/
├── app/
│   ├── api/v1/endpoints/        # 各业务 API 入口
│   ├── application/             # 应用层（ACL、事件、图谱/知识服务）
│   ├── domain/                  # 领域对象（会话上下文、会话记忆策略）
│   ├── providers/               # 可插拔模型 Provider
│   ├── services/                # 编排与策略服务
│   ├── models/                  # SQLAlchemy 模型
│   ├── schemas/                 # Pydantic 模型
│   ├── utils/                   # 工具与适配能力
│   └── main.py                  # FastAPI 应用入口
├── tests/                       # 自动化测试
├── testapi/                     # 前端 API 测试工作台
├── docker-compose.minio.yml     # MinIO 启动配置
├── run.py                       # 启动脚本（含 MCP 子进程启动）
├── mcp_services.py              # MCP 服务进程入口
├── pyproject.toml               # 依赖与项目元信息
└── README.md
```

## 快速开始

### 1. 克隆与进入目录
```bash
git clone <your-repo-url>
cd source_code_agent
```

### 2. 安装 Poetry
```bash
python -m pip install --user poetry
```

### 3. 安装依赖
```bash
python -m poetry install
```

### 4. 准备环境变量
```bash
copy .env.example .env
```
如果你使用 PowerShell，也可以：
```powershell
Copy-Item .env.example .env
```

### 5. 启动可选依赖（推荐 MinIO）
```bash
docker compose -f docker-compose.minio.yml up -d
```

### 6. 启动服务
```bash
python -m poetry run python run.py
```

启动后默认访问：
- API 服务：`http://127.0.0.1:8000`
- Swagger：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`

## 配置说明

### `.env` 关键项
可参考 `.env.example`：
- `API_V1_STR`：API 前缀，默认 `/api`
- `PROJECT_NAME`：项目名
- `SECRET_KEY`：认证密钥（生产环境务必替换）
- `CORS_ORIGINS`：CORS 白名单
- `DATABASE_URI`：数据库连接串（可覆盖默认拼接逻辑）
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`：可选模型密钥
- `MINIO_ENDPOINT` / `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` / `MINIO_SECURE`

### `config.json` 关键项
`run.py` 会读取根目录 `config.json`（或 `CONFIG_FILE` 指定文件）：
- `host`：监听地址，默认 `0.0.0.0`
- `port`：监听端口，默认 `8000`
- `reload`：是否热重载，默认 `true`

## 运行方式

### 方式一：推荐（统一入口）
```bash
python -m poetry run python run.py
```
说明：该方式会先尝试拉起 `mcp_services.py` 子进程，再启动 FastAPI。

### 方式二：仅启动 API
```bash
python -m poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 测试与质量检查

### 单元测试
```bash
python -m poetry run pytest -q
```

### 指定模块测试
```bash
python -m poetry run pytest tests/services -q
python -m poetry run pytest tests/domain -q
```

### 语法快速检查
```bash
python -m py_compile app/main.py app/services/chat_orchestrator.py app/providers/base.py
```

## API 文档与测试工作台

### 在线 API 文档
- Swagger：`/docs`
- ReDoc：`/redoc`

### 本地测试工作台（`testapi/`）
```bash
python -m http.server 8090 --directory testapi
```
访问：`http://127.0.0.1:8090/`

## 扩展指南

### 新增模型 Provider
在 `app/providers/` 下新增模块并继承 `ModelProvider`，实现必要方法后重启服务即可被自动扫描加载。

最小示例：
```python
from typing import Any, Dict, List, Optional, Union, AsyncGenerator
from app.providers.base import ModelProvider


class DemoProvider(ModelProvider):
    @property
    def provider_id(self) -> str:
        return "demo"

    @property
    def provider_name(self) -> str:
        return "Demo Provider"

    @property
    def description(self) -> str:
        return "示例 Provider"

    @property
    def icon(self) -> Optional[str]:
        return None

    @property
    def default_base_url(self) -> Optional[str]:
        return None

    @property
    def supported_model_types(self) -> List[str]:
        return ["chat"]

    @property
    def features(self) -> List[str]:
        return ["demo"]

    async def test_connection(self, api_key: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        return self.build_success_result("ok")

    async def chat_completion(self, api_key: str, messages, model: str, **kwargs) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        return {"choices": [{"message": {"role": "assistant", "content": "hello"}}]}

    async def text_completion(self, api_key: str, prompt: str, model: str, **kwargs):
        return {"choices": [{"text": "hello"}]}

    async def embedding(self, api_key: str, text, model: str, **kwargs):
        return {"data": []}
```

## 常见问题
- `ModuleNotFoundError`：请确认在项目根目录执行命令，并使用 `python -m poetry run ...`。
- API 启动但访问失败：检查 `config.json` 中端口是否被占用。
- Provider 不显示：确认新增模块位于 `app/providers/`，且类继承 `ModelProvider` 并实现抽象方法。
- 数据库连接失败：优先检查 `DATABASE_URI` 或 `DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME`。

## 相关文档
- 架构优化建议：`架构优化建议.md`
- 架构改动记录：`架构改动文档.md`
- 继承/委派优化扫描：`继承与委派优化扫描报告.md`
- 现有补充说明：`README2.md`

## 贡献指南
- 分支策略：禁止直接推送主分支，统一从 `main` 拉取后创建功能分支，命名建议 `feature/*`、`fix/*`、`refactor/*`、`docs/*`。
- 代码风格：保持类型注解与清晰命名；复杂逻辑需补充必要中文注释；避免无边界的长函数与重复分支，优先小步重构。
- 接口变更：涉及请求/响应结构、状态码或权限逻辑时，必须同步更新接口文档与调用示例，并在 PR 描述中标注兼容性影响。
- 数据与配置变更：修改数据库模型、环境变量、`config.json` 读取逻辑时，必须提供迁移说明、默认值策略与回滚方案。
- 测试门槛：新增功能或缺陷修复必须附带对应测试；至少保证受影响模块通过 `pytest`；若存在暂不覆盖场景，需在 PR 中说明风险。
- 提交规范：Commit message 遵循 Conventional Commits，建议使用 `type(scope): subject`，示例见下方。
- PR 规范：一个 PR 聚焦一个主题，描述需包含变更动机、关键改动、验证步骤、影响范围；涉及 UI/接口行为变化时附截图或调用结果。
- 文档同步：只要有行为变更，必须同步更新根目录 `README.md` 与相关专题文档（如架构文档、实验文档）。

建议的提交流程：
```bash
git checkout main
git pull
git checkout -b feature/xxx
python -m poetry run pytest -q
git add -A
git commit -m "feat(scope): concise summary"
git push -u origin feature/xxx
```

Commit message 示例：
```text
feat(provider): add model retry policy for transient errors
fix(chat): normalize stream chunk parsing for ollama provider
refactor(service): extract graph query gateway from retrieval strategy
docs(readme): refine contribution guidelines and quality gates
test(services): add chat orchestrator regression cases
```

## 许可证
如需开源发布，建议在仓库根目录补充 `LICENSE` 文件并在此处声明许可证类型。
