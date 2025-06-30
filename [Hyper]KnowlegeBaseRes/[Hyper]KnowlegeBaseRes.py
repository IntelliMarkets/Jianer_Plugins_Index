import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import json
import asyncio
import time

# 1. 导入你项目中的模块
# ==================================
from Hyper import Configurator, Listener
from Tools.deepseek import dsr114
from prerequisites.prerequisite import gen_presets

# ... (配置项和KnowledgeManager类的代码与之前相同，这里为了简洁省略) ...
# ... (请确保你使用的是上一版包含异步初始化逻辑的完整代码) ...

# -----------------------------------------------------------------------------
# 2. 配置项
# -----------------------------------------------------------------------------
KNOWLEDGE_BASE_DIR = "./data/knows/"
VECTOR_DB_PATH = "./data/vector_db.index"
TEXT_DATA_PATH = "./data/text_data.json"
EMBEDDING_MODEL_NAME = 'shibing624/text2vec-base-chinese'

try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config_data = json.load(f)
        DEEPSEEK_API_KEY = config_data.get("Others", {}).get("deepseek_key")
        if not DEEPSEEK_API_KEY:
            print("[知识库插件] 警告：在 config.json 的 'Others' -> 'deepseek_key' 中未找到 API 密钥。")
except Exception as e:
    print(f"[知识库插件] 读取配置文件失败: {e}")
    DEEPSEEK_API_KEY = None

# -----------------------------------------------------------------------------
# 3. 知识库管理器 (KnowledgeManager)
# -----------------------------------------------------------------------------
class KnowledgeManager:
    def __init__(self, model_name, knowledge_dir, vector_db_path, text_data_path):
        self.knowledge_dir = knowledge_dir
        self.vector_db_path = vector_db_path
        self.text_data_path = text_data_path
        print("[知识库管理器] 正在加载语义模型...")
        self.model = SentenceTransformer(model_name)
        print("[知识库管理器] 语义模型加载完毕。")
        self.documents = []
        self.index = None
        if os.path.exists(vector_db_path) and os.path.exists(text_data_path):
            print("[知识库管理器] 发现现有向量数据库，正在加载...")
            self._load_vector_db()
        else:
            print("[知识库管理器] 未发现向量数据库，正在构建...")
            self._build_vector_db()

    def _load_documents(self):
        docs = []
        if not os.path.exists(self.knowledge_dir):
            os.makedirs(self.knowledge_dir)
        for root, _, files in os.walk(self.knowledge_dir):
            for filename in files:
                if filename.endswith((".txt", ".md")):
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            docs.append(f.read())
                    except Exception as e:
                        print(f"[错误] 读取文件 {filename} 失败: {e}")
        return docs

    def _build_vector_db(self):
        self.documents = self._load_documents()
        if not self.documents:
            print("[警告] 知识库目录为空，无法构建向量数据库。")
            return
        print(f"[知识库管理器] 正在将 {len(self.documents)} 个文档转换为向量...")
        embeddings = self.model.encode(self.documents, show_progress_bar=True)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        faiss.write_index(self.index, self.vector_db_path)
        with open(self.text_data_path, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
        print("[知识库管理器] 向量数据库构建完成。")

    def _load_vector_db(self):
        self.index = faiss.read_index(self.vector_db_path)
        with open(self.text_data_path, 'r', encoding='utf-8') as f:
            self.documents = json.load(f)
        print(f"[知识库管理器] 成功加载 {len(self.documents)} 个文档和对应的向量索引。")

    def search(self, query: str, k: int = 3) -> list[str]:
        if self.index is None: return []
        query_vector = self.model.encode([query])
        _, indices = self.index.search(query_vector, k)
        return [self.documents[i] for i in indices[0]]

# -----------------------------------------------------------------------------
# 4. AI 回答生成器
# -----------------------------------------------------------------------------
def build_prompt_for_deepseek(persona_prompt: str, context_chunks: list[str]) -> str:
    """
    构建最终发送给大模型的系统提示.
    这个提示包含了三部分:
    1. 动态加载的机器人人格预设 (persona_prompt)
    2. 从向量数据库中检索出的相关知识 (context_chunks)
    3. 对模型回答方式的明确指示和规则
    """
    context = "\\n---\\n".join(context_chunks)
    prompt = f"""
{persona_prompt}

---
上方是你的角色设定，请在回答中严格保持这个人设。
现在，你需要严格根据下方提供的"背景资料"来回答用户的问题。

[重要规则]
- 你的回答必须简洁、友好、切中要点。
- 禁止直接复制粘贴背景资料中的原文。
- 如果背景资料中没有足够的信息来回答问题，你必须诚实地回答："根据我现有的知识，我暂时无法回答这个问题。" (你可以用自己的语气来表达这个意思)
- 不要编造信息，不要使用任何你自己的知识，你的回答唯一信源只能是下方的"背景资料"。

[背景资料]
{context}
---

请严格遵守以上所有规则，结合你的角色设定，回答用户接下来的问题。
    """.strip()
    return prompt

async def call_deepseek_with_knowledge(system_prompt: str, user_query: str) -> str:
    if not DEEPSEEK_API_KEY:
        return "错误：DeepSeek API Key 未配置，无法生成回答。"
    responder = dsr114(prompt=system_prompt, message=user_query, user_lists={}, uid="knowledge_base_user", mode="deepseek-chat", bn="智能助手", key=DEEPSEEK_API_KEY)
    final_answer = ""
    try:
        for response_part, response_type in responder.Response():
            if response_type == 'message':
                final_answer += response_part
    except Exception as e:
        print(f"[DeepSeek调用异常] {e}")
        return "抱歉，我在思考的时候遇到了点麻烦，稍后再试试吧。"
    return final_answer
    
# -----------------------------------------------------------------------------
# 5. 插件主逻辑 (已添加诊断日志)
# -----------------------------------------------------------------------------
TRIGGHT_KEYWORD = "Any"
HELP_MESSAGE = "高级问答插件：能理解并参考知识库进行智能回答。"

knowledge_manager = None
init_lock = asyncio.Lock()

async def initialize_knowledge_base():
    global knowledge_manager
    print("[知识库插件] INFO: 检测到首次调用，开始在后台进行初始化...")
    loop = asyncio.get_running_loop()
    knowledge_manager = await loop.run_in_executor(
        None, 
        KnowledgeManager,
        EMBEDDING_MODEL_NAME, 
        KNOWLEDGE_BASE_DIR, 
        VECTOR_DB_PATH, 
        TEXT_DATA_PATH
    )
    print("[知识库插件] SUCCESS: 后台初始化完成，系统已就绪。")

async def on_message(event, actions: Listener.Actions, Manager, Segments):
    # === 诊断日志 1: 检查插件是否被调用 ===
    print(f"[知识库插件] DEBUG: on_message被触发，正在处理消息: '{str(event.message).strip()}'")

    global knowledge_manager
    if knowledge_manager is None:
        async with init_lock:
            if knowledge_manager is None:
                await initialize_knowledge_base()

    message_content = str(event.message).strip().replace(f"@{event.self_id}", "").strip()
    is_at_me = any(isinstance(seg, Segments.At) and str(seg.qq) == str(event.self_id) for seg in event.message)
    
    if not is_at_me or not message_content:
        # === 诊断日志 2: 检查触发条件 ===
        # print(f"[知识库插件] DEBUG: 消息未@机器人或内容为空，插件已跳过。") # 这一行可以注释掉，因为它在正常情况下会刷屏
        return False

    print(f"[知识库插件] INFO: 已被@，开始处理问答。问题: '{message_content}'")
    
    # 1. 获取当前人格预设
    # 我们需要 uid (群号), bot_name (机器人名字), event_user (用户名字)
    # 这里的 bot_name 和 event_user 可以根据你自己的框架进行调整
    uid = str(event.group_id)
    bot_name = "智能助手" # 你可以替换成从配置或事件中获取的机器人名字
    event_user = str(event.user_id) # 你可以替换成 event.sender.card 或 .nickname
    
    # 调用prerequisite.py中的函数来获取当前应该使用的角色预设
    persona_prompt = gen_presets(uid, bot_name, event_user)
    print(f"[知识库插件] INFO: 已为群 {uid} 加载人格预设。")

    # 2. 检索
    relevant_docs = knowledge_manager.search(message_content, k=3)
    if not relevant_docs:
        # === 诊断日志 3: 检查知识库搜索结果 ===
        print(f"[知识库插件] DEBUG: 未在知识库中找到相关信息，插件已跳过。")
        return False

    print(f"[知识库插件] INFO: 在知识库中找到 {len(relevant_docs)} 条相关信息。")
    
    # 3. 增强 & 4. 生成
    final_system_prompt = build_prompt_for_deepseek(persona_prompt, relevant_docs)
    ai_answer = await call_deepseek_with_knowledge(final_system_prompt, message_content)

    # 5. 回复
    await actions.send(
        group_id=event.group_id,
        message=Manager.Message([Segments.At(event.user_id), Segments.Text("\n" + ai_answer)])
    )
    
    # === 诊断日志 4: 确认插件已成功处理消息 ===
    print(f"[知识库插件] SUCCESS: 已成功回复，消息处理流程终止 (返回 True)。")
    return True

print("[Hyper_QQ] 高级智能问答插件(诊断版)已加载。")