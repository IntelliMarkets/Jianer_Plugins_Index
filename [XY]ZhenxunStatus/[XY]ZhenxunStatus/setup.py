import os
import asyncio
from datetime import datetime
import jinja2
from playwright.async_api import async_playwright
from Hyper import Configurator

Configurator.cm = Configurator.ConfigManager(Configurator.Config(file="config.json").load_from_file())
TRIGGHT_KEYWORD = "Any"
RES_DIR = os.path.join(os.path.dirname(__file__), "res")

def format_cpu_freq(val):
    try:
        val = float(val)
        if val > 1000:
            return f"{val/1000:.2f} GHz"
        return f"{val:.0f} MHz"
    except Exception:
        return str(val)

def auto_convert_unit(val):
    try:
        val = float(val)
        units = ["B", "KB", "MB", "GB", "TB"]
        idx = 0
        while val >= 1024 and idx < len(units) - 1:
            val /= 1024
            idx += 1
        if idx == 0:
            return f"{int(val)} {units[idx]}"
        return f"{val:.2f} {units[idx]}"
    except Exception:
        return str(val)

def get_css_content():
    css_path = os.path.join(RES_DIR, "index.css")
    with open(css_path, "r", encoding="utf-8") as f:
        return f.read()

def get_image_path(filename):
    return "file:///" + os.path.abspath(os.path.join(RES_DIR, filename)).replace("\\", "/")

async def render_status_image(status_data: dict, config) -> str:
    template_path = os.path.join(RES_DIR, "index.html.jinja")
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()
    css_content = get_css_content()
    template_content = template_content.replace(
        '<link rel="stylesheet" href="/res/index.css" />',
        f'<style>{{{{ css_content }}}}</style>'
    )
    env = jinja2.Environment()
    env.filters["format_cpu_freq"] = format_cpu_freq
    env.filters["auto_convert_unit"] = auto_convert_unit
    template = env.from_string(template_content)
    top_image_path = get_image_path("top.jpg")
    abs_image_path = get_image_path("bk.png")

    owner_list = config.owner if hasattr(config, 'owner') else []
    owner_qq = str(owner_list[0]) if owner_list else "0"
    bot_avatar_path = f"http://q2.qlogo.cn/headimg_dl?dst_uin={owner_qq}&spec=640"
    html_content = template.render(
        d=status_data,
        config=config,
        css_content=css_content,
        top_image_path=top_image_path,
        abs_image_path=abs_image_path,
        bot_avatar_path=bot_avatar_path,
    )
    img_path = os.path.abspath(os.path.join(RES_DIR, f"status_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png"))
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 900, "height": 600})
        await page.set_content(html_content)
        await asyncio.sleep(0.2)
        elem = await page.query_selector("div.wrapper")
        if elem:
            await elem.screenshot(path=img_path)
        else:
            await page.screenshot(path=img_path, full_page=True)
        await browser.close()
    return img_path

async def collect_status():
    import platform
    import psutil
    import sys

    cfg = Configurator.cm.get_cfg()
    others = getattr(cfg, "others", {})
    now = datetime.now()

    cpu_freq = getattr(psutil.cpu_freq(), "current", 0)
    cpu_brand = platform.processor() or "未知CPU"

    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    memory_stat = {
        "percent": mem.percent,
        "used": mem.used,
        "total": mem.total,
    }
    swap_stat = {
        "percent": swap.percent,
        "used": swap.used,
        "total": swap.total,
    }

    disk_usage = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disk_usage.append({
                "name": part.device,
                "percent": usage.percent,
                "used": usage.used,
                "total": usage.total,
                "exception": False,
            })
        except Exception:
            disk_usage.append({
                "name": part.device,
                "percent": 0,
                "used": 0,
                "total": 0,
                "exception": True,
            })

    network_connection = [
        {"name": "真寻状态", "连接错误": False}
    ]

    current_bot = {
        "self_id": getattr(cfg, "uin", "未知"),
        "nick": others.get("bot_name", "未知"),
    }

    plugins_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plugins"))
    plugin_count = 0
    if os.path.isdir(plugins_dir):
        for entry in os.listdir(plugins_dir):
            full_path = os.path.join(plugins_dir, entry)
            if entry.endswith('.py'):
                plugin_count += 1
            elif os.path.isdir(full_path) and entry != '__pycache__':
                plugin_count += 1

    return {
        "time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "system_name": platform.platform(),
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "cpu_count": psutil.cpu_count(),
        "cpu_freq": cpu_freq,
        "cpu_brand": cpu_brand,
        "memory_stat": memory_stat,
        "swap_stat": swap_stat,
        "disk_usage": disk_usage,
        "network_connection": network_connection,
        "python_version": sys.version.split()[0],
        "plugin_count": plugin_count,  # 删除这一行
        "bot_name": others.get("bot_name", "未知"),
        "current_bot": current_bot,
        "ps_version": "1.0.0",
        "template_version": "XiaoyiDev",
        "zhenxun_version": "",
        "nonebot_version": "",
    }

async def on_message(event, actions, Manager, Segments):
    if not hasattr(event, "message"):
        return False
    msg = str(event.message).strip()
    reminder = Configurator.cm.get_cfg().others.get("reminder", "")
    if msg not in ["status", f"{reminder}状态"]:
        return False

    try:
        cfg = Configurator.cm.get_cfg()
        status_data = await collect_status()
        img_path = await render_status_image(status_data, cfg)
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message([
                Segments.Image(f"file:///{img_path}")
            ])
        )
        try:
            if os.path.exists(img_path):
                os.remove(img_path)
        except Exception as e:
            print(f"[PicStatus] 清理临时图片失败: {e}")
        return True
    except Exception as e:
        print(f"[PicStatus] 状态图片生成失败: {e}")
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(Segments.Text(f"状态图片生成失败: {e}"))
        )
        return True

print("[Xiaoyi_QQ]PicStatus状态插件已加载")