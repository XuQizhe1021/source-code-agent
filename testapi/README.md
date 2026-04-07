# testapi API测试插件

这个插件是一个前端测试面板：  
勾选接口 -> 点击执行 -> 看结果（可收纳、可删除）。

## 功能

- 支持勾选需要测试的 API
- 一键执行所选测试
- 自动处理登录并复用 token
- 自动创建图谱并复用 graphId
- 覆盖 Neo4j 测试与 MinIO 上传测试
- 结果支持折叠与删除

## 启动

先保证后端启动，再启动静态页面：

```bash
python -m http.server 8090 --directory testapi
```

浏览器打开：

- http://127.0.0.1:8090/

## 建议勾选顺序

1. GET /models/providers  
2. POST /auth/register + /auth/login  
3. POST /graphs/  
4. POST /graphs/{id}/neo4j-test  
5. POST /graphs/{id}/files/upload
