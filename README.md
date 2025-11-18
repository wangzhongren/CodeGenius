# CodeGenius - 极简本地 Python 编程 Agent（真实 v0.1）

一个老实到不能再老实的 AI 编程助手  
它现在真的只有最基础的能力，但也正因如此，几乎不可能把你的项目搞崩。

## 当前真实能力（2025-11-18 版本，100% 诚实）

- 只能指定 **1 个** 项目文件夹（不支持多选、不支持多个目录）
- Agent 只有 **3 个工具**：
  - 读取文件（read_file）
  - 创建/覆盖文件（write_file）← 目前直接覆盖
  - 删除文件（delete_file）
- 没有列出目录工具（list_dir 还没做）
- 没有搜索文件工具（只能靠 LLM 猜路径）
- 没有修改预览和人工确认步骤 → **直接覆盖原文件**
- 为了防止你骂街，会自动把原文件备份到项目根目录下的 `.codegenius_backup/yyyy-mm-dd_hh-mm-ss_原文件名`

## 它现在适合干啥（别指望太多）

你可以用它做一些“相对安全”的小任务，比如：

```text
把 utils.py 里的所有 print 换成 logger.debug
在项目里新增一个 tools/cache.py 文件，内容实现 LRUCache
把 tests/test_old.py 删除掉
把所有 requests.post( 调用加上 timeout=10 参数
```

只要路径猜对了、任务描述清楚了，成功率还不错（70~90% 取决于模型）

## 和市面主流工具的真实差距（完全不装）

| 项目                  | CodeGenius（现在）           | Cursor / Continue / Aider / Claude Code |
|-----------------------|------------------------------|-----------------------------------------|
| 支持多个项目目录      | 不支持，只支持 1 个          | 全部支持                                |
| 是否有修改前确认      | 没有，直接覆盖               | 大部分有                                |
| 是否有文件列表/搜索   | 没有，靠 LLM 猜路径          | 全都有                                  |
| 工具调用出错概率      | 极低（只有3个工具）          | 中等（工具太多容易选错）                |
| 是否会一次性改几十个文件 | 基本不会                     | 经常会                                  |
| 幻觉后能否现场补救    | 能（你看得见每一步）         | 部分能                                  |
| 隐私                  | 100% 本地（除非你用云API）   | 部分本地                                |

总结一句话：  
**它现在就是个“带备份的、3工具版、最老实的文件读写机器人”**，  
离“好用”还早，但离“敢在生产项目里试试”已经比 90% 的全自动 Agent 近多了。

## 安装 & 使用（超级简单）

```bash
git clone https://github.com/wangzhongren/CodeGenius.git
cd CodeGenius/desktop_app
python -m venv venv
# 激活虚拟环境...
pip install -r requirements.txt
cp .env.example .env   # 填你的 API_KEY 和 BASE_URL（支持 Ollama/Groq/OpenAI 等）
python codegenius_tk.py
```

使用流程：
1. 点击“选择” → 选一个项目文件夹（只能选一个）
2. 初始化 Agent
3. 直接聊天提问就行

## 接下来准备加的功能（路线图）

- [ ] 支持多文件夹选择
- [ ] 添加 list_dir 工具
- [ ] 添加模糊搜索文件工具
- [ ] 修改前 diff 预览 + 手动确认（这个最重要）
- [ ] 一键回滚到备份
- [ ] 支持本地模型完全离线运行

## 结语

这玩意儿现在还很原始，但方向是：  
**“让 AI 改代码像 cp、mv、rm 一样可预测、可回滚、可信任”**

喜欢这个“老实人”路线的朋友，欢迎 star、watch、提 issue、吐槽、PR。  
我们一起把它从 v0.1 熬成真正的生产可用工具。

MIT License © wangzhongren
