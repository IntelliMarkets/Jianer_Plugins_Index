# BiliAnalysis B站视频解析插件

一个自动解析B站视频链接并显示详细信息的群机器人插件,支持 Xiaoyi_QQ 和 Jianer_QQ 机器人框架。

## 功能特性

- 自动检测B站视频链接(支持BV号和av号)
- 支持解析短链接(b23.tv)
- 显示视频封面
- 展示视频详细信息:
  - 视频标题
  - UP主信息
  - 播放量
  - 点赞数
  - 投币数
  - 收藏数
  - 弹幕数
  - 评论数
  - 分享数

## 安装方法

1. 下载 `BiliAnalysis.py` 文件
2. 将文件放入机器人的 `plugins` 目录
3. 确保已安装必要的依赖:
```bash
pip install httpx
```
4. 重启机器人或发送 `/重载插件` 命令

## 使用方法

在群内发送任何包含B站视频链接的消息即可触发解析,支持的链接格式:
- `https://www.bilibili.com/video/BVxxxxxx`
- `https://www.bilibili.com/video/avxxxxxx`
- `https://b23.tv/xxxxxx`

## 特色功能

- 自动将大于10000的数字转换为"万"为单位的形式
- 使用emoji美化显示效果
- 视频数据完整展示
- 支持异步请求,不影响机器人其他功能
- 自定义发送延迟

## 适配版本

- Xiaoyi_QQ: [https://github.com/ValkyrieEY/Xiaoyi_QQ/](https://github.com/ValkyrieEY/Xiaoyi_QQ/)
- Jianer_QQ V3 NEXT: [https://github.com/SRInternet-Studio/Jianer_QQ_bot/](https://github.com/SRInternet-Studio/Jianer_QQ_bot/)

## 作者信息

- 作者：小依
- 博客：[https://xun.eynet.top/](https://xun.eynet.top/)

## 更新日志

### v1.2.1
- 删除解析超次数提示

### v1.2.0
- 增加权限控制
- 支持自定义发送延迟
- 优化数据格式化显示
- 修复部分bug

### v1.1.0
- 增加重复停止解析功能

### v1.0.0
- 基础视频信息解析功能
- 支持BV号和av号
- 支持短链接解析
- 添加数据格式化显示

## 开源协议

MIT License

## 问题反馈

如果遇到问题,请在以下地址提交Issue:
- Xiaoyi_QQ: [提交Issue](https://github.com/ValkyrieEY/Xiaoyi_QQ/issues)

## 贡献代码

欢迎提交Pull Request来改进这个插件！

## 鸣谢
- [Bilibili API](https://api.bilibili.com/) - 提供视频数据接口
- SR Studio - 提供框架支持