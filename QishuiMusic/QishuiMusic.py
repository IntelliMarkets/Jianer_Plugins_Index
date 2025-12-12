import re
import aiohttp
import asyncio
import os
import requests
import time
import base64
import subprocess
from Hyper import Configurator

# 匹配汽水音乐分享链接（尽量精确匹配到 qishui.douyin.com/... 部分）
_QISHUI_PATTERN = re.compile(r'https?://qishui\.douyin\.com/[^\s]+')

TRIGGHT_KEYWORD = "Any"

# 白名单文件配置
_WHITELIST_FILE = "qishui_music_whitelist.txt"
_whitelist = set()

def _load_whitelist():
    global _whitelist
    try:
        if os.path.exists(_WHITELIST_FILE):
            with open(_WHITELIST_FILE, "r", encoding="utf-8") as f:
                _whitelist = set(line.strip() for line in f if line.strip())
    except Exception:
        _whitelist = set()

def _save_whitelist():
    try:
        with open(_WHITELIST_FILE, "w", encoding="utf-8") as f:
            for group_id in _whitelist:
                f.write(f"{group_id}\n")
    except Exception:
        pass

# 初始加载白名单
_load_whitelist()

async def _convert_to_wav(input_file: str) -> str:
    try:
        if not os.path.exists(input_file):
            return input_file

        if not input_file.lower().endswith('.flac'):
            return input_file
        
        # 生成输出文件路径
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}.wav"
        
        # 如果输出文件已存在，直接返回
        if os.path.exists(output_file):
            try:
                os.remove(input_file)  # 删除原文件
            except:
                pass
            return output_file
        
        # 使用 ffmpeg 将 FLAC 转换为 WAV
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            '-y',  # 覆盖输出文件
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists(output_file):
            try:
                os.remove(input_file)  # 转换成功后删除原 FLAC 文件
            except:
                pass
            print(f"[QishuiMusic] 音频转换成功: {input_file} -> {output_file}")
            return output_file
        else:
            print(f"[QishuiMusic] 音频转换失败，返回原文件: {input_file}")
            return input_file
            
    except subprocess.TimeoutExpired:
        print(f"[QishuiMusic] 音频转换超时: {input_file}")
        return input_file
    except Exception as e:
        print(f"[QishuiMusic] 音频转换异常: {e}")
        return input_file

def _clean_lyrics(lyrics_text):
    """
    清洗歌词：移除时间轴（[start,end]）和时间标签 <start,duration,?>，
    保留纯文本歌词行和合理换行。
    """
    if not lyrics_text:
        return ""

    # 先按行处理，保留每行中去掉时间轴/标签后的文本
    lines = lyrics_text.splitlines()
    cleaned = []
    for line in lines:
        # 去掉 [123,456] 格式
        line = re.sub(r'\[\d+,\d+\]', '', line)
        # 去掉 <123,456,789> 格式
        line = re.sub(r'<\d+,\d+,\d+>', '', line)
        # 清理左右空白
        line = line.strip()
        if line:
            cleaned.append(line)
    return "\n".join(cleaned)

async def _perm(e):
    u = str(getattr(e, "user_id", ""))
    try:
        cfg_others = Configurator.cm.get_cfg().others
        root_list = cfg_others.get("ROOT_User", [])
        if isinstance(root_list, (list, tuple, set)):
            if u in root_list:
                return True
        # 检查本地文件 super/manage
        if os.path.exists("./Super_User.ini"):
            if u in open("./Super_User.ini", "r", encoding="utf-8").read().splitlines():
                return True
        if os.path.exists("./Manage_User.ini"):
            if u in open("./Manage_User.ini", "r", encoding="utf-8").read().splitlines():
                return True
    except Exception:
        pass
    return False

def _fetch_qishui_data_sync(api_url, retries=3):
    for attempt in range(retries):
        try:
            resp = requests.get(api_url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200 and "data" in data:
                    return data
            # 非200或解析失败时重试
            if attempt < retries - 1:
                time.sleep(1)
        except Exception:
            if attempt < retries - 1:
                time.sleep(1)
            else:
                raise
    return None

async def _fetch_qishui_data_async(api_url, retries=3):
    """异步请求（aiohttp），带重试"""
    for attempt in range(retries):
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(api_url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("code") == 200 and "data" in data:
                            return data
            if attempt < retries - 1:
                await asyncio.sleep(1)
        except Exception:
            if attempt < retries - 1:
                await asyncio.sleep(1)
            else:
                raise
    return None

async def on_message(event, actions, Manager, Segments, Events):
    """
    主入口函数（框架回调）
    - event: 消息事件对象（需包含 message, group_id, user_id, message_id, sender 等字段）
    - actions/Manager/Segments/Events: 由框架提供的辅助对象（保持原样调用）
    """
    # 必要属性检查
    if not hasattr(event, "message"):
        return False

    m = str(event.message).strip()
    # 读取配置（用于前缀等）
    try:
        cfg_others = Configurator.cm.get_cfg().others
    except Exception:
        cfg_others = {}
    r = cfg_others.get('reminder', '')

    # 自动获取主人信息（用于帮助文本）
    root_users = cfg_others.get('ROOT_User', []) if isinstance(cfg_others.get('ROOT_User', []), (list, tuple)) else []
    owner_qq = root_users[0] if root_users else '未设置主人'
    owner_name = cfg_others.get('qishui_plugin_owner_name', '主人')

    # 帮助命令
    if m == f"{r}汽水音乐解析帮助":
        help_text = f"""汽水音乐解析插件帮助：
命令：
{r}本群音乐解析加白 - 将本群加入白名单（停止解析）
{r}本群音乐解析删白 - 将本群移出白名单（恢复解析）
{r}更新汽水音乐插件 - 更新插件（需要权限）

白名单功能：
- 在白名单内的群聊发送汽水音乐链接时，机器人不会解析
- 而是发送提示：本群为汽水音乐解析白名群)

当前状态：
本群{'已加入' if str(getattr(event, 'group_id', '')) in _whitelist else '未加入'}白名单"""
        await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(help_text)))
        return True

    # 加白命令
    if m == f"{r}本群音乐解析加白":
        if not await _perm(event):
            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("你没有权限执行此操作")))
            return True
        gid = str(event.group_id)
        if gid not in _whitelist:
            _whitelist.add(gid)
            _save_whitelist()
            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("已添加本群到汽水音乐解析白名单，将不再解析本群音乐链接")))
        else:
            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("本群已在汽水音乐解析白名单中")))
        return True

    # 删白命令
    if m == f"{r}本群音乐解析删白":
        if not await _perm(event):
            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("你没有权限执行此操作")))
            return True
        gid = str(event.group_id)
        if gid in _whitelist:
            _whitelist.remove(gid)
            _save_whitelist()
            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("已从汽水音乐解析白名单中移除本群，将恢复解析本群音乐链接")))
        else:
            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("本群不在汽水音乐解析白名单中")))
        return True

    # 如果该群在白名单中，遇到链接只发送白名单提示
    if str(event.group_id) in _whitelist:
        mat = _QISHUI_PATTERN.search(m)
        if mat:
            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(f"本群为汽水音乐解析白名群")))
            return True
        return False

    mat = _QISHUI_PATTERN.search(m)
    if not mat:
        return False

    # 找到链接并调用解析 API
    music_url = mat.group(0)
    api_url = f"https://api.bugpk.com/api/qsmusic?url={music_url}"

    try:
        data = None
        try:
            data = _fetch_qishui_data_sync(api_url, retries=3)
        except Exception:
            data = None

        if data is None:
            data = await _fetch_qishui_data_async(api_url, retries=3)

        if data is None:
            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("汽水音乐解析失败: 所有重试尝试均失败")))
            return True
    except Exception as e:
        await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(f"汽水音乐解析失败: {e}")))
        return True

    # 检查返回结构
    if not isinstance(data, dict) or data.get("code") != 200 or "data" not in data:
        msg = data.get("msg", "未知错误") if isinstance(data, dict) else "接口返回格式错误"
        await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(f"汽水音乐解析失败: {msg}")))
        return True

    info = data["data"] or {}
    audio_url = info.get("url") or info.get("music_url") or info.get("play_url") or ""
    if not audio_url:
        await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("未找到音频链接，无法下载")))
        return True

    # 先发送音频直链
    try:
        await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(f"【音频链接】\n{audio_url}")))
    except Exception:
        pass

    lyrics_raw = info.get("lyric") or info.get("lyrics") or ""
    if lyrics_raw:
        cleaned = _clean_lyrics(lyrics_raw)
        if cleaned:
            preview = cleaned if len(cleaned) <= 1500 else (cleaned[:1500] + "...")
            chat_nodes = [
                Segments.CustomNode(
                    str(event.self_id),
                    "歌词",
                    Manager.Message([Segments.Text(preview)])
                )
            ]
            try:
                await actions.send_group_forward_msg(group_id=event.group_id, message=Manager.Message(*chat_nodes))
            except Exception as e:
                print(f"发送合并转发(歌词)失败: {e}")

    temp_dir = "temp_qishui_audio"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir, exist_ok=True)

    temp_filename = os.path.join(temp_dir, f"qsmusic_{int(time.time())}_{event.message_id}.flac")
    response = requests.get(audio_url, timeout=30, stream=True)
    if response.status_code != 200:
        await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("音频下载失败")))
        return True

    total_size = 0
    with open(temp_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                total_size += len(chunk)
                if total_size > 70 * 1024 * 1024:
                    f.close()
                    os.remove(temp_filename)
                    await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("⚠️ 音频文件过大，无法发送（>70MB）")))
                    return True

    file_size = os.path.getsize(temp_filename)
    if file_size == 0:
        os.remove(temp_filename)
        return True

    wav_file = await _convert_to_wav(temp_filename)

    try:
        await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Record(os.path.abspath(wav_file))))
        print(f"[QishuiMusic] 已发送 WAV 文件: {wav_file}")
    except Exception as send_error:
        print(f"[QishuiMusic] 发送音频失败: {send_error}")
        await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("发送音频失败")))

    # 清理
    try:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        if os.path.exists(wav_file):
            os.remove(wav_file)
    except Exception as e:
        print(f"[QishuiMusic] 清理文件时出错: {e}")

    return True

print("汽水音乐解析插件已加载")