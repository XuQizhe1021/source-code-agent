# FIX-ISSUE-006 GET /api/files/image/{file_id}/{image_name}

- 关联问题：ISSUE-006
- 问题摘要：图片不存在时返回业务码 500。
- 根因分析（精确到模块/函数/逻辑）：`app/api/v1/endpoints/files.py:serve_image` 内部先抛出 `HTTPException(404)`，但被外层 `except Exception` 捕获后改写为 500。
- 代码改动清单（文件路径 + 改动点说明）：
  - `app/api/v1/endpoints/files.py`：增加 `except HTTPException: raise`，使 404 透传。
- 修复方案说明（为什么这样修）：保持错误语义与调用方预期一致，避免前端把资源缺失误判为服务端崩溃。
- 风险评估（兼容性/副作用）：低风险，仅影响异常分支状态码。
- 验证过程（请求样例、断言点、结果）：
  - 请求：`GET /api/files/image/1/test.png`
  - 断言点：`body.code == 404`。
  - 结果：通过，证据见 `problem/evidence/ISSUE-006-verify.json`。
- 验证结论（通过/不通过）：通过
- 回滚思路（如失败如何恢复）：回滚 `files.py` 对应函数异常处理改动。
- 修复时间与状态：2026-03-31，已修复
