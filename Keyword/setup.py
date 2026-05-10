# -*- coding: utf-8 -*-
"""
Keyword关键词触发
功能：当群聊消息中包含配置文件中定义的关键词时，调用 AI 回复
"""

import json
import os

TRIGGHT_KEYWORD = "Any"
HELP_MESSAGE = "当消息中包含配置的关键词时，机器人会与你对话。\n可通过修改插件目录下的 config.json 自定义触发词。\n警告：若 config.json 缺失或格式错误，插件将启动失败。"

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_keywords():

    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"配置文件未找到：{CONFIG_PATH}")

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        keywords = data.get("trigger_keywords")
        if keywords is None:
            raise ValueError(f"配置文件中缺少 'trigger_keywords' 字段")

        if not isinstance(keywords, list):
            raise TypeError(f"'trigger_keywords' 必须是列表类型")

        # 过滤空关键词
        keywords = [k for k in keywords if isinstance(k, str) and k.strip()]
        return keywords
    except Exception as e:
        raise RuntimeError(f"读取配置文件错误：{str(e)}")

TRIGGER_KEYWORDS = load_keywords()

async def on_message(event, actions, Manager, Segments, bot_name, reminder, AIbot, EnableNetwork, cmc, sys_prompt, user_lists):

    if not hasattr(event, "group_id"):
        return False

    try:
        user_id = str(getattr(event, 'user_id', ''))
        self_id = str(getattr(event, 'self_id', ''))
        if user_id and self_id and user_id == self_id:
            return False
    except:
        pass

    user_message = str(event.message)
    if not any(keyword in user_message for keyword in TRIGGER_KEYWORDS):
        return False

    text_content = ""
    for segment in event.message:
        if isinstance(segment, Segments.Text):
            text_content += segment.text + " "
    order = text_content.strip()
    if not order:
        return False

    try:
        _, _, result = await AIbot.generate_response(EnableNetwork, cmc, sys_prompt, user_lists, event)
        
        if result:
            return True
        else:
            return False
    except Exception as e:
        print(f"[插件错误] {e}")
        error_msg = f"{bot_name}发生错误，不能回复你的消息了 ε(┬┬﹏┬┬)3"
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(Segments.Text(error_msg)),
        )
        return True