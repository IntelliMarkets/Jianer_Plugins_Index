## GroupCheckIn 群签到插件
一个支持用户签到、积分和好感度系统的群机器人插件，支持 Xiaoyi_QQ 和 Jianer_QQ 机器人框架。

## 功能特性

- 每日签到获取积分和好感度
- 查看累计签到天数
- 显示签到排名
- 签到消息携带一言
- 自动保存用户数据
- 可配置奖励范围

## 安装方法

1. 下载 `GroupCheckIn.py` 文件
2. 将文件放入机器人的 `plugins` 目录
3. 重启机器人或发送 `/重载插件` 命令

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

## 数据存储

数据存储在 `data/check_in/` 目录下：
- `total_check_in.json`: 总计签到数据
- `daily_check_in.json`: 每日签到数据
- `user_data.json`: 用户数据

## 适配版本

- Xiaoyi_QQ: [https://github.com/ValkyrieEY/Xiaoyi_QQ/](https://github.com/ValkyrieEY/Xiaoyi_QQ/)
- Jianer_QQ: [https://github.com/SRInternet-Studio/Jianer_QQ_bot/](https://github.com/SRInternet-Studio/Jianer_QQ_bot/)

## 作者信息

- 作者：小依
- 博客：[https://xun.eynet.top/](https://xun.eynet.top/)

## 开源协议

MIT License

## 更新日志

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