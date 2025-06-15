## GitHub Issues/Commit 信息获取

一个基于GitHub API的issue/commit信息获取工具，通过QQ机器人命令返回指定内容。

### 功能特点
- 获取指定issue/commit信息
- 支持查询最新或指定编号的内容
- 自动返回截图或错误信息

### 安装指南
1. 安装依赖：
   ```bash
   pip install -r requests selenium Pillow playwright
   ```
2. 配置环境：

   **请在 `IssuesCapture.py` 中配置以下常量：**
   - 设置GitHub仓库信息 (OWNER, REPO)
   - 可选配置GitHub Token (TOKEN)

### 使用说明
#### QQ机器人命令
- `[提醒词]issue latest` - 获取最新issue
- `[提醒词]issue [编号]` - 获取指定issue
- `[提醒词]commit latest` - 获取最新commit
- `[提醒词]commit [编号]` - 获取指定commit

### 注意事项
1. 需要配置正确的GitHub仓库信息
2. 使用Token可提高API调用限制
3. **需要安装 Playwright 浏览器用于截图**
