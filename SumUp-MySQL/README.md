## QQ群聊总结插件（MySQL版）

一个基于QQ群聊总结插件，使用MySQL数据库存储消息记录，利用GoogleAI的Gemini模型对群聊消息进行智能总结和数据分析。

### 功能特点
- 支持总结指定数量的历史消息（1-1000条）
- 自动估算消息的Token数量，避免超过模型限制
- 展示聊天数据看板
- 使用Gemini模型生成高质量的消息摘要
- 消息存储在MySQL数据库中，**支持数据持久化**
- 自动创建所需的数据库和表结构
- 支持自定义MySQL连接配置

### 安装指南
```bash
pip install asyncio google-generativeai pymysql
```

### 配置说明
1. 在**该插件根目录下** (也就是`setup.py`所在目录) 中创建`mysql.json`文件，并配置MySQL数据库连接信息：
```json
{
  "host": "localhost",
  "user": "root",
  "password": "password",
  "database": "jianer_chat_db",
  "port": 3306
}
```
2. 请注意在机器人的config.json中配置gemini_key和相关参数

### 使用说明
#### QQ机器人命令
- `[提醒词]总结以上N条消息` - 总结当前群聊的指定数量的消息 (0<N<=1000)
- `[提醒词]聊天数据看板` - 展示当前(或全部)群聊的聊天数据看板

### 注意事项
1. 确保MySQL数据库服务正在运行
2. 确保数据库用户有创建数据库和表的权限
3. 支持自定义Gemini模型和API基础URL
4. 消息存储在MySQL数据库中，表结构会自动创建