from Hyper import Configurator
import os
import re
import json
import httpx
import asyncio
import typing
import time

TRIGGHT_KEYWORD = "Any"
CONFIG_LOADED = False
try:
    Configurator.cm = Configurator.ConfigManager(Configurator.Config(file="config.json").load_from_file())
    CONFIG_LOADED = True
except Exception as _e:
    print(f"[ExprGen] 未能加载全局配置（可忽略，稍后运行时将尝试读取）: {_e}")

# 默认API配置路径
BASE_DIR = os.path.dirname(__file__)
API_CONFIG_PATH = os.path.join(BASE_DIR, "config", "expr_apis.json")

# 最大支持QQ参数
MAX_QQ_PARAMS = 5

# 缓存加载的api模板
_api_templates = {}


def _load_api_templates(path=API_CONFIG_PATH):
    global _api_templates
    try:
        with open(path, "r", encoding="utf-8") as f:
            _api_templates = json.load(f)
        print(f"[ExprGen] 已加载 API 模板: {list(_api_templates.keys())}")
    except Exception as e:
        print(f"[ExprGen] 加载 API 模板失败: {e}")
        _api_templates = {}


def _is_admin(event) -> bool:
    try:
        uid = str(event.user_id)
        if CONFIG_LOADED:
            try:
                cfg = Configurator.cm.get_cfg().others
                if uid in cfg.get("ROOT_User", []):
                    return True
            except Exception:
                pass
        try:
            if os.path.exists('./Super_User.ini'):
                if uid in open('./Super_User.ini', 'r', encoding='utf-8').read().splitlines():
                    return True
        except Exception:
            pass
        try:
            if os.path.exists('./Manage_User.ini'):
                if uid in open('./Manage_User.ini', 'r', encoding='utf-8').read().splitlines():
                    return True
        except Exception:
            pass
    except Exception:
        return False
    return False


def _get_reminder() -> str:
    try:
        if CONFIG_LOADED:
            return Configurator.cm.get_cfg().others.get('reminder', '')
    except Exception:
        pass
    return ''


_load_api_templates()


async def _call_api(url: str, timeout: float = 10.0) -> typing.Tuple[bool, typing.Union[bytes, str]]:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=timeout)
            content_type = resp.headers.get("content-type", "")
            if resp.status_code != 200:
                return False, f"HTTP {resp.status_code}"
            if "image" in content_type or resp.content[:4] in (b"\x89PNG", b"\xff\xd8\xff", b"RIFF"):
                return True, resp.content
            text = resp.text
            return True, text
    except Exception as e:
        return False, str(e)


async def _send_image(actions, Manager, Segments, group_id, image_bytes: bytes, caption: str = None):
    try:
        tmp_dir = os.path.join(BASE_DIR, "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_path = os.path.join(tmp_dir, f"expr_{int(time.time()*1000)}.png")
        with open(tmp_path, "wb") as f:
            f.write(image_bytes)
        msg = [Segments.Image(tmp_path)] if hasattr(Segments, 'Image') else [Segments.Text("[图片]")]
        if caption:
            msg.append(Segments.Text(caption))
        await actions.send(group_id=group_id, message=Manager.Message(msg))
        return True
    except Exception as e:
        print(f"[ExprGen] 发送图片失败: {e}")
        return False


async def on_message(event, actions, Manager, Segments):
    if not hasattr(event, 'message'):
        return False
    text = str(event.message).strip()
    reminder = _get_reminder()

    if text in (f"{reminder}制图列表"):
        if not _api_templates:
            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("当前没有可用的表情模板")))
            return True
        lines = []
        for name, tpl in _api_templates.items():
            s = tpl if isinstance(tpl, str) else tpl.get('url', '')
            required = 0
            for i in range(1, MAX_QQ_PARAMS + 1):
                if f"{'{'}qq{i}{'}'}" in s:
                    required = max(required, i)
            import re as _re
            nums = _re.findall(r"\{(\d+)\}", s)
            if nums:
                maxidx = max(int(n) for n in nums)
                required = max(required, maxidx + 1)
            if required == 0:
                required = 0
            example_params = " ".join(["123456"] * max(1, required))
            example = f"制图#{name} {example_params}" if required > 0 else f"制图#{name}"
            lines.append(f"{name} — 需要 {required} 个QQ参数|示例: {example}")
        msg_text = "可用模板清单：\n" + "\n".join(lines)
        await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(msg_text)))
        return True

    if text == f"{reminder}重载表情API":
        if not _is_admin(event):
            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("无权限执行此操作")))
            return True
        if _reload_api_templates():
            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("表情API模板已重载")))
        else:
            await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("表情API模板重载失败")))
        return True

    m = re.match(r"^(?:制图|表情|表情包)\s*#?\s*(\S+)\s*(.*)$", text)
    if not m:
        return False
    template_key = m.group(1).strip()
    params_part = m.group(2).strip()
    params = []
    if params_part:
        params = params_part.split()[:MAX_QQ_PARAMS]

    tpl = _api_templates.get(template_key)
    if not tpl:
        await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(f"未找到表情模板: {template_key}")))
        return True

    try:
        url = _build_url_from_template(tpl, params)
    except Exception as e:
        await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(f"构造API请求失败: {e}")))
        return True

    await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(f"正在调用API生成表情：{template_key}")))
    ok, content = await _call_api(url)
    if not ok:
        await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(f"API调用失败: {content}")))
        return True

    if isinstance(content, (bytes, bytearray)):
        await _send_image(actions, Manager, Segments, event.group_id, content)
        return True

    text_content = str(content).strip()
    if text_content.startswith('http'):
        try:
            await actions.send(group_id=event.group_id, message=Manager.Message([Segments.Image(text_content)]))
            return True
        except Exception:
            ok2, c2 = await _call_api(text_content)
            if ok2 and isinstance(c2, (bytes, bytearray)):
                await _send_image(actions, Manager, Segments, event.group_id, c2)
                return True
    await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text(f"API返回: {text_content}")))
    return True



def _reload_api_templates():
    try:
        _load_api_templates()
        return True
    except Exception:
        return False


def _build_url_from_template(tpl: dict, params: list) -> str:
    if isinstance(tpl, str):
        template_url = tpl
    elif isinstance(tpl, dict):
        template_url = tpl.get('url')
    else:
        raise ValueError('API 模板格式不支持')

    for i in range(MAX_QQ_PARAMS):
        key = f'qq{i+1}'
        val = params[i] if i < len(params) else ''
        template_url = template_url.replace('{' + key + '}', val)
    for i in range(MAX_QQ_PARAMS):
        placeholder = '{' + str(i) + '}'
        val = params[i] if i < len(params) else ''
        template_url = template_url.replace(placeholder, val)
    return template_url


print("[Xiaoyi_QQ]表情生成插件已加载")
