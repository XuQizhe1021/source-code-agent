# 问题总表

- 生成时间：2026-03-31T19:28:28.408747
- 问题总数：8

| IssueID | 接口 | 严重级别 | 状态 | 定位摘要 |
|---|---|---|---|---|
| ISSUE-001 | POST /api/auth/register | High | Open | 正常路径业务码 500 |
| ISSUE-002 | GET /api/agents/share/{token} | High | Open | 正常路径业务码 500 |
| ISSUE-003 | GET /api/agents/{agent_id}/share-chat/{share_id} | High | Open | 正常路径业务码 500 |
| ISSUE-004 | POST /api/agents/{agent_id}/share-chat/{share_id}/chat | High | Open | 正常路径业务码 500 |
| ISSUE-005 | GET /api/files/minio-download/{bucket}/{object_name} | Critical | Open | 正常路径请求异常 |
| ISSUE-006 | GET /api/files/image/{file_id}/{image_name} | High | Open | 正常路径业务码 500 |
| ISSUE-007 | GET /api/files/markdown-image/{path} | High | Open | 正常路径业务码 500 |
| ISSUE-008 | GET /api/files/img/{path} | High | Open | 正常路径业务码 500 |