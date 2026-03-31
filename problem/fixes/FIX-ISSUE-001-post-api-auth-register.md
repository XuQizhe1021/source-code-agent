# FIX-ISSUE-001 POST /api/auth/register

- 关联问题：ISSUE-001
- 问题摘要：注册接口正常请求返回业务码 500。
- 根因分析（精确到模块/函数/逻辑）：`app/utils/security.py` 的 `get_password_hash()` 通过 `passlib+bcrypt` 计算哈希时触发后端兼容异常，导致 `auth.register -> create_user -> get_password_hash` 抛出未处理错误并返回 500。
- 代码改动清单（文件路径 + 改动点说明）：
  - `app/utils/security.py`：改为使用 `bcrypt.hashpw` 生成密码哈希；`verify_password` 增加 `$2` 前缀哈希的 `bcrypt.checkpw` 校验路径，并保留 passlib 回退。
- 修复方案说明（为什么这样修）：直接绕开触发异常的 passlib-bcrypt 后端加载路径，使用项目已依赖的 `bcrypt` 原生实现，最小改动解决注册失败并保持旧哈希校验兼容。
- 风险评估（兼容性/副作用）：低风险。新密码哈希格式仍为 bcrypt 标准 `$2b$...`；旧数据验证逻辑兼容。
- 验证过程（请求样例、断言点、结果）：
  - 请求：`POST /api/auth/register`
  - 样例：`{\"username\":\"fix_user_<ts>\",\"password\":\"Audit123456\",\"name\":\"Fix User\",\"email\":\"fix_user_<ts>@example.com\"}`
  - 断言点：`body.code == 200`，返回对象包含 `id/username/status`。
  - 结果：通过，证据见 `problem/evidence/ISSUE-001-verify.json`。
- 验证结论（通过/不通过）：通过
- 回滚思路（如失败如何恢复）：回滚 `app/utils/security.py` 到修复前版本，并恢复原有 `CryptContext.hash/verify` 流程。
- 修复时间与状态：2026-03-31，已修复
