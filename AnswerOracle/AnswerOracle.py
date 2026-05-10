# -*- coding: utf-8 -*-

import aiohttp
import json
from Hyper import Configurator

# 加载配置获取触发前缀
Configurator.cm = Configurator.ConfigManager(
    Configurator.Config(file="config.json").load_from_file()
)
reminder = Configurator.cm.get_cfg().others.get("reminder", "/")

TRIGGHT_KEYWORD = "答案之书"
HELP_MESSAGE = f"{reminder}答案之书 (问题) —> 向答案之书提问，获得神秘答案"

async def on_message(event, actions, Manager, Segments):
    """
    答案之书插件
    使用 API: https://uapis.cn/api/v1/answerbook/ask
    """
    # 获取用户消息
    user_message = str(event.message).strip()
    
    # 提取问题内容：去除触发前缀和关键词
    # 支持格式: "/答案之书 问题" 或 "/答案之书问题"
    if f"{reminder}答案之书" in user_message:
        # 提取问题部分
        question_part = user_message.replace(f"{reminder}答案之书", "", 1).strip()
        
        # 如果没有提供问题
        if not question_part:
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(
                    Segments.Reply(event.message_id),
                    Segments.Text(f"❓ 请告诉我你想问什么～\n例如：{reminder}答案之书 我今天会有好运吗？")
                )
            )
            return True
        
        # 调用答案之书 API
        try:
            async with aiohttp.ClientSession() as session:
                # 使用 GET 请求，参数需要 URL 编码
                api_url = "https://uapis.cn/api/v1/answerbook/ask"
                params = {"question": question_part}
                
                async with session.get(api_url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        question = data.get("question", question_part)
                        answer = data.get("answer", "命运正在思考中...")
                        
                        # 发送答案
                        result_text = f"📖 答案之书 🔮\n\n❓ {question}\n\n✨ 答案：{answer}"
                        await actions.send(
                            group_id=event.group_id,
                            message=Manager.Message(
                                Segments.Reply(event.message_id),
                                Segments.Text(result_text)
                            )
                        )
                    elif resp.status == 400:
                        error_data = await resp.json()
                        error_msg = error_data.get("message", "问题无效")
                        await actions.send(
                            group_id=event.group_id,
                            message=Manager.Message(
                                Segments.Reply(event.message_id),
                                Segments.Text(f"❌ 提问失败：{error_msg}\n请换个问题再试试吧～")
                            )
                        )
                    else:
                        await actions.send(
                            group_id=event.group_id,
                            message=Manager.Message(
                                Segments.Reply(event.message_id),
                                Segments.Text("❌ 答案之书暂时无法打开，请稍后再试～ 📖✨")
                            )
                        )
                        
        except aiohttp.ClientTimeout:
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(
                    Segments.Reply(event.message_id),
                    Segments.Text("⏰ 答案之书响应超时了，网络有点慢，再试一次吧～")
                )
            )
        except aiohttp.ClientError as e:
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(
                    Segments.Reply(event.message_id),
                    Segments.Text(f"🌐 网络开小差了，答案之书打不开～\n错误：{str(e)}")
                )
            )
        except Exception as e:
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(
                    Segments.Reply(event.message_id),
                    Segments.Text("📖 答案之书翻到了空白页，出了点小问题，稍后再试试吧～")
                )
            )
            print(f"答案之书插件错误: {e}")
        
        return True
    
    return False