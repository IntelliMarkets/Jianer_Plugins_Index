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
HELP_MESSAGE = "- 自动解析汽水音乐分享链接\n- 发送汽水音乐链接即可自动解析"

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
    """
    将音频文件转换为 WAV 格式
    使用 ffmpeg 进行转换，支持 FLAC, MP3, M4A 等格式
    返回转换后的 WAV 文件路径，若转换失败返回原文件路径
    """
    try:
        if not os.path.exists(input_file):
            return input_file

        # 如果已经是 WAV 格式，直接返回
        if input_file.lower().endswith('.wav'):
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

        # 使用 ffmpeg 转换
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
                os.remove(input_file)  # 转换成功后删除原文件
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
    """
    权限检查：检查用户是否在 ROOT_User 或 Super_User/Manage_User 列表中
    注意：可能因配置格式不同需要根据你的环境调整 Configurator 的访问方式
    """
    u = str(getattr(e, "user_id", ""))  # 兼容性处理
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
    """同步请求（requests），带重试"""
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
                # 最后一次抛出异常以便上层处理
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
- 而是发送提示：本群为汽水音乐解析白名群，无法解析音乐链接，若想开启音乐解析功能，请联系{owner_name}({owner_qq})

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

    # 更新插件命令（下载覆盖当前文件）
    if m == f"{r}更新汽水音乐插件":
        if not await _perm(event):
            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("你没有权限执行此操作")))
            return True
        try:
            update_url = "https://raw.githubusercontent.com/your-repo/main/QishuiMusic.py"  # 请替换为真实仓库URL
            save_path = __file__
            resp = requests.get(update_url, timeout=30)
            if resp.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(resp.content)
                msg = f"汽水音乐插件已更新，请发送 {r}重载插件 完成重载！"
            else:
                msg = f"下载失败，状态码: {resp.status_code}"
            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(msg)))
        except Exception as e:
            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(f"更新失败: {e}")))
        return True

    # 如果该群在白名单中，遇到链接只发送白名单提示
    if str(event.group_id) in _whitelist:
        mat = _QISHUI_PATTERN.search(m)
        if mat:
            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(f"本群为汽水音乐解析白名群，无法解析音乐链接，若想开启音乐解析功能，请联系{owner_name}({owner_qq})")))
            return True
        return False

    # 非链接消息忽略
    mat = _QISHUI_PATTERN.search(m)
    if not mat:
        return False

    # 找到链接并调用解析 API
    music_url = mat.group(0)
    api_url = f"https://api.bugpk.com/api/qsmusic?url={music_url}"

    try:
        # 优先同步 fetch（避免 aiohttp 在某些框架下不可用），若失败再尝试异步
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

    # 兼容字段：title/albumname, artist/artistsname
    title = info.get("title") or info.get("albumname") or info.get("song") or "未知歌曲"
    artist = info.get("artist") or info.get("artistsname") or info.get("artists") or info.get("singer") or "未知艺术家"
    pic = info.get("pic") or info.get("cover") or ""
    fmt = info.get("Format") or info.get("format") or info.get("codec") or info.get("Codec") or "未知"
    size = info.get("Size") or info.get("size") or "未知"
    bitrate = info.get("Bitrate") or info.get("bitrate") or info.get("Bitrate_kbps") or "未知"
    audio_url = info.get("url") or info.get("music_url") or info.get("play_url") or ""

    # 构建合并转发消息（chat_nodes）
    chat_nodes = []

    # 原用户发言节点
    try:
        chat_nodes.append(
            Segments.CustomNode(
                str(event.user_id),
                getattr(getattr(event, "sender", None), "nickname", "用户"),
                Manager.Message([Segments.Text(m)])
            )
        )
    except Exception:
        # 退化为普通文本节点（以防 CustomNode 构造签名不一致）
        chat_nodes.append(Segments.Text(f"用户: {m}"))

    # 解析结果节点（拼接消息段）
    message_parts = []
    # 尽量先发送封面图片（如果有）
    if pic:
        message_parts.append(Segments.Image(pic))

    message_parts.extend([
        Segments.Text(f"🎵 歌曲: {title}"),
        Segments.Text(f"🎤 歌手: {artist}"),
        Segments.Text(f"💿 专辑: {info.get('albumname', info.get('album', '未知'))}"),
        Segments.Text("【音乐信息】"),
        Segments.Text(f"🗂 格式: {fmt}"),
        Segments.Text(f"💾 大小: {size}"),
        Segments.Text(f"🎚 比特率: {bitrate}")
    ])

    # 处理歌词（清洗并截取长度）
    lyrics = info.get("lyric") or info.get("lyrics") or ""
    if lyrics:
        cleaned = _clean_lyrics(lyrics)
        if cleaned:
            preview = cleaned if len(cleaned) <= 1500 else (cleaned[:1500] + "...")
            message_parts.append(Segments.Text("【歌词预览】"))
            # 分段发送歌词（部分平台对消息长度有限制，如果必要可改成多次发送）
            message_parts.append(Segments.Text(preview))

    # 把解析结果作为一个自定义机器人节点加入转发
    try:
        chat_nodes.append(
            Segments.CustomNode(
                str(event.self_id),
                "音乐解析",
                Manager.Message(message_parts)
            )
        )
    except Exception:
        # 如果 CustomNode 无法构造（不同框架签名差异），将 message_parts 拼成文本发送
        combined_text = "\n".join([p.text if hasattr(p, "text") else str(p) for p in message_parts if p is not None])
        chat_nodes.append(Manager.Message(Segments.Text(combined_text)))

    # 单独添加音频链接节点
    if audio_url:
        try:
            chat_nodes.append(
                Segments.CustomNode(
                    str(event.self_id),
                    "音频链接",
                    Manager.Message([
                        Segments.Text("【音频链接】"),
                        Segments.Text(audio_url)
                    ])
                )
            )
        except Exception:
            # 如果 CustomNode 无法构造，直接添加文本节点
            chat_nodes.append(Manager.Message(Segments.Text(f"【音频链接】\n{audio_url}")))

    # 发送合并转发消息（大多数框架提供 send_group_forward_msg）
    try:
        # 如果框架要求 Manager.Message(*chat_nodes) 则使用下面格式
        await actions.send_group_forward_msg(group_id=event.group_id, message=Manager.Message(*chat_nodes))
    except Exception:
        # 退化处理：逐条发送（避免完全失败）
        try:
            for node in chat_nodes:
                # 如果 node 是 Manager.Message 类型，直接发送，否则包装
                if isinstance(node, Manager.Message):
                    await actions.send(group_id=event.group_id, message=node)
                else:
                    await actions.send(group_id=event.group_id, message=Manager.Message(node))
                await asyncio.sleep(0.2)
        except Exception:
            # 最后兜底：简单文本发送
            try:
                simple_msg = f"🎵 歌曲: {title}\n🎤 歌手: {artist}\n 链接: {audio_url or '无'}"
                await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(simple_msg)))
            except Exception:
                pass

    # 同时尝试发送音频文件（如果链接有效）
    if audio_url:
        # 首先尝试直接作为 Record 发送远程 url
        try:
            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Record(audio_url)))
            return True
        except Exception:
            # 如果直接发送 URL 失败，尝试下载后发送
            pass

        # 下载到临时文件再发送（备用方案）
        try:
            # 临时目录
            temp_dir = "temp_qishui_audio"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir, exist_ok=True)

            # 根据URL确定文件扩展名
            file_ext = '.flac'  # 默认扩展名为 FLAC
            if '.mp4' in audio_url.lower():
                file_ext = '.mp4'
            elif '.m4a' in audio_url.lower():
                file_ext = '.m4a'
            elif '.mp3' in audio_url.lower():
                file_ext = '.mp3'

            temp_filename = os.path.join(temp_dir, f"qsmusic_{int(time.time())}_{event.message_id}{file_ext}")

            # 使用同步requests下载，更稳定
            response = requests.get(audio_url, timeout=30, stream=True)
            if response.status_code == 200:
                total_size = 0
                with open(temp_filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            total_size += len(chunk)
                            # 文件大小限制检查
                            if total_size > 50 * 1024 * 1024:  # 50MB
                                f.close()
                                os.remove(temp_filename)
                                await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("⚠️ 音频文件过大，无法发送（>50MB）")))
                                return True

                file_size = os.path.getsize(temp_filename)

                if file_size == 0:
                    os.remove(temp_filename)
                    return True

                # 如果不是 MP4，转换为 WAV 格式发送
                if file_ext != '.mp4':
                    # 转换为 WAV 格式
                    wav_file = await _convert_to_wav(temp_filename)

                    # 发送 WAV 文件（使用绝对路径）
                    try:
                        await actions.send(
                            group_id=event.group_id, 
                            message=Manager.Message(Segments.Record(os.path.abspath(wav_file)))
                        )
                        print(f"[QishuiMusic] 音频文件已发送: {wav_file}")
                    except Exception as send_error:
                        print(f"[QishuiMusic] 发送音频失败: {send_error}")
                        pass
                else:
                    # MP4 作为视频发送
                    try:
                        await actions.send(
                            group_id=event.group_id, 
                            message=Manager.Message(Segments.Video(os.path.abspath(temp_filename)))
                        )
                        print(f"[QishuiMusic] 视频文件已发送: {temp_filename}")
                    except Exception as send_error:
                        print(f"[QishuiMusic] 发送视频失败: {send_error}")
                        pass

                # 延迟清理临时文件
                await asyncio.sleep(5)
                try:
                    # 清理原文件和 WAV 文件
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                        print(f"[QishuiMusic] 已清理临时文件: {temp_filename}")

                    # 清理转换后的 WAV 文件
                    if file_ext != '.mp4':
                        wav_file = os.path.splitext(temp_filename)[0] + '.wav'
                        if os.path.exists(wav_file):
                            os.remove(wav_file)
                            print(f"[QishuiMusic] 已清理 WAV 文件: {wav_file}")
                except Exception as e:
                    print(f"[QishuiMusic] 清理文件时出错: {e}")
                    pass

        except Exception as download_error:
            # 下载失败也不提示，因为链接已经在转发消息中
            pass

    return True

print("汽水音乐解析插件已加载")