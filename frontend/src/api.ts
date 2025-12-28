import axios from 'axios'
import type { AnalysisResult } from './types'

// 後端 API 網址 - Production
const API_BASE = 'https://valuation-agent-1.onrender.com/api'

// 創建 axios 實例
const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 120 秒超時（Render 免費方案喚醒需要時間）
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function analyzeStock(ticker: string): Promise<AnalysisResult> {
  const response = await apiClient.post('/analyze', { ticker })
  return response.data
}

export async function getQuickQuote(ticker: string) {
  const response = await apiClient.get('/quick-quote', {
    params: { ticker }
  })
  return response.data
}

export async function healthCheck() {
  const response = await apiClient.get('/health')
  return response.data
}
