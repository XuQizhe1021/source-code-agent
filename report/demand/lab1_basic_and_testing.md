# 实验一：Python 编程基础、构建工具与测试流水线

## 1. 实验目标
本实验旨在帮助您掌握现代 Python 工程开发的基础技能，为您后续在这个学期里彻底重塑和改造本项目打下坚实的基础。通过本实验，您将学习到：
1. **项目初探与运行**：如何整体阅读一个 FastAPI 项目并尝试在本地运行它，使用 Swagger UI 进行接口调试。
2. **依赖与构建管理**：如何从传统的 `requirements.txt` 迁移到现代化的构建工具链 `Poetry`。
3. **自动化测试**：如何使用 `Pytest` 为核心工具函数编写有效的单元测试，从而建立“安全网”。
4. **AI 辅助编程**：学会在理解已有代码的基础上，利用 AI 工具（如 Cursor/Copilot）快速生成高质量的测试代码。

## 2. 实验背景
CogmAIt 是一个快速开发的 AI 后端服务。在早期工程中，开发者通常为了追求速度而牺牲了工程化规范：
- 使用简单的 `pip` 和 `requirements.txt` 管理依赖，导致环境不一致、“依赖地狱”等问题。
- 测试覆盖率极低，所有的工具函数（例如在 `app/utils` 中）都缺乏保障，修改它们可能引发不可预知的连锁反应。


## 3. 实验任务

### 任务 1：项目初探与本地域运行
在动手改造代码之前，第一步永远是让项目“跑起来”并粗略理解它的架构。作为开发者，接手一个新项目的第一天通常就是从阅读 `README` 和搭建环境开始的。

**详细操作步骤**：

1. **准备 Python 环境**：确保你的电脑上安装了 Python（建议 3.9 或以上版本）。在终端检查版本：
   ```bash
   python --version  # 或 python3 --version
   ```
2. **构建虚拟环境**：虚拟环境能隔离项目依赖，防止和其他项目冲突。在项目根目录（`cogmait-backend`）下运行：
   ```bash
   # 创建名为 venv 的虚拟环境
   python -m venv venv
   
   # 激活虚拟环境（非常重要！）
   # Mac/Linux 用户执行：
   source venv/bin/activate
   # Windows 用户执行：
   # venv\Scripts\activate
   ```
   *（提示：激活后，你的终端命令行前面应该会出现 `(venv)` 字样）*
3. **安装陈旧依赖**：使用传统的 `pip` 方式，安装 `requirements.txt` 中的依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. **环境配置**：项目中提供了一个配置模板。你需要将它复制并重命名为 `.env`：
   ```bash
   cp .env.example .env  # Windows 可以选中文本复制粘贴，或者使用 copy .env.example .env
   ```
   *（你可以打开 `.env` 文件看看里面有哪些配置项，目前使用默认值即可跑通基础服务）*
5. **启动服务**：一切就绪，让我们启动后端服务器！
   ```bash
   python run.py
   ```
   *（如果看到 `Uvicorn running on http://0.0.0.0:8000`，恭喜你，项目跑起来了！但请注意⚠️：**项目中提供的 `requirements.txt` 遗漏了大量运行所需的依赖包**。你在第一次实际运行时极有可能会遭遇 `ModuleNotFoundError` 等报错导致启动失败。这也是日常工程中常见的状况：你需要仔细阅读终端报错日志，通过实际运行来发现缺失的依赖，并自行使用 `pip install <缺失包名>` 逐步补全，直到服务能真正成功启动为止。）*
6. **探索 API 文档与寻找冗余代码**：
   - 打开浏览器访问 `http://localhost:8000/docs`。这是 FastAPI 自动生成的交互式文档 Swagger UI。
   - 尝试展开 `GET /api/v1/agents/` 或 `POST /api/v1/agents/{agent_id}/chat`，看看它们需要什么参数。
   - 结合根目录的 `README.md`，去文件管理器中粗略浏览一遍 `app/` 目录结构。
   - **🔍 探索任务：在这个早期阶段，尝试翻阅 `app/api/v1/endpoints/agents.py` 或 `app/utils/` 等文件，找出至少一处你认为是完全“废弃”、冗余、或设计极其不合理的代码分支/功能**，并在实验报告中简述你的理由（例如：有没有永远捕获不到异常的 `try-except` 块？有没有没人调用的 `def xxx()` ？或者是极其臃肿的几百行函数？）。

### 任务 2：迁移至 Poetry 并重构环境
传统的 `requirements.txt` 容易引发“依赖地狱”（缺失版本锁定、区分不清开发依赖和生产依赖等）。现代 Python 项目倾向于使用 `pyproject.toml`（配合 `Poetry`）来统一管理。

**详细操作步骤**：

1. **停止原服务并退出原环境**：
   - 在刚才运行 `python run.py` 的终端按 `Ctrl+C` 停止服务。
   - 退出原来的虚拟环境：执行 `deactivate`。把你之前创建的 `venv` 文件夹直接删除（我们不用它了！）。
2. **安装 Poetry**：如果你的电脑还没安装 Poetry，请先安装：
   ```bash
   # Mac/Linux (推荐方式)
   curl -sSL https://install.python-poetry.org | python3 -
   # Windows 可以通过 pipx 或者官方的 Powershell 脚本安装，详见 Poetry 官网文档。
   ```
3. **初始化项目**：在项目根目录执行以下命令，它会引导你创建一个 `pyproject.toml` 文件。
   ```bash
   poetry init
   ```
   *（过程中会问你项目名称、作者、版本等，部分可以直接回车跳过。但在提示 `Would you like to define your main dependencies interactively?` 时，建议输入 `no` 拒绝交互，我们一会儿手动加更快。）*
4. **迁移核心依赖**：打开 `requirements.txt` 看看里面有什么。然后用 `poetry add` 逐个或批量添加。
   ```bash
   # 请根据 txt 文件里的内容添加（不用带版本号，让 poetry 自动解析最佳版本！）
   poetry add fastapi uvicorn sqlalchemy pydantic python-dotenv jinja2 ... 
   ```
   *（注：你在执行这个命令时，Poetry 实际上在后台默默地为你重新创建了一个全新的、隔离的虚拟环境，并把包都下在里面了，同时生成了严格版本锁定的 `poetry.lock` 文件）*
5. **添加开发依赖**：测试工具 `pytest` 只有在开发时才需要，不应该部署到生产环境，因此我们要把它算作独立的 `group`：
   ```bash
   poetry add --group dev pytest pytest-asyncio
   ```
6. **使用新引擎起飞**：现在，所有的依赖都被 Poetry 接管了。你不用再使用 `source venv/...` 激活环境了！任何想要在项目中运行的命令，只需要在前面加上 `poetry run` 即可。
   让我们再次启动服务，看看是否成功完成迁移：
   ```bash
   poetry run python run.py
   ```
   *（如果依然看到 `Uvicorn running on http://0.0.0.0:8000`，说明依赖迁移大获成功！）*

### 任务 3：为核心功能织就安全网
在 `app/utils/` 目录下（如 `format_datetime` 等工具函数），如果这些基础功能在未来的重构中被改坏，上层业务逻辑就会全盘瘫痪。我们需要引入 `pytest` 编写自动化单元测试。

**详细操作步骤**：

1. **建立起手式安排目录**：
   在项目根目录下新建一个名为 `tests` 的文件夹。为了和源码结构保持一致，在里面再新建一个 `utils` 文件夹。
2. **编写你的第一个测试用例**：
   - 比如你盯上了 `app/utils/__init__.py` 或 `app/utils/config.py` 中的函数（如果没有合适的工具函数，你可以自己在这个目录下写一个简单的 `def truncate_text(text: str, max_length: int) -> str:` 用来练习）。
   - 在 `tests/utils/` 下创建一个名为 `test_xxx.py` 的文件（重点：Pytest 会自动寻找文件名以 `test_` 开头的文件）。
   - **🤖 探索：使用 AI 结对编程**
     打开你常用的 AI 工具（Cursor/Copilot/ChatGPT），把那个你想测试的工具函数代码丢给它，输入 prompt：“`我是 Python 初学者，帮我为这个函数写几个 pytest 测试用例，要有测试正常输入的 Happy Path，也要有测试边界条件（比如输入为空、超长）的 Unhappy Path，并加上详细的注释解释每一段在干什么。`”
3. **运行测试**：
   在终端执行：
   ```bash
   poetry run pytest -v  # -v 表示 verbose，会打印出详细的测试结果
   ```
   *看看是否有绿色的 `PASSED`？如果有红色的 `FAILED`，分析原因并修复它（是测试写错了，还是原来的代码真的有 bug？）*
4. **（进阶尝试）查看代码覆盖率**：
   安装覆盖率插件：
   ```bash
   poetry add --group dev pytest-cov
   ```
   然后运行：
   ```bash
   poetry run pytest --cov=app.utils tests/
   ```
   你可以清晰地看到你刚才写的测试覆盖了 `utils` 目录下百分之几的代码行数！

## 4. 实验报告及进阶挑战（评分标准）

本实验设置了不同的难度阶梯，请根据您完成的改造量级在报告中申请对应的分数等级：

*   **及格基础（60分）**：
    *   成功运行项目并提交短篇的目录架构梳理（包括指出一处冗余代码的设计缺陷，100-200字即可）。
    *   成功完成 Poetry 环境的迁移（提交 `pyproject.toml`）。
    *   为至少一个工具函数编写了简单的单元测试并运行通过。
*   **工程化标准（80分）**：
    *   达到60分标准。
    *   为 `app/utils` 下**多个核心工具类**（包含配置解析、字符串处理、特定格式转换等）编写了完善的测试用例，不仅覆盖正常逻辑，还考虑了边界和异常流。
    *   成功配置测试覆盖率工具，截屏展示所选模块的代码覆盖率超过 80%。
    *   记录并在报告中展示你在写测试时“抓到”的一个原有代码 Issue（如潜在报错、空指针对待等）。
*   **架构师潜力（100分）**：
    *   达到80分标准。
    *   **架构改造初体验**：不仅仅停留于“纯函数”测试，开始利用依赖注入（Dependency Injection）或 Mock 技术（如 `pytest-mock`），对部分带有外部依赖（如数据库读取）的函数进行伪造测试。
    *   **重构反哺**：甚至因为要写测试，你发现某些底层代码“不可测试”（例如强耦合了环境变量的读取）。你为了让它变得可测试，主动**重构（重写）了这一小片底层代码**，形成了更优雅的代码结构并配以完备的测试用例，在报告中展示你的 diff 和理由。
