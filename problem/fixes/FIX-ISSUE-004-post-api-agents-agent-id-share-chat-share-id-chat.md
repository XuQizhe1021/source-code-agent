# FIX-ISSUE-004 POST /api/agents/{agent_id}/share-chat/{share_id}/chat

- 关联问题：ISSUE-004
- 问题摘要：分享对话接口在无效 share_id 下返回业务码 500。
- 根因分析（精确到模块/函数/逻辑）：
  - 根因1：`app/utils/agent.py:get_agent_by_share_token` 空值未判空导致异常。
  - 根因2：`app/api/v1/endpoints/agents.py:share_chat_with_agent` 使用 `except Exception` 把 `HTTPException(404)` 覆盖成 500。
- 代码改动清单（文件路径 + 改动点说明）：
  - `app/utils/agent.py`：修复共享令牌空值与状态判断。
  - `app/api/v1/endpoints/agents.py`：在通用异常前增加 `except HTTPException: raise`，保留原语义状态码。
- 修复方案说明（为什么这样修）：双点修复，既阻断源头异常，又避免异常语义被错误改写为 500。
- 风险评估（兼容性/副作用）：低风险。仅影响错误路径状态码语义，不影响成功对话流程。
- 验证过程（请求样例、断言点、结果）：
  - 请求：`POST /api/agents/1/share-chat/test/chat`，`{\"message\":\"hi\"}`
  - 断言点：`body.code == 404`，提示“智能体不存在或分享链接无效”。
  - 结果：通过，证据见 `problem/evidence/ISSUE-004-verify.json`。
- 验证结论（通过/不通过）：通过
- 回滚思路（如失败如何恢复）：回滚 `agents.py` 与 `agent.py` 相关改动。
- 修复时间与状态：2026-03-31，已修复
