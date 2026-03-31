# FIX-ISSUE-003 GET /api/agents/{agent_id}/share-chat/{share_id}

- 关联问题：ISSUE-003
- 问题摘要：分享详情接口在无效 share_id 下返回业务码 500。
- 根因分析（精确到模块/函数/逻辑）：与 ISSUE-002 同根因，`get_agent_by_share_token()` 空值未处理导致异常上抛。
- 代码改动清单（文件路径 + 改动点说明）：
  - `app/utils/agent.py`：`get_agent_by_share_token` 增加空值与激活状态判断。
- 修复方案说明（为什么这样修）：复用共享令牌入口函数修复，保证所有 share_id 相关查询统一返回可预期结果。
- 风险评估（兼容性/副作用）：低风险。只修复异常分支，兼容原有业务逻辑。
- 验证过程（请求样例、断言点、结果）：
  - 请求：`GET /api/agents/1/share-chat/test`
  - 断言点：`body.code == 404`，不再返回 500。
  - 结果：通过，证据见 `problem/evidence/ISSUE-003-verify.json`。
- 验证结论（通过/不通过）：通过
- 回滚思路（如失败如何恢复）：回滚 `app/utils/agent.py` 中对应函数。
- 修复时间与状态：2026-03-31，已修复
