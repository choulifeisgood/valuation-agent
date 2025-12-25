"""
相對估值模型
基於同業倍數計算隱含價格
"""
from typing import Dict, Any, List
import yfinance as yf


class RelativeValuation:
    """
    相對估值模型
    使用同業倍數推算隱含價格
    """

    def calculate(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        計算相對估值

        使用 P/E, EV/EBITDA, EV/Revenue 等倍數
        與同業比較推算隱含價格
        """
        try:
            info = stock_data.get('info', {})
            metrics = stock_data.get('metrics', {})
            income = stock_data.get('income_statement', {})
            peers = stock_data.get('peers', [])

            current_price = stock_data.get('current_price', 0)
            shares = info.get('sharesOutstanding', 0)
            market_cap = info.get('marketCap', 0)
            enterprise_value = info.get('enterpriseValue', 0)

            # 獲取同業倍數
            peer_multiples = self._get_peer_multiples(peers)

            results = {
                'current_multiples': {},
                'peer_multiples': peer_multiples,
            }

            # 1. P/E 估值
            pe_result = self._pe_valuation(
                metrics.get('pe_ratio'),
                income.get('net_income', 0),
                shares,
                peer_multiples
            )
            results.update(pe_result)

            # 2. EV/EBITDA 估值
            ev_ebitda_result = self._ev_ebitda_valuation(
                metrics.get('ev_ebitda'),
                income.get('ebitda', 0),
                enterprise_value,
                market_cap,
                info.get('totalDebt', 0),
                info.get('totalCash', 0),
                shares,
                peer_multiples
            )
            results.update(ev_ebitda_result)

            # 3. EV/Revenue 估值 (適用於虧損公司)
            ev_revenue_result = self._ev_revenue_valuation(
                metrics.get('ev_revenue'),
                income.get('revenue', 0),
                enterprise_value,
                market_cap,
                info.get('totalDebt', 0),
                info.get('totalCash', 0),
                shares,
                peer_multiples
            )
            results.update(ev_revenue_result)

            # 4. P/B 估值
            pb_result = self._pb_valuation(
                metrics.get('pb_ratio'),
                stock_data.get('balance_sheet', {}).get('stockholders_equity', 0),
                shares,
                peer_multiples
            )
            results.update(pb_result)

            return results

        except Exception as e:
            return {'error': f'相對估值計算錯誤: {str(e)}'}

    def _get_peer_multiples(self, peers: List[str]) -> Dict[str, Any]:
        """獲取同業公司的估值倍數"""
        if not peers:
            # 使用市場平均
            return {
                'median_pe': 20,
                'median_ev_ebitda': 12,
                'median_ev_revenue': 3,
                'median_pb': 3,
                'peer_count': 0,
                'source': 'market_average'
            }

        pe_values = []
        ev_ebitda_values = []
        ev_revenue_values = []
        pb_values = []

        for peer in peers[:5]:  # 限制 5 家
            try:
                stock = yf.Ticker(peer)
                info = stock.info

                pe = info.get('trailingPE')
                if pe and 0 < pe < 100:
                    pe_values.append(pe)

                ev_ebitda = info.get('enterpriseToEbitda')
                if ev_ebitda and 0 < ev_ebitda < 50:
                    ev_ebitda_values.append(ev_ebitda)

                ev_revenue = info.get('enterpriseToRevenue')
                if ev_revenue and 0 < ev_revenue < 20:
                    ev_revenue_values.append(ev_revenue)

                pb = info.get('priceToBook')
                if pb and 0 < pb < 50:
                    pb_values.append(pb)

            except Exception:
                continue

        return {
            'median_pe': self._harmonic_mean(pe_values) if pe_values else 20,
            'median_ev_ebitda': self._harmonic_mean(ev_ebitda_values) if ev_ebitda_values else 12,
            'median_ev_revenue': self._harmonic_mean(ev_revenue_values) if ev_revenue_values else 3,
            'median_pb': self._harmonic_mean(pb_values) if pb_values else 3,
            'peer_count': len(peers),
            'pe_values': pe_values,
            'ev_ebitda_values': ev_ebitda_values,
            'source': 'peer_analysis'
        }

    def _pe_valuation(self, current_pe: float, net_income: float, shares: float,
                      peer_multiples: Dict) -> Dict[str, Any]:
        """P/E 倍數估值"""
        result = {
            'current_pe': current_pe,
            'peer_median_pe': peer_multiples.get('median_pe'),
            'pe_implied_price': None
        }

        if net_income <= 0 or shares <= 0:
            return result

        eps = net_income / shares
        peer_pe = peer_multiples.get('median_pe', 20)

        implied_price = eps * peer_pe
        result['pe_implied_price'] = round(implied_price, 2)
        result['eps'] = round(eps, 2)

        return result

    def _ev_ebitda_valuation(self, current_ev_ebitda: float, ebitda: float,
                             ev: float, market_cap: float, debt: float, cash: float,
                             shares: float, peer_multiples: Dict) -> Dict[str, Any]:
        """EV/EBITDA 倍數估值"""
        result = {
            'current_ev_ebitda': current_ev_ebitda,
            'peer_median_ev_ebitda': peer_multiples.get('median_ev_ebitda'),
            'ev_ebitda_implied_price': None
        }

        if ebitda <= 0 or shares <= 0:
            return result

        peer_multiple = peer_multiples.get('median_ev_ebitda', 12)

        # 計算隱含企業價值
        implied_ev = ebitda * peer_multiple

        # 轉換為股權價值
        implied_equity = implied_ev - debt + cash

        implied_price = implied_equity / shares
        if implied_price > 0:
            result['ev_ebitda_implied_price'] = round(implied_price, 2)
            result['implied_ev'] = round(implied_ev, 0)

        return result

    def _ev_revenue_valuation(self, current_ev_revenue: float, revenue: float,
                              ev: float, market_cap: float, debt: float, cash: float,
                              shares: float, peer_multiples: Dict) -> Dict[str, Any]:
        """EV/Revenue 倍數估值 (適用於虧損公司)"""
        result = {
            'current_ev_revenue': current_ev_revenue,
            'peer_median_ev_revenue': peer_multiples.get('median_ev_revenue'),
            'ev_revenue_implied_price': None
        }

        if revenue <= 0 or shares <= 0:
            return result

        peer_multiple = peer_multiples.get('median_ev_revenue', 3)

        # 計算隱含企業價值
        implied_ev = revenue * peer_multiple

        # 轉換為股權價值
        implied_equity = implied_ev - debt + cash

        implied_price = implied_equity / shares
        if implied_price > 0:
            result['ev_revenue_implied_price'] = round(implied_price, 2)

        return result

    def _pb_valuation(self, current_pb: float, book_value: float,
                      shares: float, peer_multiples: Dict) -> Dict[str, Any]:
        """P/B 倍數估值"""
        result = {
            'current_pb': current_pb,
            'peer_median_pb': peer_multiples.get('median_pb'),
            'pb_implied_price': None
        }

        if book_value <= 0 or shares <= 0:
            return result

        bvps = book_value / shares
        peer_pb = peer_multiples.get('median_pb', 3)

        implied_price = bvps * peer_pb
        if implied_price > 0:
            result['pb_implied_price'] = round(implied_price, 2)
            result['bvps'] = round(bvps, 2)

        return result

    @staticmethod
    def _harmonic_mean(values: List[float]) -> float:
        """
        計算調和平均數
        比算術平均更適合處理倍數，降低極端值影響
        """
        if not values:
            return None

        # 過濾無效值
        valid = [v for v in values if v and v > 0]
        if not valid:
            return None

        n = len(valid)
        harmonic = n / sum(1/v for v in valid)

        return round(harmonic, 2)
