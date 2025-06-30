from Hyper import Configurator
import re
import httpx
import json
import os
import time

# 加载配置
Configurator.cm = Configurator.ConfigManager(Configurator.Config(file="config.json").load_from_file())

# 插件信息
TRIGGHT_KEYWORD = "Any"

class BilibiliDelayManager:
    def __init__(self):
        self.data_dir = "./data/bilibili_delay/"
        os.makedirs(self.data_dir, exist_ok=True)
        self.config_file = os.path.join(self.data_dir, "delay_settings.json")
        self.delay_settings = self._load_delay_settings()
        self.last_analysis = {}

    def _load_delay_settings(self):
        if not os.path.exists(self.config_file):
            default_settings = {
                "global": 20,  # 默认全局延迟20秒
                "groups": {}   # 群组延迟设置
            }
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(default_settings, f, ensure_ascii=False, indent=2)
            return default_settings
        with open(self.config_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_delay_settings(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.delay_settings, f, ensure_ascii=False, indent=2)

    def set_delay(self, seconds: int, group_id: str = None):
        """设置延迟时间"""
        if group_id:
            self.delay_settings["groups"][group_id] = seconds
        else:
            self.delay_settings["global"] = seconds
        self._save_delay_settings()

    def can_analysis(self, url: str, group_id: str) -> bool:
        """检查群是否可以解析视频"""
        current_time = time.time()
        
        delay = self.delay_settings["groups"].get(
            group_id, 
            self.delay_settings["global"]
        )

        key = group_id
        last_time = self.last_analysis.get(key, 0)
        
        if current_time - last_time < delay:
            return False
            
        self.last_analysis[key] = current_time
        return True

    def cleanup_expired_records(self, max_age: int = 3600):
        """清理过期的解析记录"""
        current_time = time.time()
        self.last_analysis = {
            k: v for k, v in self.last_analysis.items() 
            if current_time - v < max_age
        }

def check_permission(user_id: str) -> bool:
    """检查用户是否有权限设置延迟"""
    try:
        if user_id in Configurator.cm.get_cfg().others.get("ROOT_User", []):
            return True
            
        with open("Super_User.ini", "r") as f:
            super_users = f.read().strip().split("\n")
            if user_id in super_users:
                return True
                
        with open("Manage_User.ini", "r") as f:
            manage_users = f.read().strip().split("\n")
            if user_id in manage_users:
                return True
                
        return False
    except Exception:
        return user_id in Configurator.cm.get_cfg().others.get("ROOT_User", [])

delay_manager = BilibiliDelayManager()

async def process_delay_command(message: str, event, actions, Manager, Segments):
    """处理延迟设置命令"""
    reminder = Configurator.cm.get_cfg().others["reminder"]
    user_id = str(event.user_id)
    
    if not check_permission(user_id):
        return "只有管理员才能设置解析延迟"
    
    if message.startswith(f"{reminder}设置解析全局延迟 "):
        try:
            seconds = int(message[len(f"{reminder}设置解析全局延迟 "):])
            if seconds < 0:
                return "延迟时间不能为负数"
            delay_manager.delay_settings["global"] = seconds
            delay_manager._save_delay_settings()
            return f"已设置全局解析延迟为 {seconds} 秒"
        except ValueError:
            return "请输入有效的秒数"
            
    elif message.startswith(f"{reminder}设置解析本群延迟 "):
        try:
            seconds = int(message[len(f"{reminder}设置解析本群延迟 "):])
            if seconds < 0:
                return "延迟时间不能为负数"
            delay_manager.set_delay(seconds, str(event.group_id))
            return f"已设置本群解析延迟为 {seconds} 秒"
        except ValueError:
            return "请输入有效的秒数"
    
    elif message == f"{reminder}查看解析延迟":
        group_id = str(event.group_id)
        global_delay = delay_manager.delay_settings["global"]
        group_delay = delay_manager.delay_settings["groups"].get(group_id, global_delay)
        return f"当前延迟设置:\n全局解析延迟: {global_delay}秒\n本群解析延迟: {group_delay}秒"
            
    return None

async def on_message(event, actions, Manager, Segments):
    if hasattr(event, '__class__') and event.__class__.__name__ == 'HyperListenerStartNotify':
        return False
    
    if not hasattr(event, 'message'):
        return False
        
    msg = str(event.message).strip()
    reminder = Configurator.cm.get_cfg().others["reminder"]
    
    if msg.startswith(f"{reminder}设置解析") or msg == f"{reminder}查看解析延迟":
        delay_result = await process_delay_command(msg, event, actions, Manager, Segments)
        if delay_result:
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text(delay_result))
            )
            return True
    
    # 处理 JSON 消息
    if hasattr(event, 'message') and len(event.message) > 0 and isinstance(event.message[0], Segments.Json):
        try:
            json_data = json.loads(event.message[0].data)
            json_msg = str(json_data)
            bv_match = re.search(r'www.bilibili.com/video/(BV\w+)', json_msg) or re.search(r'b23.tv/(BV\w+)', json_msg) or re.search(r'b23.tv/(\w+)', json_msg)
            av_match = re.search(r'www.bilibili.com/video/av(\w+)', json_msg) or re.search(r'b23.tv/av(\w+)', json_msg)
            if bv_match or av_match:
                msg = json_msg
            else:
                return False
        except:
            return False

    bv_match = re.search(r'www.bilibili.com/video/(BV\w+)', msg) or re.search(r'b23.tv/(BV\w+)', msg) or re.search(r'b23.tv/(\w+)', msg)
    av_match = re.search(r'www.bilibili.com/video/av(\w+)', msg) or re.search(r'b23.tv/av(\w+)', msg)
    
    if not (bv_match or av_match):
        return False

    if not delay_manager.can_analysis(msg, str(event.group_id)):
        return True
        
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
        }
        
        if bv_match:
            id = bv_match.group(1)
            if len(id) < 12:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"https://b23.tv/{id}", headers=headers, follow_redirects=True)
                    final_url = str(response.url)
                    bv_redirect = re.search(r'video/(BV\w+)', final_url)
                    if bv_redirect:
                        id = bv_redirect.group(1)
            req = f"bvid={id}"
        else:
            id = av_match.group(1)
            req = f"aid={id}"
            id = "av" + id
            
        # 请求B站API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.bilibili.com/x/web-interface/view?{req}",
                headers=headers
            )
            data = response.json()
            
        if data['code'] == 0:
            video_data = data['data']
            cover_url = video_data['pic']
            author_name = video_data['owner']['name']
            video_url = f"https://www.bilibili.com/video/{id}"
            title = video_data['title']                      # 视频标题
            view_count = video_data['stat']['view']          # 播放量
            like_count = video_data['stat']['like']          # 点赞数
            coin_count = video_data['stat']['coin']          # 投币数
            favorite_count = video_data['stat']['favorite']  # 收藏数
            share_count = video_data['stat']['share']        # 分享数
            danmaku_count = video_data['stat']['danmaku']    # 弹幕数
            reply_count = video_data['stat']['reply']        # 评论数
            
            def format_count(count):
                if count >= 10000:
                    return f"{count/10000:.1f}万"
                return str(count)
            
            message = f'''
视频标题：{title}
UP主：{author_name}
▶️播放：{format_count(view_count)}
👍点赞：{format_count(like_count)}
💰投币：{format_count(coin_count)}
⭐收藏：{format_count(favorite_count)}
📢弹幕：{format_count(danmaku_count)}
💬评论：{format_count(reply_count)}
🔗分享：{format_count(share_count)}
——————————
{video_url}'''

            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(
                    Segments.Image(cover_url),
                    Segments.Text(message)
                )
            )
            return True
        else:
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(
                    Segments.Text("视频解析失败")
                )
            )
            return True
            
    except Exception as e:
        print(f"B站视频解析出错: {e}")
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(
                Segments.Text(f"视频解析出现错误: {e}")
            )
        )
        return True

print("[Xiaoyi_QQ]B站视频解析插件已加载")