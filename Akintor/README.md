## Akintor 猜人游戏插件
一个基于 Akinator 猜人游戏的插件，用户可以通过回答一系列问题来让机器人猜测他们心中所想的人物。

### 功能特性

- 支持单人/多人同时在多个群组进行游戏
- 自动超时处理（30秒无响应自动结束）
- 支持中文问答
- 提供游戏结果图片展示
- 完整的游戏流程控制

### 安装与配置

1. 确保已安装依赖库（在设置向导中，插件中心会自动安装依赖）：
   ```
   pip install akinator-python
   ```

2. 将插件文件夹 `Akintor` 放入到 `plugins` 文件夹下

## 使用说明

### 开始游戏
在群聊中发送触发关键词+`猜人`即可开始游戏

### 游戏指令
在游戏过程中，可以使用以下指令进行回答：

- `y` - 表示"是"
- `n` - 表示"不是"
- `idk` - 表示"不知道"
- `p` - 表示"可能是"
- `pn` - 表示"可能不是"
- `b` - 返回上一题
- `exit` - 退出游戏

### 游戏流程
1. 机器人会提出一系列问题
2. 用户根据心中所想人物的情况回答
3. 经过若干问题后，机器人会猜测一个人物
4. 游戏结束，显示猜测结果和图片

## 注意事项

- 每个群同时只能有一个用户进行游戏
- 30秒无响应会自动结束游戏
- 如果服务器出现问题，会提示稍后再试

## 开发者信息

- 基于 `akinator-python` 库开发
- 需要配合 Hyper 框架使用
- 如果遇到问题，请联系插件开发者 [@RBC-AE3803](https://github.com/RBC-AE3803) [@SRInternet](https://github.com/SRInternet/)

## 错误处理

如果遇到错误，会显示错误信息并自动结束游戏。完整的错误日志会打印在控制台。

## 许可证

[MIT License]
