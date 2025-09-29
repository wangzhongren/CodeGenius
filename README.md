# CodeGenius - AI Programming Assistant / AI 编程助手

CodeGenius is an AI-powered Python programming assistant desktop application that uses large language models to help users develop Python projects. Through a graphical interface, users can interact with AI agents to generate code, modify files, manage projects, and more.

CodeGenius 是一个基于 AI 的 Python 编程助手桌面应用程序，它使用大语言模型来帮助用户开发 Python 项目。通过图形界面，用户可以与 AI 智能体交互，生成代码、修改文件、管理项目等。

## Features / 功能特性

- 🧠 **AI-Powered Programming Assistant** - Generates high-quality Python code using OpenAI-compatible APIs
- 🖥️ **Desktop GUI Application** - Modern UI based on Tkinter and ttkbootstrap
- 🎨 **Theme Switching** - Supports light and dark themes
- 📁 **Project Management** - Select project directories and manage files within them
- 🔄 **Real-time Streaming Response** - AI-generated content displayed in real-time in the chat interface
- 📝 **Logging System** - Automatically creates time-rotated log files
- ⚙️ **Flexible Configuration** - Supports custom API keys, base URLs, and model names
- 🔐 **Secure Configuration** - Sensitive information managed through environment variables

- 🧠 **AI 驱动的编程助手** - 使用 OpenAI 兼容的 API 生成高质量 Python 代码
- 🖥️ **桌面 GUI 应用** - 基于 Tkinter 和 ttkbootstrap 的现代化界面
- 🎨 **主题切换** - 支持亮色和暗色主题
- 📁 **项目管理** - 选择项目目录并管理其中的文件
- 🔄 **实时流式响应** - AI 生成的内容实时显示在聊天界面
- 📝 **日志记录** - 自动创建按日期轮转的日志文件
- ⚙️ **灵活配置** - 支持自定义 API 密钥、基础 URL 和模型名称
- 🔐 **安全配置** - 敏感信息通过环境变量管理

## System Requirements / 系统要求

- Python 3.8 or higher
- Windows, macOS, or Linux operating system

- Python 3.8 或更高版本
- Windows、macOS 或 Linux 操作系统

## Installation / 安装步骤

1. Clone or download the project locally:
   ```bash
   git clone <repository-url>
   cd ai_python_agent/desktop_app
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

1. 克隆或下载项目到本地：
   ```bash
   git clone <repository-url>
   cd ai_python_agent/desktop_app
   ```

2. 创建虚拟环境（推荐）：
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## Configuration / 配置

1. Copy the `.env.example` file and rename it to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file to enter your API key and other configurations:
   ```env
   API_KEY=your_openai_api_key_here
   BASE_URL=https://api.openai.com/v1
   MODEL_NAME=gpt-4o-mini
   ```

   You can also use other providers that support the OpenAI API format:
   - OpenRouter: `BASE_URL=https://openrouter.ai/api/v1`
   - Azure OpenAI: `BASE_URL=your_azure_endpoint`
   - Other OpenAI-compatible APIs

1. 复制 `.env.example` 文件并重命名为 `.env`：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，填入你的 API 密钥和其他配置：
   ```env
   API_KEY=your_openai_api_key_here
   BASE_URL=https://api.openai.com/v1
   MODEL_NAME=gpt-4o-mini
   ```

   你也可以使用其他支持 OpenAI API 格式的提供商：
   - OpenRouter: `BASE_URL=https://openrouter.ai/api/v1`
   - Azure OpenAI: `BASE_URL=your_azure_endpoint`
   - 其他兼容 OpenAI 的 API

## Usage / 使用方法

1. Start the application:
   ```bash
   python codegenius_tk.py
   ```

2. In the application:
   - Click the "📁 Select" button to choose your project directory
   - Click the "⚙️ Config" button to set API keys, models, and other parameters
   - Click the "🚀 Initialize Agent" button to initialize the AI agent
   - Enter programming task requirements in the input box
   - Click "Send" or press Enter to interact with the AI agent

1. 启动应用程序：
   ```bash
   python codegenius_tk.py
   ```

2. 在应用程序中：
   - 点击“📁 选择”按钮选择你的项目目录
   - 点击“⚙️ 配置”按钮设置 API 密钥、模型等参数
   - 点击“🚀 初始化智能体”按钮初始化 AI 智能体
   - 在输入框中输入编程任务需求
   - 点击“发送”或按回车键与 AI 智能体交互

## Application Architecture / 应用程序架构

- `codegenius_tk.py`: Main Tkinter GUI application / 主要的 Tkinter GUI 应用程序
- `python_programmer_agent2.py`: Python programmer agent that handles programming tasks / Python 程序员智能体，处理编程任务
- `ai_agent_factory/`: AI agent factory module containing base agents and LLM implementations / AI 智能体工厂模块，包含基础智能体和 LLM 实现
- `requirements.txt`: Project dependencies / 项目依赖
- `.env.example`: Environment variable configuration template / 环境变量配置模板

## AI Agent Functions / AI 智能体功能

The Python programmer agent can perform the following operations:
- Create new files / 创建新文件
- Read existing files / 读取现有文件
- Update file content / 更新文件内容
- Delete files / 删除文件
- Follow PEP 8 guidelines / 遵循 PEP 8 规范
- Integrate logging systems / 集成日志系统
- Use type annotations / 使用类型注解
- Add appropriate comments and documentation / 添加适当注释和文档

## Logging System / 日志系统

The application automatically creates log files in the `log/` folder within the project directory, generating one log file per day with the naming format `app_YYYY-MM-DD.log`.

应用程序会在项目目录下的 `log/` 文件夹中自动创建日志文件，每天生成一个日志文件，命名格式为 `app_YYYY-MM-DD.log`。

## Environment Variables / 环境变量

- `API_KEY`: AI service API key / AI 服务的 API 密钥
- `BASE_URL`: AI service API base URL / AI 服务的 API 基础 URL
- `MODEL_NAME`: Model name to use / 要使用的模型名称

## Troubleshooting / 故障排除

1. **Startup Issues** - Ensure all dependencies are installed / **启动问题** - 确保已安装所有依赖项
2. **API Errors** - Check the configuration in the `.env` file / **API 错误** - 检查 `.env` 文件中的配置是否正确
3. **Permission Issues** - Ensure the application has permission to access the selected project directory / **权限问题** - 确保应用程序有权限访问选择的项目目录

## Development / 开发

This application is built using the following technology stack:
- Python 3.8+
- Tkinter and ttkbootstrap (GUI)
- OpenAI Python library (AI interaction)
- python-dotenv (environment variable management)

此应用程序使用以下技术栈构建：
- Python 3.8+
- Tkinter 和 ttkbootstrap（GUI）
- OpenAI Python 库（AI 交互）
- python-dotenv（环境变量管理）

## Contributing / 贡献

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

欢迎提交问题报告和拉取请求。对于重大变更，请先开 issue 讨论你想改变的内容。

## License / 许可证

Please see the LICENSE file in the project (if it exists).

请查看项目中的 LICENSE 文件（如果存在）。

## Notes / 注意事项

- This application requires a valid AI API key to function properly / 该应用程序需要有效的 AI API 密钥才能正常工作
- API calls generated during usage will incur corresponding fees / 在使用过程中产生的 API 调用会产生相应的费用
- Please ensure compliance with the AI service provider's terms of use / 请确保遵守 AI 服务提供商的使用条款