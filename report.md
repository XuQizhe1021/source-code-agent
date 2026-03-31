# 阶段1：仓库初始化

## 做了什么
- 在项目根目录初始化 Git 仓库，并将主分支设置为 `main`。
- 按兼容方式配置远程仓库 `origin` 为 `https://github.com/XuQizhe1021/source-code-agent.git`（若已存在则更新 URL，不存在则新增）。
- 检查并维护 `.gitignore`，确保日志、依赖目录、缓存目录与运行数据目录不会被提交。
- 准备首次提交内容，用于推送到 `origin/main`。

## 遇到的问题与解决
- 问题：执行 Git 状态检查时提示当前目录不是 Git 仓库。  
  解决：先执行仓库初始化，再统一设置主分支为 `main`。
- 问题：远程仓库配置在重复执行时可能发生冲突（`origin` 可能已存在）。  
  解决：采用“存在则 `set-url`，不存在则 `add`”的兼容处理，保证流程可重复执行。

## 阶段优化点
- 是什么：将初始化与远程配置流程改为幂等脚本化步骤。  
- 为什么可优化：手动流程容易因重复执行、分支名不一致或远程冲突导致失败。  
- 如何优化：统一执行“初始化→分支标准化→远程兼容配置→验证输出”的固定顺序，并在每阶段同步维护 `.gitignore`。  
- 结果：阶段执行可重复、可追踪，且可直接推送到 `origin/main`，减少后续阶段的环境偏差风险。

# 阶段2：项目初探与本地跑通（requirements 模式）

## 执行过程
1. 阅读 `lab1_basic_and_testing.md` 的任务1要求与 `README.md`，确认本阶段以 `requirements.txt` 为依赖入口，启动命令为 `python run.py`。
2. 复制环境模板：`Copy-Item .env.example .env`。
3. 执行 `python -m pip install -r requirements.txt`，首次安装失败，报错聚焦在 `pillow==10.0.0` 与当前 Python 3.13 环境兼容性。
4. 再次启动服务时发现 `.env` 中 `CORS_ORIGINS` 格式不符合 `pydantic-settings` 对复杂类型的解析要求，将其改为 JSON 数组格式后继续。
5. 按运行日志补齐缺失依赖（`modelscope`、`pymilvus`），再次启动后服务进入可用状态，`/docs` 返回 200 且页面包含 Swagger UI。

## 依赖补齐记录
- 基础安装命令：`python -m pip install -r requirements.txt`。
- 运行时发现缺失并补齐：
  - `modelscope`（`ModuleNotFoundError: No module named 'modelscope'`）
  - `pymilvus`（日志提示向量存储模块不可用）
- 依赖冲突/兼容性记录：
  - `pillow==10.0.0` 在 Python 3.13 下构建失败，属于版本兼容性问题。
  - `mineru[core]` 与 `pypdf==3.15.5` 存在依赖约束冲突（`mineru` 需要更高版本 `pypdf`）。
- 结论：当前服务启动不依赖上述冲突路径，可在后续阶段通过统一版本策略（锁定 Python 与包版本）系统化处理。

## 项目结构梳理（简要）
- `app/main.py`：FastAPI 应用入口，挂载 API 路由。
- `app/api/v1/`：接口层，`api.py` 聚合各 endpoint。
- `app/models/`、`app/schemas/`：数据模型与请求/响应模型。
- `app/utils/`：核心工具与业务辅助逻辑（包含配置、知识库、图谱、文件处理等）。
- `run.py`：本地启动脚本，同时拉起 API 服务与 MCP 相关进程。

## 冗余代码分析（5处）
1. `app/api/v1/endpoints/agents.py`：`chat_with_agent` 与 `chat_with_agent_api` 的核心生成逻辑大段重复，维护成本高，后续修复易出现行为漂移。  
   风险：双分支代码不一致导致线上行为不可预测。
2. `app/api/v1/endpoints/agents.py`：`chat_with_agent` 中对 `agent` 的判空存在重复分支（先 404 后 500），语义冲突。  
   风险：错误码语义混乱，增加排障难度。
3. `app/api/v1/endpoints/agents.py`：响应流处理中存在 `except Exception: pass` 的吞异常写法。  
   风险：数据丢失被静默掩盖，问题难以监控与定位。
4. `app/utils/agent.py`：`get_agent_by_share_token` 对查询结果缺少空值/状态保护即直接自增计数。  
   风险：无效 token 场景触发 500，且可能绕过状态约束。
5. `app/utils/agent.py`：导入 `get_graph` 后又定义同名包装函数，命名冲突与重复封装并存。  
   风险：可读性下降，重构时易误调用或引入依赖问题。

## 阶段优化点
- 是什么：将“依赖安装→启动→按日志补齐→可访问性验证”沉淀为标准化诊断闭环。
- 为什么可优化：当前依赖声明存在版本冲突与 Python 版本兼容问题，单次安装并不能保证可运行。
- 怎么优化：在后续阶段引入“解释器版本约束 + 依赖锁定 + 启动前自检脚本（环境变量/关键依赖/端口）”，并把冲突包拆分为可选依赖组。
- 结果：本阶段已在 requirements 模式下完成可运行闭环，`/docs` 可访问，且问题清单具备后续整改输入价值。

## 尝试启动成功后，当前项目详细启动流程
1. 准备环境文件：确保根目录存在 `.env`，`CORS_ORIGINS` 使用 JSON 数组格式。
2. 安装依赖：先执行 `python -m pip install -r requirements.txt`，若失败按报错补齐缺失包。
3. 启动服务：`python run.py`。
4. 启动日志判定：
   - 出现 `启动API服务 - 监听 0.0.0.0:8000`
   - 出现 `Uvicorn running on http://0.0.0.0:8000`
   - 出现 `Application startup complete`
5. 文档验证：访问 `http://127.0.0.1:8000/docs`，期望 `Status=200` 且页面包含 `Swagger UI`。

# 阶段3：迁移到 Poetry 并重构环境

## 执行过程
1. 使用 `python -m poetry init -n` 初始化 Poetry 工程，生成 `pyproject.toml`。
2. 分批迁移主依赖并生成 `poetry.lock`，在迁移中处理版本冲突：
   - `neo4j-graphrag==1.3.0` 约束 `neo4j<6`，因此将 `neo4j` 调整为 `>=5.17,<6.0`。
   - `magic-pdf` 与 `pydantic` 存在版本约束差异，因此将 `pydantic` 调整到 `>=2.10,<2.11`。
   - `mineru` 与 `neo4j-graphrag` 在 `json-repair` 版本上互斥，当前锁定方案优先保证项目可运行与核心链路可用，暂不纳入 `mineru`。
3. 添加开发依赖组：`pytest`、`pytest-asyncio`。
4. 补齐 MinIO 运行环境：
   - 新增 `docker-compose.minio.yml` 并拉起容器；
   - 更新 `.env.example` 的 MinIO 配置项；
   - 验证 `http://127.0.0.1:9000` 可访问（200）。
5. 使用 `python -m poetry run python run.py` 启动验证，并通过 `/docs` 连通性验证。

## 迁移前后对比
- 迁移前：`requirements.txt + pip`，缺少统一锁文件，跨机器/跨时间安装结果可能漂移，冲突定位成本高。
- 迁移后：`pyproject.toml + poetry.lock`，依赖解析结果可复现，主依赖与开发依赖分层清晰，环境构建稳定性更高。

## 依赖管理优化价值
- 可复现：锁文件固定完整依赖树，减少“我这里能跑你那里不行”。
- 可维护：依赖冲突在解析阶段暴露，便于集中修复而不是运行时踩坑。
- 可协作：`dev` 依赖分组后，测试工具不会污染生产依赖面。
- 可演进：后续可继续拆分可选功能依赖组（如图谱、文档解析）降低基础安装成本。

## 阶段优化点
- 是什么：建立“Poetry 锁定 + 分组依赖 + MinIO 一键拉起”的标准化开发环境。
- 为什么：原有 requirements 流程存在版本漂移、冲突滞后暴露、外部服务缺失导致的运行告警。
- 怎么优化：统一使用 Poetry 管理依赖，新增 MinIO compose 文件与 `.env.example` 配置模板，并通过 `poetry run` 做启动验收。

## 启动流程（Poetry 主流程）
1. `python -m poetry install`
2. `Copy-Item .env.example .env`
3. `docker compose -f docker-compose.minio.yml up -d`
4. `python -m poetry run python run.py`
5. 访问 `http://127.0.0.1:8000/docs` 验证服务可用

## 阶段3补充：依赖清理与回归
- 本轮先扫描全仓导入与运行路径，再清理高置信度未使用依赖，并同步更新 `pyproject.toml` 与 `poetry.lock`。
- 已删除依赖：`alembic`、`psycopg2-binary`、`google-genai`、`neo4j-graphrag`、`fastmcp`。
- 清理后启动回归时出现 `ModuleNotFoundError: sse_starlette`，说明该包虽由其他包间接提供过，但项目代码存在直接导入，因此已改为显式主依赖补回：`sse-starlette`。
- `.gitignore` 持续维护：新增 `.ruff_cache/`、`*.db`、`*.sqlite3`，避免本地缓存与数据库文件误提交。
- 回归结果：`python -m poetry run python run.py` 可启动，`/docs` 可访问并返回 `200`，说明未误删真实运行所需依赖。

# 阶段4：建立基础测试安全网（pytest）

## 用例设计思路
- 选取 `app/utils` 中低耦合但高复用的核心函数，优先覆盖响应构造、时间处理、图标映射三类基础能力。
- 以“Happy Path + 边界/异常路径”双轨设计：
  - Happy Path：标准输入下返回结构、默认值与格式是否符合预期；
  - 边界/异常：`None`、未知映射、非目标后缀、时区输入差异等场景下行为是否稳定。
- 本阶段共覆盖 9 个测试点，涉及至少 5 个核心函数：`standard_response`、`success_response`、`error_response`、`utc_to_cst`、`format_datetime`、`get_icon_filename`、`extract_icon_from_url` 等。

## 失败到通过的修复过程
1. 首次执行 `python -m poetry run pytest -v` 失败，报错 `ModuleNotFoundError: No module named 'app'`，属于测试运行路径未包含项目根目录。
2. 新增 `tests/conftest.py`，在测试启动时将项目根目录加入 `sys.path`。
3. 二次执行 `python -m poetry run pytest -v` 全部通过（9 passed）。

## 阶段优化点
- 是什么：建立可重复执行的基础测试安全网，覆盖核心工具函数的主路径与边界路径。
- 为什么：`app/utils` 被多处业务调用，缺少测试会导致小改动引发隐蔽回归，且不易第一时间发现。
- 怎么优化：以轻量单测先覆盖稳定纯函数，再逐步扩展到更高耦合模块；同时固定 `poetry run pytest -v` 作为每阶段的回归门槛。

# 阶段5：覆盖率与工程化强化（对齐80分档）

## 覆盖率数据
- 已引入 `pytest-cov`（dev 依赖），并执行覆盖率命令：
  - `python -m poetry run pytest -v --cov=app.utils.config --cov=app.utils.response --cov=app.utils.provider_icon_mapper --cov-report=term-missing`
- 结果：
  - `app/utils/config.py`：`82%`
  - `app/utils/provider_icon_mapper.py`：`91%`
  - `app/utils/response.py`：`100%`
  - 关键模块总覆盖率：`86%`

## 用例扩展与薄弱区分析
- 本阶段新增 `tests/utils/test_config_utils.py`，覆盖配置解析、配置更新持久化、默认模板隔离等关键路径。
- 保留并复用阶段4的 `tests/utils/test_core_utils.py`，覆盖字符串映射、格式转换与统一响应构造。
- 薄弱区主要在 `config.py` 的异常分支（如读写失败日志路径）与 `provider_icon_mapper.py` 的异常解析分支，后续可通过 mock 文件异常与 URL 解析异常继续提高覆盖率。

## 抓到的 issue（现象 / 根因 / 修复）
- 现象：新增“默认配置模板不应被运行时环境污染”测试后失败，`DEFAULT_CONFIG` 被 `load_config()` 调用后意外修改。
- 根因：`load_config()` 使用浅拷贝 `DEFAULT_CONFIG.copy()`，嵌套字典与默认模板共享引用，环境变量写入时污染了默认模板。
- 修复：将浅拷贝改为深拷贝，并在补默认键时对整段默认配置使用深拷贝，避免引用共享；修复后测试通过。

## 阶段优化点
- 是什么：把“覆盖率统计 + 问题发现 + 代码修复”串成闭环流程。
- 为什么：仅有通过/失败无法衡量测试质量，覆盖率与缺口分析能指导测试投入优先级。
- 怎么优化：持续按关键模块维护覆盖率基线（≥80%），每次新增测试都要求至少覆盖一个边界/异常路径，并把失败修复过程沉淀到报告中。

# 阶段6（可选）：可测试性重构与Mock（冲刺100分）

## 不可测试点识别与原因
- 目标点：`app/utils/web_search.py` 中 `WebSearchClient.search()` 与 `get_web_search_client()`。
- 不可测试原因：
  - `search()` 内部直接实例化 `TavilyClient`，强耦合外部网络客户端，单测无法稳定隔离。
  - `get_web_search_client()` 固定直接构造 `WebSearchClient`，难以在测试中注入替身对象验证异常路径与单例行为。

## 重构前后对比
- 重构前：
  - `WebSearchClient.__init__` 仅接收 `api_key`。
  - `search()` 内部硬编码 `TavilyClient(api_key=...)`。
  - `get_web_search_client()` 无法注入自定义工厂。
- 重构后（保持行为兼容）：
  - `WebSearchClient.__init__` 新增 `tavily_client_factory` 可选参数，默认仍为 `TavilyClient`。
  - `search()` 改为通过注入工厂创建客户端，默认路径行为不变。
  - `get_web_search_client()` 新增可选 `client_factory`，默认仍创建 `WebSearchClient`，但测试可注入替身。

## 可测试性提升分析
- 新增 `tests/utils/test_web_search_utils.py`，使用 Mock/替身类覆盖：
  - 外部客户端成功返回路径；
  - 外部客户端抛异常的回退路径；
  - 文本格式化空结果/非空结果路径；
  - 单例缓存与注入工厂路径；
  - 工厂抛 `ValueError` 转换为 `HTTPException` 路径。
- 结果：无需真实网络请求即可稳定验证核心行为，降低测试脆弱性并提升回归速度。

## 阶段优化点
- 是什么：将外部依赖从“内部硬编码创建”重构为“可注入工厂”。
- 为什么：强耦合外部客户端会导致单测不稳定、难覆盖异常分支，回归成本高。
- 怎么优化：在不改变默认行为的前提下为构造点提供依赖注入入口，并配合 Mock 覆盖关键分支。
