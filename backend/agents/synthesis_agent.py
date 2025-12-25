"""
Synthesis Agent - 負責生成最終估值報告
"""
from typing import Dict, Any
from datetime import datetime


class SynthesisAgent:
    """報告生成 Agent - 整合所有分析結果"""

    def generate_report(self, ticker: str, stock_data: Dict, risk_scores: Dict, valuation: Dict) -> Dict[str, Any]:
        """生成完整估值報告"""

        # 基本資訊
        basic_info = {
            'ticker': ticker,
            'company_name': stock_data.get('company_name', ticker),
            'sector': stock_data.get('sector', 'N/A'),
            'industry': stock_data.get('industry', 'N/A'),
            'currency': stock_data.get('currency', 'USD'),
            'current_price': stock_data.get('current_price'),
            'market_cap': stock_data.get('market_cap'),
            'analysis_date': datetime.now().isoformat(),
        }

        # 關鍵指標
        metrics = self._format_metrics(stock_data.get('metrics', {}))

        # 估值結果
        valuation_summary = self._format_valuation(valuation)

        # 風險評估
        risk_summary = self._format_risk(risk_scores)

        # 投資建議
        recommendation = valuation.get('recommendation', {})

        # 分析摘要
        analysis_summary = self._generate_summary(
            basic_info, metrics, valuation_summary, risk_summary, recommendation
        )

        # 足球場圖數據
        football_field = self._generate_football_field(valuation, stock_data.get('current_price'))

        return {
            'basic_info': basic_info,
            'key_metrics': metrics,
            'valuation': valuation_summary,
            'risk_assessment': risk_summary,
            'recommendation': recommendation,
            'analysis_summary': analysis_summary,
            'football_field': football_field,
            'methodology': {
                'dcf_weight': 0.5,
                'relative_weight': 0.5,
                'note': '估值基於 DCF 內在價值與相對估值的加權平均'
            },
            'disclaimer': '本報告僅供參考，不構成投資建議。投資有風險，入市需謹慎。'
        }

    def _format_metrics(self, metrics: Dict) -> Dict[str, Any]:
        """格式化關鍵指標"""
        return {
            'valuation_ratios': {
                'pe_ratio': self._safe_round(metrics.get('pe_ratio')),
                'forward_pe': self._safe_round(metrics.get('forward_pe')),
                'pb_ratio': self._safe_round(metrics.get('pb_ratio')),
                'ps_ratio': self._safe_round(metrics.get('ps_ratio')),
                'ev_ebitda': self._safe_round(metrics.get('ev_ebitda')),
                'ev_revenue': self._safe_round(metrics.get('ev_revenue')),
            },
            'profitability': {
                'profit_margin': self._format_percent(metrics.get('profit_margin')),
                'operating_margin': self._format_percent(metrics.get('operating_margin')),
                'ebitda_margin': self._format_percent(metrics.get('ebitda_margin')),
                'roe': self._format_percent(metrics.get('roe')),
                'roa': self._format_percent(metrics.get('roa')),
            },
            'financial_health': {
                'debt_equity': self._safe_round(metrics.get('debt_equity')),
                'current_ratio': self._safe_round(metrics.get('current_ratio')),
            },
            'growth': {
                'revenue_growth': self._format_percent(metrics.get('revenue_growth')),
                'earnings_growth': self._format_percent(metrics.get('earnings_growth')),
            },
            'yield': {
                'dividend_yield': self._format_percent(metrics.get('dividend_yield')),
                'fcf_yield': self._format_percent(metrics.get('fcf_yield')),
            }
        }

    def _format_valuation(self, valuation: Dict) -> Dict[str, Any]:
        """格式化估值結果"""
        dcf = valuation.get('dcf', {})
        relative = valuation.get('relative', {})
        fair_value = valuation.get('fair_value_range', {})

        return {
            'dcf_valuation': {
                'intrinsic_value': dcf.get('intrinsic_value'),
                'wacc': self._format_percent(dcf.get('wacc')),
                'terminal_growth': self._format_percent(dcf.get('terminal_growth')),
                'fcf_growth_assumed': self._format_percent(dcf.get('fcf_growth')),
            },
            'relative_valuation': {
                'pe_implied': relative.get('pe_implied_price'),
                'ev_ebitda_implied': relative.get('ev_ebitda_implied_price'),
                'ev_revenue_implied': relative.get('ev_revenue_implied_price'),
                'peer_median_pe': relative.get('peer_median_pe'),
                'peer_median_ev_ebitda': relative.get('peer_median_ev_ebitda'),
            },
            'fair_value_range': {
                'low': fair_value.get('low'),
                'mid': fair_value.get('mid'),
                'high': fair_value.get('high'),
            }
        }

    def _format_risk(self, risk_scores: Dict) -> Dict[str, Any]:
        """格式化風險評估"""
        altman = risk_scores.get('altman_z', {})
        piotroski = risk_scores.get('piotroski_f', {})
        overall = risk_scores.get('overall_risk', {})
        flags = risk_scores.get('risk_flags', [])

        return {
            'altman_z_score': {
                'score': altman.get('score'),
                'zone': altman.get('zone'),
                'interpretation': altman.get('zone_description'),
            },
            'piotroski_f_score': {
                'score': piotroski.get('score'),
                'max_score': 9,
                'rating': piotroski.get('rating'),
                'interpretation': piotroski.get('rating_description'),
            },
            'overall_risk': {
                'level': overall.get('level'),
                'description': overall.get('description'),
            },
            'risk_flags': flags,
            'wacc_adjustment': self._format_percent(overall.get('wacc_adjustment')),
        }

    def _generate_summary(self, basic: Dict, metrics: Dict, valuation: Dict, risk: Dict, recommendation: Dict) -> str:
        """生成文字摘要"""
        company = basic.get('company_name', basic.get('ticker'))
        current_price = basic.get('current_price', 0)
        target = recommendation.get('target_price', 0)
        upside = recommendation.get('upside', 0)
        rating = recommendation.get('rating', 'HOLD')

        # 風險評估
        risk_level = risk.get('overall_risk', {}).get('level', 'MODERATE')
        altman_zone = risk.get('altman_z_score', {}).get('zone', 'UNKNOWN')

        # 估值區間
        fair_value = valuation.get('fair_value_range', {})

        summary_parts = []

        # 開頭
        summary_parts.append(f"**{company}** 估值分析報告")
        summary_parts.append("")

        # 估值結論
        if rating in ['STRONG_BUY', 'BUY']:
            summary_parts.append(f"📈 **投資評級: {self._translate_rating(rating)}**")
            summary_parts.append(f"目前股價 ${current_price:.2f} 低於目標價 ${target:.2f}，潛在上漲空間 {upside:.1f}%。")
        elif rating in ['SELL', 'REDUCE']:
            summary_parts.append(f"📉 **投資評級: {self._translate_rating(rating)}**")
            summary_parts.append(f"目前股價 ${current_price:.2f} 高於目標價 ${target:.2f}，存在 {abs(upside):.1f}% 下行風險。")
        else:
            summary_parts.append(f"⚖️ **投資評級: {self._translate_rating(rating)}**")
            summary_parts.append(f"目前股價 ${current_price:.2f} 接近目標價 ${target:.2f}，估值相對合理。")

        summary_parts.append("")

        # 估值區間
        if fair_value.get('low') and fair_value.get('high'):
            summary_parts.append(f"**估值區間**: ${fair_value['low']:.2f} - ${fair_value['high']:.2f}")

        # 風險提示
        summary_parts.append("")
        if risk_level == 'HIGH':
            summary_parts.append("⚠️ **風險警示**: 該公司存在重大財務風險，需謹慎評估。")
        elif risk_level == 'ELEVATED':
            summary_parts.append("⚠️ **風險提示**: 該公司存在多項財務警示，建議額外關注。")
        elif altman_zone == 'DISTRESS':
            summary_parts.append("⚠️ **破產風險**: Altman Z-Score 顯示該公司處於財務困境區。")

        return "\n".join(summary_parts)

    def _generate_football_field(self, valuation: Dict, current_price: float) -> Dict[str, Any]:
        """生成足球場圖數據"""
        dcf = valuation.get('dcf', {})
        relative = valuation.get('relative', {})
        fair_value = valuation.get('fair_value_range', {})

        bars = []

        # DCF 區間 (假設 +/- 15% 敏感度)
        if dcf.get('intrinsic_value'):
            dcf_val = dcf['intrinsic_value']
            bars.append({
                'method': 'DCF 估值',
                'low': round(dcf_val * 0.85, 2),
                'mid': round(dcf_val, 2),
                'high': round(dcf_val * 1.15, 2),
            })

        # P/E 相對估值
        if relative.get('pe_implied_price'):
            pe_val = relative['pe_implied_price']
            bars.append({
                'method': 'P/E 倍數',
                'low': round(pe_val * 0.9, 2),
                'mid': round(pe_val, 2),
                'high': round(pe_val * 1.1, 2),
            })

        # EV/EBITDA 相對估值
        if relative.get('ev_ebitda_implied_price'):
            ev_val = relative['ev_ebitda_implied_price']
            bars.append({
                'method': 'EV/EBITDA',
                'low': round(ev_val * 0.9, 2),
                'mid': round(ev_val, 2),
                'high': round(ev_val * 1.1, 2),
            })

        # 綜合區間
        if fair_value.get('low'):
            bars.append({
                'method': '綜合估值',
                'low': fair_value['low'],
                'mid': fair_value['mid'],
                'high': fair_value['high'],
            })

        return {
            'current_price': current_price,
            'bars': bars
        }

    def _translate_rating(self, rating: str) -> str:
        """翻譯評級"""
        translations = {
            'STRONG_BUY': '強力買入',
            'BUY': '買入',
            'ACCUMULATE': '加碼',
            'HOLD': '持有',
            'REDUCE': '減碼',
            'SELL': '賣出',
            'UNKNOWN': '無法判斷'
        }
        return translations.get(rating, rating)

    @staticmethod
    def _safe_round(value, decimals=2):
        """安全四捨五入"""
        if value is None:
            return None
        try:
            return round(float(value), decimals)
        except:
            return None

    @staticmethod
    def _format_percent(value):
        """格式化百分比"""
        if value is None:
            return None
        try:
            return f"{float(value) * 100:.2f}%"
        except:
            return None
