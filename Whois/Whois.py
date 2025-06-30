import requests
from Hyper import Configurator, Listener

Configurator.cm = Configurator.ConfigManager(Configurator.Config(file="config.json").load_from_file())

reminder = Configurator.cm.get_cfg().others["reminder"]
bot_name = Configurator.cm.get_cfg().others["bot_name"]
TRIGGHT_KEYWORD = "whois"
HELP_MESSAGE = f"{reminder}whois 域名 (必填) —> {bot_name}查询whois"

def get_domain_info(domain):
    url = f"https://v2.xxapi.cn/api/whois?domain={domain}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        outer_data = data.get("data")
        if outer_data:
            domain_data = outer_data.get("data")
            if domain_data:
                dns_servers = domain_data.get("dns_serve")
                if dns_servers:
                    return {
                        "域名名称": domain_data.get("domain_name"),
                        "域名NS服务器": dns_servers,
                        "注册时间": domain_data.get("registration_time", "没有数据"),
                        "过期时间": domain_data.get("expiration_time", "没有数据"),
                        "注册人": domain_data.get("registrant", "没有数据"),
                        "注册人邮箱": domain_data.get("registrant_contact_email", "没有数据"),
                        "注册商": domain_data.get("registrar_url", "没有数据"),
                        "域名状态": domain_data.get("domain_status", "没有数据")
                    }
                else:
                    return f"{domain_data.get('domain_name', '该域名')} 尚未注册！"
            else:
                return "未找到域名信息"
        else:
            return "未找到域名信息"

    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        return "网络请求失败"
    except Exception as e:
        print(f"发生未知错误: {e}")
        return "查询失败"

async def on_message(event, actions: Listener.Actions, Manager, Segments, order, bot_name, bot_name_en, ONE_SLOGAN):
    Toset221 = order[order.find("whois ") + len("whois "):].strip()
    if not Toset221:
        await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("请输入域名")))
        return

    domain_info = get_domain_info(Toset221)
    if isinstance(domain_info, dict):
        message = f"{domain_info['域名名称']}域名信息\n"
        message += "域名NS服务器:" + "\n".join(domain_info['域名NS服务器']) + "\n"
        message += f"注册时间:{domain_info['注册时间']}\n"
        message += f"过期时间:{domain_info['过期时间']}\n"
        message += f"注册人:{domain_info['注册人']}\n"
        message += f"注册人邮箱:{domain_info['注册人邮箱']}\n"
        message += f"注册商:{domain_info['注册商']}\n"
        message += f"域名状态:{domain_info['域名状态']}"
        await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(message)))
        print(message)

    elif isinstance(domain_info, str):
        print(domain_info)
        await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(domain_info)))
    return True