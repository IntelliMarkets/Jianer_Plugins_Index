from Hyper import Configurator
import asyncio
import threading
import time
import datetime
import traceback

# 加载配置文件
Configurator.cm = Configurator.ConfigManager(
    Configurator.Config(file="config.json").load_from_file()
)

TRIGGHT_KEYWORD = "Any"
HELP_MESSAGE = f"{Configurator.cm.get_cfg().others['reminder']}打卡状态 —> 查看今日自动打卡状态"

# 全局变量
auto_sign_started = False
sign_status = {
    "today": "",
    "total": 0,
    "success": 0,
    "failed": 0,
    "failed_groups": [],
    "is_running": False,
    "retry_count": 0
}


async def do_sign_for_all_groups(actions, Manager, retry_only_failed=False):
    """对所有群执行打卡"""
    global sign_status
    
    try:
        sign_status["is_running"] = True
        
        # 获取群列表
        echo = await actions.custom.get_group_list()
        result = Manager.Ret.fetch(echo)
        
        groups = []
        if result.data and hasattr(result.data, "raw"):
            groups = result.data.raw
        
        if not groups:
            print("[自动打卡] 群列表为空")
            sign_status["is_running"] = False
            return False
        
        # 重试模式：只处理之前失败的群
        if retry_only_failed and sign_status["failed_groups"]:
            failed_ids = [fg["group_id"] for fg in sign_status["failed_groups"]]
            groups = [g for g in groups if str(g.get("group_id")) in failed_ids]
            print(f"[自动打卡] 重试模式，共 {len(groups)} 个群需要重试")
        
        if not retry_only_failed:
            sign_status["total"] = len(groups)
            sign_status["success"] = 0
            sign_status["failed"] = 0
            sign_status["failed_groups"] = []
            sign_status["today"] = datetime.datetime.now().strftime("%Y-%m-%d")
        
        for i, group in enumerate(groups):
            group_id = str(group.get("group_id"))
            group_name = group.get("group_name", "未知群名")
            
            try:
                await actions.custom.set_group_sign(group_id=int(group_id))
                sign_status["success"] += 1
                print(f"[自动打卡] ✅ [{i+1}/{len(groups)}] 群 {group_id}({group_name}) 打卡成功")
            except Exception as e:
                error_msg = str(e)
                sign_status["failed"] += 1
                sign_status["failed_groups"].append({
                    "group_id": group_id,
                    "reason": error_msg[:100]
                })
                print(f"[自动打卡] ❌ [{i+1}/{len(groups)}] 群 {group_id} 打卡失败: {error_msg}")
        
        print(f"[自动打卡] 本轮完成: 成功 {sign_status['success']}，失败 {sign_status['failed']}")
        return sign_status["failed"] == 0
        
    except Exception as e:
        print(f"[自动打卡] 执行出错: {traceback.format_exc()}")
        return False
    finally:
        sign_status["is_running"] = False


def auto_sign_worker():
    """自动打卡后台线程"""
    global sign_status
    
    print("[自动打卡] 后台线程已启动，等待每天 00:00 执行...")
    
    while True:
        now = datetime.datetime.now()
        
        # 计算到下一个 00:00 的时间
        next_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if now >= next_midnight:
            next_midnight += datetime.timedelta(days=1)
        
        wait_seconds = (next_midnight - now).total_seconds()
        
        # 每小时检查一次
        if wait_seconds > 3600:
            time.sleep(3600)
            continue
        
        print(f"[自动打卡] 将在 {wait_seconds:.0f} 秒后 (00:00) 开始执行...")
        time.sleep(wait_seconds)
        
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        print(f"[自动打卡] ========== {today_str} 开始自动打卡 ==========")
        
        # 在新的事件循环中执行异步任务
        async def run_sign():
            from Hyper import Listener, Manager
            temp_actions = Listener.Actions()
            
            # 重置状态
            sign_status["retry_count"] = 0
            
            # 第一次尝试
            all_success = await do_sign_for_all_groups(temp_actions, Manager, retry_only_failed=False)
            
            if all_success:
                print(f"[自动打卡] 🎉 所有群打卡成功！")
                return
            
            # 失败则重试
            while sign_status["retry_count"] < 30:
                sign_status["retry_count"] += 1
                
                now = datetime.datetime.now()
                if now.hour > 0 or now.minute > 30:
                    print(f"[自动打卡] ⏰ 已超过 00:30，停止重试")
                    break
                
                # 等待到下一分钟
                time.sleep(60)
                
                current_time = datetime.datetime.now()
                print(f"[自动打卡] 🔄 第 {sign_status['retry_count']}/30 次重试 ({current_time.strftime('%H:%M')})")
                
                all_success = await do_sign_for_all_groups(temp_actions, Manager, retry_only_failed=True)
                
                if all_success:
                    print(f"[自动打卡] 🎉 重试成功！")
                    break
            
            print(f"[自动打卡] 最终结果: 成功 {sign_status['success']}/{sign_status['total']}，失败 {sign_status['failed']}")
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(run_sign())
            loop.close()
        except Exception as e:
            print(f"[自动打卡] 执行出错: {traceback.format_exc()}")


def start_auto_sign():
    global auto_sign_started
    
    if auto_sign_started:
        return
    
    sign_thread = threading.Thread(target=auto_sign_worker, daemon=True)
    sign_thread.start()
    auto_sign_started = True
    print("[自动打卡] 后台线程已启动")


async def on_message(event, actions, Manager, Segments):
    global auto_sign_started, sign_status
    
    # 启动后台线程
    if not auto_sign_started:
        start_auto_sign()
    
    if not hasattr(event, "message"):
        return False
    
    user_message = str(event.message).strip()
    reminder = Configurator.cm.get_cfg().others["reminder"]
    
    # 查询打卡状态
    if user_message == f"{reminder}打卡状态":
        if sign_status["today"] != datetime.datetime.now().strftime("%Y-%m-%d"):
            msg = "📊 今日尚未执行打卡，请等待 00:00 自动执行"
        else:
            msg = f"""📊 今日打卡状态 ({sign_status['today']})
————————————————————
总群数: {sign_status['total']}
成功: {sign_status['success']}
失败: {sign_status['failed']}
重试: {sign_status['retry_count']}/30
状态: {'🔄 进行中' if sign_status['is_running'] else '✅ 已完成'}"""
            
            if sign_status['failed'] > 0:
                msg += f"\n\n失败群列表:"
                for fg in sign_status['failed_groups'][:10]:
                    msg += f"\n- {fg['group_id']}"
        
        target_id = event.group_id if hasattr(event, "group_id") else event.user_id
        await actions.send(
            group_id=target_id if hasattr(event, "group_id") else None,
            user_id=None if hasattr(event, "group_id") else target_id,
            message=Manager.Message(Segments.Text(msg))
        )
        return True
    
    # 手动触发打卡（管理员）
    if user_message == f"{reminder}立即打卡":
        user_id = str(event.user_id)
        
        # 权限检查
        root_users = [str(u) for u in Configurator.cm.get_cfg().others.get("ROOT_User", [])]
        super_users = []
        manage_users = []
        
        try:
            with open("Super_User.ini", "r") as f:
                super_users = [line.strip() for line in f if line.strip()]
        except:
            pass
        
        try:
            with open("Manage_User.ini", "r") as f:
                manage_users = [line.strip() for line in f if line.strip()]
        except:
            pass
        
        if user_id not in root_users + super_users + manage_users:
            target_id = event.group_id if hasattr(event, "group_id") else event.user_id
            await actions.send(
                group_id=target_id if hasattr(event, "group_id") else None,
                user_id=None if hasattr(event, "group_id") else target_id,
                message=Manager.Message(Segments.Text("❌ 只有管理员可以手动触发打卡"))
            )
            return True
        
        if sign_status["is_running"]:
            target_id = event.group_id if hasattr(event, "group_id") else event.user_id
            await actions.send(
                group_id=target_id if hasattr(event, "group_id") else None,
                user_id=None if hasattr(event, "group_id") else target_id,
                message=Manager.Message(Segments.Text("⚠️ 已有打卡任务正在执行中"))
            )
            return True
        
        target_id = event.group_id if hasattr(event, "group_id") else event.user_id
        
        await actions.send(
            group_id=target_id if hasattr(event, "group_id") else None,
            user_id=None if hasattr(event, "group_id") else target_id,
            message=Manager.Message(Segments.Text("🔄 开始手动执行全群打卡..."))
        )
        
        # 重置状态并执行
        sign_status["retry_count"] = 0
        await do_sign_for_all_groups(actions, Manager, retry_only_failed=False)
        
        # 发送结果
        msg = f"""📊 手动打卡完成
————————————————————
总群数: {sign_status['total']}
成功: {sign_status['success']}
失败: {sign_status['failed']}"""
        
        if sign_status['failed'] > 0:
            msg += f"\n\n失败群列表:"
            for fg in sign_status['failed_groups'][:5]:
                msg += f"\n- {fg['group_id']}"
        
        await actions.send(
            group_id=target_id if hasattr(event, "group_id") else None,
            user_id=None if hasattr(event, "group_id") else target_id,
            message=Manager.Message(Segments.Text(msg))
        )
        
        return True
    
    return False


# 启动后台线程
start_auto_sign()

print("[群自动打卡插件] 加载成功")