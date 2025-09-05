# -*- coding: utf-8 -*-

import aiohttp
import base64
import io
import re
from PIL import Image

TRIGGHT_KEYWORD = "run"
HELP_MESSAGE = "/run [QQ号/@用户] [背景颜色(可选)] —> 生成摸摸头GIF，默认背景为透明"

async def on_message(event, actions, Manager, Segments, order, reminder, bot_name):
    # 检查是否包含触发关键词
    if not (order.startswith("run") or order.startswith("/run")):
        return False
    
    # 解析参数
    parts = order.split()
    if len(parts) < 2:
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(Segments.Text(f"格式错误！请使用：{reminder}run [QQ号/@用户] [背景颜色(可选)]"))
        )
        return True
    
    # 获取QQ号或@的用户
    target = parts[1]
    qq_number = None
    
    # 判断是QQ号还是@的用户
    if target.isdigit():
        # 纯数字，直接作为QQ号
        qq_number = target
    elif target.startswith('@'):
        # @用户格式，提取QQ号
        # 尝试从@格式中提取QQ号（格式可能是 @用户 或 @123456）
        if len(parts) >= 2:
            # 如果是@后面直接跟数字，可能是QQ号
            match = re.search(r'@(\d+)', target)
            if match:
                qq_number = match.group(1)
            else:
                # 如果不是数字，尝试从消息中的@列表获取
                if hasattr(event, 'message') and hasattr(event.message, 'at_list'):
                    at_list = event.message.at_list
                    if at_list and len(at_list) > 0:
                        qq_number = str(at_list[0].qq)
    else:
        # 尝试从消息中的@列表获取
        if hasattr(event, 'message') and hasattr(event.message, 'at_list'):
            at_list = event.message.at_list
            if at_list and len(at_list) > 0:
                qq_number = str(at_list[0].qq)
    
    # 如果还是没有获取到QQ号，报错
    if not qq_number:
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(Segments.Text("请提供有效的QQ号或@一个用户！"))
        )
        return True
    
    # 获取背景颜色（可选）
    bg_color = "transparent"  # 默认透明背景
    if len(parts) >= 3:
        # 跳过@的用户参数，取下一个参数作为背景颜色
        bg_color = parts[2]
    elif len(parts) == 2 and target.startswith('@') and len(parts) > 2:
        # 处理 @用户 颜色 的情况
        bg_color = parts[2]
    
    # 发送等待消息
    wait_msg = await actions.send(
        group_id=event.group_id,
        message=Manager.Message(Segments.Text(f"{bot_name}正在生成摸摸头GIF，请稍候..."))
    )
    
    # 调用API生成GIF
    try:
        api_url = f"http://uapis.cn/api/v1/image/motou?qq={qq_number}&bg_color={bg_color}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    # 获取GIF数据
                    gif_data = await response.read()
                    
                    # 转换为base64
                    gif_base64 = base64.b64encode(gif_data).decode('utf-8')
                    
                    # 删除等待消息
                    await actions.del_message(wait_msg.data.message_id)
                    
                    # 发送GIF
                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(
                            Segments.Image(f"base64://{gif_base64}")
                        )
                    )
                elif response.status == 400:
                    error_data = await response.json()
                    await actions.del_message(wait_msg.data.message_id)
                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(Segments.Text(f"❌ 请求参数错误：{error_data.get('error', '未知错误')}"))
                    )
                elif response.status == 500:
                    error_data = await response.json()
                    await actions.del_message(wait_msg.data.message_id)
                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(Segments.Text(f"❌ 服务器错误：{error_data.get('error', '未知错误')}"))
                    )
                else:
                    await actions.del_message(wait_msg.data.message_id)
                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(Segments.Text(f"❌ 未知错误，HTTP状态码：{response.status}"))
                    )
    
    except aiohttp.ClientError as e:
        await actions.del_message(wait_msg.data.message_id)
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(Segments.Text(f"❌ 网络请求失败：{str(e)}"))
        )
    except Exception as e:
        await actions.del_message(wait_msg.data.message_id)
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(Segments.Text(f"❌ 生成摸摸头GIF时发生未知错误：{str(e)}"))
        )
    
    return True