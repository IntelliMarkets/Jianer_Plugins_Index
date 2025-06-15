## Akintor QQ机器人插件

基于 Akinator 猜人游戏的QQ机器人插件，支持多语言和代理配置。

### 功能特点

- 基于Akinator API的猜人游戏
- 支持中文、日语、英语等多种语言
- 内置代理支持，解决API访问问题
- 自动超时机制(60秒无响应自动结束)
- 支持返回上一题和退出游戏

### 安装说明

1. 确保已安装Python 3.7+
2. 安装依赖：
   ```bash
   pip install cloudscraper beautifulsoup4 pyyaml
   ```
3. 将插件目录放入QQ机器人的plugins文件夹

### 使用说明

在QQ群中发送命令：
```
猜人
```

游戏开始后，可以通过以下方式回答问题：
- 是(y/1/是/是的/对/有/在)
- 不是(n/2/不是/不/不对/否/没有/不在)
- 我不知道(idk/3/不知道/不清楚)
- 或许是(p/4/可能是/也许是/或许是/应该是/大概是)
- 或许不是(pn/5/可能不是/也许不是/或许不是/应该不是/大概不是)
- 返回(b/B/返回/上一个)
- 退出(exit/退出)

### 配置说明

编辑`config.yaml`文件：

```yaml
proxyurl: https://example.com/  # 代理服务器地址，最后必须加/
lang: cn  # 语言配置(cn-中文, jp-日语, en-英语)
```

### 注意事项

1. 默认使用代理服务器访问Akinator API
2. 如果API不可用，可能需要更换代理或等待
3. 游戏超时时间为60秒
4. 图片加载依赖Akinator官方服务器

### 文件说明

- `Akirequest.py`: Akinator API交互核心
- `GameSession.py`: 游戏会话管理
- `setup.py`: 插件主入口
- `config.yaml`: 配置文件

### 许可证

MIT License
