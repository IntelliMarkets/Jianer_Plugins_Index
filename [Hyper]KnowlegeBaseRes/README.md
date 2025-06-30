# 高级AI问答插件 (基于RAG架构)

**作者：小泥人Hyper**

---

这是一款为您的QQ机器人设计的、基于检索增强生成 (Retrieval-Augmented Generation, RAG) 架构的智能问答插件。它能够让您的机器人不再依赖固定的、写死的回答，而是通过理解您提供的本地知识库，并结合动态的人格预设，智能地生成丰富、准确且充满个性的回答。

## ✨ 核心功能

*   **🧠 RAG 核心架构**: 采用先进的RAG方案，当用户提问时，插件会首先在您的本地知识库中进行语义检索，找到最相关的内容，然后将这些内容作为"背景资料"连同问题一起提交给大语言模型(LLM)，最终生成高质量的回答。
*   **📚 本地知识库**: 您可以轻松地通过在指定文件夹 (`data/knows/`) 中添加 `.txt` 或 `.md` 文件来扩充机器人的知识。插件会自动读取、处理并学习这些文件，支持多级子目录。
*   **🎭 动态人格预设**: 无缝集成了您项目中现有的 `prerequisite` 人格管理系统。机器人会根据不同群聊的设置，自动调用相应的人格设定来回答问题，实现"千人千面"。
*   **⚡ 异步延迟加载**: 首次加载插件时，资源密集型的初始化操作（如加载AI模型、构建向量数据库）会在后台异步执行，完全避免了因插件加载时间过长而阻塞机器人主程序或其他插件的问题。
*   **🚀 开箱即用**: 安装配置完成后，在群聊中通过 `@机器人` 的方式即可轻松触发问答。

## ⚙️ 安装指南

请遵循以下步骤来安装并配置此插件。

### 1. 放置插件文件

将 `AI_Advanced_Responder.py` 文件放入您机器人项目的 `plugins` 文件夹中。

### 2. 安装依赖库

本插件依赖于数个第三方Python库。请打开您的终端或命令行，然后使用pip来安装它们：

```bash
pip install sentence-transformers faiss-cpu numpy deepseek
```
*如果你在中国大陆，因为网络问题安装缓慢，可以尝试使用国内镜像源加速:*
```bash
pip install sentence-transformers faiss-cpu numpy deepseek -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**库作用简介:**
*   `sentence-transformers`: 用于将文本知识转换为向量（Embeddings）。
*   `faiss-cpu`: 由Facebook AI开发的高效向量相似度搜索引擎。
*   `numpy`: Python中科学计算的基础包，许多AI库都依赖它。
*   `deepseek`: 用于与DeepSeek大语言模型API交互的库。

### 3. 配置

插件的配置主要涉及两个方面：

**a) 知识库目录:**
*   请在您的项目根目录下创建一个 `data` 文件夹（如果安装了签到插件，机器人的文件夹中应该会自动生成一个data文件夹），然后在 `data` 文件夹内再创建一个 `knows` 文件夹。
*   将您希望机器人学习的所有知识库文件（`.txt` 或 `.md` 格式）放入 `data/knows/` 目录中。您可以随意创建子文件夹来组织文件。

最终目录结构应如下所示：
```
.
├── plugins/
│   └── AI_Advanced_Responder.py
├── data/
│   ├── knows/
│   │   ├── 科技/
│   │   │   └── 什么是AI.txt
│   │   └── 文学/
│   │       └── 关于鲁迅.md
│   └── ... (插件会自动生成 vector_db.index 和 text_data.json)
├── prerequisites/
│   └── ...
└── config.json
```

**b) API 密钥:**

（这一步其实可以忽略，只要在简儿的启动器里设置了密钥就行，和简儿共用一个config文件）

*   打开您项目根目录下的 `config.json` 文件。
*   确保在 `Others` 字段下，有一个名为 `deepseek_key` 的键，并将其值设置为您的 [DeepSeek API Key](https://platform.deepseek.com/)。

示例 `config.json`:
```json
{
  "Bot": {
    "self_qq": "123456",
    "password": ""
  },
  "Others": {
    "master": "10000",
    "deepseek_key": "sk-xxxxxxxxxxxxxxxxxxxx" 
  }
}
```

## 🚀 使用方法

1.  **启动机器人**: 完成上述安装和配置后，正常启动您的机器人。首次启动时，您会在控制台看到类似 `[知识库插件] 正在构建向量数据库...` 的日志，这表示插件正在学习您的知识库文件。这个过程根据您的文件数量和大小，可能需要几十秒到几分钟。完成后，数据库会自动保存，未来启动会直接加载，速度很快。
2.  **开始提问**: 在任何一个您的机器人所在的群聊中，通过 **`@机器人 <你的问题>`** 的方式即可向它提问。
3.  **享受智能回答**: 插件会自动检索知识库，并使用当前群聊配置的人格，生成独特的回答。

## ❓ 问题反馈与贡献

如果您在使用过程中遇到任何bug，或有任何好的功能建议，非常欢迎通过本项目的 GitHub Issues 页面来提交。

*   **[点此提交Issue](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/issues)**  *(请将此链接替换为您自己的仓库issues链接)*

同时也欢迎您 Fork 本项目并提交 Pull Request 来帮助改进这个插件！

## ©️ 许可证与免责声明

本项目采用 [MIT License](https://opensource.org/licenses/MIT) 开源。

**免责声明**: 本插件仅供学习和技术交流使用。作者 **小泥人Hyper** 不对使用本插件所产生的任何直接或间接后果负责。所有通过大语言模型API生成的内容，其责任由相应的模型服务提供商承担。

