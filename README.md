<div align="center">

  
# <image src="https://github.com/user-attachments/assets/f63cbae0-7251-496b-b493-6e695ac1b25f" height="45"/>  简儿 - 插件主页
<img src="https://img.shields.io/badge/OneBot-11-black?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHAAAABwCAMAAADxPgR5AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAAxQTFRF////29vbr6+vAAAAk1hCcwAAAAR0Uk5T////AEAqqfQAAAKcSURBVHja7NrbctswDATQXfD//zlpO7FlmwAWIOnOtNaTM5JwDMa8E+PNFz7g3waJ24fviyDPgfhz8fHP39cBcBL9KoJbQUxjA2iYqHL3FAnvzhL4GtVNUcoSZe6eSHizBcK5LL7dBr2AUZlev1ARRHCljzRALIEog6H3U6bCIyqIZdAT0eBuJYaGiJaHSjmkYIZd+qSGWAQnIaz2OArVnX6vrItQvbhZJtVGB5qX9wKqCMkb9W7aexfCO/rwQRBzsDIsYx4AOz0nhAtWu7bqkEQBO0Pr+Ftjt5fFCUEbm0Sbgdu8WSgJ5NgH2iu46R/o1UcBXJsFusWF/QUaz3RwJMEgngfaGGdSxJkE/Yg4lOBryBiMwvAhZrVMUUvwqU7F05b5WLaUIN4M4hRocQQRnEedgsn7TZB3UCpRrIJwQfqvGwsg18EnI2uSVNC8t+0QmMXogvbPg/xk+Mnw/6kW/rraUlvqgmFreAA09xW5t0AFlHrQZ3CsgvZm0FbHNKyBmheBKIF2cCA8A600aHPmFtRB1XvMsJAiza7LpPog0UJwccKdzw8rdf8MyN2ePYF896LC5hTzdZqxb6VNXInaupARLDNBWgI8spq4T0Qb5H4vWfPmHo8OyB1ito+AysNNz0oglj1U955sjUN9d41LnrX2D/u7eRwxyOaOpfyevCWbTgDEoilsOnu7zsKhjRCsnD/QzhdkYLBLXjiK4f3UWmcx2M7PO21CKVTH84638NTplt6JIQH0ZwCNuiWAfvuLhdrcOYPVO9eW3A67l7hZtgaY9GZo9AFc6cryjoeFBIWeU+npnk/nLE0OxCHL1eQsc1IciehjpJv5mqCsjeopaH6r15/MrxNnVhu7tmcslay2gO2Z1QfcfX0JMACG41/u0RrI9QAAAABJRU5ErkJggg==" alt="Badge">

<img src="https://img.shields.io/badge/Language-Python-coral?logo=python&logoColor=white" alt="Language">
<img alt="GitLab Stars" src="https://img.shields.io/github/stars/IntelliMarkets/Jianer_Plugins_Index?label=Stars">
<img src="https://img.shields.io/badge/插件总数-55-green?logo=stackblitz&logoColor=black&style=social" alt="Badge">

这里是简儿QQ机器人的插件市场，为市场中的插件提供下载与更新功能。

[Main Repo](https://github.com/SRInternet-Studio/Jianer_QQ_bot/)

![Alt](https://repobeats.axiom.co/api/embed/5a7b65a2df07732a101273a56c0f40add32dca69.svg "Repobeats analytics image")

</div>

## ⚡ 如何编写

请参阅文档 [简儿 NEXT 3：Create a New Plugin](https://jianer.sr-studio.cn/Create-a-New-Plugin.html)

### 文件名格式公约

> 插件文件的文件名应该严格遵守 **PEP8 命名规范**，即插件名称中只能包含**字母、数字和下划线**，且必须以字母或下划线开头，不得包含其他特殊字符，例如空格、中划线等。插件文件名必须以 `.py` 或 `.pyw` 扩展名结尾。例如，"MorseCipher_Pro.py" 是一个有效的文件名，而 "Morse-Cipher Pro.py" 不是。
> 
> **注意：未遵守命名规范的插件文件名，审核人员可能会拒绝你的 Pull Request 并要求你修改文件名。** 

## ✨ 如何上传
> [!Important]
> 
> **重要：请务必按照以下规范流程上传您的插件，不规范的上传可能会导致无法正常在设置向导中下载或更新你的插件，还有可能导致插件市场损坏。**
> 
> **对于造成插件市场损坏的账户，我们将联系其并在一段时间内撤销其推送权限。**

1.  **Fork 本仓库**
    *   访问 [https://github.com/IntelliMarkets/Jianer_Plugins_Index](https://github.com/IntelliMarkets/Jianer_Plugins_Index)。
    *   点击右上角的 "Fork" 按钮，将仓库复制到你的 GitHub 账号下。

2.  **克隆 (Clone) 你 Fork 的仓库到本地**
    *   在你的 GitHub 账号下找到你 Fork 的 Jianer_Plugins_Index 仓库。
    *   点击 "Code" 按钮，复制仓库的 URL (以 `git@github.com` 或 `https://github.com` 开头)。
    *   打开你的终端 (Terminal) 或 Git Bash，执行以下命令：

        ```bash
        git clone <你复制的仓库 URL>
        cd Jianer_Plugins_Index
        ```

3.  **创建插件目录**
    *   在本地仓库的根目录下，创建一个文件夹，**文件夹名称必须与你的插件名称保持一致**。 例如，如果你的插件名为 "YourIntelliPlugin"，则文件夹名称也必须是 "YourIntelliPlugin"。

        ```bash
        mkdir YourIntelliPlugin
        ```

4.  **复制你的插件文件到插件目录**
    *   将你的插件文件 (例如 `YourIntelliPlugin.py`，或者包含 `setup.py` 的插件文件夹) 复制到你创建的插件目录中。

5.  **创建依赖和介绍信息**
    *   在你的插件目录下，创建 `requirements.txt` ，记录你的插件所需要用到的**第三方库**。在从设置向导的插件中心安装插件时，设置向导会读取 `requirements.txt` 并进行依赖安装。

    *   在你的插件目录下，创建 `README.md` ，用于介绍你的插件（可选）。介绍内容会显示在设置向导的插件中心，插件详情页窗口中。

6.  **提交 (Commit) 你的更改**
    *   在终端中，使用以下 Git 命令来暂存、提交你的更改：

        ```bash
        git add . 
        git commit -m "添加插件：YourIntelliPlugin" 
        ```

7.  **推送 (Push) 到你的 Fork 仓库**
    *   使用以下 Git 命令将本地更改推送到你 Fork 的 GitHub 仓库：

        ```bash
        git push origin main  # 推送到 origin 仓库的 main 分支 (如果你的仓库使用其他分支，请替换 main)
        ```

8.  **创建 Pull Request (PR)(拉取请求)（重要）**
    *   访问你在 GitHub 账号下的 Fork 仓库。
    *   GitHub 会提示你 "Contribute" ，点击这个按钮，然后再点击 "Compare & pull request" 。
    *   填写 PR 的标题和描述信息，描述你添加了什么插件，以及插件的功能和您的插件测试截图。
    *   点击 "Create pull request" 按钮，提交你的 PR。

> [!Important]
> 
> 请注意，在进行拉取请求的创建时，请确保您已经完成了您的插件的测试，并且详细描述您的插件的功能,如果**您在创建拉取请求时没有对于您的插件进行测试或者发生了任何因为没有仔细阅读Jianer_QQ_bot插件规范/Jianer_Plugin_Index插件上传教程导致的一切问题**，均由插件开发者（您）来承担

9.  **等待审核**
    *   仓库维护者会审核你的 PR，如果一切符合规范，你的插件将被合并到主仓库中。

**插件目录结构示例**

```
Jianer_Plugins_Index/
├── Plugin_A/
│   ├── Plugin_A.py
│   ├── requirements.txt
│   └── README.md (可选)
└── Plugin_B/
    ├── Plugin_B/
    │   ├── setup.py
    │   └── ...
    ├── requirements.txt
    └── README.md (可选)
```

**关于 Git 命令的补充说明：**

*   **`git clone`**:  将远程仓库复制到本地。
*   **`git add`**:  将文件添加到暂存区，准备提交。
    *   `git add .`  暂存所有更改。
    *   `git add <file_name>` 暂存指定文件。
*   **`git commit`**:  提交暂存区的更改，并添加描述信息。
*   **`git push`**:  将本地更改推送到远程仓库。
*   **`origin`**:  远程仓库的别名，通常指向你 Fork 的仓库。
*   **`main` (或 `master`)**:  分支名称，指定要推送到的分支。

至此，你已成功完成了插件上传。

> [!Caution]
> 
> 作为一名合格的开发者，你不应该开发具有成人色情、暴力、血腥等违反 GitHub 社区规定 的插件上传至仓库，也不应改动别人的插件文件夹。**一经审查发现有以上行为，将会被删除插件，并在一段时间内撤销其推送权限。**

## ⬇ 如何下载、更新和卸载
1.	在设置向导中打开插件中心
2.	点击想要下载或更新的插件
3.	在弹出的窗口中，点击下载、更新或卸载

## ⚖ 许可证
如在对应的插件文件夹下无 LICENCE/LICENSE 文件，且开发者未在对应的插件文件夹下的 README.md 中特殊说明，本插件中心的全部插件均适用于 MIT 协议，协议署名默认为 Pull Requests 的发起者或推送者的 Github 昵称。

**[SR思锐 团队](https://github.com/SRInternet-Studio/) 不保留第三方开发者的插件的所有权利。**

## ❕ 关于
本文基于插件规范版本 NEXT 3 编写。插件可能基于 [HypeR](https://github.com/HarcicYang/HypeR_Bot) 框架和 OneBot 11 框架。
