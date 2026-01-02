import { useState, KeyboardEvent } from 'react'

interface SearchInputProps {
  onSearch: (ticker: string, useDemo: boolean) => void
  disabled?: boolean
}

export default function SearchInput({ onSearch, disabled }: SearchInputProps) {
  const [value, setValue] = useState('')
  const [useDEMO, setUseDEMO] = useState(false)

  const handleSubmit = () => {
    const ticker = value.trim().toUpperCase()
    if (ticker) {
      onSearch(ticker, useDEMO)
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !disabled) {
      handleSubmit()
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <svg
            className="h-5 w-5 text-slate-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value.toUpperCase())}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="輸入股票代碼 (如 AAPL, MSFT, GOOGL)"
          className="w-full pl-12 pr-32 py-4 text-lg border-2 border-slate-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none transition-all disabled:bg-slate-100 disabled:cursor-not-allowed"
        />
        <button
          onClick={handleSubmit}
          disabled={disabled || !value.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-300 focus:outline-none transition-colors disabled:bg-slate-300 disabled:cursor-not-allowed"
        >
          {disabled ? '分析中...' : '開始分析'}
        </button>
      </div>
      <div className="mt-3 flex items-center justify-center gap-2">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={useDEMO}
            onChange={(e) => setUseDEMO(e.target.checked)}
            disabled={disabled}
            className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
          />
          <span className="text-sm text-slate-600">
            DEMO 模式
          </span>
        </label>
        <span className="text-xs text-slate-400">
          (使用模擬數據，避免 API 限流)
        </span>
      </div>
      <p className="mt-2 text-center text-sm text-slate-500">
        按 Enter 或點擊按鈕開始分析
      </p>
    </div>
  )
}
