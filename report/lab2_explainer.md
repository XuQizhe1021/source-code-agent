# Lab2 讲解文档（OOP + ADT）

## 0. 文档定位
本文件面向初学者，按“为什么这样改、改了什么、怎么验证、常见坑与排查”的顺序持续记录实验二全过程。唯一评分依据为 `report/lab2_oop_and_adt.md`，所有实现与验证都必须可追溯到评分点。

## 1. 评分依据与达成策略
### 1.1 唯一依据
- `report/lab2_oop_and_adt.md`

### 1.2 执行策略
- 最小改造：优先在真实生效主链路做小切口接入
- 证据完整：每次改动都保留命令、日志、测试结果、文件路径
- 阶段闭环：现状确认 → 实现 → 测试 → 证据记录 → 文档更新

## 2. 阶段记录（持续更新）
### 阶段 1：需求解析与WBS拆解
#### 为什么这样做
先锁定评分项与真实生效路径，避免偏题和无效改造。

#### 改了什么
- 解析 `report/lab2_oop_and_adt.md`，抽取任务、评分与加分项约束
- 形成可执行 WBS、风险清单、验收清单
- 初始化本讲解文档与正式实验报告骨架

#### 怎么验证
- 验证文档存在且结构完整
- 验证后续每个阶段都能在本文件追加闭环记录

#### 常见坑与排查
- 坑：按经验改代码但未逐项映射评分点
- 排查：每次提交前对照评分矩阵检查“实现-证据-评分点”是否一一对应

### 阶段 2：项目现状与执行地图（小白版）
#### 为什么这样做
本阶段不写功能代码，只确认“系统到底走哪条线”，这样后续每一行改动都能落在真实生效链路上，避免改到旧文件或旁路实现。

#### 当前真实生效链路（从请求到模型）
- 应用入口：`run.py` 启动 `app.main:app`，`app/main.py` 通过 `app.include_router(api_router, prefix=settings.API_V1_STR)` 挂载 API
- 路由入口：`settings.API_V1_STR="/api"`，`app/api/v1/api.py` 挂载 `models.router` 与 `agents.router`
- Provider 注册链路：`app/providers/base.py`（`ModelProvider` 契约）→ `app/providers/manager.py`（扫描/加载/重载）→ `app/api/v1/endpoints/models.py`（`/models/providers*` 观测与重载）
- Model 创建链路：`app/api/v1/endpoints/models.py#create_new_model` → `app/utils/model.py#create_model`（内部调用 `provider_manager.get_provider` 校验 provider）
- Agent 调用链路：`app/api/v1/endpoints/agents.py#chat_with_agent` 与 `chat_with_agent_api` → `execute_model_inference`
- 消息组装链路：`agents.py` 中 `messages = chat_request.messages`，逐步构建 `final_messages`（系统提示、文件上下文、网络检索、知识检索、MCP结果、历史消息）后喂给模型推理

#### 最小改造点（文件级）
##### 必须改（60/80分主线）
- `app/providers/*.py`（新增一个 Provider 实现文件，遵守 `ModelProvider` 抽象契约）
- `app/api/v1/endpoints/agents.py`（将 ADT 接入至少一段 `final_messages` 真实构造流程）
- `app/domain/session_context.py`（新增 ADT，声明 AF/RI，封装防御式访问）
- `tests/...`（新增破坏性测试，证明 ADT 可防越权修改与非法状态注入）
- `report/lab2_explainer.md` 与 `report/lab2_final_experiment_report.md`（每子任务闭环后同步证据）

##### 建议改（提高稳定性与可验收性）
- `app/utils/model.py`（仅在必要时补充 provider 异常语义一致性，保持最小改动）
- `app/api/v1/endpoints/models.py`（补充 provider 可观测性证据记录点，如 reload 前后对比）
- `tests/test_provider_*.py`（Provider 最小契约测试：实例化、test_connection 返回结构）

##### 可选挑战改（100分进阶）
- `app/providers/base.py`（在证据充分前提下重塑契约，修复抽象泄露）
- `app/domain/memory/*.py` 或同职责目录（记忆抽象层组件化）
- `app/utils/file_processor.py` 及上下游（不可变 KnowledgeChunk 改造）
- `app/vector_store/*.py`（统一 `VectorStoreProvider` 抽象并实现两个子类）

#### 评分点与证据来源（必须一一映射）
| 评分点 | 代码证据 | 测试证据 | 运行/日志证据 | 文档证据 |
|---|---|---|---|---|
| 60分-新增 Provider 并可请求 | `app/providers/<new_provider>.py` | `tests/test_provider_*.py`（或等效） | `/api/models/providers` 与 `/api/models/{id}/test` 返回 | 本文档阶段记录 + 最终报告矩阵 |
| 60分-Provider→Model→Agent→对话 | `models.py`、`agents.py`、`utils/model.py` 调用链 | 对话接口回归测试 | SSE/接口返回日志、模型响应片段 | 最终报告执行证据章节 |
| 60分-定义 SessionContext | `app/domain/session_context.py` | 基础行为测试 | 初始化与调用日志 | 讲解文档“为什么/怎么做” |
| 80分-RI/AF + 防御式编程 | `SessionContext` 的 AF/RI/`_check_rep`/深拷贝防护 | 非法 role、越权修改、边界容量测试 | 异常抛出与状态不污染证明 | 最终报告评分矩阵 |
| 80分-接入真实流程 | `agents.py` 中 `final_messages` 组装改造点 | 集成测试 | 改造前后行为对比日志 | 两份报告的改造闭环 |
| 100分-任意两项进阶 | 对应抽象层代码 | 对应单测/集成测 | 运行链路截图或日志 | “100分达成说明”章节 |

#### 哪些环节必须做破坏性测试
- `SessionContext.add_message`：传入非法 role、缺失字段、异常结构，必须抛异常
- `SessionContext.get_messages`：外部拿到返回值后 append 篡改，内部状态必须不受影响
- `SessionContext` 的容量/约束：超过 RI 上限时必须阻断并保持原状态
- Provider 失败路径：错误 API Key/错误 base_url 下 `test_connection` 必须返回可解释错误

#### 如果路径未生效，排查顺序（固定顺序执行）
1. `run.py` 是否启动 `app.main:app`
2. `app/main.py` 是否 `include_router(api_router, prefix=settings.API_V1_STR)`
3. `settings.API_V1_STR` 是否仍为 `/api`
4. `app/api/v1/api.py` 是否挂载了 `models.router` 与 `agents.router`
5. `models.py` 中 `/providers`、`/providers/reload` 是否可访问
6. `provider_manager` 是否加载到目标 provider（看 `/providers/modules`）
7. Model 记录中的 `provider` 字段是否与 `provider_id` 精确匹配
8. Agent 的 `model_id` 是否有效且模型状态为 active
9. `agents.py` 实际调用是否走到 `execute_model_inference`，`final_messages` 是否已含改造内容
10. 若仍异常，再看中间件统一响应包装是否掩盖了原始 HTTP 状态

### 阶段 3：Provider从0到1接入全过程（小白可复现）
#### 为什么这样改
任务1的核心不是“换一个API地址”，而是证明系统具备可插拔扩展能力。我们通过新增一个不依赖外网的 `lab2_mock` Provider，把“扩展一个新厂商”的工作拆成可复验的最小闭环。

#### 改了什么
- 新增 `app/providers/lab2_mock_provider.py`，实现 `ModelProvider` 的全部抽象方法：`provider_id`、`provider_name`、`description`、`icon`、`default_base_url`、`supported_model_types`、`features`、`test_connection`、`chat_completion`、`text_completion`、`embedding`
- 保持现有扫描机制不变，不改注册表；依赖 `ProviderManager` 的目录扫描自动发现
- 为打通 API Key 对话链路，最小修复 `chat_with_agent_api` 中模型推理调用方式，使其正确等待异步推理结果

#### 怎么验证（可直接复现）
- Provider 可见性验证
  - 证据：`provider_manager.get_all_providers()` 输出包含 `lab2_mock`
  - 证据：`GET /api/models/providers/modules` 返回 `lab2_mock_provider` 已加载，且映射到 `lab2_mock`
- Provider -> Model 验证
  - 创建 `provider=lab2_mock` 的 chat 模型成功
  - `POST /api/models/{model_id}/test` 返回 `status=success`
- Model -> Agent -> 对话验证
  - 创建绑定该 `model_id` 的 Agent 成功
  - 生成 Agent API Key 成功
  - `POST /api/agents/chat-with-api-key` 返回 SSE，包含 `event: message_chunk` 与 `event: done`

#### 关键证据（本次实际结果）
- Provider 模块识别：
  - `HAS_LAB2_MODULE True`
  - `LAB2_MODULE_DETAIL [{"id":"lab2_mock","name":"Lab2 Mock Provider",...}]`
- 链路闭环：
  - `MODEL_ID c3231c567c1d4de388579389bf57c112`
  - `AGENT_ID 5967875af3b842178fe499aa906f082a`
  - `MODEL_TEST ... "status":"success","message":"Lab2 Mock Provider 连接成功"...`
  - `CHAT_OK True`（SSE中出现 `message_chunk` 和 `done`）

#### 为什么这体现 OOP 抽象与多态扩展
- 抽象：上层只依赖 `ModelProvider` 契约，不依赖具体类名
- 多态：`provider_manager.get_provider(model.provider)` 取到的是抽象父类引用，运行时可替换为 `openai/google/lab2_mock` 任意子类
- 开闭：新增 `lab2_mock_provider.py` 即可扩展能力，主流程无需新增 `if-else` 分支

#### 常见坑与排查
- 坑1：只写了 provider 文件但未被识别
  - 排查：看 `/api/models/providers/modules` 的 `loaded_modules` 是否含目标模块
- 坑2：模型 provider 字段与 `provider_id` 不一致
  - 排查：确认创建 Model 时 `provider` 精确等于 `lab2_mock`
- 坑3：对话链路看似成功但未产出模型内容
  - 排查：检查 SSE 是否含 `event: message_chunk`，仅 `status` 不算闭环
- 坑4：异步链路把协程当生成器迭代
  - 排查：确认推理调用处先等待再迭代，避免 `'async for' requires __aiter__` 错误

### 阶段 4：AF/RI 是什么、怎么在本项目落地（小白版）
#### AF 和 RI 是什么
- AF（抽象函数）：告诉我们“这个类在业务上代表什么”
  - 本项目中的 `SessionContext` 代表“发送给模型的一次会话消息上下文”
- RI（表示不变式）：告诉我们“这个类内部什么状态才算合法”
  - 每条消息必须有 `role` 和 `content`
  - `role` 只能是 `system/user/assistant`
  - `content` 必须是字符串
  - 消息数量不能超过上限

#### 本次怎么落地
- 新增 ADT 文件：`app/domain/session_context.py`
- 在类中明确写出 AF/RI，并通过 `_check_rep` 在状态变化后强制校验
- 内部状态私有化：使用 `_messages`，外部不能直接拿内部引用改值
- 接入真实流程：`app/api/v1/endpoints/agents.py` 的 `chat_with_agent_api` 消息组装改为使用 `SessionContext`

#### 每个防御策略在防什么错误
- 非法 role 直接拒绝
  - 防止脏数据进入模型上下文，避免出现非预期角色语义污染
- content 强类型检查
  - 防止把数字/对象当文本传入，导致下游推理或序列化异常
- get_messages 深拷贝返回
  - 防止调用方拿到返回列表后 `append/覆盖` 反向污染内部状态
- 每次 `add/prepend` 后 `_check_rep`
  - 防止某次状态更新破坏 RI 后继续运行，做到“尽早失败、尽早定位”

#### 真实接入点（最小改造）
- 接入前：`final_messages` 在端点里由裸露 list 直接 `append`
- 接入后：改为 `SessionContext.add_message(...)`，最终通过 `get_messages()` 提交给模型
- 保持改动最小：只改一段真实生效链路，不引入新框架

#### 本阶段验证结果
- 单元测试：`tests/domain/test_session_context.py`，`6 passed`
- 链路验证：`chat-with-api-key` 仍可返回 `message_chunk` + `done`
- 语法验证：`python -m py_compile app/domain/session_context.py app/api/v1/endpoints/agents.py` 通过

#### 为什么要做破坏性测试、如何读懂失败与修复
- 为什么要做
  - 正常测试只能证明“能用”，破坏性测试才能证明“不被误用时也安全”
  - ADT 的价值不在存数据，而在非法输入和越权修改时能主动拦截
- 怎么读失败
  - 如果报 `非法 role`，说明入口校验生效，成功挡住脏角色
  - 如果报 `content 必须是 str`，说明类型约束生效，防止下游异常
  - 如果报 `消息数量超过上限` 或 `_check_rep` 断言，说明不变量守护生效
- 怎么判断修复完成
  - 修复后要同时看三类证据：单测通过、真实链路仍可用、文档证据可追溯
  - 本次结果：`6 passed`，且 `FLOW_EVIDENCE` 显示 `api_key_ok=true`、`normal_ok=true`，证明“防御增强 + 旧流程不破坏”

### 阶段 5：契约重塑前后对比（给初学者看的架构收益）
#### 重塑前的问题
- Provider 对外返回语义不完全一致：有的用 `success/failed`，有的用 `error`，上层需要猜测
- 错误信息格式不统一：有时是 `message`，有时是 `error` 字符串，难以稳定做日志与验收
- 新增 Provider 虽然能接入，但“连接测试结果结构一致性”缺少统一约束

#### 本次重塑做了什么
- 在 `ModelProvider` 增加统一契约能力：
  - `build_success_result`
  - `build_failed_result`
  - `is_failed_result`
  - `extract_error_message`
  - `normalize_test_connection_result`
- 在 `app/utils/model.py` 统一消费契约：
  - 连接测试统一走 `normalize_test_connection_result`
  - 推理流程统一识别失败结果并返回一致错误结构
- 增加 `app/providers/lab2_echo_provider.py` 作为“契约重塑后的新增 Provider 证据”
- `ModelTestResponse` 增加 `error` 字段，使失败语义可被接口完整传递

#### 重塑后的收益（为什么更符合架构演进）
- 高内聚：错误语义和结果规范收敛到 `ModelProvider` 抽象层，而不是散落在每个调用点
- 低耦合：业务层不再依赖各 Provider 的私有错误格式，只依赖统一契约方法
- 可扩展：新增 Provider 只需实现基础能力并可复用统一返回构建方法，主流程几乎不用改

#### 证据点：新增Provider几乎零改动主流程
- 新增文件：`app/providers/lab2_echo_provider.py`
- 主流程未新增 if-else 分支，仍由 `ProviderManager` 扫描自动加载
- 验证结果：
  - `/api/models/providers` 可见 `lab2_echo`
  - `/api/models/providers/modules` 可见 `lab2_echo_provider`
  - 使用 `lab2_echo` 创建 Model、创建 Agent、对话 SSE 成功（`ECHO_CHAT_OK True`）

## 3. OOP 任务讲解模板（任务1）
### 3.1 为什么改
### 3.2 改了什么
### 3.3 怎么验证（Provider → Model → Agent → 对话）
### 3.4 常见坑与排查

## 4. ADT 任务讲解模板（任务2）
### 4.1 为什么改（裸露 list/dict 风险）
### 4.2 改了什么（AF/RI、防御式复制、_check_rep）
### 4.3 怎么验证（破坏性测试）
### 4.4 常见坑与排查

## 5. 100分加分项讲解模板
### 5.1 重塑核心抽象（ModelProvider 契约优化）
### 5.2 子系统改造（记忆抽象层）
### 5.3 ADT 极致应用（不可变 KnowledgeChunk）
### 5.4 多态存储解耦（VectorStoreProvider）

## 6. 命令与证据索引（持续更新）
### 6.1 关键命令
- 待补充

### 6.2 关键日志
- 待补充

### 6.3 关键测试
- 待补充
