# 实验二最终实验报告（OOP 与 ADT）

## 一、实验信息
- 实验名称：实验二——ADT 与 OOP 设计与扩展
- 项目名称：CogmAIt 后端（FastAPI）
- 唯一评分依据：`report/lab2_oop_and_adt.md`
- 执行原则：最小改造、证据完整、阶段闭环

## 二、目标与完成情况总览
本报告按评分标准逐项对齐，所有结论均由代码、测试、日志与命令证据支撑。当前为初始化版本，后续阶段将增量补齐实现与证据。

## 二点一、实验目标（本阶段）
- 完成真实生效链路确认：Provider 注册、Model 创建、Agent 调用、消息组装
- 形成最小改造点清单并分组：必须改 / 建议改 / 可选挑战改
- 形成 60→80→100 分梯度执行计划
- 明确每个评分点的证据来源、破坏性测试范围、未生效排查顺序

## 三、阶段执行记录（持续更新）
### 阶段 1：需求解析与方案拆解（已完成）
- 产出：WBS、风险清单、验收清单
- 结果：明确任务1/任务2主线与100分加分项可选路线
- 证据：`report/lab2_explainer.md`、本报告初始化提交

### 阶段 2：主路径确认与基线建立（已完成）
- 主链路确认：
  - 入口：`run.py` -> `app.main:app`
  - API 挂载：`app/main.py` + `settings.API_V1_STR="/api"`
  - 子路由：`app/api/v1/api.py` 挂载 `models.router` 与 `agents.router`
  - Provider 管理：`app/providers/base.py` + `app/providers/manager.py`
  - Model 侧调用：`app/api/v1/endpoints/models.py` + `app/utils/model.py`
  - Agent 侧调用：`app/api/v1/endpoints/agents.py`（`chat_with_agent` / `chat_with_agent_api`）
  - 消息组装：`agents.py` 中 `chat_request.messages -> final_messages -> execute_model_inference`
- 本阶段约束：仅确认基线与计划，不改功能逻辑
### 阶段 3：ADT设计接入与防御性编程（已完成）
- 新增 `app/domain/session_context.py`，完成 AF/RI 声明与防御性实现
- 在 `chat_with_agent_api` 真实消息组装路径接入 SessionContext
### 阶段 4：破坏性测试与回归验证（已完成）
- 新增 `tests/domain/test_session_context.py` 并通过 `6 passed`
- 接入后链路回归：`chat-with-api-key` 仍返回 `message_chunk` + `done`
### 阶段 5：100分加分项实现与验收（已完成）
- 挑战项A已完成：ModelProvider 契约重塑（统一返回语义、错误模型一致化、调用侧解耦）
- 挑战项B已完成：记忆子系统改造（策略化会话记忆管理 + 真实链路接入）

## 四、评分点对齐矩阵（持续更新）
| 评分档位/条目 | 实现状态 | 代码证据 | 测试证据 | 运行/日志证据 | 结论 |
|---|---|---|---|---|---|
| 60分-新增 Provider 并可发起请求 | 已完成 | `app/providers/lab2_mock_provider.py`；`app/providers/base.py`；`app/providers/manager.py` | Provider链路实测脚本（注册/登录/建模/测试） | `GET /api/models/providers`；`GET /api/models/providers/modules`；`POST /api/models/{id}/test` | 已达成 |
| 60分-Provider→Model→Agent→对话链路 | 已完成 | `app/api/v1/endpoints/models.py`；`app/api/v1/endpoints/agents.py`；`app/utils/model.py` | 链路实测脚本（创建Agent、生成API Key、对话） | `POST /api/agents/chat-with-api-key` SSE 包含 `message_chunk` + `done` | 已达成 |
| 60分-定义 SessionContext 基本结构 | 已完成 | `app/domain/session_context.py` | `tests/domain/test_session_context.py` | 端点消息组装调用日志 | 已达成 |
| 80分-RI/AF + 防御性编程完整 | 已完成 | `SessionContext` 内 AF/RI/`_check_rep`/深拷贝保护/role校验 | `test_illegal_role_is_rejected` 等 | 运行时异常可定位 + 内部状态不污染 | 已达成 |
| 80分-破坏性测试有效拦截 | 已完成 | `tests/domain/test_session_context.py` | 非法 role、非法 content、外部篡改返回值、超上限写入、内部状态篡改 | `6 passed` | 已达成 |
| 80分-SessionContext 接入真实流程 | 已完成 | `app/api/v1/endpoints/agents.py`（`chat_with_agent_api` 组装段） | API链路实测 | `chat-with-api-key` SSE 含 `message_chunk` + `done` | 已达成 |
| 100分-进阶项A（重塑核心抽象） | 已完成 | `app/providers/base.py`；`app/utils/model.py`；`app/schemas/model.py`；`app/providers/lab2_echo_provider.py` | 契约兼容与回归验证 | `/providers` 列表、`/models/{id}/test` 统一失败语义、`lab2_echo` 对话闭环 | 已达成 |
| 100分-进阶项B（子系统改造） | 已完成 | `app/domain/session_memory.py`；`app/api/v1/endpoints/agents.py`；`app/providers/lab2_echo_provider.py` | `tests/domain/test_session_memory.py` + 回归测试 | 同session两轮对话出现记忆回灌标记 + 主链路回归正常 | 已达成 |

## 四点五、最终验收矩阵（达成状态 + 证据位置）
- 60分-新增Provider并可发起请求：已达成；证据位置 `app/providers/lab2_mock_provider.py` 与本报告 5.3、8.2
- 60分-Provider→Model→Agent→对话：已达成；证据位置 `app/api/v1/endpoints/models.py`、`app/api/v1/endpoints/agents.py` 与本报告 5.3、8.2
- 60分-SessionContext基本结构：已达成；证据位置 `app/domain/session_context.py` 与本报告 6.2
- 80分-RI/AF+防御性编程：已达成；证据位置 `app/domain/session_context.py` 与本报告 6.2、6.3
- 80分-破坏性测试有效拦截：已达成；证据位置 `tests/domain/test_session_context.py` 与本报告 6.3、8.3
- 80分-SessionContext真实接入：已达成；证据位置 `app/api/v1/endpoints/agents.py` 与本报告 6.2、6.4
- 100分-挑战项A（重塑核心抽象）：已达成；证据位置 `app/providers/base.py`、`app/utils/model.py`、`app/schemas/model.py`、`app/providers/lab2_echo_provider.py` 与本报告 7.1.1
- 100分-挑战项B（记忆子系统改造）：已达成；证据位置 `app/domain/session_memory.py`、`app/api/v1/endpoints/agents.py`、`tests/domain/test_session_memory.py` 与本报告 7.1.2

## 四点一、最小改造点清单（文件级）
### 必须改
- `app/providers/*.py`（新增 Provider）
- `app/domain/session_context.py`（新增 ADT）
- `app/api/v1/endpoints/agents.py`（接入一段真实消息装配）
- `tests/` 下新增 SessionContext 破坏性测试
- `report/lab2_explainer.md`、`report/lab2_final_experiment_report.md` 持续更新

### 建议改
- `app/api/v1/endpoints/models.py`（补充 provider 观测与重载验证说明）
- `app/utils/model.py`（仅在必要时补充异常语义一致性）
- `tests/` 下补充 provider 契约最小测试

### 可选挑战改
- `app/providers/base.py`（契约重塑）
- 记忆抽象层组件文件（MemoryManager 等）
- `app/utils/file_processor.py` 与上下游（不可变 KnowledgeChunk）
- 向量存储抽象与多态实现文件

## 四点二、破坏性测试范围（硬性执行）
- `SessionContext.add_message` 非法 role/缺字段/超容量输入
- `SessionContext.get_messages` 返回值外部篡改（append、覆盖）不应影响内部状态
- Provider 失败路径（无效 key/base_url）要返回可解释错误结构
- 接入链路后，验证 `final_messages` 未被外部对象意外污染

## 四点三、未生效路径排查顺序（硬性执行）
1. 启动入口是否为 `app.main:app`
2. `main.py` 是否挂载 `api_router`
3. `API_V1_STR` 是否为预期前缀 `/api`
4. `api.py` 是否包含 models/agents 路由
5. provider 相关接口（`/models/providers*`）是否可用
6. provider 模块是否被 manager 实际加载
7. Model 的 provider 字段是否与 provider_id 一致
8. Agent 是否绑定有效 model_id 且模型为 active
9. 请求是否进入 `agents.py` 真实对话端点并走到 `execute_model_inference`
10. 若状态码异常，检查统一响应中间件是否改变了外层 HTTP 语义

## 四点四、执行计划（60→80→100）
### 60分阶段（最小可运行）
- 新增 Provider 并通过 provider 列表与模型连接测试
- 创建使用该 provider 的 Model，并完成 Agent 对话最小链路
- 定义 SessionContext 基本结构（先不大规模替换）

### 80分阶段（工程化闭环）
- 完整补齐 AF/RI/`_check_rep` 与防御式编程
- 在 `agents.py` 真实 `final_messages` 装配段接入 SessionContext
- 增加破坏性测试并回归通过，证明“拦截非法 + 内部不污染”

### 100分阶段（架构师潜力）
- 在四个进阶项中选择两项落地（优先：重塑 ModelProvider 抽象 + 记忆子系统改造）
- 每项必须具备：代码实现、测试证明、运行证据、评分矩阵映射
- 形成“最小改造但证据完整”的最终验收包

## 五、任务1：OOP扩展与契约遵守（持续更新）
### 5.1 现状确认
- Provider 扩展机制为目录扫描加载，不是硬编码注册表
- 主链路通过 `provider_manager.get_provider(model.provider)` 在运行时完成多态分发
- 原始链路中 `chat_with_agent_api` 存在异步推理调用方式不一致，导致对话验证无法闭环

### 5.2 设计与实现
- 新增 Provider：`app/providers/lab2_mock_provider.py`
  - 实现 `ModelProvider` 所有抽象契约
  - 支持 `chat/completion/embedding` 三类调用
  - `test_connection` 返回标准成功结构
  - `chat_completion(stream=True)` 返回可迭代 SSE chunk 结构
- 最小修复对话链路：`app/api/v1/endpoints/agents.py`
  - 将 API Key 对话端点中的模型推理调用调整为正确异步等待后再流式迭代

### 5.3 验证过程
- Provider识别验证
  - 结果：`HAS_LAB2_MODULE True`
  - 结果：`LAB2_MODULE_DETAIL` 含 `id=lab2_mock`
- Provider->Model验证
  - 新建模型成功：`MODEL_ID c3231c567c1d4de388579389bf57c112`
  - 连接测试成功：`"status":"success","message":"Lab2 Mock Provider 连接成功"`
- Model->Agent->对话验证
  - 新建Agent成功：`AGENT_ID 5967875af3b842178fe499aa906f082a`
  - API Key 生成成功
  - 对话SSE成功：`CHAT_OK True`，输出包含 `event: message_chunk` 与 `event: done`

### 5.4 结果与结论
- 任务1已完成 60 分档两项核心要求：新增 Provider 可用 + Provider→Model→Agent→对话闭环
- 本实现未修改现有 Provider 行为，新增能力以插件方式并入，符合最小改造策略
- OOP 价值体现：上层调用仅依赖抽象契约，新增子类即可替换运行时行为，符合多态与开闭原则

## 六、任务2：ADT改造与防御性编程（持续更新）
### 6.1 现状确认
- 原链路在 `chat_with_agent_api` 中直接使用裸露 list 组装 `final_messages`
- 该方式缺少统一入口校验，容易出现非法 role、外部引用污染、状态越界等问题

### 6.2 设计与实现（AF/RI/_check_rep）
- 新增 `SessionContext`：`app/domain/session_context.py`
  - AF：表示一次会话消息上下文
  - RI：role 仅允许 `system/user/assistant`，content 必须为字符串，消息条数不超过上限，内部消息结构固定
  - 防御实现：`add_message`/`prepend_message`/`get_messages` + `_check_rep`
- 接入真实流程：`app/api/v1/endpoints/agents.py`
  - `chat_with_agent_api` 中消息组装改为 `SessionContext` 管理
  - 最终通过 `session_context.get_messages()` 传入模型推理
- 伴随修复：保持 API Key 对话链路异步推理调用正确（先 await 再 async for）

### 6.3 破坏性测试
- 新增测试文件：`tests/domain/test_session_context.py`
- 覆盖场景：
  - 非法 role 拒绝
  - 非字符串 content 拒绝
  - 外部修改 `get_messages` 返回值不影响内部状态
  - 超过上限后拒绝写入
- 内部状态被篡改后 `_check_rep` 拦截（`内部消息 role 非法`）
- 执行结果：`6 passed`

### 6.3.1 测试设计
- 目标：验证 SessionContext 不仅“可用”，且“抗破坏”
- 方法：
  - 单元级破坏：直接注入非法 role、非法 content、返回值越权修改、超上限写入、内部状态篡改
  - 链路级回归：分别验证 `/api/agents/chat-with-api-key` 与 `/api/agents/{agent_id}/chat`
- 判定标准：
  - 非法输入必须被异常拦截
  - 合法输入链路必须继续产生 `message_chunk + done`

### 6.3.2 执行结果
- 单元测试：`python -m pytest tests/domain/test_session_context.py -q` -> `6 passed`
- 真实链路：`FLOW_EVIDENCE {"api_key_ok": true, "normal_ok": true, ...}`
- 说明：防御机制生效的同时，旧对话流程未被破坏

### 6.3.3 结论
- 评分点“防御性编程 + 破坏性测试 + 真实接入”证据齐全
- 任务2在工程化层面完成闭环，可支撑 80 分档目标

### 6.4 结果与结论
- SessionContext 已不是孤立类，已进入真实消息装配流程
- ADT 约束在代码中被强制执行，能够在状态变更后及时发现不变量破坏
- 任务2核心目标已完成，并支撑 80 分档相关条目

## 七、100分达成说明（持续更新）
### 7.1 已完成进阶项
- 挑战项A：重塑 ModelProvider 契约（完成）
- 挑战项B：记忆子系统改造（完成）

### 7.1.1 挑战项A完成证据与得分论证
- 设计目标
  - 将 Provider 返回语义收敛到抽象层，避免调用方依赖各 Provider 的私有错误格式
- 实现证据
  - `app/providers/base.py` 新增统一契约方法：`build_success_result`、`build_failed_result`、`is_failed_result`、`extract_error_message`、`normalize_test_connection_result`
  - `app/utils/model.py` 调整为统一消费契约：连接测试统一归一化，推理失败统一判定与错误抽取
  - `app/schemas/model.py` 为 `ModelTestResponse` 增加 `error` 字段，保证失败语义可观测
  - 新增 `app/providers/lab2_echo_provider.py`，未改主流程路由与控制器，仅通过 providers 目录自动扫描接入
- 回归与可用性证据
  - `PROVIDERS_COUNT 8`，且 `HAS_OPENAI True`、`HAS_LAB2_MOCK True`、`HAS_LAB2_ECHO True`
  - `HAS_ECHO_MODULE True`
  - `MOCK_TEST_STATUS success`、`ECHO_TEST_STATUS success`
  - `OPENAI_STATUS failed` 且 `OPENAI_HAS_ERROR_OBJ True`、`OPENAI_ERROR_CODE connection_failed`
  - `ECHO_CHAT_OK True`
- 得分论证
  - 满足“重塑核心抽象并带来系统性收益”：高内聚、低耦合、可扩展

### 7.1.2 挑战项B实现、验证与风险控制
- 设计目标
  - 将“会话记忆选择与裁剪”从端点流程中抽离为可复用抽象，提升连续对话稳定性
- 实现证据
  - 新增 `app/domain/session_memory.py`
    - `MemoryPolicy` 抽象接口
    - `RecentWindowPolicy` 窗口策略实现
    - `SessionMemoryManager` 记忆管理器（顺序恢复、长度裁剪、过滤空值）
  - 在 `app/api/v1/endpoints/agents.py` 的 `chat_with_agent` 与 `chat_with_agent_api` 接入：
    - 按 `session_id` 读取历史
    - 通过 `SessionMemoryManager` 注入最近会话记忆
    - 再拼接本轮消息进入 `SessionContext`
  - `app/providers/lab2_echo_provider.py` 增加记忆回灌可观测标记，便于前后行为对比验收
- 验证结果
  - 行为对比：
    - 第一轮：`TURN1_TEXT Echo: 第一轮问题`
    - 第二轮：`TURN2_TEXT Echo: 第二轮问题 | MemoryFromPrevUser: 第一轮问题`
    - `MEMORY_FEATURE_OK True`
  - 稳定性回归：
    - `MOCK_REGRESSION_OK True`（既有主链路可用）
    - `python -m pytest tests/domain/test_session_context.py tests/domain/test_session_memory.py -q` -> `11 passed`
- 风险控制
  - 采用窗口策略限制注入轮数，避免上下文无限膨胀
  - 对每条记忆做长度裁剪与空值过滤，降低异常输入风险
  - 通过策略接口隔离演进风险，后续替换策略无需修改端点主流程
### 7.2 架构收益
- Provider 抽象层统一结果语义后，调用侧不再感知各厂商差异，错误处理复杂度下降
- 会话记忆子系统策略化后，历史回灌与上下文裁剪从端点代码中解耦，便于后续替换策略
- 新增 Provider 与新增记忆策略都可通过“新增文件 + 接口实现”完成，主流程改动显著减少

### 7.3 约束与权衡
- 记忆窗口当前采用固定轮数 + 字符裁剪，优先稳定性与可解释性，后续可升级为 token 预算策略
- 为控制改造风险，挑战项A/B均采用增量接入，避免一次性重写主链路
- 回归策略以“既有 provider 可用 + 双对话链路可用”为硬门槛，确保功能不回退

## 七点四、风险与不足（客观）+ 后续工程优化建议
- 风险1：测试以领域单测和关键链路脚本为主，尚未形成完整 CI 流水线
- 风险2：会话记忆策略当前是固定窗口，未按 token budget 动态调度
- 风险3：运行环境缺少 MinIO 时会出现初始化失败日志，虽不阻塞主功能但影响观感
- 建议1：增加集成测试套件（provider注册、模型测试、对话SSE、记忆回灌）并接入 CI
- 建议2：为 `SessionMemoryManager` 新增 token 预算策略与可配置策略工厂
- 建议3：将 MinIO 初始化失败改为降级告警并在健康检查中单独上报

## 八、关键命令与证据清单（持续更新）
### 8.1 命令清单
- `python -c "from app.providers.manager import provider_manager; print([p['value'] for p in provider_manager.get_all_providers()])"`
- `python run.py`
- Provider模块观测脚本：请求 `/api/models/providers/modules`，确认 `lab2_mock_provider` 被加载
- 链路闭环脚本：注册用户 -> 登录 -> 创建Model -> 模型测试 -> 创建Agent -> 生成API Key -> `/api/agents/chat-with-api-key` 对话
- `python -m py_compile app/domain/session_context.py app/api/v1/endpoints/agents.py`
- `python -m pytest tests/domain/test_session_context.py -q`
- `python -m py_compile app/providers/base.py app/utils/model.py app/providers/lab2_echo_provider.py app/schemas/model.py`
- 挑战项A回归脚本：校验 providers 列表、新增 echo provider、openai 失败语义统一、echo 对话闭环
- `python -m py_compile app/domain/session_memory.py app/api/v1/endpoints/agents.py app/providers/lab2_echo_provider.py`
- `python -m pytest tests/domain/test_session_context.py tests/domain/test_session_memory.py -q`
- 挑战项B对比脚本：同session两轮请求验证记忆回灌 + lab2_mock主链路回归

### 8.2 日志清单
- `已加载提供商: Lab2 Mock Provider (lab2_mock)`
- `HAS_LAB2_MODULE True`
- `MODEL_TEST ... "status":"success","message":"Lab2 Mock Provider 连接成功"...`
- `CHAT_OK True`
- `EVIDENCE_SUMMARY {"provider":"lab2_mock","model_id":"c3231c567c1d4de388579389bf57c112","agent_id":"5967875af3b842178fe499aa906f082a","chat_ok":true}`
- `6 passed in 0.02s`（SessionContext 单测）
- `GOOD_CHAT_HAS_CHUNK True` 与 `GOOD_CHAT_HAS_DONE True`（接入后链路验证）
- `FLOW_EVIDENCE {"agent_id":"...","model_id":"...","api_key_ok":true,"normal_ok":true}`（新旧流程均可用）
- `PROVIDERS_COUNT 8` / `HAS_LAB2_ECHO True` / `HAS_ECHO_MODULE True`
- `OPENAI_STATUS failed` + `OPENAI_HAS_ERROR_OBJ True` + `OPENAI_ERROR_CODE connection_failed`
- `ECHO_CHAT_OK True`
- `TURN2_TEXT Echo: 第二轮问题 | MemoryFromPrevUser: 第一轮问题`
- `MEMORY_FEATURE_OK True`
- `MOCK_REGRESSION_OK True`
- `CHALLENGE_B_EVIDENCE {"echo_agent":"...","echo_model":"...","memory_feature_ok":true,"mock_regression_ok":true}`

### 8.3 测试清单
- 任务1链路实测（命令行自动化验证，覆盖 Provider识别 / Model创建 / Agent绑定 / 对话SSE）
- 任务2单测：SessionContext 防御性与不变量测试（6项）
- 任务2链路实测：`chat_with_agent_api` 接入后 SSE 回归验证
- 任务2回归补充：`chat_with_agent` 与 `chat_with_agent_api` 双链路并行验证
- 挑战项A回归：契约统一语义验证 + 既有Provider可用性回归 + 新增Provider零主流程改动接入验证
- 挑战项B测试：记忆策略单测 + 同session行为对比 + 主链路回归

## 十、最终回归结果汇总
- 运行检查：`python run.py` 可启动，Provider 自动加载 8 项（含 `lab2_mock` 与 `lab2_echo`）
- 编译检查：`python -m py_compile ...` 通过（Provider/ADT/记忆子系统/端点/Schema）
- 单元测试：`python -m pytest tests/domain/test_session_context.py tests/domain/test_session_memory.py -q` -> `11 passed`
- 关键流程：`FINAL_MOCK_CHAT_OK True`（主链路稳定）；`FINAL_MEMORY_OK True`（记忆回灌生效）
- 错误语义：`FINAL_OPENAI_STATUS failed` 且 `FINAL_OPENAI_ERROR_CODE connection_failed`（契约统一生效）

## 九、结论（持续更新）
已完成任务1、任务2及挑战项A、挑战项B，评分矩阵对应条目均已给出代码、测试与运行证据。当前实现满足“最小改造但证据完整”的目标，可支撑实验二100分验收。
