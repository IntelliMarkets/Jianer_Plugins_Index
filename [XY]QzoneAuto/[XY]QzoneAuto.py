import os
import json
import asyncio
import requests
import base64
import threading
import time
from datetime import datetime, timedelta
from Hyper import Configurator

TRIGGHT_KEYWORD = "Any"
DATA_PATH = "./data/qq_autosign/"
USER_FILE = os.path.join(DATA_PATH, "users.json")
LOGIN_API = "https://cookie.ruax.cc/login.php?do=apigetqrpic"
LOGIN_RESULT_API = "https://cookie.ruax.cc/login.php?do=apigetresult"
SIGN_API = "https://api.yuafeng.cn/ly/QQ/qzone_signIn.php"
DEFAULT_TIME = "12:00"

if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

# 加载配置
Configurator.cm = Configurator.ConfigManager(Configurator.Config(file="config.json").load_from_file())

def load_users():
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

_auto_sign_scheduler_started = False

async def on_message(event, actions, Manager, Segments):
    global _auto_sign_scheduler_started
    if not _auto_sign_scheduler_started:
        print("[QAuto][定时任务] 首次触发，自动启动定时打卡线程。")
        start_auto_sign_scheduler(actions, Manager, Segments)
        _auto_sign_scheduler_started = True

    if not hasattr(event, "message"):
        return False
    message = str(event.message).strip()
    reminder = Configurator.cm.get_cfg().others["reminder"]
    user_id = str(event.user_id)
    group_id = getattr(event, "group_id", None)

    if message == f"{reminder}申请登录":
        await actions.send(
            group_id=group_id,
            message=Manager.Message([Segments.At(user_id), Segments.Text("正在获取二维码，请稍候...")])
        )
        def get_qr_data(user_id):
            params = {"uin": user_id}
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://cookie.ruax.cc/"
            }
            try:
                resp = requests.get(LOGIN_API, params=params, headers=headers, timeout=10)
                return resp.json(), resp.text
            except Exception as e:
                print(f"[QAuto] requests异常: {e}")
                return None, str(e)
        loop = asyncio.get_event_loop()
        data, raw_text = await loop.run_in_executor(None, get_qr_data, user_id)
        if not isinstance(data, dict):
            await actions.send(
                group_id=group_id,
                message=Manager.Message([Segments.At(user_id), Segments.Text(f"获取二维码失败，接口返回内容异常：{raw_text}")])
            )
            return True
        if data.get("saveOK", -999) != 0:
            await actions.send(
                group_id=group_id,
                message=Manager.Message([Segments.At(user_id), Segments.Text(f"获取二维码失败：{data.get('msg', '未知错误')}")])
            )
            return True
        qrcode_url = data["qrcode_url"]
        web_login_url = data["web_login_url"]
        token = data["token"]
        sid = data.get("sid", None)
        print(f"[QAuto][DEBUG] 获取二维码成功，token={token} qrcode_url={qrcode_url} web_login_url={web_login_url} sid={sid}")
        qrcode_base64 = data.get("qrcode", "")
        img_path = os.path.abspath(os.path.join(DATA_PATH, f"qr_{user_id}.png"))
        if qrcode_base64.startswith("data:image"):
            try:
                b64data = qrcode_base64.split(",", 1)[1]
                with open(img_path, "wb") as f:
                    f.write(base64.b64decode(b64data))
                print(f"[QAuto] 二维码图片已保存: {img_path}")
                await actions.send(
                    group_id=group_id,
                    message=Manager.Message([
                        Segments.At(user_id),
                        Segments.Image(img_path),
                        Segments.Text(f"\n网页登录地址：{web_login_url}\n请扫码或点击链接登录。")
                    ])
                )
                img_seg = None
            except Exception as e:
                print(f"[QAuto] base64解码二维码异常: {e}")
                img_seg = Segments.Text("[二维码图片解码失败]")
        else:
            img_seg = Segments.Text("[二维码数据缺失]")
        if img_seg:
            await actions.send(
                group_id=group_id,
                message=Manager.Message([
                    Segments.At(user_id),
                    img_seg,
                    Segments.Text(f"\n网页登录地址：{web_login_url}\n请扫码或点击链接登录。")
                ])
            )
        def get_login_result(token, sid=None):
            try:
                params = {"token": token}
                if sid:
                    params["sid"] = sid
                resp = requests.get(LOGIN_RESULT_API, params=params, timeout=10)
                return resp.json(), resp.text
            except Exception as e:
                print(f"[QAuto] 登录状态requests异常: {e}")
                return None, str(e)
        for _ in range(60):
            await asyncio.sleep(3)
            print(f"[QAuto][DEBUG] 正在轮询登录状态，token={token} sid={sid}")
            result, result_text = await loop.run_in_executor(None, get_login_result, token, sid)
            print(f"[QAuto][DEBUG] 轮询返回 result={result} result_text={result_text}")
            if not isinstance(result, dict):
                print(f"[QAuto][DEBUG] 登录状态接口响应异常: {result_text}")
                continue
            if result.get("saveOK") == 0:
                keys = result["keys"]
                users = load_users()
                uid = str(user_id)
                print(f"[QAuto][DEBUG] 登录成功，准备保存用户: {uid} keys={keys}")
                users[uid] = {
                    "uin": keys["uin"],
                    "nick": keys["nick"],
                    "skey": keys["skey"],
                    "p_skey": keys["pskey"],
                    "auto_time": DEFAULT_TIME
                }
                save_users(users)
                print(f"[QAuto][DEBUG] 登录成功已保存: {uid} -> {users[uid]}")
                await actions.send(
                    group_id=group_id,
                    message=Manager.Message([Segments.At(user_id), Segments.Text("登录成功！已为你保存自动打卡信息。")] )
                )
                return True
            elif result.get("saveOK") == 1:
                print(f"[QAuto][DEBUG] 二维码已失效，result={result}")
                await actions.send(
                    group_id=group_id,
                    message=Manager.Message([Segments.At(user_id), Segments.Text("二维码已失效，请重新发送申请登录。")] )
                )
                return True
        print(f"[QAuto][DEBUG] 登录超时，最后一次result={result} result_text={result_text}")
        await actions.send(
            group_id=group_id,
            message=Manager.Message([Segments.At(user_id), Segments.Text("登录超时，请重新发送申请登录。")] )
        )
        return True

    if message.startswith(f"{reminder}设置自动打卡时间 "):
        time_str = message.replace(f"{reminder}设置自动打卡时间 ", "").strip()
        try:
            datetime.strptime(time_str, "%H:%M")
        except:
            await actions.send(
                group_id=group_id,
                message=Manager.Message([Segments.At(user_id), Segments.Text("时间格式错误，请用HH:MM格式。")] )
            )
            return True
        users = load_users()
        uid = str(user_id)
        print(f"[QAuto][DEBUG] 设置打卡时间时用户表: {users}")
        if uid not in users:
            print(f"[QAuto][DEBUG] 设置打卡时间失败，用户{uid}未登录，users={users}")
            await actions.send(
                group_id=group_id,
                message=Manager.Message([Segments.At(user_id), Segments.Text("请先申请登录。")] )
            )
            return True
        print(f"[QAuto][DEBUG] 设置打卡时间，用户{uid}原数据: {users[uid]}")
        users[uid]["auto_time"] = time_str
        save_users(users)
        print(f"[QAuto][DEBUG] 设置打卡时间后用户数据: {users[uid]}")
        await actions.send(
            group_id=group_id,
            message=Manager.Message([Segments.At(user_id), Segments.Text(f"已为你设置自动打卡时间为{time_str}")])
        )
        return True

    return False

async def auto_sign_task(actions, Manager, Segments):
    users = load_users()
    now = datetime.now().strftime("%H:%M")
    print(f"[QAuto][定时任务] 当前时间: {now}，用户表: {users}")
    def sign_request(params):
        try:
            print(f"[QAuto][定时任务] 发起打卡请求，参数: {params}")
            resp = requests.get(SIGN_API, params=params, timeout=10)
            return resp.json(), resp.text
        except Exception as e:
            print(f"[QAuto][定时任务] 自动打卡requests异常: {e}")
            return None, str(e)
    loop = asyncio.get_event_loop()
    for user_id, info in users.items():
        user_time = info.get("auto_time", DEFAULT_TIME)
        print(f"[QAuto][定时任务] 检查用户: {user_id} 设定时间: {user_time}")
        if user_time == now:
            print(f"[QAuto][定时任务] 用户{user_id}准备执行打卡。参数: uin={info.get('uin')}, skey={info.get('skey')}, p_skey={info.get('p_skey')}")
            params = {
                "uin": info["uin"],
                "skey": info["skey"],
                "p_skey": info["p_skey"],
                "text": "",
                "image": ""
            }
            resp, raw_text = await loop.run_in_executor(None, sign_request, params)
            print(f"[QAuto][定时任务] 用户{user_id} 打卡接口返回: {resp} 原始: {raw_text}")
            if isinstance(resp, dict) and resp.get("code") == 0:
                print(f"[QAuto][定时任务] 用户{user_id} 打卡成功: {resp}")
                await actions.send(
                    user_id=int(user_id),
                    message=Manager.Message(Segments.Text(f"自动打卡成功：{resp['data']['title']}"))
                )
            else:
                msg = resp["msg"] if isinstance(resp, dict) and "msg" in resp else raw_text
                print(f"[QAuto][定时任务] 用户{user_id} 打卡失败: {msg}")
                await actions.send(
                    user_id=int(user_id),
                    message=Manager.Message(Segments.Text(f"自动打卡失败：{msg}请重新申请登录。"))
                )
                if isinstance(resp, dict) and ("失效" in resp.get("msg", "") or "过期" in resp.get("msg", "")):
                    print(f"[QAuto][定时任务] 用户{user_id} skey/pskey失效，清除。")
                    users[user_id].pop("skey", None)
                    users[user_id].pop("pskey", None)
    save_users(users)

def start_auto_sign_scheduler(actions, Manager, Segments):
    def scheduler():
        loop = None
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        while True:
            try:
                coro = auto_sign_task(actions, Manager, Segments)
                if asyncio.iscoroutine(coro):
                    loop.run_until_complete(coro)
            except Exception as e:
                print(f"[QAuto][定时任务] 执行异常: {e}")
            time.sleep(60)
    t = threading.Thread(target=scheduler, daemon=True)
    t.start()

print("[Xiaoyi_QQ]QQ自动打卡插件已加载")
print("Version: 1.0.0")
print("Author: Xiaoyi")
