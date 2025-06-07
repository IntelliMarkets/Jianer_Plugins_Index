import aiohttp
from Hyper import Configurator

Configurator.cm = Configurator.ConfigManager(Configurator.Config(file="config.json").load_from_file())

TRIGGHT_KEYWORD = "转码 "
HELP_MESSAGE = f"{Configurator.cm.get_cfg().others['reminder']}转码 url/文本 —> 生成二维码图片"

HEADERS = {
    'User-Agent': 'xiaoxiaoapi/1.0.0 (https://xxapi.cn)'
}

API_URL = "https://v2.xxapi.cn/api/qrcode"

async def on_message(event, actions, Manager, Segments):
    msg = str(event.message).strip()
    reminder = Configurator.cm.get_cfg().others["reminder"]
    prefix = f"{reminder}{TRIGGHT_KEYWORD}"
    if not msg.startswith(prefix):
        return
    text = msg[len(prefix):].strip()
    if not text:
        await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("请在'转码'后输入需要生成二维码的内容，如网址或文本~")))
        return True
    params = {"text": text}
    try:
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(API_URL, params=params) as resp:
                data = await resp.json()
                if str(data.get('code')) == '200' and 'data' in data:
                    img_url = data['data']
                    await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Image(img_url)))
                else:
                    await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("二维码生成失败，请稍后再试~")))
    except Exception as e:
        await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(f"请求出错：{e}")))
    return True
