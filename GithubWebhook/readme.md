# Github Webhook

这是一个基于Github Webhook的简单推送插件，用于将GitHub Webhook请求转为图片发送到群里

[!TIP]  
当前插件经测试，与云黑插件(CloudBlacklistConsole)同时使用会造成其中一个无法加载，此问题疑似插件加载器的锅
## 安装部署

首先安装依赖

```
pip install Flask[async]
```
### 基础命令

```
[触发机器人的命令，如-]查看GH仓库关联
-查看GH仓库关联 #查看GitHub仓库关联的群
-添加GH仓库关联  <Github仓库名，需包含组织名或用户名 如:https://github.com/IntelliMarkets/Jianer_Plugins_Index/> <群号>
-删除GH仓库关联 <Github仓库名，需包含组织名或用户名 如:https://github.com/IntelliMarkets/Jianer_Plugins_Index/> <群号>
以上命令在私聊也可以用
```

