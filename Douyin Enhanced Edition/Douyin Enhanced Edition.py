import base64 as _b, binascii as _ba, httpx as _h, re as _r, asyncio
from Hyper import Configurator as _C
import time
import os

# 预编译正则表达式
_DOUYIN_PATTERN = _r.compile(r'(https?://v\.douyin\.com/[^\s]+)')

# 全局HTTP客户端（复用连接）
_client = _h.AsyncClient(timeout=10.0)

# 解密密钥
_K = "vxpinabo8u5i7"
_CI = "173022590d292f59740c0c01543113050c36370a35552340334e431212005723372a530357215c002238051f04215a4f147d281812203a1a3e391656"

def _d(ch, k):
    c = bytes.fromhex(ch)
    b = bytes([x ^ ord(k[i % len(k)]) for i, x in enumerate(c)])
    return _b.b64decode(b).decode("utf-8")

_API = _d(_CI, _K)
TRIGGHT_KEYWORD = "Any"
HELP_MESSAGE = f"{_C.cm.get_cfg().others['reminder']}抖音解析帮助 —> 查看插件使用说明"

# 白名单文件路径
_WHITELIST_FILE = "douyin_whitelist.txt"

# 初始化白名单集合
_whitelist = set()

# 加载白名单
def _load_whitelist():
    global _whitelist
    if os.path.exists(_WHITELIST_FILE):
        with open(_WHITELIST_FILE, "r") as f:
            _whitelist = set(line.strip() for line in f if line.strip())

# 保存白名单
def _save_whitelist():
    with open(_WHITELIST_FILE, "w") as f:
        for group_id in _whitelist:
            f.write(f"{group_id}\n")

# 初始化时加载白名单
_load_whitelist()

async def _perm(e):
    u = str(e.user_id)
    try:
        return (
            u in _C.cm.get_cfg().others["ROOT_User"]
            or u in open("./Super_User.ini", "r").read().splitlines()
            or u in open("./Manage_User.ini", "r").read().splitlines()
        )
    except Exception:
        return False

async def on_message(event, actions, Manager, Segments):
    if not hasattr(event, "message"):
        return False
        
    m = str(event.message).strip()
    
    # 缓存配置减少重复获取
    cfg = _C.cm.get_cfg().others
    r = cfg.get('reminder', '')
    
    # 自动获取主人信息（从配置读取）
    root_users = cfg.get('ROOT_User', [])
    if root_users:
        owner_qq = root_users[0]
    else:
        owner_qq = '未设置主人'
    owner_name = cfg.get('douyin_plugin_owner_name', '主人')
    
    # 处理帮助命令
    if m == f"{r}抖音解析帮助":
        help_text = f"""抖音解析插件帮助：
命令：
{r}本群解析加白 - 将本群加入白名单（停止解析）
{r}本群解析删白 - 将本群移出白名单（恢复解析）
{r}更新抖音解析插件 - 更新插件（需要权限）

白名单功能：
- 在白名单内的群聊发送抖音链接时，机器人不会解析
- 而是发送提示："本群为抖音解析白名群，无法解析抖音链接，若想开启抖音解析功能，请联系{owner_name}({owner_qq})"

当前状态：
本群{'已加入' if str(event.group_id) in _whitelist else '未加入'}白名单"""
        
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(Segments.Text(help_text))
        )
        return True
    
    # 处理白名单命令
    if m == f"{r}本群解析加白":
        if not await _perm(event):
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text("你没有权限执行此操作"))
            )
            return True
            
        group_id = str(event.group_id)
        if group_id not in _whitelist:
            _whitelist.add(group_id)
            _save_whitelist()
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text("已添加本群到抖音解析白名单，将不再解析本群抖音链接"))
            )
        else:
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text("本群已在抖音解析白名单中"))
            )
        return True
       
    elif m == f"{r}本群解析删白":
        if not await _perm(event):
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text("你没有权限执行此操作"))
            )
            return True
            
        group_id = str(event.group_id)
        if group_id in _whitelist:
            _whitelist.remove(group_id)
            _save_whitelist()
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text("已从抖音解析白名单中移除本群，将恢复解析本群抖音链接"))
            )
        else:
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text("本群不在抖音解析白名单中"))
            )
        return True
  
    # 处理插件更新命令
    if m == f"{r}更新抖音解析插件":
        if not await _perm(event):
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text("你没有权限执行此操作"))
            )
            return True
            
        try:
            url = "http://101.35.241.21:8888/down/V0uNtBcwT7zG.py"
            save_path = __file__
            
            resp = await _client.get(url)
            if resp.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(resp.content)
                msg = f"抖音解析插件已更新，请发送 {r}重载插件 完成重载！"
            else:
                msg = f"下载失败，状态码: {resp.status_code}"
                
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text(msg))
            )
        except Exception as e:
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text(f"更新失败: {e}"))
            )
        return True

    # 检查当前群是否在白名单中 - 发送提示消息
    if str(event.group_id) in _whitelist:
        mat = _DOUYIN_PATTERN.search(m)
        if mat:
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text(
                    f"本群为抖音解析白名群，无法解析抖音链接，若想开启抖音解析功能，请联系{owner_name}({owner_qq})"
                ))
            )
            return True
        return False

    # 正常解析流程
    mat = _DOUYIN_PATTERN.search(m)
    if not mat:
        return False
        
    d_url = mat.group(1)
    api_url = _API.format(d_url)
    
    try:
        resp = await _client.get(api_url)
        data = resp.json()
    except Exception as e:
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(Segments.Text(f"抖音解析失败: {e}"))
        )
        return True

    if data.get("code") != 0 or "data" not in data:
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(Segments.Text(f"抖音解析失败: {data.get('msg', '未知错误')}"))
        )
        return True

    info = data["data"]
    a = info.get("author", {})
    msc = info.get("music", {})
    cnt = info.get("count", {})
    desc = info.get('desc', '')
    desc = _r.sub(r'[\r\n]+', ' ', desc) if desc else "无简介"
    vurl = info.get('url', '')
    
    # 1. 创建聊天记录格式的消息
    chat_nodes = []
    
    # 用户消息部分
    chat_nodes.append(
        Segments.CustomNode(
            str(event.user_id),
            event.sender.nickname,
            Manager.Message([
                Segments.Text(f"{m}")
            ])
        )
    )
    
    # 作者信息小节
    chat_nodes.append(
        Segments.CustomNode(
            str(event.self_id),
            "小卡",
            Manager.Message([
                Segments.Image(a.get("avatar", "")),
                Segments.Text(f"作者昵称：{a.get('name', '未知')}"),
                Segments.Text(f"抖音号：{a.get('id', '未知')}"),
                Segments.Text(f"签名：{a.get('signature', '无签名')}")
            ])
        )
    )
    
    # 视频信息小节
    chat_nodes.append(
        Segments.CustomNode(
            str(event.self_id),
            "小卡",
            Manager.Message([
                Segments.Image(info.get("cover", "")),
                Segments.Text(f"简介：{desc}"),
                Segments.Text(f"标签：{info.get('tag', '无标签')}")
            ])
        )
    )
    
    # 音乐信息小节
    chat_nodes.append(
        Segments.CustomNode(
            str(event.self_id),
            "小卡",
            Manager.Message([
                Segments.Text(f"音乐：{msc.get('title', '无标题')}"),
                Segments.Text(f"作者：{msc.get('author', '未知')}"),
                Segments.Text(f"时长：{msc.get('duration', 0)}秒")
            ])
        )
    )
    
    # 统计数据小节
    chat_nodes.append(
        Segments.CustomNode(
            str(event.self_id),
            "小卡",
            Manager.Message([
                Segments.Text("【统计数据】"),
                Segments.Text(f"👍点赞：{cnt.get('like', 0)}"),
                Segments.Text(f"💬💬评论：{cnt.get('comment', 0)}"),
                Segments.Text(f"📢📢分享：{cnt.get('share', 0)}"),
                Segments.Text(f"⭐收藏：{cnt.get('collect', 0)}")
            ])
        )
    )
    
    # 直链信息小节
    chat_nodes.append(
        Segments.CustomNode(
            str(event.self_id),
            "小卡",
            Manager.Message([
                Segments.Text("【视频直链】"),
                Segments.Text(f"🔗🔗{vurl if vurl else '无直链'}")
            ])
        )
    )
    
    # 发送聊天记录
    await actions.send_group_forward_msg(
        group_id=event.group_id,
        message=Manager.Message(*chat_nodes)
    )
    
    # 2. 单独发送视频
    if vurl:
        try:
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message([Segments.Video(vurl)])
            )
        except Exception as e:
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text(f"视频发送失败：{e}"))
            )
        
    return True

print("[Xiaoyi_QQ]抖音解析插件已加载")
