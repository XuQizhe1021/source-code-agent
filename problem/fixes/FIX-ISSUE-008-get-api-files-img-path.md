# FIX-ISSUE-008 GET /api/files/img/{path}

- 关联问题：ISSUE-008
- 问题摘要：智能图片接口在资源不存在时返回业务码 500。
- 根因分析（精确到模块/函数/逻辑）：`app/api/v1/endpoints/files.py:serve_image_smart` 在所有路径尝试失败后抛出 `HTTPException(404)`，但被 `except Exception` 吞掉并改写为 500。
- 代码改动清单（文件路径 + 改动点说明）：
  - `app/api/v1/endpoints/files.py`：增加 `except HTTPException: raise`，保留 404。
- 修复方案说明（为什么这样修）：资源缺失是可预期业务场景，返回 404 才符合接口约定并便于上游正确处理。
- 风险评估（兼容性/副作用）：低风险，仅修正异常语义，不改查询路径逻辑。
- 验证过程（请求样例、断言点、结果）：
  - 请求：`GET /api/files/img/test/path.png`
  - 断言点：`body.code == 404`，提示“找不到请求的图片”。
  - 结果：通过，证据见 `problem/evidence/ISSUE-008-verify.json`。
- 验证结论（通过/不通过）：通过
- 回滚思路（如失败如何恢复）：回滚 `files.py` 对应函数异常处理改动。
- 修复时间与状态：2026-03-31，已修复
