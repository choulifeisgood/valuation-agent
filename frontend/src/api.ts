import axios from 'axios'
import type { AnalysisResult } from './types'

// 生產環境使用環境變數，開發環境使用 proxy
const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : '/api'

// 創建 axios 實例
const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 60000, // 60 秒超時（估值計算可能較慢）
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
