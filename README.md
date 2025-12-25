# AI 股票估值助手

一個基於 AI Agent 架構的股票估值分析網頁應用。輸入股票代碼後，系統會自動從 Yahoo Finance 獲取數據，執行 DCF 內在價值計算、相對估值分析、風險評分，並生成專業的投資建議報告。

## 功能特點

- **DCF 估值模型**: 基於 FCFF 方法計算內在價值
- **相對估值**: P/E、EV/EBITDA、EV/Revenue 倍數分析
- **風險評分**:
  - Altman Z-Score (破產風險預測)
  - Piotroski F-Score (財務體質評估)
- **足球場圖 (Football Field Chart)**: 視覺化估值區間
- **投資建議**: 自動生成買入/持有/賣出建議

## 技術棧

- **前端**: React + TypeScript + Tailwind CSS + Vite
- **後端**: Python Flask + yfinance
- **數據來源**: Yahoo Finance (免費 API)

## 快速開始

### 方法一：使用啟動腳本 (Windows)

1. 雙擊 `start.bat` 啟動腳本
2. 腳本會自動安裝依賴並啟動前後端服務
3. 瀏覽器會自動開啟 http://localhost:3000

### 方法二：手動啟動

#### 1. 安裝後端依賴
```bash
cd backend
pip install -r requirements.txt
```

#### 2. 啟動後端服務
```bash
cd backend
python app.py
```
後端會在 http://localhost:5000 運行

#### 3. 安裝前端依賴
```bash
cd frontend
npm install
```

#### 4. 啟動前端服務
```bash
cd frontend
npm run dev
```
前端會在 http://localhost:3000 運行

## 使用說明

1. 在搜尋框輸入美股代碼 (如 AAPL, MSFT, GOOGL)
2. 按 Enter 或點擊「開始分析」按鈕
3. 等待幾秒鐘，系統會生成完整的估值報告

## 專案結構

```
valuation-agent/
├── frontend/                 # React 前端
│   ├── src/
│   │   ├── components/      # React 組件
│   │   ├── App.tsx          # 主應用
│   │   ├── api.ts           # API 調用
│   │   └── types.ts         # TypeScript 類型
│   └── package.json
│
├── backend/                  # Python Flask 後端
│   ├── app.py               # Flask 主應用
│   ├── agents/              # AI Agent 模組
│   │   ├── data_agent.py    # 數據獲取
│   │   ├── forensic_agent.py # 風險評分
│   │   ├── valuation_agent.py # 估值計算
│   │   └── synthesis_agent.py # 報告生成
│   ├── models/              # 估值模型
│   │   ├── dcf.py           # DCF 模型
│   │   ├── relative.py      # 相對估值
│   │   └── risk_scores.py   # 風險評分
│   └── requirements.txt
│
├── start.bat                # Windows 啟動腳本
└── README.md
```

## API 端點

### POST /api/analyze
分析股票並返回估值報告

**請求:**
```json
{
  "ticker": "AAPL"
}
```

**回應:**
```json
{
  "basic_info": { ... },
  "valuation": { ... },
  "risk_assessment": { ... },
  "recommendation": { ... },
  "football_field": { ... }
}
```

### GET /api/quick-quote?ticker=AAPL
獲取快速報價

### GET /api/health
健康檢查

## 注意事項

- 本應用使用 Yahoo Finance 的免費 API，可能有請求頻率限制
- 估值結果僅供參考，不構成投資建議
- 部分財務數據可能因數據源限制而缺失

## 後續擴展

- [ ] FinBERT 情緒分析整合
- [ ] Monte Carlo 模擬
- [ ] Beneish M-Score (造假偵測)
- [ ] ML 同業聚類
- [ ] 用戶認證與儲存
