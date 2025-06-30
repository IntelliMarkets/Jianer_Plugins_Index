# GroupCheckIn 群签到插件

一个支持用户签到、积分和好感度系统的群机器人插件，支持 Xiaoyi_QQ 和 Jianer_QQ 机器人框架。

## 功能特性

- 每日签到获取积分和好感度
- 查看累计签到天数
- 显示签到排名
- 签到消息携带一言
- 自动保存用户数据
- 可配置奖励范围

## 安装方法
1. 可能需要安装额外依赖: `playwright install chromium`
2. 下载 `GroupCheckIn.py` 文件
3. 将文件放入机器人的 `plugins` 目录
4. 重启机器人或发送 `重载插件` 命令

## 配置项目

在 `data/check_in/check_in_config.json` 中可以配置以下参数：

```json
{
    "好感度": {
        "min": 1,    // 最小好感度
        "max": 10    // 最大好感度
    },
    "积分": {
        "min": 10,   // 最小积分
        "max": 100   // 最大积分
    }
}
```

## 使用方法

在群内发送 `签到` 即可，机器人会返回：
- 签到排名
- 获得的好感度和积分
- 累计签到数据
- 随机一言

在群内发送 `{reminder}添加签到指令 打卡` ，添加自定义签到指令：
- 独立数据存储
- 可自定义指令
- 多个指令同时存在

在群内发送 `{reminder}删除签到指令 打卡` ，删除自定义签到指令：
- 对已经添加的签到指令删除

在群内发送 `{reminder}切换签到发送模式` ，进行发送模式切换：
- 文本发送
- HTML渲染图片发送
- API发送
- 需要安装 `playwright` 依赖
- 操控权限为`Manage_User`及以上权限

在群内发送 `{reminder}更新签到插件` ，从云端更新插件版本：
- 云端下载需要检查网络可用性
- 云更新服务器位于上海

## 数据存储

数据存储在 `data/check_in/` 目录下：
- `check_in_config.json`: 核心数据配置
- `custom_commands.json`: 自定义指令数据
- `user/qq.json`: 用户数据

## 适配版本

- Xiaoyi_QQ: [https://github.com/ValkyrieEY/Xiaoyi_QQ/](https://github.com/ValkyrieEY/Xiaoyi_QQ/)
- Jianer_QQ: [https://github.com/SRInternet-Studio/Jianer_QQ_bot/](https://github.com/SRInternet-Studio/Jianer_QQ_bot/)

## 作者信息

- 作者：小依
- 博客：[https://xun.eynet.top/](https://xun.eynet.top/)

## 开源协议

MIT License

## 更新日志

### v1.3.0
- 增加API发送模式切换
- 增加更多发送模式以及渲染模式

### v1.2.4
- 增加了云更新功能

### v1.2.3
- 修复了发送时名称获取错误的问题
- 修复了一些已知问题

### v1.2.2
- 修复了因一言获取失败而无法签到的问题
- 修复了一言API的错误处理
- 更改了数据的存储方式
- 简化了数据存储的代码
- 去除了每日签到数据记录

### v1.1.0
- 实现自定义HTML渲染图片发送
- 允许自行替换HTML模板
- 增加相关指令
- 修复了签到排名显示问题
- 优化了代码结构
- 增加了一言API的错误处理
- 增加了图片发送失败自动转文本发送
- 增加了配置项的注释
- 优化了数据存储方式
- 修复了一些已知问题

### v1.0.0
- 实现基础签到功能
- 添加积分和好感度系统
- 集成一言API
- 支持数据持久化存储

## 问题反馈

如果遇到问题，请在以下地址提交 Issue：
- Xiaoyi_QQ: [提交 Issue](https://github.com/ValkyrieEY/Xiaoyi_QQ/issues)

## 贡献代码

欢迎提交 Pull Request 来完善这个插件！

## 鸣谢
- [HitokotaAPI](https://hitokoto.cn/) - 提供一言服务
- SR Studio - 提供框架支持