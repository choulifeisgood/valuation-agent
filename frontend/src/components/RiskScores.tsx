import type { RiskAssessment } from '../types'

interface RiskScoresProps {
  data: RiskAssessment
}

export default function RiskScores({ data }: RiskScoresProps) {
  const { altman_z_score, piotroski_f_score, overall_risk, risk_flags } = data

  const getZoneColor = (zone: string) => {
    switch (zone) {
      case 'SAFE':
        return 'bg-green-500'
      case 'GREY':
        return 'bg-yellow-500'
      case 'DISTRESS':
        return 'bg-red-500'
      default:
        return 'bg-slate-400'
    }
  }

  const getZoneLabel = (zone: string) => {
    switch (zone) {
      case 'SAFE':
        return '安全區'
      case 'GREY':
        return '灰色區'
      case 'DISTRESS':
        return '困境區'
      default:
        return '未知'
    }
  }

  const getRatingColor = (rating: string) => {
    switch (rating) {
      case 'STRONG':
        return 'text-green-600'
      case 'MODERATE':
        return 'text-yellow-600'
      case 'WEAK':
        return 'text-red-600'
      default:
        return 'text-slate-600'
    }
  }

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'LOW':
        return 'bg-green-100 text-green-800 border-green-300'
      case 'MODERATE':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'ELEVATED':
        return 'bg-orange-100 text-orange-800 border-orange-300'
      case 'HIGH':
        return 'bg-red-100 text-red-800 border-red-300'
      default:
        return 'bg-slate-100 text-slate-800 border-slate-300'
    }
  }

  const getRiskLevelLabel = (level: string) => {
    switch (level) {
      case 'LOW':
        return '低風險'
      case 'MODERATE':
        return '中等風險'
      case 'ELEVATED':
        return '中高風險'
      case 'HIGH':
        return '高風險'
      default:
        return '未知'
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-800">
          風險評估
        </h3>
        <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getRiskLevelColor(overall_risk.level)}`}>
          {getRiskLevelLabel(overall_risk.level)}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Altman Z-Score */}
        <div className="p-4 bg-slate-50 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium text-slate-700">Altman Z-Score</h4>
            <span className={`w-3 h-3 rounded-full ${getZoneColor(altman_z_score.zone)}`}></span>
          </div>
          <div className="flex items-end gap-2 mb-2">
            <span className="text-3xl font-bold text-slate-800">
              {altman_z_score.score !== null ? altman_z_score.score.toFixed(2) : 'N/A'}
            </span>
            <span className={`text-sm font-medium px-2 py-0.5 rounded ${getZoneColor(altman_z_score.zone)} text-white`}>
              {getZoneLabel(altman_z_score.zone)}
            </span>
          </div>
          <p className="text-sm text-slate-500">{altman_z_score.interpretation}</p>

          {/* Z-Score Scale */}
          <div className="mt-3">
            <div className="relative h-2 bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 rounded-full">
              {altman_z_score.score !== null && (
                <div
                  className="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-white border-2 border-slate-800 rounded-full"
                  style={{
                    left: `${Math.min(Math.max((altman_z_score.score / 5) * 100, 0), 100)}%`,
                    transform: 'translate(-50%, -50%)'
                  }}
                />
              )}
            </div>
            <div className="flex justify-between text-xs text-slate-400 mt-1">
              <span>1.81</span>
              <span>2.99</span>
              <span>5.0+</span>
            </div>
          </div>
        </div>

        {/* Piotroski F-Score */}
        <div className="p-4 bg-slate-50 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium text-slate-700">Piotroski F-Score</h4>
          </div>
          <div className="flex items-end gap-2 mb-2">
            <span className="text-3xl font-bold text-slate-800">
              {piotroski_f_score.score !== null ? piotroski_f_score.score : 'N/A'}
            </span>
            <span className="text-slate-500">/ {piotroski_f_score.max_score}</span>
            <span className={`text-sm font-medium ${getRatingColor(piotroski_f_score.rating)}`}>
              ({piotroski_f_score.rating})
            </span>
          </div>
          <p className="text-sm text-slate-500">{piotroski_f_score.interpretation}</p>

          {/* F-Score Bar */}
          <div className="mt-3">
            <div className="flex gap-1">
              {Array.from({ length: 9 }).map((_, i) => (
                <div
                  key={i}
                  className={`flex-1 h-2 rounded ${
                    piotroski_f_score.score !== null && i < piotroski_f_score.score
                      ? i < 4 ? 'bg-red-400' : i < 7 ? 'bg-yellow-400' : 'bg-green-400'
                      : 'bg-slate-200'
                  }`}
                />
              ))}
            </div>
            <div className="flex justify-between text-xs text-slate-400 mt-1">
              <span>弱</span>
              <span>中</span>
              <span>強</span>
            </div>
          </div>
        </div>
      </div>

      {/* Risk Flags */}
      {risk_flags.length > 0 && (
        <div>
          <h4 className="font-medium text-slate-700 mb-3">風險警示</h4>
          <div className="space-y-2">
            {risk_flags.map((flag, index) => (
              <div
                key={index}
                className={`flex items-start gap-3 p-3 rounded-lg ${
                  flag.type === 'CRITICAL'
                    ? 'bg-red-50 border border-red-200'
                    : 'bg-yellow-50 border border-yellow-200'
                }`}
              >
                <span className="text-lg">
                  {flag.type === 'CRITICAL' ? '🚨' : '⚠️'}
                </span>
                <div>
                  <p className={`font-medium ${
                    flag.type === 'CRITICAL' ? 'text-red-800' : 'text-yellow-800'
                  }`}>
                    {flag.flag.replace(/_/g, ' ')}
                  </p>
                  <p className={`text-sm ${
                    flag.type === 'CRITICAL' ? 'text-red-600' : 'text-yellow-600'
                  }`}>
                    {flag.message}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {risk_flags.length === 0 && (
        <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
          <span className="text-lg">✅</span>
          <p className="text-green-800">未發現重大風險警示</p>
        </div>
      )}
    </div>
  )
}
