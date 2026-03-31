# FIX-ISSUE-007 GET /api/files/markdown-image/{path}

- 关联问题：ISSUE-007
- 问题摘要：无效 Markdown 图片路径被错误返回为业务码 500。
- 根因分析（精确到模块/函数/逻辑）：`app/api/v1/endpoints/files.py:serve_markdown_image` 对路径解析失败抛出 `HTTPException(400)`，随后被通用异常分支改写成 500。
- 代码改动清单（文件路径 + 改动点说明）：
  - `app/api/v1/endpoints/files.py`：增加 `except HTTPException: raise`，保留 400/404 业务语义。
- 修复方案说明（为什么这样修）：路径格式错误属于请求参数问题，应明确返回 400，便于调用方快速定位。
- 风险评估（兼容性/副作用）：低风险。成功取图路径无改动。
- 验证过程（请求样例、断言点、结果）：
  - 请求：`GET /api/files/markdown-image/test/path.png`
  - 断言点：`body.code == 400`，提示“无法确定图片所属的文件ID”。
  - 结果：通过，证据见 `problem/evidence/ISSUE-007-verify.json`。
- 验证结论（通过/不通过）：通过
- 回滚思路（如失败如何恢复）：回滚 `files.py` 对应函数异常处理改动。
- 修复时间与状态：2026-03-31，已修复
