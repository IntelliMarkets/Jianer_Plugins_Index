import asyncio
import os
import re
import time
from Hyper import Configurator

# ---------- 加载配置 ----------
Configurator.cm = Configurator.ConfigManager(
    Configurator.Config(file="config.json").load_from_file()
)
cfg = Configurator.cm.get_cfg()
reminder = cfg.others["reminder"]

# ---------- 加载管理用户列表 ----------
def _load_user_list(filename: str) -> list:
    users = []
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            users = [line.strip() for line in f if line.strip()]
    return users

Super_User = _load_user_list("Super_User.ini")
Manage_User = _load_user_list("Manage_User.ini")
ROOT_User = cfg.others.get("ROOT_User", [])
ADMINS = set(Super_User + Manage_User + ROOT_User)

cooldown_poke = {}

TRIGGHT_KEYWORD = "戳"
HELP_MESSAGE = f"- {reminder}戳 [@用户] [次数] —> 戳一戳目标用户"

async def on_message(event, actions, Manager, Segments):
    if not hasattr(event, "group_id"):
        return False

    msg_text = str(event.message).strip()
    if not msg_text.startswith(f"{reminder}戳"):
        return False

    param_part = msg_text[len(f"{reminder}戳"):].strip()
    if not param_part:
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(Segments.Text(f"用法：{reminder}戳 @用户 [次数]"))
        )
        return True

    # 提取目标用户ID
    target_id = None
    for seg in event.message:
        if isinstance(seg, Segments.At):
            target_id = str(seg.qq)
            break
    
    # 提取次数
    count = 1
    numbers = re.findall(r"\d+", param_part)
    if numbers:
        count = int(numbers[-1])
        if count < 1:
            count = 1
        if count > 20:
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text(f"次数不能超过20次"))
            )
            return True
    
    if not target_id:
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(Segments.Text("请 @ 要戳的用户！"))
        )
        return True

    if str(target_id) == str(event.self_id):
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(Segments.Text("不能戳自己哦~"))
        )
        return True

    caller_id = str(event.user_id)
    is_admin = caller_id in ADMINS

    # 冷却检查
    if not is_admin:
        now = time.time()
        last = cooldown_poke.get(caller_id, 0)
        if now - last < 600:
            remain = int(600 - (now - last))
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text(f"冷却中，请 {remain} 秒后再试"))
            )
            return True
        cooldown_poke[caller_id] = now

    # 执行戳一戳
    success = 0
    for i in range(count):
        try:
            poke_result = await actions.custom.group_poke(
                group_id=event.group_id,
                user_id=int(target_id)
            )
            ret = Manager.Ret.fetch(poke_result)
            if ret.status == "ok":
                success += 1
            await asyncio.sleep(0.1)
        except Exception as e:
            if i == 0:
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(Segments.Text(f"戳一戳失败"))
                )
                return True

    if success > 0:
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(Segments.Text(f"已戳 {success} 次"))
        )
    
    return True