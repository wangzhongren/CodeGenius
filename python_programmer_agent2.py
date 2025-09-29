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

    def __init__(self, basellm,system_prompt=("你是个有用的助手"), project_dir="output"):
        system_prompt = system_prompt + FileOperationHandler.get_file_operation_prompt()
        
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