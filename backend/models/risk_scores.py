"""
風險評分計算模組
獨立的風險評分計算邏輯
"""
from typing import Dict, Any


class RiskScoreCalculator:
    """
    風險評分計算器
    包含 Altman Z-Score、Piotroski F-Score 等
    """

    @staticmethod
    def calculate_altman_z(working_capital: float, retained_earnings: float,
                           ebit: float, market_cap: float, total_liabilities: float,
                           revenue: float, total_assets: float) -> Dict[str, Any]:
        """
        計算 Altman Z-Score

        Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5

        其中:
        X1 = Working Capital / Total Assets
        X2 = Retained Earnings / Total Assets
        X3 = EBIT / Total Assets
        X4 = Market Cap / Total Liabilities
        X5 = Revenue / Total Assets
        """
        if total_assets <= 0:
            return {'score': None, 'zone': 'UNKNOWN'}

        x1 = working_capital / total_assets
        x2 = retained_earnings / total_assets
        x3 = ebit / total_assets
        x4 = market_cap / total_liabilities if total_liabilities > 0 else 0
        x5 = revenue / total_assets

        z_score = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5

        if z_score < 1.81:
            zone = 'DISTRESS'
        elif z_score < 2.99:
            zone = 'GREY'
        else:
            zone = 'SAFE'

        return {
            'score': round(z_score, 2),
            'zone': zone,
            'components': {
                'X1': round(x1, 4),
                'X2': round(x2, 4),
                'X3': round(x3, 4),
                'X4': round(x4, 4),
                'X5': round(x5, 4),
            }
        }

    @staticmethod
    def calculate_beneish_m(dsri: float, gmi: float, aqi: float, sgi: float,
                            depi: float, sgai: float, tata: float, lvgi: float) -> Dict[str, Any]:
        """
        計算 Beneish M-Score (造假偵測)

        M = -4.84 + 0.92*DSRI + 0.528*GMI + 0.404*AQI + 0.892*SGI
            + 0.115*DEPI - 0.172*SGAI + 4.679*TATA - 0.327*LVGI

        M > -1.78 表示可能有財務造假
        """
        m_score = (-4.84 + 0.92 * dsri + 0.528 * gmi + 0.404 * aqi +
                   0.892 * sgi + 0.115 * depi - 0.172 * sgai +
                   4.679 * tata - 0.327 * lvgi)

        if m_score > -1.78:
            flag = 'RED_FLAG'
            interpretation = '可能存在財務操縱風險'
        else:
            flag = 'NORMAL'
            interpretation = '未發現明顯造假跡象'

        return {
            'score': round(m_score, 2),
            'flag': flag,
            'interpretation': interpretation,
            'threshold': -1.78
        }


# 輔助函數：計算 Beneish M-Score 所需的比率
def calculate_beneish_ratios(current: Dict, previous: Dict) -> Dict[str, float]:
    """
    計算 Beneish M-Score 所需的各項比率

    Args:
        current: 當期財務數據
        previous: 前期財務數據

    Returns:
        包含各比率的字典
    """

    def safe_divide(a, b, default=1):
        if b == 0 or b is None:
            return default
        return a / b if a is not None else default

    # DSRI: Days Sales in Receivables Index
    dsri = safe_divide(
        safe_divide(current.get('receivables'), current.get('revenue')),
        safe_divide(previous.get('receivables'), previous.get('revenue'))
    )

    # GMI: Gross Margin Index
    curr_gm = safe_divide(
        current.get('gross_profit'),
        current.get('revenue')
    )
    prev_gm = safe_divide(
        previous.get('gross_profit'),
        previous.get('revenue')
    )
    gmi = safe_divide(prev_gm, curr_gm)

    # AQI: Asset Quality Index
    curr_aq = 1 - safe_divide(
        current.get('current_assets', 0) + current.get('ppe', 0),
        current.get('total_assets')
    )
    prev_aq = 1 - safe_divide(
        previous.get('current_assets', 0) + previous.get('ppe', 0),
        previous.get('total_assets')
    )
    aqi = safe_divide(curr_aq, prev_aq)

    # SGI: Sales Growth Index
    sgi = safe_divide(current.get('revenue'), previous.get('revenue'))

    # DEPI: Depreciation Index
    curr_depi = safe_divide(
        current.get('depreciation'),
        current.get('depreciation', 0) + current.get('ppe', 0)
    )
    prev_depi = safe_divide(
        previous.get('depreciation'),
        previous.get('depreciation', 0) + previous.get('ppe', 0)
    )
    depi = safe_divide(prev_depi, curr_depi)

    # SGAI: SG&A Index
    curr_sgai = safe_divide(current.get('sga'), current.get('revenue'))
    prev_sgai = safe_divide(previous.get('sga'), previous.get('revenue'))
    sgai = safe_divide(curr_sgai, prev_sgai)

    # TATA: Total Accruals to Total Assets
    tata = safe_divide(
        current.get('net_income', 0) - current.get('operating_cash_flow', 0),
        current.get('total_assets')
    )

    # LVGI: Leverage Index
    curr_lvgi = safe_divide(
        current.get('total_debt'),
        current.get('total_assets')
    )
    prev_lvgi = safe_divide(
        previous.get('total_debt'),
        previous.get('total_assets')
    )
    lvgi = safe_divide(curr_lvgi, prev_lvgi)

    return {
        'dsri': dsri,
        'gmi': gmi,
        'aqi': aqi,
        'sgi': sgi,
        'depi': depi,
        'sgai': sgai,
        'tata': tata,
        'lvgi': lvgi
    }
