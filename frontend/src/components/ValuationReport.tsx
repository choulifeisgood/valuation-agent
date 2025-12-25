import type { AnalysisResult } from '../types'
import RiskScores from './RiskScores'
import FootballFieldChart from './FootballFieldChart'

interface ValuationReportProps {
  data: AnalysisResult
}

export default function ValuationReport({ data }: ValuationReportProps) {
  const { basic_info, key_metrics, valuation, risk_assessment, recommendation, football_field } = data

  const getRatingColor = (rating: string) => {
    switch (rating) {
      case 'STRONG_BUY':
      case 'BUY':
        return 'bg-green-100 text-green-800 border-green-300'
      case 'ACCUMULATE':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300'
      case 'HOLD':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'REDUCE':
        return 'bg-orange-100 text-orange-800 border-orange-300'
      case 'SELL':
        return 'bg-red-100 text-red-800 border-red-300'
      default:
        return 'bg-slate-100 text-slate-800 border-slate-300'
    }
  }

  const getRatingLabel = (rating: string) => {
    const labels: Record<string, string> = {
      'STRONG_BUY': '強力買入',
      'BUY': '買入',
      'ACCUMULATE': '加碼',
      'HOLD': '持有',
      'REDUCE': '減碼',
      'SELL': '賣出',
      'UNKNOWN': '無法判斷'
    }
    return labels[rating] || rating
  }

  const formatCurrency = (value: number | null, currency: string = 'USD') => {
    if (value === null || value === undefined) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value)
  }

  const formatLargeNumber = (value: number | null) => {
    if (value === null || value === undefined) return 'N/A'
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`
    return `$${value.toFixed(2)}`
  }

  return (
    <div className="space-y-6">
      {/* Header Card - Company Info & Recommendation */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            {/* Company Info */}
            <div>
              <div className="flex items-center gap-3">
                <h2 className="text-2xl font-bold text-slate-800">
                  {basic_info.company_name}
                </h2>
                <span className="px-3 py-1 bg-slate-100 text-slate-600 rounded-full text-sm font-medium">
                  {basic_info.ticker}
                </span>
              </div>
              <p className="mt-1 text-slate-500">
                {basic_info.sector} | {basic_info.industry}
              </p>
              <div className="mt-2 flex items-center gap-4 text-sm">
                <span className="text-slate-600">
                  市值: {formatLargeNumber(basic_info.market_cap)}
                </span>
                <span className="text-slate-600">
                  現價: {formatCurrency(basic_info.current_price, basic_info.currency)}
                </span>
              </div>
            </div>

            {/* Recommendation Badge */}
            <div className="flex flex-col items-center md:items-end gap-2">
              <span className={`px-4 py-2 rounded-lg border-2 font-bold text-lg ${getRatingColor(recommendation.rating)}`}>
                {getRatingLabel(recommendation.rating)}
              </span>
              <div className="text-right">
                <p className="text-sm text-slate-500">目標價</p>
                <p className="text-xl font-bold text-slate-800">
                  {formatCurrency(recommendation.target_price, basic_info.currency)}
                </p>
                {recommendation.upside !== null && (
                  <p className={`text-sm font-medium ${recommendation.upside >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {recommendation.upside >= 0 ? '+' : ''}{recommendation.upside}%
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Description */}
          <p className="mt-4 text-slate-600">
            {recommendation.description}
          </p>
        </div>
      </div>

      {/* Football Field Chart */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-800 mb-4">
          估值區間分析 (Football Field)
        </h3>
        <FootballFieldChart data={football_field} currency={basic_info.currency} />
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Valuation Details */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">
            估值詳情
          </h3>

          {/* DCF */}
          <div className="mb-6">
            <h4 className="text-sm font-medium text-slate-500 uppercase tracking-wider mb-3">
              DCF 內在價值
            </h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-slate-500">內在價值</p>
                <p className="text-lg font-bold text-slate-800">
                  {formatCurrency(valuation.dcf_valuation.intrinsic_value, basic_info.currency)}
                </p>
              </div>
              <div>
                <p className="text-sm text-slate-500">WACC</p>
                <p className="text-lg font-medium text-slate-700">
                  {valuation.dcf_valuation.wacc || 'N/A'}
                </p>
              </div>
            </div>
          </div>

          {/* Relative */}
          <div className="mb-6">
            <h4 className="text-sm font-medium text-slate-500 uppercase tracking-wider mb-3">
              相對估值
            </h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-slate-500">P/E 隱含價格</p>
                <p className="text-lg font-medium text-slate-700">
                  {formatCurrency(valuation.relative_valuation.pe_implied, basic_info.currency)}
                </p>
              </div>
              <div>
                <p className="text-sm text-slate-500">EV/EBITDA 隱含價格</p>
                <p className="text-lg font-medium text-slate-700">
                  {formatCurrency(valuation.relative_valuation.ev_ebitda_implied, basic_info.currency)}
                </p>
              </div>
            </div>
          </div>

          {/* Fair Value Range */}
          <div className="p-4 bg-blue-50 rounded-lg">
            <h4 className="text-sm font-medium text-blue-800 mb-2">綜合估值區間</h4>
            <div className="flex items-center justify-between">
              <span className="text-blue-600">
                {formatCurrency(valuation.fair_value_range.low, basic_info.currency)}
              </span>
              <span className="text-xl font-bold text-blue-800">
                {formatCurrency(valuation.fair_value_range.mid, basic_info.currency)}
              </span>
              <span className="text-blue-600">
                {formatCurrency(valuation.fair_value_range.high, basic_info.currency)}
              </span>
            </div>
            <div className="flex justify-between text-xs text-blue-500 mt-1">
              <span>低估值</span>
              <span>中間值</span>
              <span>高估值</span>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">
            關鍵指標
          </h3>

          <div className="space-y-4">
            {/* Valuation Ratios */}
            <div>
              <h4 className="text-sm font-medium text-slate-500 mb-2">估值倍數</h4>
              <div className="grid grid-cols-3 gap-3">
                <MetricBox label="P/E" value={key_metrics.valuation_ratios.pe_ratio} suffix="x" />
                <MetricBox label="P/B" value={key_metrics.valuation_ratios.pb_ratio} suffix="x" />
                <MetricBox label="EV/EBITDA" value={key_metrics.valuation_ratios.ev_ebitda} suffix="x" />
              </div>
            </div>

            {/* Profitability */}
            <div>
              <h4 className="text-sm font-medium text-slate-500 mb-2">獲利能力</h4>
              <div className="grid grid-cols-3 gap-3">
                <MetricBox label="淨利率" value={key_metrics.profitability.profit_margin} />
                <MetricBox label="ROE" value={key_metrics.profitability.roe} />
                <MetricBox label="ROA" value={key_metrics.profitability.roa} />
              </div>
            </div>

            {/* Financial Health */}
            <div>
              <h4 className="text-sm font-medium text-slate-500 mb-2">財務健康</h4>
              <div className="grid grid-cols-2 gap-3">
                <MetricBox label="D/E Ratio" value={key_metrics.financial_health.debt_equity} suffix="%" />
                <MetricBox label="流動比率" value={key_metrics.financial_health.current_ratio} suffix="x" />
              </div>
            </div>

            {/* Growth */}
            <div>
              <h4 className="text-sm font-medium text-slate-500 mb-2">成長指標</h4>
              <div className="grid grid-cols-2 gap-3">
                <MetricBox label="營收成長" value={key_metrics.growth.revenue_growth} />
                <MetricBox label="盈餘成長" value={key_metrics.growth.earnings_growth} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Risk Assessment */}
      <RiskScores data={risk_assessment} />

      {/* Analysis Summary */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-800 mb-4">
          分析摘要
        </h3>
        <div className="prose prose-slate max-w-none">
          {data.analysis_summary.split('\n').map((line, i) => (
            <p key={i} className="text-slate-600 mb-2">
              {line}
            </p>
          ))}
        </div>
        <p className="mt-4 text-sm text-slate-400 italic">
          {data.disclaimer}
        </p>
      </div>
    </div>
  )
}

// Helper component for metrics
function MetricBox({ label, value, suffix = '' }: { label: string; value: number | string | null; suffix?: string }) {
  const displayValue = value === null || value === undefined ? 'N/A' :
    typeof value === 'string' ? value :
    `${value.toFixed(2)}${suffix}`

  return (
    <div className="p-3 bg-slate-50 rounded-lg">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="text-sm font-semibold text-slate-700">{displayValue}</p>
    </div>
  )
}
