import asyncio
import re, os, shutil
import traceback
from Tools.GoogleAI import Context, Roles, Parts
from Tools.user_info import get_nickname_by_userid as get_user_nickname
from collections import defaultdict, deque, Counter
import pickle, gc
from Hyper import Configurator
Configurator.cm = Configurator.ConfigManager(Configurator.Config(file="config.json").load_from_file())
from Hyper import Events
from Tools.websocket_message import ws_custom_api
TRIGGHT_KEYWORD = "Any"
HELP_MESSAGE = f'''{Configurator.cm.get_cfg().others["reminder"]}总结以上N条消息 —> 总结当前群聊的指定数量的消息 (0<N<=1000)
{Configurator.cm.get_cfg().others["reminder"]}聊天数据看板 —> 展示当前(或全部)群聊的聊天数据看板'''
# client = Context(
#     api_key=Configurator.cm.get_cfg().others["gemini_key"],
#     model=Configurator.cm.get_cfg().others.get("gemini_model", "gemini-2.0-flash-exp"),
#     base_url=Configurator.cm.get_cfg().others.get("gemini_base_url", "https://generativelanguage.googleapis.com"),
#     system_instruction="""你是一个专业的聊天总结助手，根据聊天记录总结摘要，请不要使用Markdown格式，
        
# ### 总结要求：
# 1. 用紧凑的格式呈现，少于{max_tokens // 10}个汉字
# 2. 关键点或关键决策点需加粗
# 3. 标注提出重要意见的成员
# 4. 如果有，请列出未解决的问题
# 5. 总结后给出建议或方案
# 6. 尽量不要使用 Markdown 格式
# 7. 通过空行来分割板块"""
    
# ) 
client = Context(
    api_key=Configurator.cm.get_cfg().others["gemini_key"],
    model=Configurator.cm.get_cfg().others.get("gemini_model", "gemini-2.0-flash-exp"),
    base_url=Configurator.cm.get_cfg().others.get("gemini_base_url", "https://generativelanguage.googleapis.com")
) 

def default_factory():
    return {
        "history": deque(maxlen=1000),  
        "token_counter": 0 
    }

def load_chat_db():
    """加载聊天数据库，如果文件不存在则创建新的"""
    chat_db = defaultdict(default_factory)
    pkl_path = os.path.join("data", 'sum_up', 'chat_db.pkl')
    
    if os.path.exists(pkl_path) and os.path.getsize(pkl_path) > 0:
        try:
            with open(pkl_path, 'rb') as f:
                loaded_db = pickle.load(f)
                # 兼容新存储格式：纯字典（history 列表，token_counter 整数）
                if isinstance(loaded_db, dict):
                    for group_id, data in loaded_db.items():
                        history_list = data.get("history", [])
                        token_counter = int(data.get("token_counter", 0))
                        chat_db[group_id]["history"] = deque(history_list, maxlen=1000)
                        chat_db[group_id]["token_counter"] = token_counter
                    print(f"SumUp: 成功加载 {len(loaded_db)} 个群聊，共 {sum(len(data['history']) for data in loaded_db.values())} 条历史消息")
                else:
                    # 旧格式（直接pickle整个defaultdict）可能因模块名变化无法反序列化
                    # 此处不再直接使用旧对象，改为初始化空库，避免导入错误
                    print("SumUp: 检测到旧格式聊天记录，因插件模块名变化无法安全加载，已跳过并使用新格式初始化")
        except Exception as e:
            print(f"SumUp: 加载历史消息失败: {traceback.format_exc}")
    else:
        print("SumUp: 未找到历史数据文件，创建新的数据库")
    
    return chat_db

chat_db = load_chat_db()

# 估算Token（中文≈1字/Tok，英文≈1词/4字母）
def estimate_tokens(text: str) -> int:
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    non_chinese = len(text) - chinese_chars
    return chinese_chars + (non_chinese // 4) + 1

def add_message(group_id: str, user: str, content: str, chat_db=chat_db):
    """添加消息并更新Token计数"""
    tokens = estimate_tokens(f"{user}: {content}")
    chat_db[group_id]["history"].append({"user": user, "content": content})
    chat_db[group_id]["token_counter"] += tokens
    return chat_db

def max_summarizable_msgs(group_id: str, max_tokens=800000) -> int:
    """计算当前群聊最多可总结的消息条数"""
    history = chat_db[group_id]["history"]
    total_tokens = 0
    count = 0
    # 从最新消息向前回溯，直到Token超限
    for msg in reversed(history):
        msg_tokens = estimate_tokens(f"{msg['user']}: {msg['content']}")
        if total_tokens + msg_tokens > max_tokens:
            break
        total_tokens += msg_tokens
        count += 1
    return count

def handle_summary_request(group_id: str, match, chat_db=chat_db):
    """处理用户总结请求（如：'总结以上100条消息'）"""
    try:
        n = int(match.group(1))
        if n <= 0 or n > 1000:
            return "❌ 命令格式错误！请用：'总结以上N条消息' (0<N<=1000)"
        
        total_tokens = sum(estimate_tokens(f"{msg['user']}: {msg['content']}") 
                        for msg in list(chat_db[group_id]["history"])[-n:])
        max_tokens = 800000  # Gemini 模型的 token 限制，预留缓冲
        if total_tokens > max_tokens:
            max_n = max_summarizable_msgs(group_id, max_tokens)
            return f"⚠️ 消息过长（{total_tokens} Tokens > 上限{max_tokens}）\n最多可总结{max_n}条消息"
        
        if len(list(chat_db[group_id]["history"])) < 5:
            return "⚠️ 消息过少（少于 5 条消息）"
        
        messages = "\n".join(f"{msg['user']}: {msg['content']}" for msg in list(chat_db[group_id]["history"])[-n:])
        prompt = f'''请根据以下群聊记录生成摘要：
        
### 聊天记录：
{messages}
        
### 总结要求：
1. 用紧凑的格式呈现，详细但少于{max_tokens // 10}个汉字
2. 关键点或关键决策点需加粗
3. 标注提出重要意见的成员
4. 如果有，请列出未解决的问题
5. 总结后给出建议或方案
6. 尽量不要使用 Markdown 格式'''

        # 使用 GoogleAI 的 gen_content 方法
        user_content = Roles.User(Parts.Text(prompt))
        response_generator = client.gen_content(user_content, model_override="gemini-2.0-flash", stream=False)
        
        # 收集所有响应内容
        full_response = ""
        for response_chunk, _ in response_generator:
            full_response += response_chunk
        
        return full_response
    except Exception as e:
        return f"❌ 总结时发生异常：\n{e}"

async def handle_node_messages(data: dict):
    temp_db = defaultdict(lambda: {
        "history": deque(maxlen=1000),  
        "token_counter": 0 
    })
    
    print(f"SumUp: 开始处理 {data}")
    framework_response = await ws_custom_api("get_version_info", {})
    app_name = ""
    if isinstance(framework_response, dict):
        data_part = framework_response.get('data', {})
        if isinstance(data_part, dict):
            app_name = data_part.get('app_name', '')
        else:
            app_name = str(framework_response.get('data', ''))
        
    print(f"SumUp: 检测到框架: {app_name}")
    
    if "NapCat.Onebot" in app_name:
        print("SumUp: 使用 NapCat 格式解析")
        message_count = 0
        skipped_count = 0
        if 'messages' in data:
            print(f"SumUp: 使用直接 messages 格式解析，共 {len(data['messages'])} 条消息")
            for i, message_item in enumerate(data['messages']):
                print(f"SumUp: 处理第 {i+1} 条消息: {message_item.keys()}")
                
                sender = message_item.get('sender', {})
                nickname = sender.get('nickname', str(message_item.get('user_id', '')))
                message_list = message_item.get('message', [])
                
                print(f"SumUp: 发送者: {nickname}, 消息列表长度: {len(message_list)}")
                
                text_parts = []
                for j, message_content in enumerate(message_list):
                    print(f"SumUp:  消息内容 {j+1}: 类型={message_content.get('type')}, 数据={message_content.get('data', {})}")
                    if message_content.get('type') == 'text':
                        text_data = message_content.get('data', {})
                        text = text_data.get('text', '')
                        if text:
                            text_parts.append(text)
                            
                full_text = ''.join(text_parts)
                print(f"SumUp: 提取的文本: '{full_text}'")
                
                if full_text:
                    print(f"SumUp: 添加群聊消息 {nickname}: {full_text} 到临时数据库")
                    temp_db = add_message(0, nickname, full_text, temp_db)
                    message_count += 1
                else:
                    print(f"SumUp: 跳过消息 - 无文本内容")
                    skipped_count += 1
                    
            print(f"SumUp: 成功解析 {message_count} 条消息，跳过 {skipped_count} 条消息")
                    
        elif 'data' in data and 'messages' in data['data']:
            print(f"SumUp: 使用嵌套 data.messages 格式解析，共 {len(data['data']['messages'])} 条消息")
            for i, message_item in enumerate(data['data']['messages']):
                sender = message_item.get('sender', {})
                nickname = sender.get('nickname', str(message_item.get('user_id', '')))
                message_list = message_item.get('message', [])
                
                text_parts = []
                for message_content in message_list:
                    if message_content.get('type') == 'text':
                        text_data = message_content.get('data', {})
                        text = text_data.get('text', '')
                        if text:
                            text_parts.append(text)
                            
                full_text = ''.join(text_parts)
                
                if full_text:
                    print(f"SumUp: 添加群聊消息 {nickname}: {full_text} 到临时数据库")
                    temp_db = add_message(0, nickname, full_text, temp_db)
                    message_count += 1
                else:
                    skipped_count += 1
                    
            print(f"SumUp: 成功解析 {message_count} 条消息，跳过 {skipped_count} 条消息")

    else:
        print("SumUp: 使用Lagrange.OneBot格式解析")
        message_count = 0
        for message_node in data['message']:
            if message_node.get('type') == 'node':
                node_data = message_node.get('data', {})
                nickname = node_data.get('nickname', node_data.get('user_id', ''))
                content_list = node_data.get('content', [])
                
                text_parts = []
                for content_item in content_list:
                    if content_item.get('type') == 'text':
                        text_data = content_item.get('data', {})
                        text = text_data.get('text', '')
                        if text:
                            text_parts.append(text)
                            
                full_text = ''.join(text_parts)
                
                if full_text:
                    print(f"SumUp: 添加群聊消息 {nickname}: {full_text} 到临时数据库")
                    temp_db = add_message(0, nickname, full_text, temp_db)
                    message_count += 1
        
        print(f"SumUp: 成功解析 {message_count} 条消息")
    
    print(f"SumUp: 处理完成，共收集 {len(temp_db[0]['history'])} 条消息")
    return temp_db

def calculate_hot_words(messages, min_count=1, max_words=5, recursion_depth=0):
    """计算热词排行
    
    Args:
        messages: 消息列表，每个元素是字典包含'content'键
        min_count: 最小出现次数
        max_words: 最多返回的热词数量
        recursion_depth: 当前递归深度（用于防止无限递归）
        
    Returns:
        list: 热词列表，按出现次数排序
    """
    # 设置递归深度限制，防止无限递归
    if recursion_depth > 20:
        return []
    
    # 使用正则提取中文单词（只提取中文，且长度在2-4个字符之间）
    all_words = []
    # 常见停用词列表
    stop_words = {
        '的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', 
        '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', 
        '自己', '这', '但', '而', '于', '以', '可', '为', '之', '与', '则', '其', '或', 
        '即', '因', '及', '由', '时', '等', '所', '并', '且', '着', '呢', '吗', '啊', 
        '吧', '呀', '哦', '恩', '嗯', '哈', '嘿', '嘻', '呗', '哒', '啦', '哟', '呼'
    }
    
    for msg in messages:
        # 只提取中文字符，排除数字、英文和其他符号
        # 使用lookbehind和lookahead来确保我们提取的是完整的中文词语
        words = re.findall(r'(?<![\u4e00-\u9fff])([\u4e00-\u9fff]{2,4})(?![\u4e00-\u9fff])', msg['content'])
        # 过滤掉停用词
        filtered_words = [word for word in words if word not in stop_words]
        all_words.extend(filtered_words)
    
    # 统计词频
    word_count = Counter(all_words)
    
    # 如果热词不足3个，降低标准
    if len([w for w, c in word_count.items() if c >= min_count]) < 3 and min_count > 1:
        min_count -= 1
        return calculate_hot_words(messages, min_count, max_words, recursion_depth + 1)
    
    # 按词频排序，取前max_words个
    hot_words = [word for word, _ in word_count.most_common(max_words) if _ >= min_count]
    
    # 确保至少有3个热词（使用迭代方式，避免递归）
    current_min_count = min_count
    while len(hot_words) < 3 and current_min_count > 1:
        current_min_count -= 1
        hot_words = [word for word, _ in word_count.most_common(max_words) if _ >= current_min_count]
    
    return hot_words

def generate_chat_summary(group_id, chat_db=chat_db):
    """生成单个群的聊天数据看板
    
    Args:
        group_id: 群号
        chat_db: 聊天数据库
        
    Returns:
        str: 格式化的数据看板字符串
    """
    if group_id not in chat_db:
        return f"群：{group_id}\n消息总数：0\n发言人数：0\n热词排行：暂无数据"
    
    # 获取群聊数据
    group_data = chat_db[group_id]
    messages = list(group_data['history'])
    message_count = len(messages)
    
    # 计算发言人数
    speakers = set(msg['user'] for msg in messages)
    speaker_count = len(speakers)
    
    # 计算热词排行
    if message_count > 0:
        # 先尝试使用默认标准获取热词
        hot_words = calculate_hot_words(messages, 1, 5)
        
        # 确保热词数量符合要求（3-5个）
        if len(hot_words) < 3:
            # 如果热词不足3个，尝试使用更低的标准
            hot_words = calculate_hot_words(messages, 0, 5)
        
        # 格式化热词排行
        hot_words_str = '；'.join(hot_words) if hot_words else "暂无足够热词"
    else:
        hot_words_str = "暂无数据"
    
    # 格式化结果
    hot_words_str = hot_words_str.replace('图片', '[图片]')
    summary = f"群：{group_id}\n消息总数：{message_count}\n发言人数：{speaker_count}\n热词排行：{hot_words_str}"
    return summary
    
# async def get_user_info(uid, Manager, actions):
#     try:
#         gc.collect()
#         for _ in range(6):
#             info = Manager.Ret.fetch(await actions.custom.get_stranger_info(user_id=uid, no_cache=True))
#             if 'nickname' not in info.data.raw:
#                 raise ValueError(f"{uid} is not a valid user ID.")
#             if str(info.data.raw.get('user_id', '未知')) == str(uid):
#                 break
        
#         return True, info.data.raw
#     except Exception as e:
#         print(f"SumUp: 获取用户 {uid} 信息失败: {e}")
#         return False, str(uid)
    
# async def get_user_nickname(uid, Manager, actions) -> str:
#     s, user_info = await get_user_info(uid, Manager, actions)
#     if s:
#         return f"@{user_info['nickname']}"
#     else:
#         return str(uid)
    
async def on_message(event, actions, Manager, Events, Segments, bot_name, gen_message, ADMINS, CONFUSED_WORD):
    global chat_db
    if not isinstance(event, Events.GroupMessageEvent):
        return None
    
    message: str = ""
    user_message = str(event.message).strip()
    reminder_prefix = Configurator.cm.get_cfg().others['reminder']
    
    # 使用更灵活的匹配方式，确保命令能被正确识别
    if user_message.startswith(reminder_prefix) and '聊天数据看板' in user_message:
        if '@all' in user_message or '@全体' in user_message:
            if not str(event.user_id) in ADMINS:
                await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(CONFUSED_WORD.format(bot_name=bot_name))))
                return True
            
            # 生成所有群的数据看板汇总
            chat_summary = """===== 全群聊天数据看板 ====="""
            # 遍历所有群聊数据
            for group_id in chat_db:
                group_summary = generate_chat_summary(group_id)
                chat_summary += f"\n{group_summary}\n{'-'*30}"
            
            # 发送汇总数据
            await actions.send_group_forward_msg(
                group_id=event.group_id,
                message=Manager.Message(Segments.CustomNode(
                    str(event.self_id),
                    bot_name,
                    Manager.Message(Segments.Text(chat_summary))
            )))
        else:
            # 生成当前群的数据看板
            chat_summary = generate_chat_summary(event.group_id)
            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Reply(event.message_id), Segments.Text(chat_summary)))
        return True
    match = re.search(r"总结(?:以上|最近)?(\d+)(?:条|个)?消息", user_message)
    if match and user_message.startswith(Configurator.cm.get_cfg().others["reminder"]):
        selfID = await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(f"请等待，{bot_name} 正在总结消息......φ(゜▽゜*)♪")))
        if isinstance(event.message[0], Segments.Reply):
            content = await actions.get_msg(event.message[0].id)
            msg = gen_message({"message": content.data["message"]})
            for i in msg:
                if isinstance(i, Segments.Forward):
                    data = Manager.Ret.fetch(await actions.custom.get_forward_msg(id=i.id)).data.raw
                    node_messages = await handle_node_messages(data)
                    message = handle_summary_request(0, match, node_messages)
                    break
                
            if not message:
                message = "❌ 未找到转发的消息！\n请确保引用消息的是一条聊天记录，并确保消聊天记录中包含需要总结的消息"
        else:
            message = handle_summary_request(event.group_id, match)
            
        if len(message) < 400:
            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Reply(event.message_id), Segments.Text(message)))
        else:
            await actions.send_group_forward_msg(
                group_id=event.group_id,
                message=Manager.Message(Segments.CustomNode(
                                        str(event.self_id),
                                        bot_name,
                                        Manager.Message(Segments.Text(message))
                    )
                )
            )
        await actions.del_message(selfID.data.message_id)
        return True
    else:
        if event.group_id not in chat_db:
            print(f"SumUp: 群组 {event.group_id} 不存在于`chat_db`中，将初始化")
            
        nike = await get_user_nickname(event.user_id, Manager, actions)
        chat_db = add_message(event.group_id, nike, user_message)
        
        # 调试日志：显示添加后的状态
        print(f"SumUp: 添加ID为 {event.user_id} 的用户 {nike} 的信息到数据库，现有 {len(chat_db[event.group_id]['history'])} 条消息")
        
        try:
            os.makedirs(os.path.join("data", 'sum_up'), exist_ok=True)
            pkl_path = os.path.join("data", 'sum_up', 'chat_db.pkl')
            backup_path = pkl_path + '.backup'
            # 备份旧文件
            try:
                if os.path.exists(pkl_path):
                    shutil.copy2(pkl_path, backup_path)
            except Exception as be:
                print(f"SumUp: 备份旧聊天记录失败: {be}")
            # 以稳定格式保存：纯字典（避免default_factory导致的模块引用）
            serializable = {}
            for gid, data in chat_db.items():
                serializable[str(gid)] = {
                    "history": list(data["history"]),
                    "token_counter": int(data["token_counter"])
                }
            with open(pkl_path, 'wb') as f:
                pickle.dump(serializable, f)
        except Exception as e:
            print(f"SumUp: 保存聊天记录失败: {e}")
            
        return None
    
# 初始化时确保数据目录存在
os.makedirs(os.path.join("data", 'sum_up'), exist_ok=True)