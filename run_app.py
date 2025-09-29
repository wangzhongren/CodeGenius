# -*- coding: utf-8 -*-
"""
启动Python程序员智能体桌面应用
"""

import sys
import os

# 添加父目录到Python路径，以便导入ai_agent_factory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 现在运行主应用
if __name__ == "__main__":
    from main import create_ui
    create_ui()