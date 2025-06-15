from datetime import datetime
import requests, os
from Hyper import Configurator
Configurator.cm = Configurator.ConfigManager(Configurator.Config(file="config.json").load_from_file())
from Tools.capture_screenshot import capture_full_page_screenshot

TRIGGHT_KEYWORD = "Any"
HELP_MESSAGE = f'''{Configurator.cm.get_cfg().others["reminder"]}issue (编号)/latest —> 返回仓库指定编号/最新的issue
       {Configurator.cm.get_cfg().others["reminder"]}commit (编号)/latest —> 返回仓库指定编号/最新的commit'''
       
OWNER: str = "SRInternet-Studio"
REPO: str = "Jianer_QQ_bot"
TOKEN: str = ""
       
async def on_message(event, actions, Manager, Segments, Events, reminder):
    global OWNER, REPO
    if isinstance(event, Events.GroupMessageEvent) or isinstance(event, Events.PrivateMessageEvent):
        if f"{reminder}issue" in str(event.message):
            msg = str(event.message).split(" ")
            if f"{reminder}issue" != msg[0] or len(msg) < 2:
                return False
            
            selfID = await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(f"请等待，正在获取 issue 内容……")))
            image = ""
            match msg[1]:
                case "latest":
                    image = await capture_full_page_screenshot(await get_latest_github_urls("issues?state=all&sort=created&direction=desc&"), "repo_content")
                case _:
                    image = await capture_full_page_screenshot(f"https://github.com/{OWNER}/{REPO}/issues/{msg[1]}", "repo_content")
                    
            await actions.del_message(selfID.data.message_id)
            if image and os.path.isfile(image):
                await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Reply(event.message_id), Segments.Image(image)))
                os.remove(image)
            else:
                await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Reply(event.message_id), Segments.Text('''无法获取指定 issue 的内容，可能是因为：
    1. 指定的 issue 编号不存在
    2. 设定的 REPO 和 OWNER 有误
    3. 设定的仓库里没有任何 issue
    4. 网络问题导致无法连接至 Github
    5. 内容请求次数过多，被 API 阻止''')))
            return True
        
        elif f"{reminder}commit" in str(event.message):
            msg = str(event.message).split(" ")
            if f"{reminder}commit" != msg[0] or len(msg) < 2:
                return False
            
            selfID = await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(f"请等待，正在获取 commit 内容……")))
            image = ""
            match msg[1]:
                case "latest":
                    image = await capture_full_page_screenshot(await get_latest_github_urls("commits?"), "repo_content")
                case _:
                    image = await capture_full_page_screenshot(f"https://github.com/{OWNER}/{REPO}/commit/{msg[1]}", "repo_content", max_height=6080)
                    
            await actions.del_message(selfID.data.message_id)
            if image and os.path.isfile(image):
                await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Reply(event.message_id), Segments.Image(image)))
                os.remove(image)
            else:
                await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Reply(event.message_id), Segments.Text('''无法获取指定 commit 的内容，可能是因为：
    1. 指定的 commit 编号不存在
    2. 设定的 REPO 和 OWNER 有误
    3. 设定的仓库里没有任何 commit
    4. 网络问题导致无法连接至 Github
    5. 内容请求次数过多，被 API 阻止''')))
            return True
        else:
            return False

async def get_latest_github_urls(target: str) -> str:
    global OWNER, REPO, TOKEN
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {TOKEN}" if TOKEN else None
    }

    try:
        urls = []
        if "issues" in target:
            url = f"https://api.github.com/repos/{OWNER}/{REPO}/{target}per_page=1"
            response = requests.get(url, headers=headers)
            latest = response.json()[0] if response.json() else None
            issue_number = latest["number"]
            urls.append(f"https://github.com/{OWNER}/{REPO}/issues/{issue_number}")
        elif "commit" in target:
            urls.append(await get_latest_commit(OWNER, REPO, TOKEN))
        else:
            urls.append("")
        
        return urls[0]
    except:
        return ""

async def get_latest_commit(owner, repo, token=None):
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}" if token else None
    }

    branches_url = f"https://api.github.com/repos/{owner}/{repo}/branches"
    branches = requests.get(branches_url, headers=headers).json()
    
    all_commits = []
    for branch in branches:
        commit_url = f"https://api.github.com/repos/{owner}/{repo}/commits?sha={branch['name']}&per_page=1"
        commit_data = requests.get(commit_url, headers=headers).json()
        if commit_data:
            commit = commit_data[0]
            commit["branch"] = branch["name"]
            all_commits.append(commit)
    
    if not all_commits:
        return ""
        
    latest_commit = max(
        all_commits,
        key=lambda x: datetime.strptime(
            x["commit"]["committer"]["date"],
            "%Y-%m-%dT%H:%M:%SZ"
        )
    )
    
    commit_info =  {
        "sha": latest_commit["sha"],
        "branch": latest_commit["branch"],
        "message": latest_commit["commit"]["message"],
        "url": latest_commit["html_url"]
    }
    
    return commit_info["url"]