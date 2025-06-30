# DouyinAnalysis 抖音视频解析插件

一个自动解析抖音短视频链接并显示详细信息的群机器人插件，支持 Xiaoyi_QQ 和 Jianer_QQ 机器人框架。

## 功能特性

- 自动检测抖音短视频链接（支持 v.douyin.com 分享链接）
- 展示作者头像与信息
- 展示视频封面与详细信息：
  - 视频简介
  - 标签
  - 音乐信息
  - 点赞/评论/分享/收藏数
  - 视频直链
- 自动下载并发送视频文件（如机器人支持）

## 安装方法

1. 下载 `[XY]DouyinAnalysis.py` 文件
2. 将文件放入机器人的 `plugins` 目录
3. 确保已安装必要的依赖:
```bash
pip install httpx
```
4. 重启机器人或发送 `/重载插件` 命令

## 使用方法

在群内发送任何包含抖音短视频分享链接（如 `https://v.douyin.com/xxxxxx/`）的消息即可自动触发解析。

## 特色功能

- 自动识别并解析抖音短视频链接
- 展示作者头像、昵称、签名等详细信息
- 展示视频简介、标签、音乐、数据统计等
- 支持发送视频直链和自动下载视频文件（如机器人支持）
- 简洁美观的消息格式
- 支持异步请求，不影响机器人其他功能

## 适配版本

- Xiaoyi_QQ: [https://github.com/ValkyrieEY/Xiaoyi_QQ/](https://github.com/ValkyrieEY/Xiaoyi_QQ/)
- Jianer_QQ V3 NEXT: [https://github.com/SRInternet-Studio/Jianer_QQ_bot/](https://github.com/SRInternet-Studio/Jianer_QQ_bot/)

## 作者信息

- 作者：小依
- 博客：[https://xun.eynet.top/](https://xun.eynet.top/)

## 更新日志

### v1.0.2
- 增加云更新功能

### v1.0.0
- 支持抖音短视频链接自动解析
- 展示作者与视频详细信息
- 支持发送视频直链和自动下载视频

## 开源协议

MIT License

## 问题反馈

如果遇到问题，请在以下地址提交 Issue：
- Xiaoyi_QQ: [提交 Issue](https://github.com/ValkyrieEY/Xiaoyi_QQ/issues)

## 贡献代码

欢迎提交 Pull Request 来完善这个插件！

## 鸣谢
- [冷雨枫林API](https://api.yuafeng.cn/) - 提供视频解析接口
- SR Studio - 提供框架支持