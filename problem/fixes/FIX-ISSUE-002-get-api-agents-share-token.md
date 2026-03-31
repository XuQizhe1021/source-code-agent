# FIX-ISSUE-002 GET /api/agents/share/{token}

- 关联问题：ISSUE-002
- 问题摘要：无效 share token 请求返回业务码 500。
- 根因分析（精确到模块/函数/逻辑）：`app/utils/agent.py` 的 `get_agent_by_share_token()` 未判断 `share_token` 为空，直接执行 `usage_count += 1` 导致 `NoneType` 异常。
- 代码改动清单（文件路径 + 改动点说明）：
  - `app/utils/agent.py`：增加 `share_token` 空值与 `is_active` 判断，不满足条件直接返回 `None`。
- 修复方案说明（为什么这样修）：保持原调用链不变，仅在共享令牌查询函数补齐基础判空与有效性校验，让上层路由按既有 404 语义返回。
- 风险评估（兼容性/副作用）：低风险。仅影响无效/失效 token 分支，不改变有效 token 正常路径。
- 验证过程（请求样例、断言点、结果）：
  - 请求：`GET /api/agents/share/test`
  - 断言点：`body.code == 404`，错误信息为“智能体不存在或分享链接无效”。
  - 结果：通过，证据见 `problem/evidence/ISSUE-002-verify.json`。
- 验证结论（通过/不通过）：通过
- 回滚思路（如失败如何恢复）：回滚 `app/utils/agent.py` 对 `get_agent_by_share_token` 的改动。
- 修复时间与状态：2026-03-31，已修复
