import os
from Tools.site_catch import Catcher
import random
async def get_image(ckname,ckicon,sjlx,data114514): 
    catcher = await Catcher.init()
    try:
        with open(os.path.abspath("./plugins/GithubWebhook/src/githubsend.html"), "r", encoding="utf-8") as f:
            html = f.read()
        html = html.replace("{ckicon}", ckname)
        html = html.replace("{ckname}", ckicon)
        html = html.replace("{sjlx}", sjlx)
        html = html.replace("{data114514}", data114514)
        akiname = random.randint(1, 114514)
        with open(f"./temps/ghtz-{akiname}.html", "w", encoding="utf-8") as f:
            f.write(html)
        res = await catcher.catch(f"file://{os.path.abspath(f'./temps/ghtz-{akiname}.html')}",(1366,768)) 
        os.remove(f"./temps/ghtz-{akiname}.html")
        return res
    finally:
        await catcher.quit()

# 处理消息的函数
async def ghtz(ckname,ckicon,sjlx,data114514):
    imagename = await get_image(ckname,ckicon,sjlx,data114514)
    return os.path.abspath(imagename)