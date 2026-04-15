# -*- coding: utf-8 -*-
"""
随机表情表态插件
功能：对回复的消息直接点上20个不同的随机表情
"""

import random
import asyncio

from Hyper import Configurator

# ============ 插件元信息 ============
TRIGGHT_KEYWORD = "表情"

# 获取触发前缀
_config = Configurator.cm.get_cfg()
_reminder = _config.others.get("reminder", "/")

HELP_MESSAGE = f" {_reminder}表情 —> 为该消息点上20个不同的随机表情 🎉"


# ============ 完整的QQ表情ID列表 ============
ALL_EMOJI_IDS = [
    4, 5, 8, 9, 10, 12, 14, 16, 21, 23, 24, 25, 26, 27, 28, 29, 30,
    32, 33, 34, 38, 39, 41, 42, 43, 49, 53, 60, 63, 66, 74, 75, 76,
    78, 79, 85, 89, 96, 97, 98, 99, 100, 101, 102, 103, 104, 106, 109,
    111, 116, 118, 120, 122, 123, 124, 125, 129, 144, 147, 171, 173,
    174, 175, 176, 179, 180, 181, 182, 183, 201, 203, 212,  219,
    222, 227, 232, 243, 246, 262, 264, 265, 266, 267, 268, 269,
    270, 271, 272, 273, 277, 278, 281, 282, 284, 285, 287, 289, 290,
    9728, 9749, 9786, 10024, 10060, 10068, 127801, 127817, 127838,
    127866, 127867, 127881, 128046, 128051, 128053, 128074, 128076,
    128077, 128079, 128147, 128157, 128164, 128166, 128168, 128170,
    128293, 128513, 128514, 128516, 128522, 128524, 128527, 128530,
    128531, 128532, 128536, 128538, 128540, 128541, 128557
]

# 记录每条消息已点的表情
liked_records = {}


async def on_message(event, actions, Manager, Segments):
    """插件入口函数"""
    
    # 获取被回复的消息ID
    target_message_id = None
    for segment in event.message:
        if isinstance(segment, Segments.Reply):
            target_message_id = segment.id
            break
    
    if not target_message_id:
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(
                Segments.Reply(event.message_id),
                Segments.Text(f"请回复一条消息再使用此命令哦~")
            )
        )
        return True  # 阻断AI回复
    
    # 初始化记录
    if target_message_id not in liked_records:
        liked_records[target_message_id] = set()
    
    # 获取可用的表情
    available = [eid for eid in ALL_EMOJI_IDS if eid not in liked_records[target_message_id]]
    need = min(20 - len(liked_records[target_message_id]), len(available), 20)
    
    if need <= 0:
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(
                Segments.Reply(event.message_id),
                Segments.Text(f"这条消息已经点满20个表情了")
            )
        )
        return True
    
    # 随机选择
    selected = random.sample(available, need)
    success_count = 0
    
    for emoji_id in selected:
        try:
            await actions.custom.set_msg_emoji_like(
                group_id=event.group_id,
                message_id=target_message_id,
                emoji_id=str(emoji_id),
                is_add=True
            )
            liked_records[target_message_id].add(emoji_id)
            success_count += 1
        except Exception as e:
            print(f"[随机表情] 失败: {emoji_id}, {e}")
        
    
    # 只发送最终结果
    await actions.send(
        group_id=event.group_id,
        message=Manager.Message(
            Segments.Reply(event.message_id),
            Segments.Text(f"好了🤓")
        )
    )
    
    return True  # 阻断AI回复