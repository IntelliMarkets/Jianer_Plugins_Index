import asyncio
import re
from Hyper import Configurator, Events

TRIGGHT_KEYWORD = "群待办"
HELP_MESSAGE = f'''{Configurator.cm.get_cfg().others['reminder']}群待办 —> 快捷设置群待办'''

#！！！机器人要有管理员权限才行，否则设置不了群待办！！！

# 白名单开关：True=启用白名单，False=禁用白名单（所有群都可以使用）
WHITE_LIST_ENABLED = False

# 白名单，只有在白名单中的群聊才会响应
WHITE_LIST = [
    "114514",
    "350234"
]


async def on_message(event, actions, Manager, Events: Events, Segments, reminder):
    # 只处理群消息
    if not isinstance(event, Events.GroupMessageEvent):
        return None
    
    # 白名单检查：只有白名单中的群聊才会响应（如果启用白名单）
    if WHITE_LIST_ENABLED and str(event.group_id) not in WHITE_LIST:
        return None
    
    # 检查是否回复了消息
    if isinstance(event.message[0], Segments.Reply):
        try:
            # 设置群待办
            await actions.custom.set_group_todo(
                group_id=event.group_id,
                message_id=event.message[0].id
            )
            
            # 发送成功提示
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(
                    Segments.Reply(event.message_id),
                    Segments.Text("✅ 已将此消息设为群待办啦")
                )
            )
            return True
            
        except Exception as e:
            # 发送错误提示
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(
                    Segments.Reply(event.message_id),
                    Segments.Text(f"❌ 设置群待办失败：{str(e)}")
                )
            )
            return True
    else:
        # 提示用户需要回复消息
        txt = f'''⚠️ 请回复一条消息后发送'{Configurator.cm.get_cfg().others['reminder']}群待办'命令'''
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(
                Segments.Reply(event.message_id),
                Segments.Text(txt)
            )
        )
        return True        
