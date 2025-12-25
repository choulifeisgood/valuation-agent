"""
DCF (Discounted Cash Flow) 估值模型
基於 FCFF 方法計算內在價值
"""
from typing import Dict, Any
from config import Config


class DCFModel:
    """
    現金流折現模型
    計算公式:
    - FCFF = EBIT × (1 - Tax) + D&A - CapEx - ΔNWC
    - Value = Σ(FCF_t / (1+WACC)^t) + Terminal Value / (1+WACC)^n
    - Terminal Value = FCF_n × (1+g) / (WACC - g)
    """

    def __init__(self):
        self.risk_free_rate = Config.DEFAULT_RISK_FREE_RATE
        self.market_risk_premium = Config.DEFAULT_MARKET_RISK_PREMIUM
        self.terminal_growth = Config.DEFAULT_TERMINAL_GROWTH_RATE
        self.projection_years = Config.DEFAULT_PROJECTION_YEARS

    def calculate(self, stock_data: Dict[str, Any], wacc_adjustment: float = 0) -> Dict[str, Any]:
        """
        計算 DCF 內在價值

        Args:
            stock_data: 股票數據
            wacc_adjustment: WACC 風險調整 (基於風險評分)

        Returns:
            包含內在價值與計算細節的字典
        """
        try:
            # 獲取必要數據
            info = stock_data.get('info', {})
            income = stock_data.get('income_statement', {})
            balance = stock_data.get('balance_sheet', {})
            cash_flow = stock_data.get('cash_flow', {})

            # 計算 WACC
            wacc = self._calculate_wacc(info, balance, wacc_adjustment)
            if wacc is None or wacc <= self.terminal_growth:
                return {'error': 'WACC 計算失敗或低於終值成長率', 'intrinsic_value': None}

            # 計算基期 FCF
            base_fcf = self._calculate_base_fcf(income, cash_flow, balance)
            if base_fcf is None or base_fcf <= 0:
                # 嘗試使用營業現金流
                base_fcf = cash_flow.get('operating_cash_flow', 0) - cash_flow.get('capital_expenditure', 0)
                if base_fcf <= 0:
                    return {'error': 'FCF 為負或無法計算', 'intrinsic_value': None}

            # 估計成長率
            fcf_growth = self._estimate_growth_rate(stock_data)

            # 預測 FCF
            projected_fcf = self._project_fcf(base_fcf, fcf_growth, self.projection_years)

            # 計算現值
            pv_fcf = self._calculate_pv(projected_fcf, wacc)

            # 計算終值
            terminal_value = self._calculate_terminal_value(
                projected_fcf[-1], wacc, self.terminal_growth
            )
            pv_terminal = terminal_value / ((1 + wacc) ** self.projection_years)

            # 企業價值
            enterprise_value = pv_fcf + pv_terminal

            # 計算股權價值
            total_debt = balance.get('total_debt', 0)
            cash = balance.get('cash', 0)
            equity_value = enterprise_value - total_debt + cash

            # 每股價值
            shares = info.get('sharesOutstanding', stock_data.get('shares_outstanding', 0))
            if shares <= 0:
                return {'error': '無法獲取流通股數', 'intrinsic_value': None}

            intrinsic_value = equity_value / shares

            return {
                'intrinsic_value': round(intrinsic_value, 2),
                'enterprise_value': round(enterprise_value, 0),
                'equity_value': round(equity_value, 0),
                'wacc': round(wacc, 4),
                'terminal_growth': self.terminal_growth,
                'fcf_growth': round(fcf_growth, 4),
                'base_fcf': round(base_fcf, 0),
                'terminal_value': round(terminal_value, 0),
                'pv_fcf': round(pv_fcf, 0),
                'pv_terminal': round(pv_terminal, 0),
                'projected_fcf': [round(f, 0) for f in projected_fcf],
                'projection_years': self.projection_years,
            }

        except Exception as e:
            return {'error': f'DCF 計算錯誤: {str(e)}', 'intrinsic_value': None}

    def _calculate_wacc(self, info: Dict, balance: Dict, adjustment: float = 0) -> float:
        """
        計算加權平均資本成本 (WACC)
        WACC = (E/V) × Re + (D/V) × Rd × (1-t)
        """
        try:
            # 股權成本 (CAPM)
            beta = info.get('beta', 1.0)
            if beta is None or beta <= 0:
                beta = 1.0

            cost_of_equity = self.risk_free_rate + beta * self.market_risk_premium

            # 債務成本 (簡化: 使用合成評級法)
            total_debt = balance.get('total_debt', 0)
            if total_debt <= 0:
                # 無負債，WACC = Cost of Equity
                return cost_of_equity + adjustment

            # 估計債務成本 (基於利息覆蓋率)
            interest_coverage = info.get('interestCoverage', 10)
            if interest_coverage is None:
                interest_coverage = 10

            if interest_coverage > 8:
                credit_spread = 0.01  # AAA/AA
            elif interest_coverage > 4:
                credit_spread = 0.02  # A/BBB
            elif interest_coverage > 2:
                credit_spread = 0.04  # BB
            else:
                credit_spread = 0.08  # B or lower

            cost_of_debt = self.risk_free_rate + credit_spread

            # 稅率
            tax_rate = 0.21  # 假設美國企業稅率

            # 市值與債務
            market_cap = info.get('marketCap', 0)
            if market_cap <= 0:
                return cost_of_equity + adjustment

            # 計算權重
            total_value = market_cap + total_debt
            weight_equity = market_cap / total_value
            weight_debt = total_debt / total_value

            # WACC
            wacc = (weight_equity * cost_of_equity +
                    weight_debt * cost_of_debt * (1 - tax_rate))

            return wacc + adjustment

        except Exception:
            # 預設使用 Cost of Equity
            return self.risk_free_rate + self.market_risk_premium + adjustment

    def _calculate_base_fcf(self, income: Dict, cash_flow: Dict, balance: Dict) -> float:
        """
        計算基期自由現金流 (FCFF)
        FCFF = EBIT × (1 - Tax) + D&A - CapEx - ΔNWC
        """
        try:
            # 優先使用現金流量表的 FCF
            if cash_flow.get('free_cash_flow'):
                return cash_flow['free_cash_flow']

            # 計算 FCFF
            ebit = income.get('ebit') or income.get('operating_income', 0)
            tax_rate = 0.21

            # NOPAT
            nopat = ebit * (1 - tax_rate)

            # 加回 D&A
            depreciation = (cash_flow.get('depreciation') or
                           income.get('depreciation', 0))

            # 減去 CapEx
            capex = cash_flow.get('capital_expenditure', 0)

            # 減去 ΔNWC
            delta_nwc = cash_flow.get('change_in_working_capital', 0)

            fcff = nopat + depreciation - capex - delta_nwc

            return fcff if fcff > 0 else None

        except Exception:
            return None

    def _estimate_growth_rate(self, stock_data: Dict) -> float:
        """估計 FCF 成長率"""
        metrics = stock_data.get('metrics', {})
        info = stock_data.get('info', {})

        # 嘗試使用營收成長率
        revenue_growth = metrics.get('revenue_growth') or info.get('revenueGrowth')
        earnings_growth = metrics.get('earnings_growth') or info.get('earningsGrowth')

        if revenue_growth and 0 < revenue_growth < 0.5:
            # 使用營收成長率，但衰減
            base_growth = revenue_growth
        elif earnings_growth and 0 < earnings_growth < 0.5:
            base_growth = earnings_growth
        else:
            # 預設保守成長
            base_growth = 0.05

        # 限制成長率範圍
        return max(0.02, min(base_growth, 0.20))

    def _project_fcf(self, base_fcf: float, growth_rate: float, years: int) -> list:
        """預測未來 FCF"""
        projected = []
        fcf = base_fcf

        # 兩階段成長: 前期高成長，後期衰減至終值成長
        for i in range(years):
            # 成長率逐年衰減
            year_growth = growth_rate * (1 - i / (years * 2))
            year_growth = max(year_growth, self.terminal_growth)
            fcf = fcf * (1 + year_growth)
            projected.append(fcf)

        return projected

    def _calculate_pv(self, cash_flows: list, discount_rate: float) -> float:
        """計算現金流現值總和"""
        pv = 0
        for i, cf in enumerate(cash_flows, 1):
            pv += cf / ((1 + discount_rate) ** i)
        return pv

    def _calculate_terminal_value(self, final_fcf: float, wacc: float, growth: float) -> float:
        """
        計算終值 (Gordon Growth Model)
        TV = FCF_n × (1+g) / (WACC - g)
        """
        if wacc <= growth:
            # 避免除以零或負數
            growth = wacc - 0.01

        return final_fcf * (1 + growth) / (wacc - growth)
