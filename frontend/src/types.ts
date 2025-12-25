export interface AnalysisResult {
  error?: string
  basic_info: BasicInfo
  key_metrics: KeyMetrics
  valuation: ValuationSummary
  risk_assessment: RiskAssessment
  recommendation: Recommendation
  analysis_summary: string
  football_field: FootballField
  methodology: Methodology
  disclaimer: string
}

export interface BasicInfo {
  ticker: string
  company_name: string
  sector: string
  industry: string
  currency: string
  current_price: number
  market_cap: number
  analysis_date: string
}

export interface KeyMetrics {
  valuation_ratios: {
    pe_ratio: number | null
    forward_pe: number | null
    pb_ratio: number | null
    ps_ratio: number | null
    ev_ebitda: number | null
    ev_revenue: number | null
  }
  profitability: {
    profit_margin: string | null
    operating_margin: string | null
    ebitda_margin: string | null
    roe: string | null
    roa: string | null
  }
  financial_health: {
    debt_equity: number | null
    current_ratio: number | null
  }
  growth: {
    revenue_growth: string | null
    earnings_growth: string | null
  }
  yield: {
    dividend_yield: string | null
    fcf_yield: string | null
  }
}

export interface ValuationSummary {
  dcf_valuation: {
    intrinsic_value: number | null
    wacc: string | null
    terminal_growth: string | null
    fcf_growth_assumed: string | null
  }
  relative_valuation: {
    pe_implied: number | null
    ev_ebitda_implied: number | null
    ev_revenue_implied: number | null
    peer_median_pe: number | null
    peer_median_ev_ebitda: number | null
  }
  fair_value_range: {
    low: number | null
    mid: number | null
    high: number | null
  }
}

export interface RiskAssessment {
  altman_z_score: {
    score: number | null
    zone: string
    interpretation: string
  }
  piotroski_f_score: {
    score: number | null
    max_score: number
    rating: string
    interpretation: string
  }
  overall_risk: {
    level: string
    description: string
  }
  risk_flags: RiskFlag[]
  wacc_adjustment: string | null
}

export interface RiskFlag {
  type: 'CRITICAL' | 'WARNING'
  flag: string
  message: string
}

export interface Recommendation {
  rating: string
  description: string
  upside: number | null
  current_price: number
  target_price: number
}

export interface FootballField {
  current_price: number
  bars: FootballBar[]
}

export interface FootballBar {
  method: string
  low: number
  mid: number
  high: number
}

export interface Methodology {
  dcf_weight: number
  relative_weight: number
  note: string
}
