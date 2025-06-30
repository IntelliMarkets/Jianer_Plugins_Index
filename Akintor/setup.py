from plugins.Akintor.Akirequest import Akinator
import asyncio
import os
from plugins.Akintor.akianswer import *
from Hyper import Logger
from Hyper.Events import *
import datetime
import yaml
from Hyper import Configurator
Configurator.cm = Configurator.ConfigManager(Configurator.Config(file="config.json").load_from_file())
logger = Logger.Logger()
config = Configurator.cm.get_cfg()
logger.set_level(config.log_level)
user_akinator_states = {}
TRIGGHT_KEYWORD = "Any"
HELP_MESSAGE = f"{Configurator.cm.get_cfg().others["reminder"]}猜人 —> 启动 Akintor 游戏"
akisendmode = "image"
async def start_akinator(language="jp", max_retries=3):
    for attempt in range(max_retries):
        try:
            akinator = Akinator(lang=language)
            await asyncio.to_thread(akinator.start_game)
            if akinator.question:
                return akinator, akinator.question
            else:
                logger.log(f"AKI已游戏启动但问题获取失败 开始重试 ({attempt + 1}/{max_retries})", level=levels.WARNING)
        except Exception as e:
            logger.log(f"启动AKI失败 开始重试 原因:{e} ({attempt + 1}/{max_retries})", level=levels.WARNING)
            await asyncio.sleep(1)
    logger.log(f"无法启动AKI游戏，达到最大重试次数({max_retries}/{max_retries})", level=levels.CRITICAL)
    return None, None

async def handle_akinator(event, actions, Manager, Segments,reminder):
    user_id = event.user_id
    group_id = event.group_id
    user_message = str(event.message).lower()

    if user_message == f"{reminder}猜人":
        if user_id in user_akinator_states:
            await actions.send(group_id=group_id, message=Manager.Message(Segments.Text("您已在游戏中。请回答问题或输入 'q' 退出。")))
            return

        akinator_obj, question = await start_akinator()
        if akinator_obj and question:
            user_akinator_states[user_id] = {"akinator": akinator_obj, "question": question, "message_id": None, "last_activity": datetime.datetime.now()}
            try:
                if akisendmode == "text":
                    raise
                image_path = await akiwt114(akinator_obj.step, question, akinator_obj.akitude)
                if image_path:
                    selfID = await actions.send(group_id=group_id, message=Manager.Message(Segments.At(user_id), Segments.Image(image_path)))
                    user_akinator_states[user_id]["message_id"] = selfID.data.message_id
                    os.remove(image_path)
                else:
                    raise
            except Exception:
                await actions.send(group_id=group_id, message=Manager.Message(Segments.At(user_id), Segments.Text(f"{akinator_obj.step}.{akinator_obj.question}\n是(y)\n不是(n)\n我不知道(idk)\n或许是(p)\n或许不是(pn)\n上一题(b)\n退出(exit)")))
        else:
            await actions.send(group_id=group_id, message=Manager.Message(Segments.Text("Akinator 启动失败，请稍后重试。")))
    elif user_id in user_akinator_states:
        timeout = 30
        now = datetime.datetime.now()
        last_activity = user_akinator_states[user_id].get("last_activity")

        if last_activity and (now - last_activity).total_seconds() > timeout:
            del user_akinator_states[user_id]
            await actions.send(group_id=group_id, message=Manager.Message(Segments.At(user_id), Segments.Text("游戏超时，已自动结束。")))
            return

        user_akinator_states[user_id]["last_activity"] = now

        akinator_data = user_akinator_states[user_id]
        akinator_obj = akinator_data["akinator"]
        question = akinator_data["question"]
        message_id = akinator_data["message_id"]

        if user_message == "q":
            del user_akinator_states[user_id]
            await actions.send(group_id=group_id, message=Manager.Message(Segments.Text("已退出 Akinator 游戏。")))
            return

        elif user_message == "b":
            await asyncio.to_thread(akinator_obj.go_back)
            if akinator_obj.question:
                if message_id:
                    await actions.del_message(message_id=message_id)
                try:
                    if akisendmode == "text":
                        raise
                    image_path = await akiwt114(akinator_obj.step, akinator_obj.question, akinator_obj.akitude)
                    if image_path:
                        selfID = await actions.send(group_id=group_id, message=Manager.Message(Segments.At(user_id), Segments.Image(image_path)))
                        user_akinator_states[user_id]["message_id"] = selfID.data.message_id
                        os.remove(image_path)
                    else:
                        raise
                except Exception:
                    await actions.send(group_id=group_id, message=Manager.Message(Segments.At(user_id), Segments.Text(f"{akinator_obj.step}.{akinator_obj.question}\n是(y)\n不是(n)\n我不知道(idk)\n或许是(p)\n或许不是(pn)\n上一题(b)\n退出(exit)")))
            else:
                await actions.send(group_id=group_id, message=Manager.Message(Segments.Text("返回失败，请退出，然后重试")))

        elif user_message in ["y", "n", "idk", "p", "pn"]:
            await asyncio.to_thread(akinator_obj.post_answer, user_message)
            if akinator_obj.progression >= 80 and akinator_obj.name != None:
                message = f"我猜是 {akinator_obj.name}! \n出自: {akinator_obj.description} \n已自动结束游戏！"
                try:
                    if akinator_obj.photo:
                        if message_id:
                            await actions.del_message(message_id=message_id)
                        if akisendmode == "text":
                            raise
                        image114666 = await akianswer114(akinator_obj.name, akinator_obj.description, akinator_obj.photo)
                        await actions.send(group_id=group_id, message=Manager.Message(Segments.At(user_id), Segments.Text("我猜:"), Segments.Image(image114666), Segments.Text("已自动结束游戏！")))
                        os.remove(image114666)
                    else:
                        if message_id:
                            await actions.del_message(message_id=message_id)
                        await actions.send(group_id=group_id, message=Manager.Message(Segments.At(user_id), Segments.Text(message)))
                except Exception:
                        await actions.send(group_id=group_id, message=Manager.Message(Segments.At(user_id), Segments.Image(akinator_obj.photo),Segments.Text(message)))
                del user_akinator_states[user_id]
                return
            else:
                if akinator_obj.question:
                    if message_id:
                        await actions.del_message(message_id=message_id)
                    try:
                        if akisendmode == "text":
                            raise
                        image_path = await akiwt114(akinator_obj.step, akinator_obj.question, akinator_obj.akitude)
                        if image_path:
                            selfID = await actions.send(group_id=group_id, message=Manager.Message(Segments.At(user_id), Segments.Image(image_path)))
                            user_akinator_states[user_id]["message_id"] = selfID.data.message_id
                            os.remove(image_path)
                        else:
                            raise
                    except Exception:
                        await actions.send(group_id=group_id, message=Manager.Message(Segments.At(user_id), Segments.Text(f"{akinator_obj.step}.{akinator_obj.question}\n是(y)\n不是(n)\n我不知道(idk)\n或许是(p)\n或许不是(pn)\n上一题(b)\n退出(exit)")))
                else:
                    message = f"我猜是 {akinator_obj.name}! \n出自: {akinator_obj.description}  \n已自动结束游戏！"
                    if akinator_obj.photo:
                        if message_id:
                            await actions.del_message(message_id=message_id)
                        try:
                            if akisendmode == "text":
                                raise
                            image114666 = await akianswer114(akinator_obj.name, akinator_obj.description, akinator_obj.photo)
                            await actions.send(group_id=group_id, message=Manager.Message(Segments.At(user_id), Segments.Text("我猜:"), Segments.Image(image114666), Segments.Text("已自动结束游戏！")))
                        except Exception:
                            await actions.send(group_id=group_id, message=Manager.Message(Segments.At(user_id), Segments.Text(message)))
                    else:
                        if message_id:
                            await actions.del_message(message_id=message_id)
                        await actions.send(group_id=group_id, message=Manager.Message(Segments.At(user_id), Segments.Text(message)))
                    del user_akinator_states[user_id]
                    return


async def on_message(event, Events, actions, Manager, Segments, reminder):
        global akisendmode
        with open(os.path.abspath("./plugins/Akintor/config.yaml"), 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        akisendmode = data.get('sendmode', "image")
        if not isinstance(event, Events.GroupMessageEvent):
            return False
        if str(event.message) == f"{reminder}更改AKI发送状态":
            if akisendmode == "image":
                akisendmode = "text"
                await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(f"已切换aki发送模式为:{akisendmode}")))
            else:
                akisendmode = "image"
                await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(f"已切换aki发送模式为:{akisendmode}")))
            data['sendmode'] = str(akisendmode)
            with open(os.path.abspath("./plugins/Akintor/config.yaml"), 'w', encoding='utf-8') as f:
                yaml.safe_dump(data, f, indent=4)
            return True
        if str(event.message) == f"{reminder}猜人" or event.user_id in user_akinator_states:
            await handle_akinator(event, actions, Manager, Segments,reminder)
            return True