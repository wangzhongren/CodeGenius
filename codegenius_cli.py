import os
import sys
import logging
import logging.handlers
import datetime
from pathlib import Path
import configparser
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import queue
import threading

# 强制 stdout/stderr 使用 UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# 尝试导入模块
try:
    from python_programmer_agent2 import PythonProgrammerAgent
    from ai_agent_factory.llms.base_llm_openai import OpenAILLM
except ImportError as e:
    print(f"❌ 导入错误: 缺少依赖模块:\n{e}\n请确保已安装所有依赖。", file=sys.stderr)
    sys.exit(1)

# ----------------------------
# 配置与工具函数
# ----------------------------

def setup_logging(project_dir):
    log_dir = Path(project_dir) / "log"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"app_{datetime.date.today().strftime('%Y-%m-%d')}.log"
    handler = logging.handlers.TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)
    root_logger.addHandler(console_handler)

def load_config_from_env():
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent
    else:
        app_dir = Path(__file__).parent

    for _ in range(3):
        env_file = app_dir / ".env"
        if env_file.exists():
            load_dotenv(dotenv_path=env_file)
            return True
        app_dir = app_dir.parent

    os.environ.setdefault("API_KEY", "YOUR_API_KEY")
    os.environ.setdefault("BASE_URL", "https://api.openai.com/v1")
    os.environ.setdefault("MODEL_NAME", "gpt-4o-mini")
    return False

def load_app_config(app_dir):
    config = configparser.ConfigParser()
    config_file = app_dir / "config.ini"
    system_prompt_default = (
        "你是一位专业的Python程序员，精通各种Python开发任务。\n"
        "你需要根据用户的需求，完成Python项目的开发工作。\n"
        "\n你的职责包括：\n"
        "1. 分析用户需求并设计合适的Python解决方案\n"
        "2. 创建符合Python最佳实践的代码\n"
        "3. 实现模块化、可维护的代码结构\n"
        "4. 编写必要的文档和注释\n"
        "5. 按照项目组织结构创建必要的文件和目录\n"
        "\n重要要求：\n"
        "1. 代码必须遵循PEP 8规范\n"
        "2. 添加适当的类型注解\n"
        "3. 包含必要的docstring\n"
        "4. 在合适的地方添加错误处理\n"
        "5. 项目最外层**仅允许存在一个文件：`main.py`**\n"
        "6. 所有其他代码必须放入子目录\n"
        "7. 敏感配置不得硬编码\n"
        "8. **必须集成日志系统**（按天轮转，输出到 log/）\n"
        "9. 你不准运行代码，只生成代码和说明\n"
    )
    if config_file.exists():
        config.read(config_file, encoding="utf-8")
        if 'settings' in config:
            project_folder = config['settings'].get('project_folder', '')
            system_prompt = config['settings'].get('system_prompt', system_prompt_default)
            return project_folder, system_prompt
    return '', system_prompt_default

def save_app_config(app_dir, project_folder, system_prompt):
    config = configparser.ConfigParser()
    config['settings'] = {
        'project_folder': project_folder,
        'system_prompt': system_prompt
    }
    with open(app_dir / "config.ini", 'w', encoding='utf-8') as f:
        config.write(f)

# ----------------------------
# CLI 应用主类
# ----------------------------

class CodeGeniusCLI:
    def __init__(self):
        self.app_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
        load_config_from_env()
        self.project_folder, self.system_prompt = load_app_config(self.app_dir)
        self.agent = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.message_queue = queue.Queue()
        self.streaming = False
        self.current_ai_text = ""
        self.running = True

        # 启动队列处理器线程（用于流式输出）
        self.queue_thread = threading.Thread(target=self._process_message_queue, daemon=True)
        self.queue_thread.start()

    def _process_message_queue(self):
        """在独立线程中处理消息队列，避免阻塞主线程"""
        while self.running:
            try:
                msg_type, data = self.message_queue.get(timeout=0.1)
                if msg_type == "stream_token":
                    print(data, end='', flush=True)
                    self.current_ai_text += data
                elif msg_type == "stream_start":
                    print("\n🧠 CodeGenius: ", end='', flush=True)
                    self.streaming = True
                    self.current_ai_text = ""
                elif msg_type == "stream_end":
                    if self.current_ai_text.strip():
                        print()  # 换行
                    self.streaming = False
            except queue.Empty:
                continue

    def update_streaming_message(self, token: str):
        self.message_queue.put(("stream_token", token))

    def cleanup_streaming(self):
        self.message_queue.put(("stream_end", None))

    def get_multiline_input(self, prompt="👤 你: "):
        """
        获取多行用户输入，输入 '/done' 表示结束。
        返回拼接后的字符串（保留换行）。
        如果用户输入 'quit'/'exit'，则返回该字符串以便主循环处理退出。
        """
        print(prompt, end='', flush=True)
        lines = []
        while True:
            try:
                line = input()
                stripped = line.strip()
                if stripped == "/done":
                    break
                if stripped in ("quit", "exit", "q"):
                    return stripped  # 用于主循环判断退出
                lines.append(line)
            except KeyboardInterrupt:
                print("\n(输入已取消)")
                return None
            except EOFError:  # Ctrl+D / Ctrl+Z
                print("\n(输入结束)")
                break
        return "\n".join(lines)

    def initialize_agent(self, project_folder: str, api_key: str, base_url: str, model_name: str):
        if not project_folder:
            print("❌ 项目文件夹不能为空！", file=sys.stderr)
            return False
        if not api_key or api_key == "YOUR_API_KEY":
            print("❌ API 密钥无效！", file=sys.stderr)
            return False
        if not base_url.startswith(("http://", "https://")):
            print("❌ Base URL 必须以 http:// 或 https:// 开头！", file=sys.stderr)
            return False
        if not model_name:
            print("❌ 模型名称不能为空！", file=sys.stderr)
            return False

        try:
            print("🚀 正在初始化智能体...")
            llm = OpenAILLM(api_key=api_key, base_url=base_url, model_name=model_name)
            self.agent = PythonProgrammerAgent(
                basellm=llm,
                project_dir=project_folder,
                system_prompt=self.system_prompt
            )
            self.agent.set_token_deal_call_back(update_ui_callback=self.update_streaming_message)
            os.chdir(project_folder)
            setup_logging(project_folder)
            save_app_config(self.app_dir, project_folder, self.system_prompt)
            print("✅ 智能体初始化成功！")
            return True
        except Exception as e:
            print(f"❌ 初始化失败: {e}", file=sys.stderr)
            logging.exception("Agent 初始化异常")
            return False

    def run(self):
        print("🧠 CodeGenius - AI 编程助手 (命令行版)")
        print("=" * 50)

        # 1. 获取项目目录
        if not self.project_folder:
            while True:
                folder = input("📁 请输入项目文件夹路径（或拖入文件夹）: ").strip().strip('"')
                if os.path.isdir(folder):
                    if os.access(folder, os.R_OK | os.W_OK):
                        self.project_folder = folder
                        break
                    else:
                        print("❌ 无读写权限，请选择其他目录。")
                else:
                    print("❌ 路径无效，请输入有效目录。")

        # 2. 获取 API 配置
        api_key = os.getenv("API_KEY", "").strip()
        base_url = os.getenv("BASE_URL", "https://api.openai.com/v1").strip()
        model_name = os.getenv("MODEL_NAME", "gpt-4o-mini").strip()

        if not api_key or api_key == "YOUR_API_KEY":
            api_key = input("🔑 请输入 API 密钥: ").strip()

        # 3. 初始化 Agent
        if not self.initialize_agent(self.project_folder, api_key, base_url, model_name):
            print("❌ 无法继续，请检查配置后重试。")
            return

        # 4. 主交互循环
        print("\n💬 输入你的编程任务（输入 'quit' 退出；多行输入请以 '/done' 结束）:")
        while True:
            try:
                user_input = self.get_multiline_input()
                if user_input is None:
                    continue
                if user_input.strip() in ('quit', 'exit', 'q'):
                    print("👋 再见！")
                    break
                if not user_input.strip():
                    continue  # 跳过纯空输入

                print("🧠 CodeGenius 正在思考...", end='', flush=True)
                self.message_queue.put(("stream_start", None))

                future = self.executor.submit(self.agent.chat, user_input)
                response = future.result()

                # 如果有非流式响应（如 JSON 文件操作结果），打印出来
                if response and response.strip() and not self.streaming:
                    print(f"\n🧠 CodeGenius: {response}")

                self.cleanup_streaming()

            except KeyboardInterrupt:
                print("\n\n👋 被用户中断，再见！")
                break
            except Exception as e:
                print(f"\n❌ 运行时错误: {e}", file=sys.stderr)
                logging.exception("运行时异常")

        self.running = False
        self.executor.shutdown(wait=True)

# ----------------------------
# 入口
# ----------------------------

if __name__ == "__main__":
    app = CodeGeniusCLI()
    try:
        app.run()
    except Exception as e:
        print(f"💥 程序崩溃: {e}", file=sys.stderr)
        sys.exit(1)