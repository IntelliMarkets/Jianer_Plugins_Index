import asyncio
import random
import time
import aiohttp
from random import randint
import dataclasses
import json
from Hyper import Configurator, Events
Configurator.cm = Configurator.ConfigManager(Configurator.Config(file="config.json").load_from_file())

WEBSOCKET_URL = f"ws://{Configurator.cm.get_cfg().connection.host}:{Configurator.cm.get_cfg().connection.port}"

TRIGGHT_KEYWORD = "Any"
HELP_MESSAGE = f'''{Configurator.cm.get_cfg().others['reminder']}发电 (名字) —> 对某个人表达内心深处的诉求
       我今天棒不棒 —> 让{Configurator.cm.get_cfg().others['bot_name']}来评评你今天表现怎么样'''


import json
import asyncio
import uuid
import aiohttp
from aiohttp import ClientTimeout


async def get_user_info_from_websocket(user_id, Manager=None, actions=None):
    """
    通过WebSocket获取用户信息
    
    Args:
        user_id (int): 用户QQ号
        Manager: Manager对象（保持兼容性，实际不使用）
        actions: actions对象（保持兼容性，实际不使用）
        
    Returns:
        tuple: (是否成功, 用户信息字典)
    """
    try:
        # 设置超时时间：连接超时10秒，总超时30秒
        timeout = ClientTimeout(total=30, connect=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.ws_connect(WEBSOCKET_URL) as ws:
                # 构造请求数据
                request_data = {
                    "action": "get_stranger_info",
                    "params": {
                        "user_id": user_id
                    },
                    "echo": f"get_user_info_{user_id}"
                }
                
                # 发送请求
                await ws.send_str(json.dumps(request_data))
                
                # 接收响应，设置接收超时
                try:
                    async with asyncio.timeout(20):  # 20秒接收超时
                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                response = json.loads(msg.data)
                                if response.get('echo') == f"get_user_info_{user_id}":
                                    if response.get('status') == 'ok':
                                        return True, response.get('data')
                                    else:
                                        print(f"获取用户信息失败: {response.get('message', '未知错误')}")
                                        return False, None
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                print(f'WebSocket错误: {ws.exception()}')
                                return False, None
                except asyncio.TimeoutError:
                    print(f"接收用户信息超时 (用户ID: {user_id})")
                    return False, None
                        
    except Exception as e:
        print(f"连接WebSocket时出错: {e}")
        return False, None

async def get_nickname_by_userid(user_id, Manager=None, actions=None):
    """
    根据用户ID获取昵称
    
    Args:
        user_id (int): 用户QQ号
        Manager: Manager对象（保持兼容性，实际不使用）
        actions: actions对象（保持兼容性，实际不使用）
        
    Returns:
        str: 用户昵称，如果获取失败返回'未知用户'
    """
    success, user_info = await get_user_info_from_websocket(user_id, Manager, actions)
    if success and user_info and isinstance(user_info, dict):
        # 尝试多个可能的昵称字段
        nickname = user_info.get('nickname') or user_info.get('nick') or '未知用户'
        return nickname
    else:
        return '未知用户'



@dataclasses.dataclass
class UserInfo:
    goodness: int
    time: int

    @property
    def level(self) -> str:
        if 0 <= self.goodness <= 20:
            return "嗯~今天表现不乖，下次一定要听话哦"
        elif 20 < self.goodness <= 40:
            return "看着顺眼"
        elif 40 < self.goodness <= 60:
            return "亲爱的太棒啦！"
        elif 60 < self.goodness <= 80:
            return "来，抱一个~嗯~"
        else:
            return "👍_ _ _👍"

    @classmethod
    def build(cls) -> "UserInfo":
        return cls(randint(0, 100), int(time.time()))

users: dict[str, UserInfo] = {}
with open("./assets/quick.json", "r", encoding="utf-8") as f:
    words = json.load(f)["ele"]


async def on_message(event, actions, Manager, Events: Events, Segments, reminder):
        if not isinstance(event, Events.GroupMessageEvent):
            return None
        
        if "今天棒不棒" in str(event.message):
            if "我" in str(event.message):
                name = "\n你"
                uin = str(event.user_id)
            elif "@" in str(event.message):
                name = ""
                uin = event.message[0].qq
            else:
                return

            if str(uin) not in users.keys():
                users[str(uin)] = UserInfo.build()

            msg = Manager.Message(
                Segments.At(uin),
                Segments.Text(
                    f" {name}今天的分数: {users[str(uin)].goodness}\n评级: {users[str(uin)].level}")
            )

            await actions.send(
                group_id=event.group_id,
                user_id=event.user_id,
                message=msg
            )
            return True

        elif str(event.message).startswith(f"{reminder}发电"):
            uin = 0
            for i in event.message:
                if isinstance(i, Segments.At):
                    uin = i.qq
                    break
            if uin == 0:
                tag = str(event.message).replace(f"{reminder}发电", "", 1)
            else:
                tag = f"@{await get_nickname_by_userid(uin)}"

            word = random.choice(words).replace("{target_name}", tag)
            await actions.send(
                group_id=event.group_id,
                user_id=event.user_id,
                message=Manager.Message(
                    Segments.Reply(event.message_id), Segments.Text(word)
                )
            )
            return True
