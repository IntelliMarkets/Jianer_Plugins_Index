# QAuto QQ自动打卡插件

一个支持扫码登录、自动定时打卡的QQ群机器人插件，适配 Xiaoyi_QQ 和 Jianer_QQ 机器人框架。

> ⚠️ 本插件及其API服务端仅限部署在中国大陆服务器使用，无法用于境外服务器或违反相关法律法规的用途。

## 功能特性

- 支持QQ扫码登录，自动获取skey/pskey
- 支持自定义每日自动打卡时间
- 支持多用户独立管理
- 登录、打卡、异常等状态详细日志输出
- 所有用户数据本地JSON存储
- 完善的接口异常处理
- 兼容Jianer_QQ_bot-NEXT-PREVIEW主程序

## 安装方法

1. 下载 `QAuto.py` 文件
2. 放入机器人 `plugins` 目录
3. 确保已安装依赖：
   ```bash
   pip install requests
   ```
4. 配置API服务端（详见下方）
5. 重启机器人或发送 `/重载插件` 命令

## API服务端部署

- 推荐将 `cookie/` 目录下的PHP源码部署在中国大陆服务器
- 需支持PHP 7.0+，建议使用Apache/Nginx+PHP
- 仅限中国大陆服务器，禁止境外部署
- 访问 `login.php` 测试接口可用性

## 配置文件

插件会自动创建并维护以下文件：

```
data/
└── qq_autosign/
    └── users.json   # 用户数据
```

## 使用方法

### 基础命令
```
{reminder}申请登录         # 申请扫码登录，获取二维码
{reminder}设置自动打卡时间 HH:MM   # 设置每日自动打卡时间
```

### 示例
```
/申请登录
/设置自动打卡时间 08:30
```

## 特色功能

- 支持扫码登录，自动轮询登录状态
- 登录成功后自动保存skey/pskey
- 每日定时自动打卡，失败自动提醒
- 详细控制台调试日志，便于排查问题
- 完善的接口异常与超时处理

## 适配版本

- Xiaoyi_QQ: https://github.com/ValkyrieEY/Xiaoyi_QQ/
- Jianer_QQ V3 NEXT: https://github.com/SRInternet-Studio/Jianer_QQ_bot/

## 作者信息

- 作者：小依
- 博客：https://xun.eynet.top/

## 开源协议

MIT License

## 法律声明

- 本插件及API服务端仅限中国大陆服务器连接，无法用于境外服务器或任何违法用途。
- 使用本插件即代表同意遵守中国大陆相关法律法规，因违规使用造成的后果由使用者自行承担。
- 插件仅供学习。

## 问题反馈

如有问题请在以下地址提交 Issue：
- Xiaoyi_QQ: https://github.com/ValkyrieEY/Xiaoyi_QQ/issues

## 鸣谢
- SR Studio - 提供框架支持
- 冷雨枫林API - 提供部分接口支持
