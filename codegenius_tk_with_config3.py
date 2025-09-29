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
from tkinter import filedialog, messagebox
import configparser
import queue
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Dict, Any
import textwrap
import re

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
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent
    else:
        app_dir = Path(__file__).parent

    env_file = app_dir / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
        return True

    for _ in range(2):
        app_dir = app_dir.parent
        env_file = app_dir / ".env"
        if env_file.exists():
            load_dotenv(dotenv_path=env_file)
            return True
        
    os.environ.setdefault("API_KEY", "YOUR_API_KEY")
    os.environ.setdefault("BASE_URL", "https://api.openai.com/v1")
    os.environ.setdefault("MODEL_NAME", "gpt-4o-mini")
    return False

# 加载应用配置文件
def load_app_config(app_dir):
    config = configparser.ConfigParser()
    config_file = app_dir / "config.ini"
    
    if config_file.exists():
        config.read(config_file, encoding="utf-8")
        if 'settings' in config:
            project_folder = config['settings'].get('project_folder', '')
            system_prompt = config['settings'].get('system_prompt', '')
            return project_folder, system_prompt
    return '', (
        "你是一位专业的Python程序员，精通各种Python开发任务。\n"
        "你需要根据用户的需求，完成Python项目的开发工作。\n"
        "请始终输出可运行、结构清晰、注释完整的代码。\n"
        "如果任务复杂，请分步骤实现，并解释每一步的逻辑。"
    )

# 保存应用配置文件
def save_app_config(app_dir, project_folder, system_prompt):
    config = configparser.ConfigParser()
    config['settings'] = {
        'project_folder': project_folder,
        'system_prompt': system_prompt
    }
    config_file = app_dir / "config.ini"
    with open(config_file, 'w', encoding='utf-8') as f:
        config.write(f)

class VirtualChatWidget:
    """高性能虚拟化聊天组件"""
    
    def __init__(self, parent, width=800, height=400):
        self.parent = parent
        self.width = width
        self.height = height
        self.is_dark = False
        
        # 消息存储
        self.messages: List[Dict] = []
        self.visible_messages: List[Dict] = []
        self.streaming_buffer = ""
        self.is_streaming = False
        
        # 渲染相关
        self.canvas = tk.Canvas(parent, width=width, height=height, bg='white')
        self.scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # 布局
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
        
        # 字体和颜色
        self.font_normal = ('Microsoft YaHei', 10)
        self.font_bold = ('Microsoft YaHei', 10, 'bold')
        self.font_italic = ('Microsoft YaHei', 9, 'italic')
        
        self.colors = {
            'bg_light': '#ffffff',
            'bg_dark': '#2b2b2b',
            'text_light': '#000000',
            'text_dark': '#ffffff',
            'user_light': '#007bff',
            'user_dark': '#4dabf7',
            'ai_light': '#6c757d',
            'ai_dark': '#adb5bd',
            'header_light': '#6c757d',
            'header_dark': '#adb5bd'
        }
        
        # 绑定事件
        self.canvas.bind('<Configure>', self._on_resize)
        self.canvas.bind('<MouseWheel>', self._on_scroll)
        
        # 渲染参数
        self.line_height = 20
        self.padding_x = 10
        self.padding_y = 5
        self.header_height = 25
        self.total_height = 0
        
    def set_dark_mode(self, is_dark: bool):
        """设置暗色模式"""
        self.is_dark = is_dark
        bg_color = self.colors['bg_dark'] if is_dark else self.colors['bg_light']
        self.canvas.configure(bg=bg_color)
        self._render_all()
        
    def add_message(self, sender: str, text: str, is_user: bool = False):
        """添加消息"""
        message = {
            'sender': sender,
            'text': text,
            'is_user': is_user,
            'timestamp': time.time(),
            'lines': []
        }
        self.messages.append(message)
        self._calculate_message_layout(message)
        self._render_all()
        
    def start_streaming(self):
        """开始流式输出"""
        self.is_streaming = True
        self.streaming_buffer = ""
        
    def update_streaming(self, token: str):
        """更新流式输出"""
        if not self.is_streaming:
            return
            
        self.streaming_buffer += token
        # 限制渲染频率 - 每100ms渲染一次
        current_time = time.time()
        if hasattr(self, '_last_stream_render'):
            if current_time - self._last_stream_render < 0.1:  # 100ms
                return
        self._last_stream_render = current_time
        
        self._render_streaming()
        
    def end_streaming(self):
        """结束流式输出"""
        if self.is_streaming:
            self.is_streaming = False
            if self.streaming_buffer.strip():
                self.add_message("CodeGenius", self.streaming_buffer.strip())
            self.streaming_buffer = ""
            self._render_all()
            
    def _calculate_message_layout(self, message: Dict):
        """计算消息的布局"""
        text = message['text']
        max_width = self.width - 2 * self.padding_x - 20
        
        # 包装文本
        if message['is_user']:
            header = f"【你】"
        else:
            header = f"【CodeGenius】"
            
        # 计算头部
        message['lines'] = [header]
        message['line_types'] = ['header']
        
        # 计算正文
        wrapped_lines = textwrap.wrap(text, width=max_width // 7)  # 估算字符宽度
        for line in wrapped_lines:
            message['lines'].append(line)
            message['line_types'].append('text')
            
    def _render_all(self):
        """渲染所有消息"""
        self.canvas.delete("all")
        
        bg_color = self.colors['bg_dark'] if self.is_dark else self.colors['bg_light']
        self.canvas.configure(bg=bg_color)
        
        y = self.padding_y
        max_width = self.width - 2 * self.padding_x
        
        for message in self.messages:
            # 渲染消息
            for i, (line, line_type) in enumerate(zip(message['lines'], message['line_types'])):
                if line_type == 'header':
                    color = self.colors['header_dark'] if self.is_dark else self.colors['header_light']
                    font = self.font_italic
                else:
                    if message['is_user']:
                        color = self.colors['user_dark'] if self.is_dark else self.colors['user_light']
                    else:
                        color = self.colors['ai_dark'] if self.is_dark else self.colors['ai_light']
                    font = self.font_normal
                    
                self.canvas.create_text(
                    self.padding_x, y, 
                    text=line, 
                    anchor='nw', 
                    fill=color, 
                    font=font,
                    width=max_width
                )
                y += self.line_height
                
            # 消息间距
            y += self.padding_y
            
        # 渲染流式内容
        if self.is_streaming and self.streaming_buffer:
            self._render_streaming_at_position(y)
            
        # 更新滚动区域
        self.total_height = y
        self.canvas.configure(scrollregion=(0, 0, self.width, self.total_height))
        
    def _render_streaming(self):
        """渲染流式内容"""
        self.canvas.delete("streaming")
        self._render_streaming_at_position(self.total_height)
        
    def _render_streaming_at_position(self, y: int):
        """在指定位置渲染流式内容"""
        max_width = self.width - 2 * self.padding_x
        
        # 渲染头部
        self.canvas.create_text(
            self.padding_x, y, 
            text="【CodeGenius】", 
            anchor='nw', 
            fill=self.colors['header_dark'] if self.is_dark else self.colors['header_light'], 
            font=self.font_italic,
            width=max_width,
            tags="streaming"
        )
        y += self.line_height
        
        # 渲染流式文本
        wrapped_lines = textwrap.wrap(self.streaming_buffer, width=max_width // 7)
        for line in wrapped_lines:
            self.canvas.create_text(
                self.padding_x, y, 
                text=line, 
                anchor='nw', 
                fill=self.colors['ai_dark'] if self.is_dark else self.colors['ai_light'], 
                font=self.font_normal,
                width=max_width,
                tags="streaming"
            )
            y += self.line_height
            
        # 更新滚动区域
        streaming_height = y
        total_height = max(self.total_height, streaming_height)
        self.canvas.configure(scrollregion=(0, 0, self.width, total_height))
        self.canvas.yview_moveto(1.0)  # 自动滚动到底部
        
    def _on_resize(self, event):
        """处理窗口大小变化"""
        self.width = event.width
        self.height = event.height
        # 重新计算所有消息的布局
        for message in self.messages:
            self._calculate_message_layout(message)
        self._render_all()
        
    def _on_scroll(self, event):
        """处理鼠标滚动"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
    def clear(self):
        """清空聊天记录"""
        self.messages.clear()
        self.streaming_buffer = ""
        self.is_streaming = False
        self.canvas.delete("all")
        self.total_height = 0

class HighPerformanceCodeGeniusApp:
    def __init__(self, root: ttk.Window):
        # 判断应用目录
        if getattr(sys, 'frozen', False):
            self.app_dir = Path(sys.executable).parent
        else:
            self.app_dir = Path(__file__).parent
        
        load_config_from_env()
        
        # 加载应用配置
        default_project_folder, default_system_prompt = load_app_config(self.app_dir)
        self.project_folder = default_project_folder
        self.system_prompt_var = tk.StringVar(value=default_system_prompt)
        
        self.root = root
        self.root.title("🧠 CodeGenius - AI 编程助手")
        self.root.geometry("1000x750")
        self.root.minsize(800, 600)

        self.is_dark = False
        self.style = ttk.Style("cosmo")
        self.agent = None
        self.config_win_visible = False
        
        # 高性能消息处理
        self.setup_high_performance_messaging()
        self.create_widgets()
        
        # 如果有默认 project_folder，设置并初始化日志
        if self.project_folder:
            self.folder_var.set(f"📁 {os.path.basename(self.project_folder)}")
            os.chdir(self.project_folder)
            setup_logging(self.project_folder)

    def setup_high_performance_messaging(self):
        """设置高性能消息处理系统"""
        self.message_queue = queue.Queue()
        self.processing = True
        self.last_render_time = 0
        self.RENDER_INTERVAL = 0.033  # 30fps
        
        # 启动消息处理线程
        self.message_thread = threading.Thread(target=self._process_message_queue, daemon=True)
        self.message_thread.start()

    def _process_message_queue(self):
        """独立线程处理消息队列"""
        while self.processing:
            try:
                # 非阻塞获取消息
                try:
                    msg_type, data = self.message_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                    
                current_time = time.time()
                
                if msg_type == "add_message":
                    self.chat_widget.add_message(data["sender"], data["text"], data["is_user"])
                    self._schedule_render()
                    
                elif msg_type == "start_stream":
                    self.chat_widget.start_streaming()
                    self._schedule_render()
                    
                elif msg_type == "stream_token":
                    self.chat_widget.update_streaming(data)
                    # 流式更新使用独立的渲染调度
                    if current_time - self.last_render_time >= self.RENDER_INTERVAL:
                        self._render_now()
                    
                elif msg_type == "end_stream":
                    self.chat_widget.end_streaming()
                    self._schedule_render()
                    
            except Exception as e:
                logging.error(f"消息处理错误: {e}")

    def _schedule_render(self):
        """调度渲染（防抖）"""
        current_time = time.time()
        if current_time - self.last_render_time >= self.RENDER_INTERVAL:
            self._render_now()

    def _render_now(self):
        """立即渲染"""
        self.last_render_time = time.time()
        self.root.after_idle(self.chat_widget._render_all)

    def add_message(self, sender: str, text: str = "", is_user: bool = False):
        """添加消息到队列"""
        self.message_queue.put(("add_message", {
            "sender": sender, 
            "text": text, 
            "is_user": is_user
        }))

    def update_streaming_message(self, token: str):
        """更新流式消息到队列"""
        self.message_queue.put(("stream_token", token))

    def start_streaming(self):
        """开始流式输出"""
        self.message_queue.put(("start_stream", None))

    def cleanup_streaming(self):
        """清理流式输出"""
        self.message_queue.put(("end_stream", None))

    def create_widgets(self):
        # 顶部栏
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="🧠 CodeGenius", font=("", 16, "bold"), bootstyle=PRIMARY).pack(side=tk.LEFT)

        right_frame = ttk.Frame(top_frame)
        right_frame.pack(side=tk.RIGHT)

        self.config_btn = ttk.Button(right_frame, text="⚙️ 配置", bootstyle=OUTLINE, command=self.open_config)
        self.config_btn.pack(side=tk.LEFT, padx=5)

        self.theme_btn = ttk.Button(right_frame, text="🌙 暗色", bootstyle=OUTLINE, command=self.toggle_theme)
        self.theme_btn.pack(side=tk.LEFT, padx=5)

        # 主区域
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Banner
        self.banner_frame = ttk.Frame(main_frame, bootstyle="warning", padding=10)
        ttk.Label(
            self.banner_frame,
            text="⚠️ 请先选择项目文件夹并初始化智能体",
            bootstyle="inverse-warning",
            font=("", 10)
        ).pack()
        self.banner_frame.pack(fill=tk.X, pady=(0, 10))
        self.banner_frame.pack_forget()

        # 高性能聊天组件
        chat_container = ttk.Frame(main_frame)
        chat_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.chat_widget = VirtualChatWidget(chat_container)
        self.chat_widget.canvas.pack(fill=tk.BOTH, expand=True)

        # 输入区 —— 使用 grid 布局修复位置问题 ✅
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(10, 0))
        input_frame.columnconfigure(0, weight=1)  # Text 占据剩余空间

        self.input_field = ttk.Text(
            input_frame,
            height=3,
            font=("Microsoft YaHei", 10),
            wrap=tk.WORD
        )
        self.input_field.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.send_btn = ttk.Button(
            input_frame,
            text="发送",
            bootstyle=PRIMARY,
            command=self.send_task
        )
        self.send_btn.grid(row=0, column=1, sticky="ns")  # 垂直拉伸对齐

        self.input_field.bind("<Return>", self.on_enter)
        self.input_field.focus_set()  # 自动聚焦

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, bootstyle="secondary", padding=(10, 5))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 配置窗口
        self.create_config_window()

    def create_config_window(self):
        self.config_win = ttk.Toplevel(self.root)
        self.config_win.title("⚙️ 配置")
        self.config_win.geometry("450x800")
        self.config_win.withdraw()
        self.config_win.transient(self.root)

        frame = ttk.Frame(self.config_win, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="⚙️ 配置", font=("", 14, "bold")).pack(pady=(0, 15))

        folder_frame = ttk.Frame(frame)
        folder_frame.pack(fill=tk.X, pady=5)
        self.folder_var = tk.StringVar(value="未选择项目" if not self.project_folder else f"📁 {os.path.basename(self.project_folder)}")
        ttk.Label(folder_frame, textvariable=self.folder_var, bootstyle="secondary").pack(side=tk.LEFT)
        ttk.Button(folder_frame, text="📁 选择", command=self.select_folder, bootstyle=OUTLINE).pack(side=tk.RIGHT)

        self.api_key_var = tk.StringVar(value=os.getenv("API_KEY", "YOUR_API_KEY"))
        self.base_url_var = tk.StringVar(value=os.getenv("BASE_URL", "https://api.openai.com/v1").strip())
        self.model_var = tk.StringVar(value=os.getenv("MODEL_NAME", "gpt-4o-mini"))

        for label, var in [("API 密钥:", self.api_key_var), ("Base URL:", self.base_url_var), ("模型:", self.model_var)]:
            ttk.Label(frame, text=label).pack(anchor=tk.W, pady=(10, 0))
            entry = ttk.Entry(frame, textvariable=var, width=50)
            if label == "API 密钥:":
                entry.config(show="*")
            entry.pack(fill=tk.X, pady=5)

        ttk.Label(frame, text="系统提示词:").pack(anchor=tk.W, pady=(10, 0))
        self.system_prompt_text = ttk.Text(frame, height=15, width=50, font=("Microsoft YaHei", 10))
        self.system_prompt_text.insert("1.0", self.system_prompt_var.get())
        self.system_prompt_text.pack(fill=tk.X, pady=5)

        init_btn = ttk.Button(frame, text="🚀 初始化智能体", bootstyle=SUCCESS, command=self.initialize_agent)
        init_btn.pack(pady=20)

    def toggle_theme(self):
        if self.is_dark:
            self.style.theme_use("cosmo")
            self.theme_btn.config(text="🌙 暗色")
            self.is_dark = False
            self.chat_widget.set_dark_mode(False)
        else:
            self.style.theme_use("darkly")
            self.theme_btn.config(text="☀️ 亮色")
            self.is_dark = True
            self.chat_widget.set_dark_mode(True)

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
            system_prompt = self.system_prompt_text.get("1.0", tk.END).strip()
            save_app_config(self.app_dir, self.project_folder, system_prompt)

    def open_config(self):
        if self.config_win_visible:
            self.config_win.lift()
            return
        self.config_win_visible = True
        self.config_win.deiconify()
        self.config_win.lift()
        self.config_win.protocol("WM_DELETE_WINDOW", self.close_config)

    def close_config(self):
        system_prompt = self.system_prompt_text.get("1.0", tk.END).strip()
        save_app_config(self.app_dir, self.project_folder, system_prompt)
        self.config_win_visible = False
        self.config_win.withdraw()

    def on_enter(self, event=None):
        # 按 Enter 发送，Shift+Enter 换行
        if event.state & 0x1:  # Shift 键按下
            return
        self.send_task()
        return "break"

    def send_task(self):
        if not self.check_agent_ready():
            return
        task = self.input_field.get("1.0", tk.END).strip()
        if not task:
            messagebox.showwarning("输入为空", "请输入任务内容")
            return
        self.input_field.delete("1.0", tk.END)
        self.add_message("你", task, is_user=True)
        self.start_streaming()
        self.status_var.set("思考中...")
        self.send_btn.config(state=tk.DISABLED)
        
        # 使用线程执行任务
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
        self.send_btn.config(state=tk.NORMAL)

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
        if show:
            self.banner_frame.pack(fill=tk.X, pady=(0, 10))
        else:
            self.banner_frame.pack_forget()

    def initialize_agent(self):
        if not self.project_folder:
            messagebox.showwarning("提示", "请先选择项目文件夹！")
            return
        api_key = self.api_key_var.get().strip()
        base_url = self.base_url_var.get().strip()
        model_name = self.model_var.get().strip()
        system_prompt = self.system_prompt_text.get("1.0", tk.END).strip()

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

        save_app_config(self.app_dir, self.project_folder, system_prompt)

        self.status_var.set("初始化中...")
        self.send_btn.config(state=tk.DISABLED)
        self.config_btn.config(state=tk.DISABLED)
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
            llm = OpenAILLM(
                api_key=api_key,
                base_url=base_url,
                model_name=model_name
            )
            if not system_prompt:
                raise ValueError("系统提示词不能为空！")
            
            agent = PythonProgrammerAgent(
                basellm=llm,
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
        self.send_btn.config(state=tk.NORMAL)
        self.config_btn.config(state=tk.NORMAL)

    def destroy(self):
        """清理资源"""
        self.processing = False
        if hasattr(self, 'message_thread') and self.message_thread.is_alive():
            self.message_thread.join(timeout=1.0)

if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")
    app = HighPerformanceCodeGeniusApp(root)
    
    try:
        root.mainloop()
    finally:
        app.destroy()