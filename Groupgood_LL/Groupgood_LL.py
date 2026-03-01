import asyncio
import websocket
import json
from Hyper import Configurator, Events
Configurator.cm = Configurator.ConfigManager(Configurator.Config(file="config.json").load_from_file())
config = Configurator.cm.get_cfg()
TRIGGHT_KEYWORD = "Any"
HELP_MESSAGE = f'''{Configurator.cm.get_cfg().others['reminder']}设置精华 —> 快捷设置精华
{Configurator.cm.get_cfg().others['reminder']}删除精华 —> 快捷删除精华'''

# 白名单开关：True=启用白名单，False=禁用白名单（所有群都可以使用）
WHITE_LIST_ENABLED = False
WHITE_LIST = ["114514", "350234"]

# WS 配置项
WS_URL = f"ws://{getattr(config.connection, 'host', '127.0.0.1')}:{getattr(config.connection, 'port', 5004)}"

async def on_message(event, actions, Manager, Events: Events, Segments, reminder):
    # 只处理群消息
    if not isinstance(event, Events.GroupMessageEvent):
        return None
    
    # 检查是否是设为/置精华或删除精华命令
    msg_str = str(event.message)
    reminder_prefix = Configurator.cm.get_cfg().others['reminder']
    
    # 判断是设置还是删除
    is_set = f"{reminder_prefix}设为精华" in msg_str or f"{reminder_prefix}设置精华" in msg_str
    is_delete = f"{reminder_prefix}删除精华" in msg_str or f"{reminder_prefix}移除精华" in msg_str
    
    if is_set or is_delete:
        # 白名单检查：只有白名单中的群聊才会响应（如果启用白名单）
        if WHITE_LIST_ENABLED and str(event.group_id) not in WHITE_LIST:
            return True
        # 检查是否回复了消息
        if isinstance(event.message[0], Segments.Reply):
            try:
                fail_reason = ""
                ws = await asyncio.to_thread(websocket.create_connection, WS_URL)
                try:
                    action_type = "delete_essence_msg" if is_delete else "set_essence_msg"
                    await asyncio.to_thread(ws.send, json.dumps({"action": action_type, "params": {"message_id": event.message[0].id}}))
                    max_wait_time = 5
                    start_time = asyncio.get_event_loop().time()
                    response_received = False
                    
                    while asyncio.get_event_loop().time() - start_time < max_wait_time:
                        response = await asyncio.to_thread(ws.recv)
                        res_json = json.loads(response)
                        
                        if res_json.get("post_type") == "meta_event":
                            continue
                        
                        response_received = True
                        error_code = res_json.get("data", {}).get("result", {}).get("errorCode", -1)
                        error_wording = res_json.get("data", {}).get("result", {}).get("wording", "")
                        
                        if error_code == 0 and error_wording == "":
                            success_msg = "✅ 已删除此消息的精华状态" if is_delete else "✅ 已将此消息设为精华啦"
                            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Reply(event.message[0].id), Segments.At(event.user_id), Segments.Text(success_msg)))
                            return True
                        else:
                            if error_wording:
                                fail_reason = f"失败：{error_wording}（错误码：{error_code}）"
                            elif error_code != 0:
                                fail_reason = f"失败：未知错误（错误码：{error_code}）"
                            else:
                                fail_reason = "失败：未获取到明确错误信息"
                            action_name = "删除精华" if is_delete else "设置精华"
                            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Reply(event.message_id), Segments.Text(f"❌ {action_name}失败！\n📌 失败原因：{fail_reason}")))
                            return True
                        break
                    
                    if not response_received:
                        fail_reason = "超时错误：5秒内未收到业务响应（可能服务端无返回）"
                        action_name = "删除精华" if is_delete else "设置精华"
                        await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Reply(event.message_id), Segments.Text(f"❌ {action_name}失败！\n📌 失败原因：{fail_reason}")))
                        return True
                finally:
                    await asyncio.to_thread(ws.close)
            except Exception as e:
                action_name = "删除精华" if is_delete else "设置精华"
                await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Reply(event.message_id), Segments.Text(f"❌ {action_name}失败！\n📌 失败原因：{str(e)}")))
                return True
        else:
            cmd_hint = "删除精华/移除精华" if is_delete else "设为精华/设置精华"
            txt = f'''⚠️ 请回复一条消息后发送'{Configurator.cm.get_cfg().others['reminder']}{cmd_hint}'命令'''
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(
                    Segments.Reply(event.message_id),
                    Segments.At(event.user_id),
                    Segments.Text(txt)
                )
            )
            return True
    return None

