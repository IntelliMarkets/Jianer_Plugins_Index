# ZhenxunStatus 状态插件

一个支持获取系统状态并渲染为图片的群机器人插件，支持 Xiaoyi_QQ 和 Jianer_QQ 机器人框架。

## 功能特性

- 获取系统时间、CPU 使用率、内存使用率、磁盘使用情况等系统状态信息
- 将系统状态信息渲染为图片并发送到群聊
- 支持自定义 HTML 模板和 CSS 样式
- 自动清理临时生成的图片文件

## 安装方法
1. 可能需要安装额外依赖: `playwright install chromium`
2. 下载 `setup.py` 文件和 `res` 目录
3. 将 `setup.py` 文件和 `res` 目录放入机器人的 `plugins` 目录
4. 重启机器人或发送 `重载插件` 命令

## 配置项目

插件会获取 `config.json` 中以下参数：

```json
{
    "owner": ["QQ号"],  // 机器人主人的 QQ 号
    "others": {
        "bot_name": "机器人昵称",  // 机器人昵称
        "reminder": "前缀"  // 指令前缀
    }
}
```

## 使用方法

在群内发送 `status` 或 `{reminder}状态` 即可，机器人会返回一张包含系统状态信息的图片。
## 示例
![返回图片示例](https://img.picui.cn/free/2025/06/14/684d5ea9d9026.png)

## 数据存储

无核心数据存储，临时生成的图片文件会在发送后自动清理。

## 适配版本

- Xiaoyi_QQ: [https://github.com/ValkyrieEY/Xiaoyi_QQ/](https://github.com/ValkyrieEY/Xiaoyi_QQ/)
- Jianer_QQ V3 NEXT: [https://github.com/SRInternet-Studio/Jianer_QQ_bot/](https://github.com/SRInternet-Studio/Jianer_QQ_bot/)

## 作者信息

- 作者：小依
- 博客：[https://xun.eynet.top/](https://xun.eynet.top/)

## 更新日志

### v1.0.1
- 更新了图片直链地址

### v1.0.0
- 提供基础功能

## 开源协议

MIT License

## 问题反馈

如果遇到问题，请在以下地址提交 Issue：
- Xiaoyi_QQ: [提交 Issue](https://github.com/ValkyrieEY/Xiaoyi_QQ/issues)

## 贡献代码

## 鸣谢
- NoneBot - 提供基础模板，本插件适配自NoneBot
- SR Studio - 提供框架支持
