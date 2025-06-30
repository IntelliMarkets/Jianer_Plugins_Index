# Akintor

這是一個基於Akintor-Python庫調用Akintor在Bot進行猜人遊戲的插件，由於Akintor_Python庫原本的請求會被Cloudflare(以下簡稱CF)阻攔，導致無法正常啟動，為此，我們將Akintor_Python庫的請求源碼放到了插件裡，使用cloudscraper繞過CF請求來進行遊戲

## 功能特性

- 🚀 問題可以以圖片(image)、文字(text)發送
- ⚙️ 圖片發送模式下，在22:00~次日06:00時圖片將是深色，防止夜間閃光(
- 💬 提供使用幫助信息
- 🔒 內置錯誤處理和友好提示
- 📦 可配置化設計，通過JSON文件管理設置

## 安裝與配置

### 依賴安裝

```
pip install cloudscraper bs4 pyyaml
```

## 使用方法

### 基礎命令

```
[觸發機器人的命令，如-]猜人
-猜人 #觸發遊戲
-更改AKI发送状态 #更改發送模式text image
回答問題時根據bot給的提示進行回答即可(回答問題時無需加觸發機器人的命令)
```

## 自定義配置


| 配置項            | 說明                    | 默認值     |
| :---------------- | :---------------------- | :--------- |
| `reminder`        | 命令前綴符號            | `你設置的` |
| `TRIGGHT_KEYWORD` | 觸發關鍵詞 (代碼中修改) | `猜人`     |

## config.yaml


| 配置項     | 說明                               | 默認值 |
| :--------- | :--------------------------------- | :----- |
| `lang`     | 語言                               | `cn`   |
| `proxyurl` | 代理地址(如服務器在國內則需要配置) | `null` |
| `sendmode` | 發送模式 | `image` |

### 代理配置(CF Worker)

打開以下網址

https://github.com/ymyuuu/Cloudflare-Workers-Proxy

複製worker.js裡面的全部內容，打開[CF](https://dash.cloudflare.com)

1. 註冊 Cloudflare 賬戶：如果您尚未擁有 Cloudflare 賬戶，請在 [Cloudflare 官方網站](https://www.cloudflare.com/) 上註冊一個賬戶。
2. 創建 Workers 腳本：登錄到 Cloudflare 賬戶後，進入 "Workers" 部分，創建一個新的 Workers 腳本。
3. 將提供的反向代理腳本(worker.js)粘貼到 Workers 編輯器中。
4. 保存並部署：保存腳本後，點擊 "Deploy" 按鈕，以部署您的 Workers 腳本。
5. 配置域名：在 Cloudflare 中，將您的域名與部署的 Workers 腳本關聯。確保將流量路由到您的 Workers 腳本。(沒有自己的域名用cf默認的worker.dev域名國內可能無法使用))
6. 將域名填寫在config.yaml中的proxyurl即可，注意，url最後面一定要有/