# 从零开始启动（含MinIO）教学文档

## 1. 文档目标

本教程面向第一次接触本项目的同学，目标是用最短路径完成“环境就绪 -> MinIO与Neo4j启动 -> 后端启动 -> Lab2与知识图谱后端能力复验”。

## 2. 已实测环境与结果

- `docker compose version`：已实测通过（v5.1.0）
- `docker compose -f docker-compose.minio.yml up -d`：已实测通过
- `docker compose -f docker-compose.minio.yml ps`：已实测可见 `source-code-agent-minio` 运行中
- `http://127.0.0.1:9000/minio/health/live`：已实测返回 `200`
- `source-code-agent-neo4j`：已实测启动成功，`http://127.0.0.1:7474` 返回 `200`
- `python -m pytest tests/domain/test_session_context.py tests/domain/test_session_memory.py -q`：已实测 `14 passed`
- `python run.py`：已实测可启动 API 服务

## 3. 一次性启动命令（可复制）

本节同时给出 PowerShell 与 CMD 两套写法。你当前终端提示形如 `E:\...>` 时通常是 CMD，请优先使用 CMD 版本。

### 3.1 启动 Docker Desktop（若已启动可跳过）

```powershell
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

### 3.2 启动 MinIO

```powershell
docker compose -f docker-compose.minio.yml up -d
docker compose -f docker-compose.minio.yml ps
python -c "import requests; print(requests.get('http://127.0.0.1:9000/minio/health/live', timeout=10).status_code)"
```

修改了 `MINIO_ROOT_USER/MINIO_ROOT_PASSWORD` 后，必须重建容器使环境变量生效：

```powershell
docker compose -f docker-compose.minio.yml down
docker rm -f source-code-agent-minio
docker compose -f docker-compose.minio.yml up -d --force-recreate minio
docker inspect source-code-agent-minio --format "{{range .Config.Env}}{{println .}}{{end}}" | findstr MINIO_ROOT
```

同时要保证**后端读取的 MinIO 凭证一致**，否则会出现 `InvalidAccessKeyId`：

```powershell
$env:MINIO_ACCESS_KEY="xqz"
$env:MINIO_SECRET_KEY="xqzxqzxqz"
python run.py
```

如果希望永久生效，请在项目根目录创建 `.env`（或修改已有 `.env`）并写入：

```env
MINIO_ACCESS_KEY=xqz
MINIO_SECRET_KEY=xqzxqzxqz
```

### 3.3 启动 Neo4j（知识图谱后端依赖）

PowerShell 版本：

```powershell
docker start source-code-agent-neo4j
if($LASTEXITCODE -ne 0){
  docker run -d --name source-code-agent-neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password -e NEO4J_PLUGINS='[""apoc""]' neo4j:5.15
}
docker ps --filter "name=source-code-agent-neo4j" --format "{{.Names}}|{{.Status}}|{{.Ports}}"
python -c "import requests; print(requests.get('http://127.0.0.1:7474', timeout=10).status_code)"
```

CMD 版本（你当前这种终端建议用这个）：

```bat
docker inspect source-code-agent-neo4j >nul 2>&1
docker rm -f source-code-agent-neo4j
docker run -d --name source-code-agent-neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5.15
docker ps --filter "name=source-code-agent-neo4j" --format "{{.Names}}|{{.Status}}|{{.Ports}}"
python -c "import requests; print(requests.get('http://127.0.0.1:7474', timeout=10).status_code)"
```

### 3.4 运行核心回归

```powershell
python -m py_compile app/providers/base.py app/providers/lab2_mock_provider.py app/providers/lab2_echo_provider.py app/domain/session_context.py app/domain/session_memory.py app/utils/model.py app/api/v1/endpoints/agents.py app/schemas/model.py
python -m pytest tests/domain/test_session_context.py tests/domain/test_session_memory.py -q
```

### 3.5 启动后端

```powershell
python -m poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 4. 知识图谱后端复验（可复制脚本）

```powershell
@'
import time, json, requests
base='http://127.0.0.1:8000/api'
seed=str(int(time.time()))
username=f'graph_user_{seed}'
password='Lab2Pass123!'
s=requests.Session()
reg=s.post(f'{base}/auth/register',json={'username':username,'password':password,'name':'Graph User','email':f'{username}@example.com','role':'admin'},timeout=30)
login=s.post(f'{base}/auth/login',json={'username':username,'password':password,'remember':False},timeout=30)
token=login.json()['data']['token']
headers={'Authorization':f'Bearer {token}'}
lg=s.get(f'{base}/graphs/',headers=headers,timeout=30)
cr=s.post(f'{base}/graphs/',headers=headers,json={'name':f'课程图谱_{seed}','description':'验收创建','config':{'domain':'teaching'}},timeout=30)
print('REGISTER',reg.status_code)
print('LOGIN',login.status_code)
print('LIST_GRAPHS',lg.status_code)
print('CREATE_GRAPH',cr.status_code)
if cr.status_code==200:
    gid=cr.json()['data']['id']
    dt=s.get(f'{base}/graphs/{gid}',headers=headers,timeout=30)
    print('GET_GRAPH',dt.status_code)
print('GRAPH_ACCEPTANCE_DONE')
'@ | python -
```

## 5. Lab2关键流程复验（可复制脚本）

```powershell
@'
import json
import time
import requests
base='http://127.0.0.1:8000/api'
seed=str(int(time.time()))
username=f'lab2_user_{seed}'
password='Lab2Pass123!'
s=requests.Session()
s.post(f'{base}/auth/register',json={'username':username,'password':password,'name':'Lab2 User','email':f'{username}@example.com','role':'admin'},timeout=30)
login=s.post(f'{base}/auth/login',json={'username':username,'password':password,'remember':False},timeout=30).json()
headers={'Authorization':f"Bearer {login['data']['token']}"}
def create_model(provider,name,base_url):
    return s.post(f'{base}/models/',json={'name':name,'provider':provider,'type':'chat','api_key':'lab2-dummy-key','base_url':base_url,'description':'audit','config':{'temperature':0.1},'tool_call_support':False,'function_call_support':False,'vision_support':False,'thinking_support':False,'mcp_support':False,'default_prompt':'You are a helper','max_context_length':4000,'extra_body_params':{}},headers=headers,timeout=30).json()['data']['id']
def create_agent(model_id,name):
    return s.post(f'{base}/agents/',json={'name':name,'type':'chat','description':'audit','model_id':model_id,'system_prompt':'你是验证助手','welcome_message':'你好','config':{'temperature':0.2},'enable_web_search':False,'status':'active','knowledgeIds':[],'graphIds':[],'mcpServiceIds':[]},headers=headers,timeout=30).json()['data']['id']
def get_key(agent_id):
    return s.post(f'{base}/agents/{agent_id}/generate-api-key',headers=headers,timeout=30).json()['data']['api_key']
def read(resp,max_lines=50):
    lines=[]
    for line in resp.iter_lines(decode_unicode=True):
        if line:
            lines.append(line)
        if len(lines)>=max_lines:
            break
    text='\n'.join(lines)
    acc=[]
    for line in lines:
        if line.startswith('data: '):
            try:
                obj=json.loads(line[6:])
                if obj.get('choices'):
                    c=obj['choices'][0].get('delta',{}).get('content')
                    if c: acc.append(c)
            except: pass
    return text,''.join(acc)
mock_m=create_model('lab2_mock',f'audit-mock-{seed}','mock://lab2')
mock_a=create_agent(mock_m,f'audit-mock-agent-{seed}')
mock_k=get_key(mock_a)
r=s.post(f'{base}/agents/chat-with-api-key',json={'messages':[{'role':'user','content':'主链路回归'}],'stream':True,'session_id':f's-{seed}'},headers={'api-key':mock_k},timeout=60,stream=True)
txt,_=read(r)
mock_ok=('event: message_chunk' in txt and 'event: done' in txt)
echo_m=create_model('lab2_echo',f'audit-echo-{seed}','mock://echo')
echo_a=create_agent(echo_m,f'audit-echo-agent-{seed}')
echo_k=get_key(echo_a)
sid=f'm-{seed}'
r1=s.post(f'{base}/agents/chat-with-api-key',json={'messages':[{'role':'user','content':'第一轮问题'}],'stream':True,'session_id':sid},headers={'api-key':echo_k},timeout=60,stream=True)
_,_t1=read(r1)
r2=s.post(f'{base}/agents/chat-with-api-key',json={'messages':[{'role':'user','content':'第二轮问题'}],'stream':True,'session_id':sid},headers={'api-key':echo_k},timeout=60,stream=True)
_,t2=read(r2)
mem_ok='MemoryFromPrevUser: 第一轮问题' in t2
print('FINAL_AUDIT_MOCK_OK',mock_ok)
print('FINAL_AUDIT_MEMORY_OK',mem_ok)
print('FINAL_AUDIT',json.dumps({'mock_ok':mock_ok,'memory_ok':mem_ok},ensure_ascii=False))
'@ | python -
```

## 6. 常见故障排查

- 若 `docker compose up` 报 pipe 不存在：先执行 3.1 启动 Docker Desktop，再重试
- 若 MinIO 健康检查非 200：检查 9000 端口占用，或执行 `docker compose -f docker-compose.minio.yml restart`
- 若 Neo4j 启动失败：先看 `docker ps -a --filter "name=source-code-agent-neo4j"`，再执行 `docker start source-code-agent-neo4j`
- 若提示 `container name ... already in use`：说明容器已存在，不要再 `docker run`，直接执行 `docker start source-code-agent-neo4j`
- 若 Neo4j 容器反复 `Exited (1)`：执行以下重建命令后再启动  
  `docker rm -f source-code-agent-neo4j`  
  `docker run -d --name source-code-agent-neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5.15`
- 若日志报 `InvalidAccessKeyId`：说明 MinIO 容器凭证与后端凭证不一致；按“3.2”同时重建容器并设置 `MINIO_ACCESS_KEY/MINIO_SECRET_KEY`
- 若图谱接口不可用：确认 `python run.py` 已启动且 `GET /api/graphs/` 返回 200
- 若对话接口无返回：确认 `http://127.0.0.1:8000/docs` 可访问
- Neo4j浏览器访问：http://127.0.0.1:7474/browser/

## 6.1 Neo4j Browser 登录信息（必填项说明）

- Database：留空（默认数据库），或填写 `neo4j`
- Authentication type：选择 `Username / Password`
- Username：`neo4j`
- Password：`password`

## 6.2 MinIO 登录说明
- MinIO 控制台地址：`http://127.0.0.1:9001`
- `http://127.0.0.1:9000` 是 S3 API 端口，不是 Web 登录页

## 7. 收尾命令

```powershell
docker stop source-code-agent-neo4j
docker compose -f docker-compose.minio.yml down
```
