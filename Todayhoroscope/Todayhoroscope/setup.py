import random
import json
import os
from datetime import datetime

FORTUNE_CACHE = {}

TRIGGHT_KEYWORD = "Any"
HELP_MESSAGE = "今日运势 —> 查看你今日的运势信息"

# 获取当前插件目录路径
plugin_directory = os.path.dirname(os.path.abspath(__file__))

# 加载运势数据
fortune_data_path = os.path.join(plugin_directory, 'fortune_data.json')
with open(fortune_data_path, 'r', encoding='utf-8') as f:
    LOCAL_FORTUNE_DATA = json.load(f)

def get_local_fortune(user_qq):
    today_str = datetime.now().strftime("%Y-%m-%d")
    cache_key = (user_qq, today_str)

    # 1. 检查缓存
    if cache_key in FORTUNE_CACHE:
        title, text = FORTUNE_CACHE[cache_key]
    else:
        # 2. 缓存中没有，生成新运势
        key = str(random.randint(0, 8))
        fortune_level = LOCAL_FORTUNE_DATA[key]
        
        title = fortune_level["title"]
        text = random.choice(fortune_level["texts"])
        
        # 写入缓存
        FORTUNE_CACHE[cache_key] = (title, text)

    # 3. 格式化输出
    fortune_text = (
        f"【运势等级】: {title}\n"
        f"【签文】: {text}"
    )
    return fortune_text


async def on_message(event, actions, Manager, Segments):
    full_msg = str(event.message).strip()
    
    if full_msg != "今日运势":
        return False
    
    user_qq = getattr(event, "user_id", None)

    if not user_qq:
        await actions.send(
            group_id=getattr(event, "group_id", None) or getattr(event, "user_id", None),
            message=Manager.Message(Segments.Text("获取用户ID失败，无法查询运势。"))
        )
        return True

    fortune_text = get_local_fortune(user_qq)
    image_url = "https://pic.mcxclr.top"

    footer = "仅供娱乐｜相信科学｜请勿迷信"

    at_segment = Segments.At(user_qq)

    parts = [
        at_segment,
        Segments.Text(" 🎲 今日运势：\n"),
        Segments.Text(f"{fortune_text}\n\n"),
        Segments.Image(image_url),
        Segments.Text("\n" + footer)
    ]

    await actions.send(
        group_id=getattr(event, "group_id", None) or getattr(event, "user_id", None),
        message=Manager.Message(*parts)
    )
    return True