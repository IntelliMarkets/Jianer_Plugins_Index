from Hyper import Logger,Listener
from Hyper.Events import *
import re
from Hyper import Configurator
from plugins.GithubWebhook.bot_group_send import *
from plugins.GithubWebhook.bot_send import run_webhook_app
Configurator.cm = Configurator.ConfigManager(Configurator.Config(file="config.json").load_from_file())
TRIGGHT_KEYWORD = "Any"
async def on_message(event, actions: Listener.Actions, Manager, Segments,reminder,Events):
    if isinstance(event, Events.HyperListenerStartNotify):
        print("触发gh启动事件")
        run_webhook_app(Segments,Manager,actions)
    elif isinstance(event, Events.PrivateMessageEvent):
        print("触发私聊gh")
        if f"{reminder}添加GH仓库关联 " in str(event.message):
            message_content = str(event.message)[str(event.message).find(f"{reminder}添加GH仓库关联 ") + len(f"{reminder}添加GH仓库关联 "):].strip()
            match = re.match(r"(\S+)\s+(\d+)", message_content)

            if match:
                repo_name = match.group(1)
                qq_group = match.group(2)
                add_group(repo_name, qq_group)
                await actions.send(user_id=event.user_id,message=Manager.Message(Segments.Text(f"已将仓库 {repo_name} 与群 {qq_group} 关联")))
            else:
                await actions.send(user_id=event.user_id,message=Manager.Message(Segments.Text(f"输入格式错误，请使用 {reminder}添加GH仓库关联 <仓库名> <群号>")))
            return True
        elif f"{reminder}删除GH仓库关联 " in str(event.message):
            message_content = str(event.message)[str(event.message).find(f"{reminder}删除GH仓库关联 ") + len(f"{reminder}删除GH仓库关联 "):].strip()
            match = re.match(r"(\S+)\s+(\d+)", message_content)

            if match:
                repo_name = match.group(1)
                qq_group = match.group(2)
                add_group(repo_name, qq_group)
                await actions.send(user_id=event.user_id,message=Manager.Message(Segments.Text(f"已将仓库 {repo_name} 与群 {qq_group} 取消关联")))
            else:
                await actions.send(user_id=event.user_id,message=Manager.Message(Segments.Text(f"输入格式错误，请使用 {reminder}删除GH仓库关联 <仓库名> <群号>")))
            return True
        elif f"{reminder}查看GH仓库关联 " in str(event.message) or f"{reminder}查看GH仓库关联 " == str(event.message):
            message_content = str(event.message)[str(event.message).find(f"{reminder}查看GH仓库关联 ") + len(f"{reminder}查看GH仓库关联 "):].strip()
            if message_content:  # 检查是否提供了仓库名
                repo_name = message_content
                repo_info = get_repo_info(repo_name, filepath)
                await actions.send(group_id=event.group_id,message=Manager.Message(Segments.Text(repo_info)))
            else: # 没有提供仓库名，则显示所有仓库的信息
                data = load_group()
                if data:
                    reply_message = ""
                    for repo_name in data:
                        repo_info = get_repo_info(repo_name, filepath)
                        reply_message += repo_info + "\n"
                    await actions.send(user_id=event.user_id,message=Manager.Message(Segments.Text(reply_message)))
                else:
                    await actions.send(user_id=event.user_id,message=Manager.Message(Segments.Text("目前没有任何仓库关联信息。")))
            return True
    elif f"{reminder}添加GH仓库关联 " in str(event.message):
        message_content = str(event.message)[str(event.message).find(f"{reminder}添加GH仓库关联 ") + len(f"{reminder}添加GH仓库关联 "):].strip()
        match = re.match(r"(\S+)\s+(\d+)", message_content)

        if match:
            repo_name = match.group(1)
            qq_group = match.group(2)
            add_group(repo_name, qq_group)
            await actions.send(group_id=event.group_id,message=Manager.Message(Segments.Text(f"已将仓库 {repo_name} 与群 {qq_group} 关联")))
        else:
            await actions.send(group_id=event.group_id,message=Manager.Message(Segments.Text(f"输入格式错误，请使用 {reminder}添加GH仓库关联 <仓库名> <群号>")))
        return True
    elif f"{reminder}删除GH仓库关联 " in str(event.message):
        message_content = str(event.message)[str(event.message).find(f"{reminder}删除GH仓库关联 ") + len(f"{reminder}删除GH仓库关联 "):].strip()
        match = re.match(r"(\S+)\s+(\d+)", message_content)

        if match:
            repo_name = match.group(1)
            qq_group = match.group(2)
            add_group(repo_name, qq_group)
            await actions.send(group_id=event.group_id,message=Manager.Message(Segments.Text(f"已将仓库 {repo_name} 与群 {qq_group} 取消关联")))
        else:
            await actions.send(group_id=event.group_id,message=Manager.Message(Segments.Text(f"输入格式错误，请使用 {reminder}删除GH仓库关联 <仓库名> <群号>")))
        return True
    elif f"{reminder}查看GH仓库关联 " in str(event.message) or f"{reminder}查看GH仓库关联" == str(event.message):
        message_content = str(event.message)[str(event.message).find(f"{reminder}查看GH仓库关联 ") + len(f"{reminder}查看GH仓库关联 "):].strip()
        if message_content:  # 检查是否提供了仓库名
            repo_name = message_content
            repo_info = get_repo_info(repo_name)
            await actions.send(group_id=event.group_id,message=Manager.Message(Segments.Text(repo_info)))
        else: # 没有提供仓库名，则显示所有仓库的信息
            data = load_group()
            if data:
                reply_message = ""
                for repo_name in data:
                    repo_info = get_repo_info(repo_name)
                    reply_message += repo_info + "\n"
                await actions.send(group_id=event.group_id,message=Manager.Message(Segments.Text(reply_message)))
            else:
                await actions.send(group_id=event.group_id,message=Manager.Message(Segments.Text("目前没有任何仓库关联信息。")))

            return True

    