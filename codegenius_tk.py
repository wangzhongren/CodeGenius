import os
import sys
import threading
import logging
import logging.handlers
import datetime
from pathlib import Path
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, scrolledtext

# 尝试导入模块
try:
    from python_programmer_agent2 import PythonProgrammerAgent
    from ai_agent_factory.llms.base_llm_openai import OpenAILLM
    from dotenv import load_dotenv
except ImportError as e:
    messagebox.showerror("导入错误", f"缺少依赖模块:\n{e}\n请确保已安装所有依赖。")
    sys.exit(1)

# 日志配置
def setup_logging(project_dir):
    log_dir = os.path.join(project_dir, "log")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"app_{datetime.date.today().strftime('%Y-%m-%d')}.log")
    handler = logging.handlers.TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    logging.getLogger().addHandler(console_handler)
    logging.getLogger().setLevel(logging.DEBUG)

# 加载环境变量
def load_config_from_env():
    # 判断是否是 PyInstaller 打包后的环境
    if getattr(sys, 'frozen', False):
        # 打包后：EXE 所在目录
        app_dir = Path(sys.executable).parent
    else:
        # 开发时：当前脚本所在目录
        app_dir = Path(__file__).parent

    env_file = app_dir / ".env"
    print(app_dir)
    # 尝试加载 .env
    if env_file.exists():
        print("存在")
        
        load_dotenv(dotenv_path=env_file)
        print(os.getenv("API_KEY", "YOUR_API_KEY"));
        # print(os.get)
        return True

    # 可选：向上查找 1-2 层（适用于复杂项目结构）
    for _ in range(2):
        app_dir = app_dir.parent
        env_file = app_dir / ".env"
        if env_file.exists():
            load_dotenv(dotenv_path=env_file)
            return True
        
    # 默认值（建议留作 fallback）
    os.environ.setdefault("API_KEY", "YOUR_API_KEY")
    os.environ.setdefault("BASE_URL", "https://api.openai.com/v1")  # 注意：无空格！
    os.environ.setdefault("MODEL_NAME", "gpt-4o-mini")
    return False

class CodeGeniusApp:
    def __init__(self, root: ttk.Window):
        load_config_from_env()
        
        self.root = root
        self.root.title("🧠 CodeGenius - AI 编程助手")
        self.root.geometry("1000x750")
        self.root.minsize(800, 600)

        self.is_dark = False
        self.style = ttk.Style("cosmo")
        self.project_folder = ""
        self.agent = None
        self.streaming = False
        self.current_ai_text = ""
        self.config_win_visible = False
        self.create_widgets()
        

    def create_widgets(self):
        # 顶部栏
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=ttk.X)

        ttk.Label(top_frame, text="🧠 CodeGenius", font=("", 16, "bold"), bootstyle=PRIMARY).pack(side=ttk.LEFT)

        right_frame = ttk.Frame(top_frame)
        right_frame.pack(side=ttk.RIGHT)

        self.config_btn = ttk.Button(right_frame, text="⚙️ 配置", bootstyle=OUTLINE, command=self.open_config)
        self.config_btn.pack(side=ttk.LEFT, padx=5)

        self.theme_btn = ttk.Button(right_frame, text="🌙 暗色", bootstyle=OUTLINE, command=self.toggle_theme)
        self.theme_btn.pack(side=ttk.LEFT, padx=5)

        # 主区域
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=ttk.BOTH, expand=True)

        # Banner (Uncommented and defined properly)
        self.banner_frame = ttk.Frame(main_frame, bootstyle="warning", padding=10)
        ttk.Label(
            self.banner_frame,
            text="⚠️ 请先选择项目文件夹并初始化智能体",
            bootstyle="inverse-warning",
            font=("", 10)
        ).pack()
        self.banner_frame.pack(fill=ttk.X, pady=(0, 10))
        self.banner_frame.pack_forget()  # Hidden initially

        # 聊天区
        self.chat_text = scrolledtext.ScrolledText(
            main_frame, wrap=ttk.WORD, state=ttk.DISABLED,
            font=("Microsoft YaHei", 10), padx=10, pady=10
        )
        self.chat_text.pack(fill=ttk.BOTH, expand=True, pady=(0, 10))

        # 输入区
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=ttk.X)
        self.input_field = ttk.Text(input_frame, height=3, font=("Microsoft YaHei", 10))
        self.input_field.pack(side=ttk.LEFT, fill=ttk.X, expand=True, padx=(0, 10))
        self.send_btn = ttk.Button(input_frame, text="发送", bootstyle=PRIMARY, command=self.send_task)
        self.send_btn.pack(side=ttk.RIGHT)
        self.input_field.bind("<Return>", self.on_enter)

        # 状态栏
        self.status_var = ttk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, bootstyle="secondary", padding=(10, 5))
        status_bar.pack(side=ttk.BOTTOM, fill=ttk.X)

        # 配置窗口
        self.create_config_window()

    def create_config_window(self):
        self.config_win = ttk.Toplevel(self.root)
        self.config_win.title("⚙️ 配置")
        self.config_win.geometry("450x800")
        self.config_win.withdraw()
        self.config_win.transient(self.root)

        frame = ttk.Frame(self.config_win, padding=20)
        frame.pack(fill=ttk.BOTH, expand=True)

        ttk.Label(frame, text="⚙️ 配置", font=("", 14, "bold")).pack(pady=(0, 15))

        folder_frame = ttk.Frame(frame)
        folder_frame.pack(fill=ttk.X, pady=5)
        self.folder_var = ttk.StringVar(value="未选择项目")
        ttk.Label(folder_frame, textvariable=self.folder_var, bootstyle="secondary").pack(side=ttk.LEFT)
        ttk.Button(folder_frame, text="📁 选择", command=self.select_folder, bootstyle=OUTLINE).pack(side=ttk.RIGHT)

        self.api_key_var = ttk.StringVar(value=os.getenv("API_KEY", "YOUR_API_KEY"))
        self.base_url_var = ttk.StringVar(value=os.getenv("BASE_URL", "https://api.openai.com/v1").strip())
        self.model_var = ttk.StringVar(value=os.getenv("MODEL_NAME", "gpt-4o-mini"))
        self.system_prompt_var = ttk.StringVar(value=(
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
            "6. 所有其他代码（如 models、services、utils、config 等）必须放入对应的子目录中\n"
            "7. 敏感配置（如数据库密码、API密钥等）**不得硬编码在代码中**，应通过环境变量或配置模块加载\n"
            "8. **必须集成日志系统**：\n"
            "   - 日志同时输出到控制台和文件\n"
            "   - 日志文件存放在项目根目录下的 `log/` 文件夹中（目录需自动创建）\n"
            "   - 每天生成一个日志文件，命名格式为 `app_YYYY-MM-DD.log`\n"
            "   - 使用 `logging` 模块 + `TimedRotatingFileHandler` 实现按天轮转\n"
            "   - 日志格式应包含时间、日志级别、模块名和消息\n"
            "9. 你不准运行代码,如果需要运行，请说明步骤，让对方来代劳\n"
            "\n项目配置信息（供你参考，用于生成配置加载逻辑）：\n" 
        ))

        for label, var in [("API 密钥:", self.api_key_var), ("Base URL:", self.base_url_var), ("模型:", self.model_var)]:
            ttk.Label(frame, text=label).pack(anchor=ttk.W, pady=(10, 0))
            entry = ttk.Entry(frame, textvariable=var, width=50)
            if label == "API 密钥:":
                entry.config(show="*")
            entry.pack(fill=ttk.X, pady=5)

        ttk.Label(frame, text="系统提示词:").pack(anchor=ttk.W, pady=(10, 0))
        self.system_prompt_text = ttk.Text(frame, height=15, width=50, font=("Microsoft YaHei", 10))
        self.system_prompt_text.insert("1.0", self.system_prompt_var.get())
        self.system_prompt_text.pack(fill=ttk.X, pady=5)

        init_btn = ttk.Button(frame, text="🚀 初始化智能体", bootstyle=SUCCESS, command=self.initialize_agent)
        init_btn.pack(pady=20)

    def toggle_theme(self):
        if self.is_dark:
            self.style.theme_use("cosmo")
            self.theme_btn.config(text="🌙 暗色")
            self.is_dark = False
        else:
            self.style.theme_use("darkly")
            self.theme_btn.config(text="☀️ 亮色")
            self.is_dark = True

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            if not os.access(folder, os.R_OK | os.W_OK):
                messagebox.showerror("错误", "所选文件夹无读写权限！")
                return
            self.project_folder = folder
            self.folder_var.set(f"📁 {os.path.basename(folder)}")
            os.chdir(folder)
            setup_logging(self.project_folder)
            # self.check_agent_ready()

    def open_config(self):
        if self.config_win_visible:
            self.config_win.lift()
            return
        self.config_win_visible = True
        self.config_win.deiconify()
        self.config_win.lift()
        self.config_win.protocol("WM_DELETE_WINDOW", self.close_config)

    def close_config(self):
        self.config_win_visible = False
        self.config_win.withdraw()

    def add_message(self, sender: str, text: str = "", is_user: bool = False, stream: bool = False):
        self.chat_text.config(state=ttk.NORMAL)
        if is_user:
            self.chat_text.insert(ttk.END, f"【你】\n{text}\n\n", "user")
            self.chat_text.tag_config("user", foreground="#007bff", font=("Microsoft YaHei", 10, "bold"))
        else:
            if stream:
                self.streaming = True
                self.current_ai_text = ""
                self.chat_text.insert(ttk.END, "【CodeGenius】\n", "ai_header")
                self.chat_text.tag_config("ai_header", foreground="#6c757d", font=("Microsoft YaHei", 9, "italic"))
                self.ai_stream_start = self.chat_text.index(ttk.END + "-1c")
                self.chat_text.insert(ttk.END, "", "ai_stream")
            else:
                self.chat_text.insert(ttk.END, f"【CodeGenius】\n{text}\n\n", "ai")
                self.chat_text.tag_config("ai", foreground="#6c757d", font=("Microsoft YaHei", 10))
        self.chat_text.see(ttk.END)
        self.chat_text.config(state=ttk.DISABLED)
        logging.debug(f"Added message: {sender} - {text[:50]}...")

    def _update_stream_ui(self, token: str):
        if not self.streaming:
            return
        self.current_ai_text += token
        self.chat_text.config(state=ttk.NORMAL)
        try:
            self.chat_text.delete(self.ai_stream_start, ttk.END)
        except tk.TclError:
            self.ai_stream_start = self.chat_text.index(ttk.END)
        self.chat_text.insert(ttk.END, token, "ai_stream")
        color = "#e0e0e0" if self.is_dark else "#333333"
        self.chat_text.tag_config("ai_stream", foreground=color)
        self.chat_text.see(ttk.END)
        self.chat_text.config(state=ttk.DISABLED)
        logging.debug(f"Streamed token: {token[:50]}...")

    def update_streaming_message(self, token: str):
        self.root.after(0, lambda: self._update_stream_ui(token))

    def cleanup_streaming(self):
        if self.streaming:
            self.streaming = False
            final_text = self.current_ai_text.strip()
            self.current_ai_text = ""
            if hasattr(self, 'ai_stream_start'):
                del self.ai_stream_start
            self.chat_text.config(state=ttk.NORMAL)
            self.chat_text.insert(ttk.END, f"{final_text}\n\n", "ai")
            self.chat_text.tag_config("ai", foreground="#6c757d", font=("Microsoft YaHei", 10))
            self.chat_text.see(ttk.END)
            self.chat_text.config(state=ttk.DISABLED)
            logging.debug("Streaming cleanup completed")

    def on_enter(self, event=None):
        self.send_task()
        return "break"

    def send_task(self):
        if not self.check_agent_ready():
            return
        task = self.input_field.get("1.0", ttk.END).strip()
        if not task:
            messagebox.showwarning("输入为空", "请输入任务内容")
            return
        self.input_field.delete("1.0", ttk.END)
        self.add_message("你", task, is_user=True)
        self.add_message("CodeGenius", stream=True)
        self.status_var.set("思考中...")
        self.send_btn.config(state=ttk.DISABLED)
        threading.Thread(target=self.run_agent_task, args=(task,), daemon=True).start()

    def run_agent_task(self, task: str):
        try:
            self.agent.chat(task)
        except Exception as e:
            self.root.after(0, lambda: self.add_message("系统", f"❌ 错误: {str(e)}"))
        finally:
            self.root.after(0, self.cleanup_streaming)
            self.root.after(0, lambda: self._enable_send_btn())

    def _enable_send_btn(self):
        self.status_var.set("就绪")
        self.send_btn.config(state=ttk.NORMAL)

    def check_agent_ready(self) -> bool:
        if not self.project_folder:
            self.show_banner(True)
            messagebox.showwarning("提示", "请先选择项目文件夹！")
            return False
        if self.agent is None:
            self.show_banner(True)
            messagebox.showwarning("提示", "请先初始化智能体！")
            return False
        self.show_banner(False)
        return True

    def show_banner(self, show: bool):
        pass;
        # if show:
        #     self.banner_frame.pack(fill=ttk.X, pady=(0, 10))
        # else:
        #     self.banner_frame.pack_forget()

    def initialize_agent(self):
        if not self.project_folder:
            messagebox.showwarning("提示", "请先选择项目文件夹！")
            return
        api_key = self.api_key_var.get().strip()
        base_url = self.base_url_var.get().strip()
        model_name = self.model_var.get().strip()
        system_prompt = self.system_prompt_text.get("1.0", ttk.END).strip()

        if not api_key or api_key == "YOUR_API_KEY":
            messagebox.showerror("错误", "请填写有效的 API 密钥！")
            return
        if not base_url.startswith("http"):
            messagebox.showerror("错误", "Base URL 必须以 http:// 或 https:// 开头！")
            return
        if not model_name:
            messagebox.showerror("错误", "请填写有效的模型名称！")
            return
        if not system_prompt:
            messagebox.showerror("错误", "请填写系统提示词！")
            return

        self.status_var.set("初始化中...")
        self.send_btn.config(state=ttk.DISABLED)
        self.config_btn.config(state=ttk.DISABLED)
        self.root.update()

        progress_win = ttk.Toplevel(self.root)
        progress_win.title("初始化中")
        progress_win.geometry("300x100")
        progress_win.transient(self.root)
        ttk.Label(progress_win, text="正在初始化智能体，请稍候...", padding=20).pack()
        progress_win.update()

        threading.Thread(target=self._init_agent_background, args=(progress_win, api_key, base_url, model_name, system_prompt), daemon=True).start()

    def _init_agent_background(self, progress_win, api_key, base_url, model_name, system_prompt):
        try:
            # Initialize LLM
            llm = OpenAILLM(
                api_key=api_key,
                base_url=base_url,
                model_name=model_name
            )
            if not system_prompt:
                raise ValueError("系统提示词不能为空！")
            
            # Initialize PythonProgrammerAgent (adjust parameters based on actual constructor)
            agent = PythonProgrammerAgent(
                basellm = llm,
                project_dir=self.project_folder,
                system_prompt=system_prompt
            )
            agent.set_token_deal_call_back(update_ui_callback=self.update_streaming_message)
            self.root.after(0, lambda: self._on_init_success(agent, progress_win))
        except Exception as error:
            logging.error(f"初始化失败: {error}")
            self.root.after(0, lambda: self._on_init_error(str(error), progress_win))

    def _on_init_success(self, agent, progress_win):
        self.agent = agent
        progress_win.destroy()
        messagebox.showinfo("成功", "智能体初始化成功！")
        self.status_var.set("就绪")
        self.show_banner(False)
        self.close_config()
        self._restore_buttons()

    def _on_init_error(self, error_msg, progress_win):
        progress_win.destroy()
        messagebox.showerror("错误", f"初始化失败:\n{error_msg}")
        self.status_var.set("就绪")
        self._restore_buttons()

    def _restore_buttons(self):
        self.send_btn.config(state=ttk.NORMAL)
        self.config_btn.config(state=ttk.NORMAL)

if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")
    app = CodeGeniusApp(root)
    root.mainloop()