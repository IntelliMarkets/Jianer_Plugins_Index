import json
from typing import List
import os
global filepath
filepath=os.path.abspath("./plugins/GithubWebhook/gh_group_send.json")
def load_group():
    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)
        print(f"文件 {filepath} 不存在，已创建新文件。")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_group(data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def add_group(repo_name, send_group):
    data = load_group()
    if repo_name not in data:
        data[repo_name] = []
    if send_group not in data[repo_name]:
        data[repo_name].append(send_group)
    save_group(data)
    print(f"已将群 {send_group} 添加到仓库 {repo_name}")

def remove_group(repo_name, send_group):
    data = load_group()
    if repo_name in data and send_group in data[repo_name]:
        data[repo_name].remove(send_group)
        save_group(data)
        print(f"已将群 {send_group} 从仓库 {repo_name} 中移除")
    else:
        print(f"仓库 {repo_name} 未关联群 {send_group}")

def get_groups(repo_name: str) -> List[str]:
    data = load_group()
    if repo_name in data:
        return data[repo_name]
    else:
        return []
def get_repo_info(repo_name: str) -> str:
    """获取仓库关联信息，并格式化输出"""
    repo1_groups = get_groups(repo_name)
    if repo1_groups:
        formatted_groups = ", ".join(repo1_groups)
        return f"仓库名: {repo_name} 已关联的群: {formatted_groups}"
    else:
        if repo_name not in load_group(filepath):
            return f"此仓库: {repo_name}未定义发送群号/或此仓库无记录，丢弃"
        else:
            return f"仓库名: {repo_name} 未关联任何 QQ 群"

async def send_message_groups(repo_name: str, message,actions):
    send1_groups = get_groups(repo_name)
    if send1_groups:
        for group_id in send1_groups:
            try:
                await actions.send(group_id=int(group_id), message=message)
                print(f"消息已发送至群: {group_id}")
            except Exception as e:
                print(f"向群 {group_id} 发送消息失败: {e}")
    else:
        if repo_name not in load_group(filepath):
            print(f"此仓库: {repo_name}未定义发送群号/或此仓库无记录，丢弃")
        else:
            print(f"仓库 {repo_name} 未关联任何群")
# 示例用法：
# add_qq_group("repo1", "123456")
# add_qq_group("repo1", "654321")
# add_qq_group("repo2", "987654")
# remove_qq_group("repo1", "123456")
# print(get_qq_groups("repo1"))  # 输出: ['654321']
# print(get_qq_groups("repo2"))  # 输出: ['987654']
# print(get_qq_groups("repo3"))  # 输出: []