好的！现在立刻给你终极真实版 —— 连“自动备份”这句都删掉，一句废话没有，一句牛逼没吹，纯纯的“老实得发光”：
HTML<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>下载 CodeGenius 终极真实版 README.md</title>
  <style>
    body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Oxygen,Ubuntu,Cantarell,"Open Sans","Helvetica Neue",sans-serif;background:#f6f8fa;margin:0;height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;color:#24292e;}
    h1{font-size:2.5rem;margin-bottom:1rem;}
    p{font-size:1.2rem;max-width:680px;text-align:center;margin-bottom:3rem;color:#586069;}
    button{font-size:1.4rem;padding:16px 48px;background:#2ea44f;color:white;border:none;border-radius:8px;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,0.15);transition:all .2s;}
    button:hover{background:#2c974b;transform:translateY(-2px);}
    .footer{margin-top:4rem;font-size:0.9rem;color:#888;}
  </style>
</head>
<body>
  <h1>CodeGenius</h1>
  <p>2025-11-18 终极真实能力版 README<br>—— 连备份都没有，纯纯的硬刚</p>
  <button id="downloadBtn">下载 README.md</button>
  <div class="footer">一点就下 · 直接粘仓库 · 老实人专属</div>

  <script>
    const markdownContent = `# CodeGenius - 极简本地 Python 编程 Agent（终极真实 v0.1.1）

我现在就是一个最最最老实的文件读写机器人。  
连自动备份都没有，改前直接覆盖，纯靠你自己 git 救命。

## 当前 100% 真实能力（2025-11-18）

- 只能指定 **1 个** 项目文件夹
- Agent 拥有 **4 个工具**：
  - list_dir → 列出目录（能看到路径了！）
  - read_file → 读文件
  - write_file → **直接覆盖原文件**（无备份、无预览、无确认）
  - delete_file → 直接删除（也没确认）
- 没有搜索文件功能
- 没有 diff 预览
- 没有人工确认步骤
- 没有备份机制（你没做，我就不写）

## 它现在适合干啥（谨慎使用！）

只有在下面这几种情况才敢用：

\`\`\`text
先列出目录结构，然后把 utils.py 里的 print 换成 logger.debug
在 project/ 下新增 config.py 内容如下……
删除 tests/test_legacy.py 这个文件
\`\`\`

路径对了 + 模型不抽风 = 成功  
路径错了或模型抽风 = 你自己 git revert

## 和主流工具真实差距（完全不装）

| 项目                  | CodeGenius（现在）       | Cursor / Aider / Claude Code |
|-----------------------|--------------------------|------------------------------|
| 支持多文件夹          | 不支持                   | 全支持                       |
| 能否列目录            | 支持                     | 支持                         |
| 是否有修改预览/确认   | 完全没有                 | 大部分有                     |
| 是否会批量改文件      | 基本不会                 | 经常会                       |
| 是否有备份            | 没有                     | 大部分有                     |
| 工具调用出错概率      | 极低（只有4个）          | 中等                         |
| 敢不敢在生产项目用    | 你敢我也不拦着           | 他们敢                       |

一句话总结：  
**我现在就是 ls + cat + echo > + rm 的 AI 版**  
用前请先 git commit，出了事别骂我。

## 安装使用

\`\`\`bash
git clone https://github.com/wangzhongren/CodeGenius.git
cd CodeGenius/desktop_app
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python codegenius_tk.py
\`\`\`

用之前记得：
\`\`\`bash
git add .
git commit -m "before codegenius 救命存档"
\`\`\`

## 路线图（接下来必须做的）

- [ ] 加上自动备份（最紧急！）
- [ ] 修改前 diff 预览 + 手动 Y/n 确认
- [ ] 支持多文件夹
- [ ] 文件模糊搜索
- [ ] 一键回滚

## 结语

这玩意儿现在就是个“带大模型的危险脚本”  
但方向是对的：极简工具 + 可见每一步 + 最终可信任

喜欢这个“从零开始老实做”的风格，欢迎 star、watch、吐槽、PR  
咱们一起把它从“危险”变成“生产可用”

MIT License © wangzhongren
