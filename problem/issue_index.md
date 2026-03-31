# 问题总表

- 生成时间：2026-03-31T19:53:00
- 问题总数：8
- 已修复：8
- 待复测：0
- 修复失败：0

| IssueID | 接口 | 严重级别 | 状态 | 定位摘要 |
|---|---|---|---|---|
| ISSUE-001 | POST /api/auth/register | High | 已修复 | 密码哈希后端兼容异常导致500（证据：ISSUE-001-verify.json） |
| ISSUE-002 | GET /api/agents/share/{token} | High | 已修复 | share_token 判空缺失导致500（证据：ISSUE-002-verify.json） |
| ISSUE-003 | GET /api/agents/{agent_id}/share-chat/{share_id} | High | 已修复 | share_token 判空缺失导致500（证据：ISSUE-003-verify.json） |
| ISSUE-004 | POST /api/agents/{agent_id}/share-chat/{share_id}/chat | High | 已修复 | HTTPException 被通用异常覆盖为500（证据：ISSUE-004-verify.json） |
| ISSUE-005 | GET /api/files/minio-download/{bucket}/{object_name} | Critical | 已修复 | 文件不存在被误映射为500（证据：ISSUE-005-verify.json） |
| ISSUE-006 | GET /api/files/image/{file_id}/{image_name} | High | 已修复 | 图片不存在被误映射为500（证据：ISSUE-006-verify.json） |
| ISSUE-007 | GET /api/files/markdown-image/{path} | High | 已修复 | 参数错误被误映射为500（证据：ISSUE-007-verify.json） |
| ISSUE-008 | GET /api/files/img/{path} | High | 已修复 | 资源缺失被误映射为500（证据：ISSUE-008-verify.json） |
