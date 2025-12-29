"""
AI 股票估值 Agent - Flask 主應用
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from agents.data_agent import DataAgent
from agents.forensic_agent import ForensicAgent
from agents.valuation_agent import ValuationAgent
from agents.synthesis_agent import SynthesisAgent
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# CORS 配置 - 允許所有來源
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=False)

# 初始化 Agents
data_agent = DataAgent()
forensic_agent = ForensicAgent()
valuation_agent = ValuationAgent()
synthesis_agent = SynthesisAgent()


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({'status': 'healthy', 'message': 'Valuation Agent API is running'})


def get_demo_data(ticker):
    """返回模擬數據用於展示"""
    demo_stocks = {
        'DEMO': {
            'ticker': 'DEMO',
            'company_name': 'Demo Company Inc.',
            'sector': 'Technology',
            'industry': 'Software',
            'current_price': 150.00,
            'market_cap': 2500000000000,
            'beta': 1.2,
        },
        'AAPL': {
            'ticker': 'AAPL',
            'company_name': 'Apple Inc.',
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
            'current_price': 195.00,
            'market_cap': 3000000000000,
            'beta': 1.25,
        },
        'MSFT': {
            'ticker': 'MSFT',
            'company_name': 'Microsoft Corporation',
            'sector': 'Technology',
            'industry': 'Software',
            'current_price': 425.00,
            'market_cap': 3150000000000,
            'beta': 0.9,
        }
    }
    return demo_stocks.get(ticker, demo_stocks['DEMO'])


@app.route('/api/analyze', methods=['POST'])
def analyze_stock():
    """
    主要估值分析端點
    接收股票代碼，回傳完整估值報告
    """
    try:
        data = request.get_json()
        ticker = data.get('ticker', '').upper().strip()
        use_demo = data.get('demo', False) or ticker == 'DEMO'

        if not ticker:
            return jsonify({'error': '請提供股票代碼'}), 400

        # Demo 模式 - 返回模擬報告
        if use_demo:
            demo_info = get_demo_data(ticker if ticker != 'DEMO' else 'DEMO')
            price = demo_info['current_price']
            return jsonify({
                'basic_info': {
                    'ticker': demo_info['ticker'],
                    'company_name': demo_info['company_name'],
                    'sector': demo_info['sector'],
                    'industry': demo_info['industry'],
                    'currency': 'USD',
                    'current_price': price,
                    'market_cap': demo_info['market_cap'],
                    'analysis_date': '2025-12-28',
                },
                'key_metrics': {
                    'valuation_ratios': {
                        'pe_ratio': 28.5,
                        'forward_pe': 25.2,
                        'pb_ratio': 12.3,
                        'ps_ratio': 7.8,
                        'ev_ebitda': 22.1,
                        'ev_revenue': 8.5,
                    },
                    'profitability': {
                        'profit_margin': '25.0%',
                        'operating_margin': '30.2%',
                        'ebitda_margin': '35.5%',
                        'roe': '45.0%',
                        'roa': '22.0%',
                    },
                    'financial_health': {
                        'debt_equity': 1.8,
                        'current_ratio': 1.1,
                    },
                    'growth': {
                        'revenue_growth': '12.5%',
                        'earnings_growth': '15.8%',
                    },
                    'yield': {
                        'dividend_yield': '0.5%',
                        'fcf_yield': '3.2%',
                    },
                },
                'valuation': {
                    'dcf_valuation': {
                        'intrinsic_value': price * 1.15,
                        'wacc': '10.5%',
                        'terminal_growth': '2.5%',
                        'fcf_growth_assumed': '8.0%',
                    },
                    'relative_valuation': {
                        'pe_implied': price * 1.08,
                        'ev_ebitda_implied': price * 1.05,
                        'ev_revenue_implied': price * 1.02,
                        'peer_median_pe': 26.5,
                        'peer_median_ev_ebitda': 20.0,
                    },
                    'fair_value_range': {
                        'low': price * 0.9,
                        'mid': price * 1.1,
                        'high': price * 1.3,
                    },
                },
                'risk_assessment': {
                    'altman_z_score': {
                        'score': 3.2,
                        'zone': '安全區',
                        'interpretation': '財務狀況良好，破產風險極低',
                    },
                    'piotroski_f_score': {
                        'score': 7,
                        'max_score': 9,
                        'rating': '財務健康',
                        'interpretation': '公司財務體質強健',
                    },
                    'overall_risk': {
                        'level': '低風險',
                        'description': '公司財務穩健，估值合理',
                    },
                    'risk_flags': [],
                    'wacc_adjustment': None,
                },
                'recommendation': {
                    'rating': '買入',
                    'description': '基於 DCF 和相對估值分析，股價具有上漲空間',
                    'upside': 0.15,
                    'current_price': price,
                    'target_price': price * 1.15,
                },
                'football_field': {
                    'current_price': price,
                    'bars': [
                        {'method': 'DCF 估值', 'low': price * 0.95, 'mid': price * 1.15, 'high': price * 1.35},
                        {'method': 'P/E 倍數', 'low': price * 0.9, 'mid': price * 1.08, 'high': price * 1.25},
                        {'method': 'EV/EBITDA', 'low': price * 0.88, 'mid': price * 1.05, 'high': price * 1.22},
                    ],
                },
                'methodology': {
                    'dcf_weight': 0.6,
                    'relative_weight': 0.4,
                    'note': 'DCF 採用 FCFF 模型，相對估值採用同業中位數',
                },
                'analysis_summary': f'[DEMO 模式] {demo_info["company_name"]} 是一家領先的{demo_info["industry"]}公司。基於 DCF 和相對估值分析，目標價為 ${price * 1.15:.2f}，相對當前價格有 15% 的上漲空間。',
                'disclaimer': '此為展示用模擬數據，僅供系統功能測試，不構成投資建議。',
                'demo_mode': True,
            })

        # Step 1: 數據獲取 (Data Agent)
        stock_data = data_agent.fetch_stock_data(ticker)
        if stock_data.get('error'):
            # 如果是限流錯誤，建議使用 demo 模式
            if '限流' in stock_data['error']:
                return jsonify({
                    'error': stock_data['error'],
                    'hint': '可以輸入 "DEMO" 來測試系統功能'
                }), 404
            return jsonify({'error': stock_data['error']}), 404

        # Step 2: 風險評分 (Forensic Agent)
        risk_scores = forensic_agent.calculate_risk_scores(stock_data)

        # Step 3: 估值計算 (Valuation Agent)
        valuation_result = valuation_agent.calculate_valuation(stock_data, risk_scores)

        # Step 4: 報告生成 (Synthesis Agent)
        report = synthesis_agent.generate_report(
            ticker=ticker,
            stock_data=stock_data,
            risk_scores=risk_scores,
            valuation=valuation_result
        )

        return jsonify(report)

    except Exception as e:
        return jsonify({'error': f'分析過程發生錯誤: {str(e)}'}), 500


@app.route('/api/quick-quote', methods=['GET'])
def quick_quote():
    """快速報價端點"""
    ticker = request.args.get('ticker', '').upper().strip()
    if not ticker:
        return jsonify({'error': '請提供股票代碼'}), 400

    try:
        quote = data_agent.get_quick_quote(ticker)
        return jsonify(quote)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 根路徑重定向到健康檢查
@app.route('/')
def root():
    return jsonify({
        'name': 'AI Stock Valuation Agent API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'analyze': 'POST /api/analyze',
            'quick_quote': 'GET /api/quick-quote'
        }
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'true').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
