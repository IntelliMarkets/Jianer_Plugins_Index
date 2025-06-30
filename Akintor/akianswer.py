import os
import re
import datetime
from Tools.site_catch import Catcher

async def get_image(akiname,akichuqu,image114514): 
    catcher = await Catcher.init()
    try:
        with open(os.path.abspath("./plugins/Akintor/src/akianswer.html"), "r", encoding="utf-8") as f:
            html = f.read()
        html = html.replace("{akiname}", akiname)
        html = html.replace("{aki2}", akichuqu)
        html = html.replace("{image114514}", image114514)
        print(image114514)
        html = html.replace("{name114}",os.path.abspath("./plugins/Akintor/src/name114514.ttf"))
        html = html.replace("{name514}",os.path.abspath("./plugins/Akintor/src/Probert_Condensed_Bold.otf"))
        with open(f"./temps/akianswer-{akiname}.html", "w", encoding="utf-8") as f:
            f.write(html)
        res = await catcher.catch(f"file://{os.path.abspath(f'./temps/akianswer-{akiname}.html')}",(1920,1080)) 
        os.remove(f"./temps/akianswer-{akiname}.html")
        return res
    finally:
        await catcher.quit()
#处理Aki答案图片发送
async def akianswer114(akiname,akichuqu,image114514):
    imagename = await get_image(akiname,akichuqu,image114514)
    return os.path.abspath(imagename)
#-----------------------------------------------------------------------------------------------------------------------------------------
async def get_image1(akinumber,akiwt,akiimage114514): 
    catcher = await Catcher.init()
    try:
        # 判断是否为夜间时间
        now = datetime.datetime.now()
        hour = now.hour
        is_night = 22 <= hour <= 23 or 0 <= hour <= 5
        if is_night: #如果处于夜间时间,使用深色页面，防止Sr夜间爆炸
            with open(os.path.abspath("./plugins/Akintor/src/akiwtdark.html"), "r", encoding="utf-8") as f:
                html = f.read()
        else:
            with open(os.path.abspath("./plugins/Akintor/src/akiwt.html"), "r", encoding="utf-8") as f:
                html = f.read()
        html = html.replace("{wtnumber}", str(akinumber))
        html = html.replace("{question114514}", akiwt)
        html = html.replace("{akiimage114514}", akiimage114514)
        html = html.replace("{name114}",os.path.abspath("./plugins/Akintor/src/name114514.ttf"))
        html = html.replace("{name514}",os.path.abspath("./plugins/Akintor/src/Probert_Condensed_Bold.otf"))
        safe_akiwt = re.sub(r'[\\/*?:"<>|]', "", akiwt)
        with open(f"./temps/akiwt-{safe_akiwt}{akinumber}.html", "w", encoding="utf-8") as f:
            f.write(html)
        res = await catcher.catch(f"file://{os.path.abspath(f'./temps/akiwt-{safe_akiwt}{akinumber}.html')}",(1024,768)) 
        os.remove(f"./temps/akiwt-{safe_akiwt}{akinumber}.html")
        return res
    finally:
        await catcher.quit()

#处理aki问题图片发送
async def akiwt114(akinumber,akiwt,akiimage114514):
    imagename = await get_image1(akinumber,akiwt,akiimage114514)
    return os.path.abspath(imagename)