# 修复汇总报告

- 修复时间：2026-03-31
- 问题总数：8
- 修复成功：8
- 待复测：0
- 修复失败：0
- 修复成功率：100%

## 修复范围
- ISSUE-001：`POST /api/auth/register`
- ISSUE-002：`GET /api/agents/share/{token}`
- ISSUE-003：`GET /api/agents/{agent_id}/share-chat/{share_id}`
- ISSUE-004：`POST /api/agents/{agent_id}/share-chat/{share_id}/chat`
- ISSUE-005：`GET /api/files/minio-download/{bucket}/{object_name}`
- ISSUE-006：`GET /api/files/image/{file_id}/{image_name}`
- ISSUE-007：`GET /api/files/markdown-image/{path}`
- ISSUE-008：`GET /api/files/img/{path}`

## 关键修复结论
- 注册接口 500 根因已定位为密码哈希后端兼容异常，已切换到原生 bcrypt 生成并保留校验兼容。
- 智能体分享链路 500 根因已定位为 share_token 空值未判定，已补齐空值与激活状态检查。
- 文件相关接口 500 根因已定位为 `HTTPException` 被通用异常覆盖，已统一保留 400/404 语义返回。

## 验证证据
- 汇总证据：`problem/evidence/fix_verification_summary.json`
- 单项证据：`problem/evidence/ISSUE-001-verify.json` ~ `ISSUE-008-verify.json`

## 剩余问题
- 无

## 风险项
- 当前项目全局中间件统一返回 HTTP 200，真实状态码位于响应体 `code` 字段；调用方必须按 `code` 做错误处理。
- 密码哈希策略已改为原生 bcrypt 生成，建议后续补充鉴权回归测试，覆盖历史用户与新注册用户登录流程。
