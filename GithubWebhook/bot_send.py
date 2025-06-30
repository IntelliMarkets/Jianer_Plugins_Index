import os
from flask import Flask, jsonify, request,abort
import json
import hmac
import hashlib
from plugins.GithubWebhook.ghts import ghtz
from Hyper import Configurator
from plugins.GithubWebhook.bot_group_send import *
Configurator.cm = Configurator.ConfigManager(Configurator.Config(file="config.json").load_from_file())
webhook_app = Flask(__name__)
# GITHUB_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET')#此GH密钥配置在环境变量中,如懒的配置变量，可将此条 os.environ.get('GITHUB_WEBHOOK_SECRET')改为"您要设置的API密钥"
GITHUB_SECRET = "114514"#此处可直接设置

@webhook_app.route('/', methods=['GET'])
def index():
        return "GitHub Webhook 监听已运行！"
global Manager
global Segments
def run_webhook_app(segments, manager, actions_param):
    global Manager, Segments, actions
    Manager = manager
    Segments = segments
    actions = actions_param
    print("启动 GitHub Webhook 监听，端口 2525...")
    webhook_app.run(host='0.0.0.0', port=2525, debug=False)
@webhook_app.route('/webhook', methods=['POST'])
async def github_webhook():
            global actions
            event_type = request.headers.get('X-GitHub-Event')
            payload = request.json
            if not payload:
                print("Received empty or invalid payload.")
                return jsonify({"message": "Invalid payload"}), 400
            signature = request.headers.get('X-Hub-Signature-256')
            if signature is None:
                abort(403, description="X-Hub-Signature-256 header missing") # 返回 403
            mac = hmac.new(GITHUB_SECRET.encode(), msg=request.data, digestmod=hashlib.sha256)
            calculated_signature = f"sha256={mac.hexdigest()}"

            # 验证Github签名
            if not hmac.compare_digest(signature, calculated_signature):
                abort(403, description="Invalid signature") # 返回 403
            repo_name = payload.get('repository', {}).get('full_name', 'N/A')
            repo_avatar_url = payload.get('repository', {}).get('owner', {}).get('avatar_url', 'N/A')

            print("="*50)
            print(f"收到 GitHub 事件: {event_type}")
            print(f"仓库: {repo_name}")
            print(f"仓库图标 URL: {repo_avatar_url}")
            print("-" * 50)
            message = ""
            if event_type == 'push':
                ref = payload.get('ref')
                commits = payload.get('commits', [])
                message += f"  分支: {ref}\n"
                message += f"  提交数量: {len(commits)}\n"
                for commit in commits:
                    commit_id = commit.get('id', 'N/A')[:7]
                    author = commit.get('author', {}).get('name', 'N/A')
                    commit_message = commit.get('message', '').strip()
                    message += f"    - [{commit_id}] {commit_message} (作者: {author})\n"

            elif event_type == 'issues':
                action = payload.get('action')
                issue = payload.get('issue', {})
                issue_title = issue.get('title', 'N/A')
                issue_number = issue.get('number', 'N/A')
                issue_user = issue.get('user', {}).get('login', 'N/A')
                issue_body = issue.get('body', '').strip()
                message += f"  操作: {action}\n"
                message += f"  Issue #{issue_number}: {issue_title}\n"
                message += f"  由 {issue_user} 创建/操作\n"
                if issue_body:
                    message += f"  内容: {issue_body[:200]}...\n" if len(issue_body) > 200 else f"  内容: {issue_body}\n"

            elif event_type == 'issue_comment':
                action = payload.get('action')
                issue = payload.get('issue', {})
                comment = payload.get('comment', {})
                issue_title = issue.get('title', 'N/A')
                issue_number = issue.get('number', 'N/A')
                comment_user = comment.get('user', {}).get('login', 'N/A')
                comment_body = comment.get('body', '').strip()
                message += f"  操作: {action}\n"
                message += f"  对 Issue #{issue_number} ({issue_title}) 的评论\n"
                message += f"  评论者: {comment_user}\n"
                if comment_body:
                    message += f"  评论内容: {comment_body[:200]}...\n" if len(comment_body) > 200 else f"  评论内容: {comment_body}\n"

            elif event_type == 'pull_request':
                action = payload.get('action')
                pr = payload.get('pull_request', {})
                pr_title = pr.get('title', 'N/A')
                pr_number = pr.get('number', 'N/A')
                pr_user = pr.get('user', {}).get('login', 'N/A')
                pr_state = pr.get('state', 'N/A')
                message += f"  操作: {action}\n"
                message += f"  Pull Request #{pr_number}: {pr_title}\n"
                message += f"  状态: {pr_state}\n"
                message += f"  由 {pr_user} 创建/操作\n"
            # elif event_type == 'create':
            #     ref_type = payload.get('ref_type')
            #     ref = payload.get('ref')
            #     master_branch = payload.get('master_branch')
            #     description = payload.get('description')
            #     message += f"  类型: {ref_type}\n"
            #     message += f"  名称: {ref}\n"
            #     message += f"  主分支: {master_branch}\n"
            #     message += f"  描述: {description}\n"

            # elif event_type == 'delete':
            #     ref_type = payload.get('ref_type')
            #     ref = payload.get('ref')
            #     message += f"  类型: {ref_type}\n"
            #     message += f"  名称: {ref}\n"

            # elif event_type == 'star':
            #     action = payload.get('action')
            #     sender = payload.get('sender', {}).get('login', 'N/A')
            #     message += f"  操作: {action}\n"
            #     message += f"  用户: {sender}\n"

            else:
                message += f"  未处理的事件类型: {event_type}\n"
                message += f"  完整消息: {json.dumps(payload, indent=2)}\n"
            if get_groups(repo_name) == []:
                print("此仓库未定义发送群号/或此仓库无记录，丢弃")
                return jsonify({"message": "repo Not Found"}), 403
            image666 = await ghtz(repo_avatar_url,repo_name,event_type,message)
            print(image666)
            message1145=Manager.Message(Segments.Image(image666))
            await send_message_groups(str(repo_name),message1145,actions)
            os.remove(image666)
            # 返回成功响应给 GitHub
            return jsonify({"message": "Webhook received successfully!"}), 200