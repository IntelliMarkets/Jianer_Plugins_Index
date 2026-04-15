import asyncio
import os
import time
from Hyper import Configurator
from Hyper.Events import GroupMessageEvent

# 加载配置文件
Configurator.cm = Configurator.ConfigManager(
    Configurator.Config(file="config.json").load_from_file()
)
BOT_NAME = Configurator.cm.get_cfg().others.get("bot_name", "简儿")
REMINDER = Configurator.cm.get_cfg().others.get("reminder", "#")

TRIGGHT_KEYWORD = "Any"
HELP_MESSAGE = f"""{REMINDER}踢1级 —> 列出群内等级=1的成员
{REMINDER}踢人白名单 添加 QQ号 —> 添加踢人白名单
{REMINDER}踢人白名单 移除 QQ号 —> 移除白名单
{REMINDER}踢人白名单 列表 —> 查看当前白名单"""

# ---------- 白名单管理 ----------
WHITELIST_FILE = "kick_whitelist.sr"

def load_whitelist():
    if not os.path.exists(WHITELIST_FILE):
        return set()
    with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}

def save_whitelist(whitelist):
    with open(WHITELIST_FILE, "w", encoding="utf-8") as f:
        for qq in whitelist:
            f.write(f"{qq}\n")

# ---------- 权限管理（懒加载，只加载一次）----------
_ADMINS_CACHE = None

def load_admins():
    global _ADMINS_CACHE
    if _ADMINS_CACHE is not None:
        return _ADMINS_CACHE
    
    admins = set()
    root_users = Configurator.cm.get_cfg().others.get("ROOT_User", [])
    admins.update(str(u) for u in root_users)
    
    if os.path.exists("Super_User.ini"):
        with open("Super_User.ini", "r", encoding="utf-8") as f:
            admins.update(line.strip() for line in f if line.strip())
    if os.path.exists("Manage_User.ini"):
        with open("Manage_User.ini", "r", encoding="utf-8") as f:
            admins.update(line.strip() for line in f if line.strip())
    
    _ADMINS_CACHE = admins
    return admins

# ---------- 等待确认状态管理 ----------
pending_confirm = {}

async def clear_pending(group_id, requester_id):
    await asyncio.sleep(300)
    key = (group_id, requester_id)
    if key in pending_confirm:
        del pending_confirm[key]

def is_target_level(level):
    try:
        level_int = int(level)
        return level_int <= 1
    except (TypeError, ValueError):
        return False

# ---------- 插件主函数 ----------
async def on_message(event, actions, Manager, Segments):
    # 只处理群消息事件
    if not isinstance(event, GroupMessageEvent):
        return False

    msg = str(event.message).strip()
    
    # 检查消息是否以配置的前缀开头
    if not msg.startswith(REMINDER):
        return False

    user_id = str(event.user_id)
    admins = load_admins()
    
    if user_id not in admins:
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(Segments.Text("权限不足，只有管理员可以使用此命令。"))
        )
        return True

    # 移除前缀，获取命令部分
    cmd_content = msg[len(REMINDER):].strip()
    parts = cmd_content.split()
    
    if not parts:
        return False
    
    cmd = parts[0].lower()

    # ---------- 踢1级 ----------
    if cmd == "踢1级":
        try:
            echo = await actions.custom.get_group_member_list(group_id=event.group_id)
            result = Manager.Ret.fetch(echo)
            members = result.data.raw

            target_members = []
            for m in members:
                user_id_val = m.get('user_id')
                if not user_id_val or user_id_val == 0:
                    continue
                level = m.get('level', 0)
                if not is_target_level(level):
                    continue
                name = m.get('card') or m.get('nickname') or ""
                if name == "Q群管家":
                    continue
                target_members.append({
                    "user_id": user_id_val,
                    "name": name,
                    "level": level
                })

            if not target_members:
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(Segments.Text("本群没有等级≤1的有效成员。"))
                )
                return True

            key = (event.group_id, user_id)
            pending_confirm[key] = {
                "members": target_members,
                "timestamp": time.time()
            }
            asyncio.create_task(clear_pending(event.group_id, user_id))

            msg_lines = [f"以下为等级≤1的用户共有{len(target_members)}名，请在5分钟内输入{REMINDER}yes确认清理", "==============="]
            for m in target_members:
                msg_lines.append(f"{m['user_id']} {m['name']} (等级{m['level']})")
            msg_lines.append("===============")
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text("\n".join(msg_lines)))
            )
        except Exception as e:
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text(f"获取成员列表失败：{str(e)}"))
            )
        return True

    # ---------- yes（确认踢人）----------
    elif cmd == "yes":
        key = (event.group_id, user_id)
        if key not in pending_confirm:
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text(f"没有待确认的踢人操作，请先使用 {REMINDER}踢1级 列出成员。"))
            )
            return True

        state = pending_confirm[key]
        if time.time() - state["timestamp"] > 300:
            del pending_confirm[key]
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text("确认超时，请重新执行 {REMINDER}踢1级。"))
            )
            return True

        whitelist = load_whitelist()
        members_to_kick = state["members"]
        total = len(members_to_kick)
        kicked = 0
        skipped_whitelist = 0
        failed = 0

        for m in members_to_kick:
            qq = str(m["user_id"])
            if qq in whitelist:
                skipped_whitelist += 1
                continue
            try:
                await actions.set_group_kick(group_id=event.group_id, user_id=m["user_id"])
                kicked += 1
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"踢出 {m['user_id']}({m['name']}) 失败: {e}")
                failed += 1

        del pending_confirm[key]

        result_msg = f"清理完成。共{total}名等级≤1的成员，已踢出{kicked}人，跳过白名单{skipped_whitelist}人，失败{failed}人。"
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(Segments.Text(result_msg))
        )
        return True

    # ---------- 踢人白名单 添加 ----------
    elif cmd == "踢人白名单" and len(parts) >= 3 and parts[1] == "添加":
        qq_to_add = parts[2].strip()
        if not qq_to_add.isdigit():
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text("QQ号必须为纯数字。"))
            )
            return True
        whitelist = load_whitelist()
        whitelist.add(qq_to_add)
        save_whitelist(whitelist)
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(Segments.Text(f"已将 {qq_to_add} 添加到踢人白名单。"))
        )
        return True

    # ---------- 踢人白名单 移除 ----------
    elif cmd == "踢人白名单" and len(parts) >= 3 and parts[1] == "移除":
        qq_to_remove = parts[2].strip()
        whitelist = load_whitelist()
        if qq_to_remove in whitelist:
            whitelist.remove(qq_to_remove)
            save_whitelist(whitelist)
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text(f"已将 {qq_to_remove} 从白名单移除。"))
            )
        else:
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text(f"{qq_to_remove} 不在白名单中。"))
            )
        return True

    # ---------- 踢人白名单 列表 ----------
    elif cmd == "踢人白名单" and len(parts) >= 2 and parts[1] == "列表":
        whitelist = load_whitelist()
        if not whitelist:
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text("白名单为空。"))
            )
        else:
            lines = ["当前踢人白名单："] + list(whitelist)
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text("\n".join(lines)))
            )
        return True

    # 不是本插件的命令，放行给其他插件
    return False