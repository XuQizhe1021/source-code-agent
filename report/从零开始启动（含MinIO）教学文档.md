# 从零开始启动（含MinIO）教学文档

## 1. 文档目标
本教程面向第一次接触本项目的同学，目标是用最短路径完成“环境就绪 -> MinIO启动 -> 后端启动 -> Lab2关键能力复验”。

## 2. 已实测环境与结果
- `docker compose version`：已实测通过（v5.1.0）
- `docker compose -f docker-compose.minio.yml up -d`：已实测通过
- `docker compose -f docker-compose.minio.yml ps`：已实测可见 `source-code-agent-minio` 运行中
- `http://127.0.0.1:9000/minio/health/live`：已实测返回 `200`
- `python -m pytest tests/domain/test_session_context.py tests/domain/test_session_memory.py -q`：已实测 `14 passed`
- `python run.py`：已实测可启动 API 服务

## 3. 一次性启动命令（可复制）
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

### 3.3 运行核心回归
```powershell
python -m py_compile app/providers/base.py app/providers/lab2_mock_provider.py app/providers/lab2_echo_provider.py app/domain/session_context.py app/domain/session_memory.py app/utils/model.py app/api/v1/endpoints/agents.py app/schemas/model.py
python -m pytest tests/domain/test_session_context.py tests/domain/test_session_memory.py -q
```

### 3.4 启动后端
```powershell
python run.py
```

## 4. Lab2关键流程复验（可复制脚本）
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

## 5. 常见故障排查
- 若 `docker compose up` 报 pipe 不存在：先执行 3.1 启动 Docker Desktop，再重试
- 若 MinIO 健康检查非 200：检查 9000 端口占用，或执行 `docker compose -f docker-compose.minio.yml restart`
- 若对话接口无返回：确认 `python run.py` 已启动且 `http://127.0.0.1:8000/docs` 可访问

## 6. 收尾命令
```powershell
docker compose -f docker-compose.minio.yml down
```
