import aiohttp
from Hyper import Configurator
Configurator.cm = Configurator.ConfigManager(Configurator.Config(file="config.json").load_from_file())

TRIGGHT_KEYWORD = "jytkt"
HELP_MESSAGE = f"{Configurator.cm.get_cfg().others['reminder']}jytkt —> 获取一个随机的jy姜头口头图片"

async def on_message(event, actions, Manager, Segments, bot_name):
    try:

        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("https://api.jiangtokoto.cn/memes/random") as response:
                if response.status == 200:
                    await actions.send(
                        group_id=event.group_id,
                        user_id=event.user_id,
                        message=Manager.Message([
                            Segments.Image(file="https://api.jiangtokoto.cn/memes/random")
                        ])
                    )
                else:
                    await actions.send(
                        group_id=event.group_id,
                        user_id=event.user_id,
                        message=Manager.Message(Segments.Text(f"API请求失败，状态码: {response.status} - {bot_name}"))
                    )
            
    except aiohttp.ClientError as e:
        await actions.send(
            group_id=event.group_id,
            user_id=event.user_id,
            message=Manager.Message(Segments.Text(f"姜头口头API请求出错: {str(e)} - {bot_name}"))
        )
    except Exception as e:
        await actions.send(
            group_id=event.group_id,
            user_id=event.user_id,
            message=Manager.Message(Segments.Text(f"获取姜头口头图片时发生未知错误: {str(e)} - {bot_name}"))
        )

    return True
