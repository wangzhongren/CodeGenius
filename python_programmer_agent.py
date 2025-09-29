import json
import re
import os
from ai_agent_factory.agent.baseagent import BaseAgent
from ai_agent_factory.llms.base_llm_openai import OpenAILLM
from ai_agent_factory.utils.file_operation_handler import FileOperationHandler

class PythonProgrammerAgent(BaseAgent):
    """
    Python程序员智能体 - 专门处理Python开发任务的智能体
    """

    def __init__(self, basellm,system_prompt="", project_dir="output"):
        system_prompt = (
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
    "数据库配置：\n"
    "  MYSQL_HOST=106.14.112.246\n"
    "  MYSQL_PORT=9876\n"
    "  MYSQL_USER=root\n"
    "  MYSQL_PASSWORD=Th_mysql_123456\n"
    "  MYSQL_DATABASE=thspider\n"
    "  REDIS_HOST=106.14.112.246\n"
    "  REDIS_PORT=6379\n"
    "  REDIS_PASSWORD=tinghai2022\n"
    "  REDIS_DB=14\n"
    "  RABBITMQ_HOST=106.14.112.246\n"
    "  RABBITMQ_PORT=5672\n"
    "  RABBITMQ_USER=admin\n"
    "  RABBITMQ_PASSWORD=admin2022\n"
    "  RABBITMQ_VHOST=/\n"
    "  SQLITE_PATH=./database.sqlite\n"
    "\n阿里云配置：\n"
    "  ALIYUN_ACCESS_KEY_ID=LTAIGYvHrAs8eow2\n"
    "  ALIYUN_ACCESS_KEY_SECRET=yHrOl28pR5dAgfYXfrV7GkwFXn00ja\n"
    "  ALIYUN_REGION=cn-shanghai\n"
    "\n阿里云表格存储（OTS）：\n"
    "  OTS_ENDPOINT=https://abujlb3.cn-shanghai.ots.aliyuncs.com\n"
    "  OTS_INSTANCE_NAME=abujlb3\n"
    "\n阿里云OSS：\n"
    "  OSS_ENDPOINT=https://oss-cn-shanghai.aliyuncs.com\n"
    "  OSS_BUCKET_NAME=abujlbjson\n"
    "\nOpenAI API（兼容DashScope）：\n"
    "  OPENAI_API_KEY=sk-97650777219a49a19c80c1c9791da101\n"
    "  OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1\n"
    "\n你应基于上述配置设计合理的配置管理模块（如 `config/settings.py`），\n"
    "使用 `os.getenv()` 或 `python-dotenv` 从 `.env` 文件加载值，\n"
    "并在代码中引用配置项，而非直接写入密钥。\n"
    "\n文件操作指令支持：\n"
) + FileOperationHandler.get_file_operation_prompt()
        
        super().__init__(basellm, system_prompt, max_context=50)
        self.files = []
        self.project_dir = project_dir
        self.file_handler = FileOperationHandler(project_dir)
        self.current_response = ""  # 用于累积流式 token

    def set_token_deal_call_back(self,update_ui_callback):
        self.update_ui_callback  = update_ui_callback;

    def token_deal(self, token: str):
        """
        处理流式返回的每个 token，并通过回调更新 UI
        """
        self.current_response += token
        if self.update_ui_callback:
            self.update_ui_callback(token)
        print(token, end='', flush=True)

    def todo(self, token: str):
        """
        处理完整的 AI 回复
        """
        try:
            need_data = []
            print(f"\n🔍 收到Python开发响应，长度: {len(token)} 字符")
            
            # 检查是否包含文件操作标记
            if FileOperationHandler.has_file_operations(token):
                print("✅ 检测到文件操作指令")
                
                def callback(op, result):
                    need_data.append(result)
                
                result = self.file_handler.handle_tagged_file_operations(token, callback)
                if result:
                    print("✅ 文件操作处理完成")
                self.chat(json.dumps(need_data, ensure_ascii=False))
            else:
                print("⚠️ 未检测到文件操作指令")
                # 普通文本已通过 token_deal 实时更新 UI，此处无需重复处理
                self.current_response = ""  # 重置累积响应
                
        except Exception as e:
            print(f"\n❌ Python程序员处理失败: {e}")
            import traceback
            traceback.print_exc()
            print("原始响应:", token)
            return f"错误: {str(e)}"

    def create_file(self, filename: str, content: str):
        """
        创建文件
        """
        return self.file_handler.create_file(filename, content)

    def read_file(self, filename: str):
        """
        读取文件
        """
        return self.file_handler.read_file(filename)

    def update_file(self, filename: str, content: str):
        """
        更新文件
        """
        return self.file_handler.update_file(filename, content)

    def delete_file(self, filename: str):
        """
        删除文件
        """
        return self.file_handler.delete_file(filename)

    def list_files(self):
        """
        列出所有文件
        """
        return self.file_handler.list_files()