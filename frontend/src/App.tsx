import { useState } from 'react'
import SearchInput from './components/SearchInput'
import ValuationReport from './components/ValuationReport'
import LoadingSpinner from './components/LoadingSpinner'
import { analyzeStock } from './api'
import type { AnalysisResult } from './types'

function App() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<AnalysisResult | null>(null)

  const handleSearch = async (ticker: string, useDemo: boolean = false) => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const data = await analyzeStock(ticker, useDemo)
      if (data.error) {
        setError(data.error)
      } else {
        setResult(data)
      }
    } catch (err: any) {
      console.error('API Error:', err)
      const errorMsg = err?.response?.data?.error || err?.message || '未知錯誤'
      setError(`連接失敗: ${errorMsg} (API: https://valuation-agent-1.onrender.com)`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-slate-800">
              AI 股票估值助手
            </h1>
            <p className="mt-2 text-slate-600">
              輸入股票代碼，獲取華爾街等級的估值分析報告
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Search Section */}
        <div className="mb-8">
          <SearchInput onSearch={handleSearch} disabled={loading} />
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-16">
            <LoadingSpinner />
            <p className="mt-4 text-slate-600">正在分析股票數據...</p>
            <p className="mt-2 text-sm text-slate-500">
              首次請求可能需要 30-60 秒（伺服器喚醒中），請耐心等候
            </p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <div className="text-red-600 text-lg font-medium mb-2">
              分析失敗
            </div>
            <p className="text-red-500">{error}</p>
          </div>
        )}

        {/* Result */}
        {result && !loading && (
          <ValuationReport data={result} />
        )}

        {/* Empty State */}
        {!loading && !error && !result && (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">📊</div>
            <h2 className="text-xl font-medium text-slate-700 mb-2">
              開始您的估值分析
            </h2>
            <p className="text-slate-500">
              輸入美股代碼（如 AAPL、MSFT、GOOGL）開始分析
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-2">
              {['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'].map((ticker) => (
                <button
                  key={ticker}
                  onClick={() => handleSearch(ticker)}
                  className="px-4 py-2 bg-white border border-slate-300 rounded-full text-sm text-slate-600 hover:bg-slate-50 hover:border-slate-400 transition-colors"
                >
                  {ticker}
                </button>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-sm text-slate-500">
          <p>本報告僅供參考，不構成投資建議。投資有風險，入市需謹慎。</p>
          <p className="mt-2">
            資料來源: Yahoo Finance | 估值方法: DCF + 相對估值
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
