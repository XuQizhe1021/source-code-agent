# example_use 最小使用案例

这个目录提供一个“尽可能小”的可运行案例：  
**注册用户 -> 登录 -> 查看 Provider 列表 -> 创建知识图谱 -> 上传文件（走MinIO） -> 测试Neo4j连接**。

同时提供：
- 脚本版：`minimal_case.py`
- 前端版：`index.html`

## 前置条件

- 后端已启动：`python run.py`
- API 地址默认：`http://127.0.0.1:8000/api`

## 运行

```bash
python example_use/minimal_case.py
```

### 前端方式（推荐）

```bash
python -m http.server 8088 --directory example_use
```

打开：
- http://127.0.0.1:8088/

页面按钮按顺序点击：
1) 检查后端  
2) 注册  
3) 登录  
4) 查看Provider列表  
5) 创建知识图谱  
6) 测试Neo4j连接  
7) 上传文件到图谱（走MinIO）

可选环境变量：

```bash
set BASE_URL=http://127.0.0.1:8000/api
```

## 预期结果

- 输出 `REGISTER: 200`
- 输出 `LOGIN: 200`
- 输出 `PROVIDERS_COUNT: ...`
- 输出 `CREATE_GRAPH: 200`
- 输出 `UPLOAD_FILE_TO_MINIO: 200`
- 输出 `NEO4J_TEST: 200`
- 前端日志区显示对应请求状态为 `200`
