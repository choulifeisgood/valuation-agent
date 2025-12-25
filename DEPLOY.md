# 部署指南 - AI 股票估值助手

本指南說明如何將應用部署到 Vercel（前端）+ Render（後端），讓搜尋引擎可以收錄。

---

## 前置需求

1. [GitHub 帳號](https://github.com)
2. [Vercel 帳號](https://vercel.com) - 可用 GitHub 登入
3. [Render 帳號](https://render.com) - 可用 GitHub 登入

---

## 步驟一：上傳程式碼到 GitHub

### 1.1 初始化 Git 倉庫

```bash
cd "C:\claude code project\valuation-agent"
git init
git add .
git commit -m "Initial commit: AI Stock Valuation Agent"
```

### 1.2 創建 GitHub Repository

1. 前往 https://github.com/new
2. Repository name: `valuation-agent`
3. 設為 Public（讓搜尋引擎可以看到）
4. 點擊 "Create repository"

### 1.3 推送到 GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/valuation-agent.git
git branch -M main
git push -u origin main
```

---

## 步驟二：部署後端到 Render

### 2.1 創建 Web Service

1. 登入 https://dashboard.render.com
2. 點擊 "New +" → "Web Service"
3. 連接您的 GitHub 帳號（如果尚未連接）
4. 選擇 `valuation-agent` repository

### 2.2 配置服務

| 設定項目 | 值 |
|---------|-----|
| Name | `valuation-agent-api` |
| Region | 選擇最近的區域 (如 Singapore) |
| Branch | `main` |
| Root Directory | `backend` |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |

### 2.3 設定環境變數

在 "Environment" 區塊添加：

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.0` |
| `DEBUG` | `false` |
| `CORS_ORIGINS` | `https://your-frontend.vercel.app` (稍後更新) |

### 2.4 點擊 "Create Web Service"

等待部署完成後，您會獲得一個網址，例如：
```
https://valuation-agent-api.onrender.com
```

**記住這個網址，後續步驟需要使用！**

---

## 步驟三：部署前端到 Vercel

### 3.1 導入專案

1. 登入 https://vercel.com
2. 點擊 "Add New..." → "Project"
3. 選擇 `valuation-agent` repository

### 3.2 配置專案

| 設定項目 | 值 |
|---------|-----|
| Framework Preset | `Vite` |
| Root Directory | `frontend` |
| Build Command | `npm run build` |
| Output Directory | `dist` |

### 3.3 設定環境變數

點擊 "Environment Variables" 添加：

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://valuation-agent-api.onrender.com` (您的 Render 網址) |

### 3.4 點擊 "Deploy"

等待部署完成後，您會獲得一個網址，例如：
```
https://valuation-agent.vercel.app
```

---

## 步驟四：更新 CORS 設定

### 4.1 回到 Render Dashboard

1. 進入 `valuation-agent-api` 服務
2. 點擊 "Environment" 標籤
3. 更新 `CORS_ORIGINS` 為您的 Vercel 網址：
   ```
   https://valuation-agent.vercel.app
   ```
4. 點擊 "Save Changes"
5. 服務會自動重新部署

---

## 步驟五：更新 SEO 設定

### 5.1 更新 meta tags

編輯 `frontend/index.html`，將所有 `your-domain.vercel.app` 替換為您的實際網址：

```html
<link rel="canonical" href="https://valuation-agent.vercel.app/" />
<meta property="og:url" content="https://valuation-agent.vercel.app/" />
```

### 5.2 更新 sitemap.xml

編輯 `frontend/public/sitemap.xml`：

```xml
<loc>https://valuation-agent.vercel.app/</loc>
```

### 5.3 更新 robots.txt

編輯 `frontend/public/robots.txt`：

```
Sitemap: https://valuation-agent.vercel.app/sitemap.xml
```

### 5.4 推送更新

```bash
git add .
git commit -m "Update SEO with production URLs"
git push
```

Vercel 會自動重新部署。

---

## 步驟六：提交到搜尋引擎

### 6.1 Google Search Console

1. 前往 https://search.google.com/search-console
2. 添加資源 → 輸入您的網址
3. 通過 HTML 標籤或 DNS 驗證所有權
4. 提交 sitemap：`https://your-domain.vercel.app/sitemap.xml`

### 6.2 Bing Webmaster Tools

1. 前往 https://www.bing.com/webmasters
2. 添加網站
3. 驗證所有權
4. 提交 sitemap

---

## 完成！

您的網站現在已經：
- ✅ 部署到公開網址
- ✅ 可被搜尋引擎收錄
- ✅ 具有 SEO 優化
- ✅ 支援社群分享 (Open Graph)

---

## 常見問題

### Q: 後端 API 很慢怎麼辦？
A: Render 免費方案會在閒置時休眠，首次請求需要 30-60 秒喚醒。升級付費方案可避免休眠。

### Q: 如何使用自訂網域？
A:
- Vercel: Settings → Domains → 添加您的網域
- Render: Settings → Custom Domains → 添加網域
- 記得在 DNS 添加 CNAME 記錄

### Q: API 請求失敗？
A: 檢查：
1. CORS_ORIGINS 是否設定正確
2. VITE_API_URL 是否指向正確的 Render 網址
3. Render 服務是否正常運行

### Q: 如何查看錯誤日誌？
A:
- Vercel: 專案頁面 → Logs
- Render: 服務頁面 → Logs

---

## 免費方案限制

| 平台 | 限制 |
|------|------|
| Vercel Free | 100GB 流量/月, 無限部署 |
| Render Free | 750小時/月, 閒置會休眠, 512MB RAM |

對於個人專案或 MVP，免費方案通常足夠使用。
