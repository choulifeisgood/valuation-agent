"""
Data Agent - 負責從 Yahoo Finance 獲取股票數據
"""
import yfinance as yf
import pandas as pd
import time
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# 內存緩存：儲存成功獲取的股票數據
_cache: Dict[str, Dict[str, Any]] = {}
_cache_expiry: Dict[str, datetime] = {}
CACHE_DURATION = timedelta(hours=1)  # 緩存 1 小時


class DataAgent:
    """數據獲取 Agent - 獲取財務報表與市場數據"""

    def _get_from_cache(self, ticker: str) -> Optional[Dict[str, Any]]:
        """從緩存獲取數據"""
        if ticker in _cache and ticker in _cache_expiry:
            if datetime.now() < _cache_expiry[ticker]:
                print(f"[Cache Hit] {ticker}")
                return _cache[ticker]
            else:
                # 緩存過期，清除
                del _cache[ticker]
                del _cache_expiry[ticker]
        return None

    def _save_to_cache(self, ticker: str, data: Dict[str, Any]):
        """儲存數據到緩存"""
        if not data.get('error'):
            _cache[ticker] = data
            _cache_expiry[ticker] = datetime.now() + CACHE_DURATION
            print(f"[Cache Save] {ticker}")

    def _retry_with_backoff(self, func, max_retries=3, quick_mode=False):
        """
        帶有指數退避的重試機制
        quick_mode: 快速模式，減少延遲以適應 Render 30 秒超時
        """
        last_error = None
        for attempt in range(max_retries):
            try:
                # 首次請求不延遲，後續請求短延遲
                if attempt > 0:
                    delay = random.uniform(0.5, 1.5) if quick_mode else random.uniform(1, 2)
                    time.sleep(delay)
                return func()
            except Exception as e:
                last_error = e
                error_str = str(e)
                if '429' in error_str or 'Too Many Requests' in error_str:
                    # 快速退避以適應超時限制
                    wait_time = min((2 ** attempt) * 2 + random.uniform(1, 2), 8)
                    print(f"Rate limited, waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                else:
                    raise e
        # 明確標記為限流錯誤
        raise Exception(f"RATE_LIMITED: Yahoo Finance API 暫時限流，請稍後再試")

    def fetch_stock_data(self, ticker: str) -> Dict[str, Any]:
        """
        獲取完整股票數據
        包含: 基本資料、財務報表、市場數據、同業列表
        """
        # 先檢查緩存
        cached = self._get_from_cache(ticker)
        if cached:
            return cached

        try:
            # 添加隨機延遲，減少被限流機會
            time.sleep(random.uniform(0.5, 1.5))

            stock = yf.Ticker(ticker)

            # 使用重試機制獲取 info
            def get_info():
                info = stock.info
                # 檢查是否被限流（info 會是空的或缺少關鍵字段）
                if not info or len(info) < 5:
                    raise Exception("429 Too Many Requests - Empty response")
                return info

            info = self._retry_with_backoff(get_info)

            # 檢查股票是否存在（此時已經通過重試機制，info 應該有數據）
            if not info or info.get('regularMarketPrice') is None:
                # 再次檢查是否是限流導致的空數據
                if not info or len(info) < 10:
                    return {'error': f'Yahoo Finance API 暫時無法獲取 {ticker} 的數據，請稍後再試'}
                return {'error': f'找不到股票代碼: {ticker}'}

            # 獲取財務報表
            income_stmt = self._get_income_statement(stock)
            balance_sheet = self._get_balance_sheet(stock)
            cash_flow = self._get_cash_flow(stock)

            # 計算關鍵指標
            metrics = self._calculate_metrics(info, income_stmt, balance_sheet, cash_flow)

            # 獲取同業公司
            peers = self._get_peers(stock, info)

            result = {
                'ticker': ticker,
                'company_name': info.get('longName', info.get('shortName', ticker)),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'currency': info.get('currency', 'USD'),
                'current_price': info.get('regularMarketPrice', info.get('currentPrice', 0)),
                'market_cap': info.get('marketCap', 0),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'beta': info.get('beta', 1.0),
                'info': info,
                'income_statement': income_stmt,
                'balance_sheet': balance_sheet,
                'cash_flow': cash_flow,
                'metrics': metrics,
                'peers': peers
            }

            # 儲存到緩存
            self._save_to_cache(ticker, result)
            return result

        except Exception as e:
            error_str = str(e)
            if 'RATE_LIMITED' in error_str or '429' in error_str or 'Too Many Requests' in error_str:
                return {'error': f'Yahoo Finance API 暫時限流，請等待 1-2 分鐘後再試'}
            return {'error': f'獲取數據時發生錯誤: {error_str}'}

    def _get_income_statement(self, stock: yf.Ticker) -> Dict[str, Any]:
        """獲取損益表數據"""
        try:
            income = stock.income_stmt
            if income.empty:
                return {}

            latest = income.iloc[:, 0]  # 最新一年
            prev = income.iloc[:, 1] if income.shape[1] > 1 else latest

            return {
                'revenue': self._safe_get(latest, 'Total Revenue'),
                'revenue_prev': self._safe_get(prev, 'Total Revenue'),
                'gross_profit': self._safe_get(latest, 'Gross Profit'),
                'operating_income': self._safe_get(latest, 'Operating Income'),
                'ebit': self._safe_get(latest, 'EBIT'),
                'ebitda': self._safe_get(latest, 'EBITDA'),
                'net_income': self._safe_get(latest, 'Net Income'),
                'net_income_prev': self._safe_get(prev, 'Net Income'),
                'interest_expense': self._safe_get(latest, 'Interest Expense'),
                'tax_expense': self._safe_get(latest, 'Tax Provision'),
                'depreciation': self._safe_get(latest, 'Depreciation And Amortization In Income Statement'),
            }
        except Exception:
            return {}

    def _get_balance_sheet(self, stock: yf.Ticker) -> Dict[str, Any]:
        """獲取資產負債表數據"""
        try:
            balance = stock.balance_sheet
            if balance.empty:
                return {}

            latest = balance.iloc[:, 0]
            prev = balance.iloc[:, 1] if balance.shape[1] > 1 else latest

            return {
                'total_assets': self._safe_get(latest, 'Total Assets'),
                'total_assets_prev': self._safe_get(prev, 'Total Assets'),
                'current_assets': self._safe_get(latest, 'Current Assets'),
                'current_assets_prev': self._safe_get(prev, 'Current Assets'),
                'total_liabilities': self._safe_get(latest, 'Total Liabilities Net Minority Interest'),
                'current_liabilities': self._safe_get(latest, 'Current Liabilities'),
                'current_liabilities_prev': self._safe_get(prev, 'Current Liabilities'),
                'total_debt': self._safe_get(latest, 'Total Debt'),
                'long_term_debt': self._safe_get(latest, 'Long Term Debt'),
                'stockholders_equity': self._safe_get(latest, 'Stockholders Equity'),
                'stockholders_equity_prev': self._safe_get(prev, 'Stockholders Equity'),
                'retained_earnings': self._safe_get(latest, 'Retained Earnings'),
                'retained_earnings_prev': self._safe_get(prev, 'Retained Earnings'),
                'working_capital': self._safe_get(latest, 'Working Capital'),
                'working_capital_prev': self._safe_get(prev, 'Working Capital'),
                'cash': self._safe_get(latest, 'Cash And Cash Equivalents'),
                'inventory': self._safe_get(latest, 'Inventory'),
                'inventory_prev': self._safe_get(prev, 'Inventory'),
                'receivables': self._safe_get(latest, 'Receivables'),
                'receivables_prev': self._safe_get(prev, 'Receivables'),
                'payables': self._safe_get(latest, 'Payables'),
            }
        except Exception:
            return {}

    def _get_cash_flow(self, stock: yf.Ticker) -> Dict[str, Any]:
        """獲取現金流量表數據"""
        try:
            cf = stock.cash_flow
            if cf.empty:
                return {}

            latest = cf.iloc[:, 0]

            return {
                'operating_cash_flow': self._safe_get(latest, 'Operating Cash Flow'),
                'capital_expenditure': abs(self._safe_get(latest, 'Capital Expenditure')),
                'free_cash_flow': self._safe_get(latest, 'Free Cash Flow'),
                'depreciation': self._safe_get(latest, 'Depreciation And Amortization'),
                'change_in_working_capital': self._safe_get(latest, 'Change In Working Capital'),
            }
        except Exception:
            return {}

    def _calculate_metrics(self, info: Dict, income: Dict, balance: Dict, cash_flow: Dict) -> Dict[str, Any]:
        """計算關鍵財務指標"""
        metrics = {}

        try:
            # 從 info 獲取現成指標
            metrics['pe_ratio'] = info.get('trailingPE') or info.get('forwardPE')
            metrics['forward_pe'] = info.get('forwardPE')
            metrics['pb_ratio'] = info.get('priceToBook')
            metrics['ps_ratio'] = info.get('priceToSalesTrailing12Months')
            metrics['ev_ebitda'] = info.get('enterpriseToEbitda')
            metrics['ev_revenue'] = info.get('enterpriseToRevenue')
            metrics['profit_margin'] = info.get('profitMargins')
            metrics['operating_margin'] = info.get('operatingMargins')
            metrics['roe'] = info.get('returnOnEquity')
            metrics['roa'] = info.get('returnOnAssets')
            metrics['debt_equity'] = info.get('debtToEquity')
            metrics['current_ratio'] = info.get('currentRatio')
            metrics['dividend_yield'] = info.get('dividendYield')
            metrics['payout_ratio'] = info.get('payoutRatio')
            metrics['revenue_growth'] = info.get('revenueGrowth')
            metrics['earnings_growth'] = info.get('earningsGrowth')
            metrics['enterprise_value'] = info.get('enterpriseValue')

            # 計算 EBITDA Margin
            if income.get('ebitda') and income.get('revenue'):
                metrics['ebitda_margin'] = income['ebitda'] / income['revenue']

            # 計算 FCF Yield
            if cash_flow.get('free_cash_flow') and info.get('marketCap'):
                metrics['fcf_yield'] = cash_flow['free_cash_flow'] / info['marketCap']

        except Exception:
            pass

        return metrics

    def _get_peers(self, stock: yf.Ticker, info: Dict) -> list:
        """獲取同業公司列表"""
        # 嘗試使用 yfinance 的推薦功能
        try:
            recommendations = stock.recommendations
            if recommendations is not None and not recommendations.empty:
                # 這不是同業，但可以作為參考
                pass
        except Exception:
            pass

        # 根據行業定義常見同業
        industry_peers = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMD', 'INTC'],
            'Consumer Cyclical': ['AMZN', 'TSLA', 'HD', 'NKE', 'MCD', 'SBUX'],
            'Financial Services': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C'],
            'Healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'MRK', 'LLY'],
            'Communication Services': ['GOOGL', 'META', 'DIS', 'NFLX', 'CMCSA'],
            'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG'],
            'Industrials': ['CAT', 'BA', 'HON', 'UPS', 'RTX'],
            'Consumer Defensive': ['PG', 'KO', 'PEP', 'WMT', 'COST'],
        }

        sector = info.get('sector', '')
        peers = industry_peers.get(sector, [])

        # 排除自身
        ticker = info.get('symbol', '')
        peers = [p for p in peers if p != ticker]

        return peers[:5]  # 返回最多5個同業

    def get_quick_quote(self, ticker: str) -> Dict[str, Any]:
        """快速獲取即時報價"""
        try:
            stock = yf.Ticker(ticker)

            # 使用重試機制
            def get_info():
                info = stock.info
                if not info or len(info) < 5:
                    raise Exception("429 Too Many Requests - Empty response")
                return info

            info = self._retry_with_backoff(get_info, max_retries=2, quick_mode=True)

            return {
                'ticker': ticker,
                'name': info.get('longName', ticker),
                'price': info.get('regularMarketPrice'),
                'change': info.get('regularMarketChange'),
                'change_percent': info.get('regularMarketChangePercent'),
                'volume': info.get('regularMarketVolume'),
                'market_cap': info.get('marketCap'),
            }
        except Exception as e:
            error_str = str(e)
            if 'RATE_LIMITED' in error_str or '429' in error_str or 'Too Many Requests' in error_str:
                return {'error': 'Yahoo Finance API 暫時限流，請等待 1-2 分鐘後再試'}
            return {'error': error_str}

    def get_peer_multiples(self, peers: list) -> Dict[str, Dict]:
        """獲取同業公司的估值倍數"""
        multiples = {}
        for peer in peers:
            try:
                stock = yf.Ticker(peer)
                info = stock.info
                multiples[peer] = {
                    'pe': info.get('trailingPE'),
                    'forward_pe': info.get('forwardPE'),
                    'ev_ebitda': info.get('enterpriseToEbitda'),
                    'ev_revenue': info.get('enterpriseToRevenue'),
                    'pb': info.get('priceToBook'),
                }
            except Exception:
                continue
        return multiples

    @staticmethod
    def _safe_get(series: pd.Series, key: str, default: float = 0) -> float:
        """安全地從 Series 中獲取值"""
        try:
            value = series.get(key)
            if pd.isna(value):
                return default
            return float(value)
        except Exception:
            return default
