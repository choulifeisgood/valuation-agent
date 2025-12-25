"""
Forensic Agent - 負責計算風險評分與財務體質分析
"""
from typing import Dict, Any
from config import Config


class ForensicAgent:
    """風險評估 Agent - 計算 Altman Z-Score、Piotroski F-Score"""

    def calculate_risk_scores(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """計算所有風險評分"""
        balance = stock_data.get('balance_sheet', {})
        income = stock_data.get('income_statement', {})
        cash_flow = stock_data.get('cash_flow', {})
        info = stock_data.get('info', {})

        # 計算各項風險評分
        altman = self._calculate_altman_z(balance, income, info)
        piotroski = self._calculate_piotroski_f(balance, income, cash_flow)

        # 綜合風險評估
        risk_flags = self._evaluate_risk_flags(altman, piotroski, stock_data)

        return {
            'altman_z': altman,
            'piotroski_f': piotroski,
            'risk_flags': risk_flags,
            'overall_risk': self._get_overall_risk(altman, piotroski, risk_flags)
        }

    def _calculate_altman_z(self, balance: Dict, income: Dict, info: Dict) -> Dict[str, Any]:
        """
        計算 Altman Z-Score (破產預測)
        Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5

        X1 = Working Capital / Total Assets
        X2 = Retained Earnings / Total Assets
        X3 = EBIT / Total Assets
        X4 = Market Cap / Total Liabilities
        X5 = Revenue / Total Assets
        """
        try:
            total_assets = balance.get('total_assets', 0)
            if total_assets == 0:
                return {'score': None, 'zone': 'UNKNOWN', 'components': {}}

            working_capital = balance.get('working_capital', 0)
            retained_earnings = balance.get('retained_earnings', 0)
            ebit = income.get('ebit') or income.get('operating_income', 0)
            total_liabilities = balance.get('total_liabilities', 0)
            market_cap = info.get('marketCap', 0)
            revenue = income.get('revenue', 0)

            # 計算各組成部分
            x1 = working_capital / total_assets if total_assets else 0
            x2 = retained_earnings / total_assets if total_assets else 0
            x3 = ebit / total_assets if total_assets else 0
            x4 = market_cap / total_liabilities if total_liabilities else 0
            x5 = revenue / total_assets if total_assets else 0

            # 計算 Z-Score
            z_score = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5

            # 判定區域
            if z_score < Config.ALTMAN_Z_DISTRESS:
                zone = 'DISTRESS'
                zone_desc = '財務困境區 - 破產風險高'
            elif z_score < Config.ALTMAN_Z_SAFE:
                zone = 'GREY'
                zone_desc = '灰色區 - 需關注'
            else:
                zone = 'SAFE'
                zone_desc = '安全區 - 財務健康'

            return {
                'score': round(z_score, 2),
                'zone': zone,
                'zone_description': zone_desc,
                'components': {
                    'X1_working_capital_ratio': round(x1, 4),
                    'X2_retained_earnings_ratio': round(x2, 4),
                    'X3_ebit_ratio': round(x3, 4),
                    'X4_market_equity_ratio': round(x4, 4),
                    'X5_asset_turnover': round(x5, 4),
                }
            }

        except Exception as e:
            return {'score': None, 'zone': 'ERROR', 'error': str(e)}

    def _calculate_piotroski_f(self, balance: Dict, income: Dict, cash_flow: Dict) -> Dict[str, Any]:
        """
        計算 Piotroski F-Score (財務體質 0-9分)

        獲利能力 (4分):
        1. ROA > 0
        2. Operating Cash Flow > 0
        3. ROA 增加 (ΔROA > 0)
        4. CFO > Net Income (盈餘品質)

        槓桿與流動性 (3分):
        5. 長期負債減少
        6. 流動比率提高
        7. 無新股發行

        營運效率 (2分):
        8. 毛利率提高
        9. 資產周轉率提高
        """
        scores = {}
        total = 0

        try:
            total_assets = balance.get('total_assets', 0)
            total_assets_prev = balance.get('total_assets_prev', total_assets)
            net_income = income.get('net_income', 0)
            net_income_prev = income.get('net_income_prev', 0)
            cfo = cash_flow.get('operating_cash_flow', 0)
            revenue = income.get('revenue', 0)
            revenue_prev = income.get('revenue_prev', revenue)
            gross_profit = income.get('gross_profit', 0)

            # 1. ROA > 0
            roa = net_income / total_assets if total_assets else 0
            scores['roa_positive'] = 1 if roa > 0 else 0

            # 2. CFO > 0
            scores['cfo_positive'] = 1 if cfo > 0 else 0

            # 3. ΔROA > 0
            roa_prev = net_income_prev / total_assets_prev if total_assets_prev else 0
            scores['roa_increasing'] = 1 if roa > roa_prev else 0

            # 4. CFO > Net Income (盈餘品質)
            scores['accruals'] = 1 if cfo > net_income else 0

            # 5. 長期負債減少 (簡化：使用 debt/equity 比較)
            debt_equity = balance.get('total_debt', 0) / balance.get('stockholders_equity', 1) if balance.get('stockholders_equity') else 0
            scores['leverage_decreasing'] = 1 if debt_equity < 0.5 else 0  # 簡化判斷

            # 6. 流動比率提高
            current_ratio = balance.get('current_assets', 0) / balance.get('current_liabilities', 1) if balance.get('current_liabilities') else 0
            current_ratio_prev = balance.get('current_assets_prev', 0) / balance.get('current_liabilities_prev', 1) if balance.get('current_liabilities_prev') else 0
            scores['liquidity_improving'] = 1 if current_ratio > current_ratio_prev else 0

            # 7. 無股本稀釋 (簡化：假設無)
            scores['no_dilution'] = 1

            # 8. 毛利率提高
            gross_margin = gross_profit / revenue if revenue else 0
            gross_margin_prev = gross_profit / revenue_prev if revenue_prev else 0
            scores['margin_improving'] = 1 if gross_margin >= gross_margin_prev else 0

            # 9. 資產周轉率提高
            turnover = revenue / total_assets if total_assets else 0
            turnover_prev = revenue_prev / total_assets_prev if total_assets_prev else 0
            scores['turnover_improving'] = 1 if turnover >= turnover_prev else 0

            total = sum(scores.values())

            # 評級
            if total >= 8:
                rating = 'STRONG'
                rating_desc = '財務體質優良'
            elif total >= 5:
                rating = 'MODERATE'
                rating_desc = '財務體質中等'
            else:
                rating = 'WEAK'
                rating_desc = '財務體質偏弱'

            return {
                'score': total,
                'max_score': 9,
                'rating': rating,
                'rating_description': rating_desc,
                'components': scores
            }

        except Exception as e:
            return {'score': None, 'rating': 'ERROR', 'error': str(e)}

    def _evaluate_risk_flags(self, altman: Dict, piotroski: Dict, stock_data: Dict) -> list:
        """評估風險標記"""
        flags = []

        # Altman Z-Score 風險
        if altman.get('zone') == 'DISTRESS':
            flags.append({
                'type': 'CRITICAL',
                'flag': 'BANKRUPTCY_RISK',
                'message': 'Altman Z-Score 顯示高破產風險，建議避免估值或大幅提高風險溢價'
            })
        elif altman.get('zone') == 'GREY':
            flags.append({
                'type': 'WARNING',
                'flag': 'FINANCIAL_STRESS',
                'message': 'Altman Z-Score 處於灰色區域，財務狀況需密切關注'
            })

        # Piotroski F-Score 風險
        if piotroski.get('score') is not None and piotroski['score'] < 4:
            flags.append({
                'type': 'WARNING',
                'flag': 'WEAK_FUNDAMENTALS',
                'message': 'Piotroski F-Score 偏低，顯示財務基本面較弱'
            })

        # 負債風險
        metrics = stock_data.get('metrics', {})
        debt_equity = metrics.get('debt_equity')
        if debt_equity and debt_equity > 200:  # D/E > 2
            flags.append({
                'type': 'WARNING',
                'flag': 'HIGH_LEVERAGE',
                'message': f'負債權益比 {debt_equity:.1f}% 偏高，財務槓桿風險較大'
            })

        # 獲利能力風險
        roe = metrics.get('roe')
        if roe and roe < 0:
            flags.append({
                'type': 'WARNING',
                'flag': 'NEGATIVE_ROE',
                'message': 'ROE 為負，公司處於虧損狀態'
            })

        return flags

    def _get_overall_risk(self, altman: Dict, piotroski: Dict, flags: list) -> Dict[str, Any]:
        """綜合風險評估"""
        critical_flags = [f for f in flags if f['type'] == 'CRITICAL']
        warning_flags = [f for f in flags if f['type'] == 'WARNING']

        if critical_flags:
            level = 'HIGH'
            description = '高風險 - 存在重大財務風險，估值需謹慎'
            wacc_adjustment = Config.WACC_DISTRESS_PREMIUM
        elif len(warning_flags) >= 2:
            level = 'ELEVATED'
            description = '中高風險 - 存在多項財務警示，需額外風險溢價'
            wacc_adjustment = 0.015
        elif warning_flags:
            level = 'MODERATE'
            description = '中等風險 - 存在部分警示，需注意'
            wacc_adjustment = 0.005
        else:
            level = 'LOW'
            description = '低風險 - 財務狀況良好'
            wacc_adjustment = 0

        return {
            'level': level,
            'description': description,
            'wacc_adjustment': wacc_adjustment,
            'critical_count': len(critical_flags),
            'warning_count': len(warning_flags)
        }
