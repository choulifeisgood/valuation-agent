import type { FootballField } from '../types'

interface FootballFieldChartProps {
  data: FootballField
  currency: string
}

export default function FootballFieldChart({ data, currency }: FootballFieldChartProps) {
  const { current_price, bars } = data

  if (!bars || bars.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500">
        無法生成估值區間圖表
      </div>
    )
  }

  // Find min and max for scaling
  const allValues = bars.flatMap(b => [b.low, b.mid, b.high]).filter(v => v > 0)
  const minValue = Math.min(...allValues, current_price) * 0.9
  const maxValue = Math.max(...allValues, current_price) * 1.1
  const range = maxValue - minValue

  const getPosition = (value: number) => {
    return ((value - minValue) / range) * 100
  }

  const formatPrice = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  const getBarColor = (index: number) => {
    const colors = [
      'bg-blue-500',
      'bg-emerald-500',
      'bg-violet-500',
      'bg-amber-500',
    ]
    return colors[index % colors.length]
  }

  const getLightColor = (index: number) => {
    const colors = [
      'bg-blue-200',
      'bg-emerald-200',
      'bg-violet-200',
      'bg-amber-200',
    ]
    return colors[index % colors.length]
  }

  return (
    <div className="space-y-4">
      {/* Chart */}
      <div className="relative pt-8 pb-4 ml-28">
        {/* Current Price Line */}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-red-500 z-10"
          style={{ left: `${getPosition(current_price)}%` }}
        >
          <div className="absolute -top-6 left-1/2 -translate-x-1/2 whitespace-nowrap">
            <span className="px-2 py-1 bg-red-500 text-white text-xs rounded font-medium">
              現價 {formatPrice(current_price)}
            </span>
          </div>
        </div>

        {/* Bars */}
        <div className="space-y-3">
          {bars.map((bar, index) => (
            <div key={index} className="relative h-10">
              {/* Method Label */}
              <div className="absolute right-full mr-3 top-1/2 -translate-y-1/2 text-sm font-medium text-slate-700 whitespace-nowrap w-24 text-right">
                {bar.method}
              </div>

              {/* Bar Background (full range) */}
              <div
                className={`absolute h-full rounded-lg ${getLightColor(index)}`}
                style={{
                  left: `${getPosition(bar.low)}%`,
                  width: `${getPosition(bar.high) - getPosition(bar.low)}%`
                }}
              />

              {/* Bar Center (mid point) */}
              <div
                className={`absolute top-1/2 -translate-y-1/2 w-2 h-6 rounded ${getBarColor(index)}`}
                style={{ left: `${getPosition(bar.mid)}%`, marginLeft: '-4px' }}
              />

              {/* Low value */}
              <div
                className="absolute top-full mt-1 text-xs text-slate-500"
                style={{ left: `${getPosition(bar.low)}%`, transform: 'translateX(-50%)' }}
              >
                {formatPrice(bar.low)}
              </div>

              {/* High value */}
              <div
                className="absolute top-full mt-1 text-xs text-slate-500"
                style={{ left: `${getPosition(bar.high)}%`, transform: 'translateX(-50%)' }}
              >
                {formatPrice(bar.high)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center gap-4 justify-center pt-6 border-t border-slate-100">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
          <span className="text-sm text-slate-600">現價</span>
        </div>
        {bars.map((bar, index) => (
          <div key={index} className="flex items-center gap-2">
            <div className={`w-3 h-3 ${getBarColor(index)} rounded`}></div>
            <span className="text-sm text-slate-600">{bar.method}</span>
          </div>
        ))}
      </div>

      {/* Interpretation */}
      <div className="text-center text-sm text-slate-500 mt-4">
        {current_price < bars[bars.length - 1]?.low ? (
          <span className="text-green-600">現價低於估值區間下緣，可能存在低估</span>
        ) : current_price > bars[bars.length - 1]?.high ? (
          <span className="text-red-600">現價高於估值區間上緣，可能存在高估</span>
        ) : (
          <span>現價位於估值區間內，估值相對合理</span>
        )}
      </div>
    </div>
  )
}
