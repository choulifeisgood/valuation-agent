"""
Valuation Agent - 負責計算內在價值 (DCF) 與相對估值
"""
from typing import Dict, Any, List
from config import Config
from models.dcf import DCFModel
from models.relative import RelativeValuation


class ValuationAgent:
    """估值計算 Agent - 整合 DCF 與相對估值"""

    def __init__(self):
        self.dcf_model = DCFModel()
        self.relative_model = RelativeValuation()

    def calculate_valuation(self, stock_data: Dict[str, Any], risk_scores: Dict[str, Any]) -> Dict[str, Any]:
        """
        計算完整估值
        包含: DCF 內在價值、相對估值、估值區間
        """
        # 獲取 WACC 調整
        overall_risk = risk_scores.get('overall_risk', {})
        wacc_adjustment = overall_risk.get('wacc_adjustment', 0)

        # 1. 計算 DCF 價值
        dcf_result = self.dcf_model.calculate(stock_data, wacc_adjustment)

        # 2. 計算相對估值
        relative_result = self.relative_model.calculate(stock_data)

        # 3. 綜合估值區間
        fair_value_range = self._calculate_fair_value_range(dcf_result, relative_result)

        # 4. 投資建議
        current_price = stock_data.get('current_price', 0)
        recommendation = self._get_recommendation(current_price, fair_value_range)

        return {
            'dcf': dcf_result,
            'relative': relative_result,
            'fair_value_range': fair_value_range,
            'recommendation': recommendation,
            'wacc_used': dcf_result.get('wacc'),
            'methodology_weights': {
                'dcf': 0.5,
                'relative': 0.5
            }
        }

    def _calculate_fair_value_range(self, dcf: Dict, relative: Dict) -> Dict[str, Any]:
        """計算綜合估值區間"""
        values = []

        # 收集所有估值點
        if dcf.get('intrinsic_value'):
            values.append(dcf['intrinsic_value'])

        if relative.get('pe_implied_price'):
            values.append(relative['pe_implied_price'])

        if relative.get('ev_ebitda_implied_price'):
            values.append(relative['ev_ebitda_implied_price'])

        if relative.get('ev_revenue_implied_price'):
            values.append(relative['ev_revenue_implied_price'])

        if not values:
            return {'low': None, 'mid': None, 'high': None}

        # 計算區間
        values = [v for v in values if v and v > 0]
        if not values:
            return {'low': None, 'mid': None, 'high': None}

        values.sort()

        # 使用四分位數
        n = len(values)
        if n == 1:
            mid = values[0]
            low = mid * 0.85
            high = mid * 1.15
        elif n == 2:
            low = values[0]
            high = values[1]
            mid = (low + high) / 2
        else:
            low = values[0]
            high = values[-1]
            mid = sum(values) / n

        return {
            'low': round(low, 2),
            'mid': round(mid, 2),
            'high': round(high, 2),
            'values_used': len(values)
        }

    def _get_recommendation(self, current_price: float, fair_value: Dict) -> Dict[str, Any]:
        """生成投資建議"""
        if not current_price or not fair_value.get('mid'):
            return {
                'rating': 'UNKNOWN',
                'description': '無法計算估值',
                'upside': None
            }

        mid_value = fair_value['mid']
        low_value = fair_value.get('low', mid_value * 0.85)
        high_value = fair_value.get('high', mid_value * 1.15)

        upside = (mid_value - current_price) / current_price

        # 建議邏輯
        if current_price < low_value * 0.9:  # 低於低估值 10%
            rating = 'STRONG_BUY'
            description = '顯著低估 - 股價遠低於合理價值區間'
        elif current_price < low_value:  # 低於低估值
            rating = 'BUY'
            description = '低估 - 股價低於估值區間下緣'
        elif current_price < mid_value:  # 低於中間值
            rating = 'ACCUMULATE'
            description = '略低估 - 股價低於中間估值'
        elif current_price <= high_value:  # 在區間內
            rating = 'HOLD'
            description = '合理估值 - 股價在估值區間內'
        elif current_price <= high_value * 1.1:  # 高於高估值 10% 內
            rating = 'REDUCE'
            description = '略高估 - 股價高於估值區間'
        else:  # 高於高估值 10%
            rating = 'SELL'
            description = '顯著高估 - 股價遠高於合理價值'

        return {
            'rating': rating,
            'description': description,
            'upside': round(upside * 100, 1),  # 百分比
            'current_price': current_price,
            'target_price': round(mid_value, 2)
        }
