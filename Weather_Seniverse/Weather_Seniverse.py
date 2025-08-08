from Hyper import Configurator
import requests
import json
import os
from datetime import datetime

Configurator.cm = Configurator.ConfigManager(Configurator.Config(file="config.json").load_from_file())

TRIGGHT_KEYWORD = "天气"
HELP_MESSAGE = f"{Configurator.cm.get_cfg().others['reminder']}天气 城市名 —> 查询指定城市的天气信息，包括今明后三天预报哦~"



# 心知天气API配置
NOW_API_URL = 'https://api.seniverse.com/v3/weather/now.json'
DAILY_API_URL = 'https://api.seniverse.com/v3/weather/daily.json'
LIFE_SUGGESTION_API_URL = 'https://api.seniverse.com/v3/life/suggestion.json'
API_KEY = 'xxx'  # 你的心知天气API Key

# 创建数据存储目录
WEATHER_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'weather'))
os.makedirs(WEATHER_DATA_DIR, exist_ok=True)

def get_user_data_path(user_id):
    """获取用户数据文件路径"""
    return os.path.join(WEATHER_DATA_DIR, f"{user_id}.json")

def load_user_data(user_id):
    """加载用户数据，若文件为空或损坏则重置为初始值"""
    user_file = get_user_data_path(user_id)
    if os.path.exists(user_file):
        try:
            with open(user_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.strip():
                    # 文件为空，重置
                    raise ValueError('empty file')
                return json.loads(content)
        except Exception:
            # 文件损坏或为空，重置
            data = {"count": 0, "last_used": ""}
            save_user_data(user_id, data)
            return data
    return {"count": 0, "last_used": ""}

def save_user_data(user_id, data):
    """保存用户数据"""
    user_file = get_user_data_path(user_id)
    try:
        with open(user_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存用户天气数据失败: {e}")

def update_weather_usage(user_id):
    """更新用户使用次数"""
    user_data = load_user_data(user_id)
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 如果是今天第一次使用
    if user_data["last_used"] != today:
        user_data["count"] += 1
    
    user_data["last_used"] = today
    save_user_data(user_id, user_data)
    return user_data["count"]

# 辅助函数，尝试将值转为整数
def try_parse_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

async def on_message(event, actions, Manager, Segments):
    msg = str(event.message)
    reminder = Configurator.cm.get_cfg().others["reminder"]
    prefix = f"{reminder}天气"
    if not msg.startswith(prefix):
        return
    
    # 更新用户使用次数
    usage_count = update_weather_usage(str(event.user_id))
    
    city_query = msg[len(prefix):].strip()
    if not city_query:
        await actions.send(group_id=event.group_id, message=Manager.Message(
            Segments.Reply(event.message_id), 
            Segments.Text("小可爱，忘记输入城市名字啦！例如：-天气 北京 (づ｡◕‿‿◕｡)づ")
        ))
        return True
    

    # 构造心知天气实况API参数
    now_params = {
        'key': API_KEY,
        'location': city_query,
        'language': 'zh-Hans',
        'unit': 'c',
    }
    # 构造心知天气未来3天天气API参数
    daily_params = {
        'key': API_KEY,
        'location': city_query,
        'language': 'zh-Hans',
        'unit': 'c',
        'start': 0,
        'days': 3,
    }

    try:
        # 获取实况天气
        now_resp = requests.get(NOW_API_URL, params=now_params, timeout=10)
        # 获取未来3天天气
        daily_resp = requests.get(DAILY_API_URL, params=daily_params, timeout=10)
        # 获取生活指数（紫外线、空气污染扩散条件、舒适度、雨伞）
        life_params = {
            'key': API_KEY,
            'location': city_query,
            'language': 'zh-Hans',
            'days': 2,
        }
        life_resp = requests.get(LIFE_SUGGESTION_API_URL, params=life_params, timeout=10)


        if now_resp.status_code == 200 and daily_resp.status_code == 200 and life_resp.status_code == 200:
            now_data = now_resp.json()
            daily_data = daily_resp.json()
            life_data = life_resp.json()

            # 解析实况天气数据
            now_results = now_data.get('results', None)
            now_info = None
            if isinstance(now_results, list) and len(now_results) > 0:
                now_info = now_results[0]
            elif isinstance(now_results, dict):
                now_info = now_results
            else:
                now_info = {}
            location = {}
            now_weather = {}
            if isinstance(now_info, dict):
                location = now_info.get('location', {}) if isinstance(now_info.get('location', {}), dict) else {}
                now_weather = now_info.get('now', {}) if isinstance(now_info.get('now', {}), dict) else {}
            city_name = location.get('name', '未知城市') if isinstance(location, dict) else '未知城市'

            temp_str = now_weather.get('temperature', '??') if isinstance(now_weather, dict) else '??'  # 实时温度
            humidity_str = now_weather.get('humidity', '??') if isinstance(now_weather, dict) else '??'  # 实时湿度
            info = now_weather.get('text', '晴朗') if isinstance(now_weather, dict) else '晴朗'  # 天气现象
            direct = now_weather.get('wind_direction', '微风') if isinstance(now_weather, dict) else '微风'  # 风向
            power = now_weather.get('wind_scale', '轻轻吹') if isinstance(now_weather, dict) else '轻轻吹'  # 风力等级

            temp_val = try_parse_int(temp_str)
            humidity_val = try_parse_int(humidity_str)

            cute_message_parts = [f"喵~ {city_name}的实时天气来咯！✧٩(ˊωˋ*)و✧"]
            # 添加使用次数信息
            cute_message_parts.append(f"✨ 这是你本月第 {usage_count} 次查询天气啦！")

            # 天气状况判断
            if "晴" in info:
                cute_message_parts.append(f"☀️ 今天是大晴天，{info}！心情也要阳光起来呀！")
            elif "多云" in info:
                cute_message_parts.append(f"🌥️ 现在是{info}，偶尔能见到太阳公公哦~")
            elif "阴" in info:
                cute_message_parts.append(f"☁️ {info}天啦，不过也要保持好心情呀！")
            elif "雨" in info:
                cute_message_parts.append(f"🌧️ 下{info}啦！出门记得带上心爱的小雨伞哦~")
            elif "雪" in info:
                cute_message_parts.append(f"❄️ 哇！下{info}了！可以堆雪人打雪仗啦！")
            else:
                cute_message_parts.append(f"ฅ 天气宝宝说：现在是 {info} 哦！")

            # 温度判断
            if temp_val is not None:
                if temp_val < 10:
                    cute_message_parts.append(f"🌡️ 温度：{temp_str}°C (有点冷哦，快穿上暖暖的衣服！🧥)")
                elif temp_val <= 25:
                    cute_message_parts.append(f"🌡️ 温度：{temp_str}°C (温度刚刚好，超舒服的！😊)")
                else:
                    cute_message_parts.append(f"🌡️ 温度：{temp_str}°C (热乎乎的，记得防晒补水哦！☀️)")
            else:
                cute_message_parts.append(f"🌡️ 温度：{temp_str}°C (暖暖的还是凉凉的？)")

            cute_message_parts.append(f"🍃 风儿：{direct} {power}级 (记得带伞或帽子哦！)")

            # 今日湿度（从daily接口获取）
            daily_results = daily_data.get('results', None)
            daily_info = None
            if isinstance(daily_results, list) and len(daily_results) > 0:
                daily_info = daily_results[0]
            elif isinstance(daily_results, dict):
                daily_info = daily_results
            else:
                daily_info = {}
            daily_weather = []
            if isinstance(daily_info, dict):
                daily_weather = daily_info.get('daily', [])
            elif isinstance(daily_info, list):
                daily_weather = daily_info
            today_humidity = None
            if isinstance(daily_weather, list) and len(daily_weather) >= 1:
                first_day = daily_weather[0]
                if isinstance(first_day, dict):
                    today_humidity = first_day.get('humidity', None)
            if today_humidity is not None:
                cute_message_parts.append(f"💧 今天的湿度：{today_humidity}% (注意补水哦~)")
            else:
                cute_message_parts.append(f"💧 今天的湿度：未知 (空气湿润吗？)")

            # 生活指数
            life_results = life_data.get('results', None)
            life_info = None
            if isinstance(life_results, list) and len(life_results) > 0:
                life_info = life_results[0]
            elif isinstance(life_results, dict):
                life_info = life_results
            else:
                life_info = {}


            suggestion = {}
            if isinstance(life_info, dict):
                sug = life_info.get('suggestion', {})
                if isinstance(sug, dict):
                    suggestion = sug
                elif isinstance(sug, list) and len(sug) > 0:
                    # 只取第一天的 suggestion
                    first_sug = sug[0]
                    if isinstance(first_sug, dict):
                        suggestion = first_sug

            # 紫外线
            uv = suggestion.get('uv', {}) if isinstance(suggestion, dict) else {}
            uv_brief = uv.get('brief', '未知') if isinstance(uv, dict) else '未知'
            uv_details = uv.get('details', '') if isinstance(uv, dict) else ''

            # 空气污染扩散条件
            air_pollution = suggestion.get('air_pollution', {}) if isinstance(suggestion, dict) else {}
            air_pollution_brief = air_pollution.get('brief', '未知') if isinstance(air_pollution, dict) else '未知'
            air_pollution_details = air_pollution.get('details', '') if isinstance(air_pollution, dict) else ''

            # 舒适度
            comfort = suggestion.get('comfort', {}) if isinstance(suggestion, dict) else {}
            comfort_brief = comfort.get('brief', '未知') if isinstance(comfort, dict) else '未知'
            comfort_details = comfort.get('details', '') if isinstance(comfort, dict) else ''

            # 雨伞
            umbrella = suggestion.get('umbrella', {}) if isinstance(suggestion, dict) else {}
            umbrella_brief = umbrella.get('brief', '未知') if isinstance(umbrella, dict) else '未知'
            umbrella_details = umbrella.get('details', '') if isinstance(umbrella, dict) else ''

            # 拼接生活指数信息（全部未知则不显示）
            if not (uv_brief == air_pollution_brief == comfort_brief == umbrella_brief == '未知'):
                cute_message_parts.append("\n【生活指数小贴士】")
                cute_message_parts.append(f"🌞 紫外线：{uv_brief}，{uv_details}")
                cute_message_parts.append(f"🌫️ 空气污染扩散：{air_pollution_brief}，{air_pollution_details}")
                cute_message_parts.append(f"😊 舒适度：{comfort_brief}，{comfort_details}")
                cute_message_parts.append(f"☔ 雨伞建议：{umbrella_brief}，{umbrella_details}")

            # 解析未来3天天气数据
            # 明天
            if isinstance(daily_weather, list) and len(daily_weather) >= 2:
                next_day = daily_weather[1]
                if isinstance(next_day, dict):
                    next_day_weather = next_day.get('text_day', '未知')
                    next_day_temp = f"{next_day.get('low', '??')}~{next_day.get('high', '??')}℃"
                    cute_message_parts.append(f"☀️ 明天会是 {next_day_weather}, 温度在 {next_day_temp} 之间哦! (｡･ω･｡)ﾉ♡")
                else:
                    cute_message_parts.append("☀️ 明天的天气有点神秘，暂时看不到呢~")
            else:
                cute_message_parts.append("☀️ 明天的天气有点神秘，暂时看不到呢~")

            # 后天
            if isinstance(daily_weather, list) and len(daily_weather) >= 3:
                day_after_next = daily_weather[2]
                if isinstance(day_after_next, dict):
                    day_after_next_weather = day_after_next.get('text_day', '未知')
                    day_after_next_temp = f"{day_after_next.get('low', '??')}~{day_after_next.get('high', '??')}℃"
                    cute_message_parts.append(f"🌤️ 后天呢, {day_after_next_weather}, 温度大约 {day_after_next_temp}~ (＾▽＾)")
                else:
                    cute_message_parts.append("🌤️ 后天的天气也有点神秘，暂时看不到呢~")
            else:
                cute_message_parts.append("🌤️ 后天的天气也有点神秘，暂时看不到呢~")

            cute_message = "\n".join(cute_message_parts)
            await actions.send(group_id=event.group_id, message=Manager.Message(
                Segments.Reply(event.message_id), 
                Segments.Text(cute_message)
            ))
        else:
            await actions.send(group_id=event.group_id, message=Manager.Message(
                Segments.Reply(event.message_id), 
                Segments.Text("哎呀！天气预报卫星好像开小差了，稍后再试试吧！(｡•́︿•̀｡)")
            ))
    except requests.exceptions.Timeout:
        await actions.send(group_id=event.group_id, message=Manager.Message(
            Segments.Reply(event.message_id), 
            Segments.Text("网络有点慢，天气信息飞不过来啦~稍后再试哦！")
        ))
    except Exception as e:
        await actions.send(group_id=event.group_id, message=Manager.Message(
            Segments.Reply(event.message_id), 
            Segments.Text(f"程序兽遇到了一点小麻烦：{e}，快叫主人来看看！QAQ")
        ))
    return True

# 插件加载时打印信息
print("[天气查询插件] 已成功加载")
print(f"数据存储路径: {WEATHER_DATA_DIR}")
print(f"触发关键词: {TRIGGHT_KEYWORD}")
print("功能: 查询城市天气信息并记录用户使用次数")
