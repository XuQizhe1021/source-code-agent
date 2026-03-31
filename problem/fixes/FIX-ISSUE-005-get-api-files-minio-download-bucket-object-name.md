# FIX-ISSUE-005 GET /api/files/minio-download/{bucket}/{object_name}

- 关联问题：ISSUE-005
- 问题摘要：文件不存在时返回业务码 500，且被登记为关键问题。
- 根因分析（精确到模块/函数/逻辑）：`app/api/v1/endpoints/files.py:direct_download_from_minio` 捕获了所有异常，`HTTPException(404)` 被通用异常分支重写为 500。
- 代码改动清单（文件路径 + 改动点说明）：
  - `app/api/v1/endpoints/files.py`：在该函数增加 `except HTTPException: raise`，保留 404。
- 修复方案说明（为什么这样修）：最小改动恢复接口约定语义，文件不存在属于业务可预期错误，应返回 404 而非 500。
- 风险评估（兼容性/副作用）：低风险。仅修改异常映射，成功下载路径不受影响。
- 验证过程（请求样例、断言点、结果）：
  - 请求：`GET /api/files/minio-download/test/test?download=false`
  - 断言点：`body.code == 404`，错误信息为“文件不存在”。
  - 结果：通过，证据见 `problem/evidence/ISSUE-005-verify.json`。
- 验证结论（通过/不通过）：通过
- 回滚思路（如失败如何恢复）：回滚 `files.py` 中该函数的异常处理改动。
- 修复时间与状态：2026-03-31，已修复
