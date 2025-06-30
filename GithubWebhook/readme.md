# Github Webhook

這是一個基於Github Webhook的簡單推送插件，用於將GitHub Webhook請求轉為圖片發送到群裡

[!TIP]  
當前插件經測試，與雲黑插件(CloudBlacklistConsole)同時使用會造成其中一個無法加載，此問題疑似插件加載器的鍋

## 安裝部署

首先安裝依賴

```
pip install Flask[async]
```

### 基礎命令

```
[觸發機器人的命令，如-]查看GH仓库关联
-查看GH仓库关联 #查看GitHub倉庫關聯的群
-添加GH仓库关联  <Github倉庫名，需包含組織名或用戶名 如:https://github.com/IntelliMarkets/Jianer_Plugins_Index/> <群號>
-刪除GH仓库关联 <Github倉庫名，需包含組織名或用戶名 如:https://github.com/IntelliMarkets/Jianer_Plugins_Index/> <群號>
以上命令在私聊也可以用
```

## 使用方法
在需要推送的倉庫點擊Settings，找到Webhooks,點擊 Add webhook
Payload URL:填寫你的伺服器公網IP地址:端口(預設2525,你可以在bot_send.py中修改)/webhook
Content type:這裡一定要選application/json
Secret:自定義一個密鑰，這個密鑰一定要與你在bot_send.py中定義的GITHUB_SECRET一致，不然會403

SSL verification:看你是否配置了SSL證書，有配就可以開
Which events would you like to trigger this webhook?:這裡說您希望哪些事件觸發此 Webhook？，自己選擇，完成點 add webhook，就配置好了