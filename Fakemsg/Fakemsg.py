import re
import asyncio
from Hyper import Configurator

Configurator.cm = Configurator.ConfigManager(Configurator.Config(file="config.json").load_from_file())
TRIGGHT_KEYWORD = "伪造消息"
HELP_MESSAGE = f"{Configurator.cm.get_cfg().others['reminder']}伪造消息 [QQ号说内容|QQ号说内容] - 用于伪造恶搞群友或者好友的消息"

async def on_message(event, actions, Manager, Segments, Events, ROOT_User, Super_User, Manage_User, config=None):
    message_text = str(event.message).strip()
    
    if TRIGGHT_KEYWORD not in message_text:
        return False
    
    group_id = getattr(event, 'group_id', None)
    
    fake_messages = await parse_fake_messages(event)
    
    if not fake_messages:
        await actions.send(
            group_id=group_id,
            message=Manager.Message(Segments.Text(
                "格式错误！请使用以下格式：\n"
                f"{TRIGGHT_KEYWORD} 123456说你好|789012说大家好\n"
                f"或者：{TRIGGHT_KEYWORD} @用户 说你好\n"
                f"注意：QQ号必须是6-10位数字"
            ))
        )
        return True
    
    try:
        await send_fake_messages(event, actions, Manager, Segments, fake_messages)
        return True
        
    except Exception as e:
        await actions.send(
            group_id=group_id,
            message=Manager.Message(Segments.Text(f"发送失败：{str(e)}"))
        )
        return True

async def parse_fake_messages(event):
    fake_messages = []
    message_text = str(event.message).strip()
    
    content_text = message_text.replace(TRIGGHT_KEYWORD, "").strip()
    
    # 处理@用户的情况
    if hasattr(event.message, 'at_list') and event.message.at_list:
        at_users = event.message.at_list
        # 使用正则匹配@用户说内容，允许说字前后有空格
        match = re.search(r'说\s*(.+)', content_text)
        if match:
            content = match.group(1).strip()
            for user_qq in at_users:
                fake_messages.append((str(user_qq), content))
    
    # 处理QQ号说内容的情况
    pattern = r'(\d{6,10})\s*说\s*([^|]+)'
    matches = re.findall(pattern, content_text)
    for qq, content in matches:
        fake_messages.append((qq, content.strip()))
    
    # 处理多个消息用|分隔的情况
    if '|' in content_text:
        messages = content_text.split('|')
        for msg in messages:
            msg = msg.strip()
            match = re.match(r'(\d{6,10})\s*说\s*(.+)', msg)
            if match:
                qq, content = match.groups()
                # 检查是否已存在相同的QQ号+内容组合，避免重复
                if (qq, content.strip()) not in fake_messages:
                    fake_messages.append((qq, content.strip()))
    
    return fake_messages

async def send_fake_messages(event, actions, Manager, Segments, fake_messages):
    forward_nodes = []
    
    for qq, content in fake_messages:
        try:
            user_info = await get_user_info(int(qq), actions)
            nickname = user_info['nickname'] if user_info else f"用户{qq}"
            
            node = Segments.CustomNode(
                qq,
                nickname,
                Manager.Message(Segments.Text(content))
            )
            forward_nodes.append(node)
            
        except Exception:
            node = Segments.CustomNode(
                qq,
                f"用户{qq}",
                Manager.Message(Segments.Text(content))
            )
            forward_nodes.append(node)
    
    if not forward_nodes:
        await actions.send(
            group_id=getattr(event, 'group_id', None),
            message=Manager.Message(Segments.Text("没有有效的伪造消息可发送"))
        )
        return
    
    if hasattr(event, 'group_id'):
        await actions.send_group_forward_msg(
            group_id=event.group_id,
            message=Manager.Message(*forward_nodes)
        )

async def get_user_info(user_id, actions):
    try:
        user_info = await actions.custom.get_stranger_info(user_id=user_id)
        return user_info
    except Exception:
        return None

async def on_notice(event, actions, Manager, Segments, Events):
    pass

async def on_request(event, actions, Manager, Segments, Events):
    pass