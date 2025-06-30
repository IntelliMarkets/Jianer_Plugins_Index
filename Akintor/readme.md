# Akintor

这是一个基于Akintor-Python库调用Akintor在Bot进行猜人游戏的插件，由于Akintor_Python库原本的请求会被Cloudflare(以下简称CF)阻拦,导致无法正常启动,为此，我们将Akintor_Python库的请求源码放到了插件里，使用cloudscraper绕过CF请求来进行游戏

## 功能特性

- 🚀 问题可以以图片(image),文字(text发送)
- ⚙️ 图片发送模式下,在22:00~次日06:00时图片将是深色,防止Sr夜间爆炸(
- 💬 提供使用帮助信息
- 🔒 内置错误处理和友好提示
- 📦 可配置化设计，通过JSON文件管理设置

## 安装与配置

### 依赖安装

```
pip install cloudscraper bs4 pyyaml
```

## 使用方法

### 基础命令

```
[触发机器人的命令，如-]猜人
-猜人 #触发游戏
-更改AKI发送状态 #更改发送模式text image
回答问题时根据bot给的提示进行回答即可(回答问题时无需加触发机器人的命令)
```

## 自定义配置


| 配置项            | 说明                    | 默认值     |
| :---------------- | :---------------------- | :--------- |
| `reminder`        | 命令前缀符号            | `你设置的` |
| `TRIGGHT_KEYWORD` | 触发关键词 (代码中修改) | `猜人`     |

## config.yaml


| 配置项     | 说明                               | 默认值 |
| :--------- | :--------------------------------- | :----- |
| `lang`     | 语言                               | `cn`   |
| `proxyurl` | 代理地址(如服务器在国内则需要配置) | `null` |


| `sendmode` | 发送模式 | `image` |
| :--------- | :------- | :------ |

### 代理配置(CF Worker)

打开以下网址

https://github.com/ymyuuu/Cloudflare-Workers-Proxy

复制worker.js里面的全部内容，打开[CF](https://dash.cloudflare.com)

1. 注册 Cloudflare 账户：如果您尚未拥有 Cloudflare 账户，请在 [Cloudflare 官方网站](https://www.cloudflare.com/) 上注册一个账户。
2. 创建 Workers 脚本：登录到 Cloudflare 账户后，进入 "Workers" 部分，创建一个新的 Workers 脚本。
3. 将提供的反向代理脚本(worker.js)粘贴到 Workers 编辑器中。
4. 保存并部署：保存脚本后，点击 "Deploy" 按钮，以部署您的 Workers 脚本。
5. 配置域名：在 Cloudflare 中，将您的域名与部署的 Workers 脚本关联。确保将流量路由到您的 Workers 脚本。(没有自己的域名用cf默认的worker.dev域名国内可能无法使用))
6. 将域名填写在config.yaml中的proxyurl即可，注意，url最后面一定要有/
