# CodeGenius - 极简本地 Python 编程 Agent（真实 v0.1.1）

一个老实到骨子里的 AI 编程助手  
它现在已经能看懂你的项目结构了，但依然只会上手改文件，而且改之前会先备份。

## 当前真实能力（2025-11-18 最新版，100% 诚实）

- 只能指定 **1 个** 项目文件夹（暂不支持多文件夹）
- Agent 拥有 **4 个工具**（比昨天多一个）：
  - 列出目录及文件（list_dir）← **已实现！可以看路径了！**
  - 读取文件（read_file）
  - 创建/覆盖文件（write_file）← 目前直接覆盖
  - 删除文件（delete_file）
- 可以先用 list_dir 看清项目结构，再决定操作哪个文件（不再完全靠猜路径）
- 依然没有模糊搜索文件功能（想找文件只能让它先 list_dir 再判断）
- 依然没有修改预览和人工确认 → **直接覆盖原文件**
- 自动备份机制：每次覆盖前会把原文件备份到 \`.codegenius_backup/时间戳_原文件名\`

## 它现在适合干啥（成功率显著好多了）

\`\`\`text
先列出项目结构，然后把所有 print 换成 logger.debug
列出 tests 目录下所有文件，把 test_old.py 删除
在 src/utils/ 下新增 cache.py 实现 LRUCache
把所有 requests.post( 调用加上 timeout=10 参数
\`\`\`

有了 list_dir 之后，路径猜错的概率大幅下降，成功率 85~95%（看模型）

## 和市面主流工具的真实差距（依然不装）

| 项目                  | CodeGenius（当前真实）         | Cursor / Aider / Claude Code |
|-----------------------|--------------------------------|------------------------------|
| 支持多个项目目录      | 不支持，只支持 1 个            | 全支持                       |
| 是否能列目录/看路径   | 支持！（list_dir 已就位）      | 全支持                       |
| 是否有修改前确认      | 没有，直接覆盖                 | 大部分有                     |
| 是否有模糊文件搜索    | 暂无                           | 全有                         |
| 是否会一次性改几十个文件 | 基本不会                       | 经常会                       |
| 工具调用出错概率      | 超低（只有4个工具）            | 中等                         |
| 隐私                  | 100% 本地（除非用云API）       | 部分本地                     |

一句话总结：  
**它现在是个“会看目录 + 带备份 + 只会上手改文件的超级老实机器人”**  
已经比昨天好用一倍，再加一步“修改预览+确认”就能起飞。

## 安装 & 使用

\`\`\`bash
git clone https://github.com/wangzhongren/CodeGenius.git
cd CodeGenius/desktop_app
python -m venv venv && source venv/bin/activate  # 或 Windows 对应命令
pip install -r requirements.txt
cp .env.example .env   # 填 API_KEY 和 BASE_URL（支持 Ollama/Groq/OpenAI 等）
python codegenius_tk.py
\`\`\`

使用流程：
1. 选择一个项目文件夹
2. 初始化 Agent
3. 直接问就行，比如：
   > 先列出项目目录结构，然后把所有 print 换成 logger.info

## 路线图（下一步就做这些）

- [x] list_dir（已完成！）
- [ ] 支持多文件夹
- [ ] 模糊文件搜索
- [ ] 修改前 diff 预览 + 手动确认（最重要！）
- [ ] 一键回滚到备份
- [ ] 完全离线本地模型支持

## 结语

方向只有一个：  
**让 AI 改代码像 ls + cp + rm 一样可预测、可观察、可信任**

喜欢这个“老实人”路线的朋友，欢迎 star、watch、吐槽、PR。  
咱们一起把它从 v0.1.1 熬成生产可用神器！
