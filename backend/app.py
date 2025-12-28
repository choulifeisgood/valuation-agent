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
            return jsonify({
                'basic_info': {
                    'ticker': demo_info['ticker'],
                    'company_name': demo_info['company_name'],
                    'sector': demo_info['sector'],
                    'industry': demo_info['industry'],
                    'currency': 'USD',
                    'current_price': demo_info['current_price'],
                    'market_cap': demo_info['market_cap'],
                },
                'key_metrics': {
                    'pe_ratio': 28.5,
                    'pb_ratio': 12.3,
                    'ps_ratio': 7.8,
                    'ev_ebitda': 22.1,
                    'profit_margin': 0.25,
                    'roe': 0.45,
                    'debt_equity': 1.8,
                    'current_ratio': 1.1,
                },
                'valuation': {
                    'dcf_value': demo_info['current_price'] * 1.15,
                    'relative_value': demo_info['current_price'] * 1.08,
                    'fair_value_low': demo_info['current_price'] * 0.9,
                    'fair_value_mid': demo_info['current_price'] * 1.1,
                    'fair_value_high': demo_info['current_price'] * 1.3,
                },
                'risk_assessment': {
                    'altman_z': 3.2,
                    'altman_zone': '安全區',
                    'piotroski_f': 7,
                    'piotroski_rating': '財務健康',
                    'risk_level': '低風險',
                },
                'recommendation': {
                    'rating': '買入',
                    'target_price': demo_info['current_price'] * 1.15,
                    'upside': 0.15,
                },
                'football_field': [
                    {'method': 'DCF', 'low': demo_info['current_price'] * 0.95, 'mid': demo_info['current_price'] * 1.15, 'high': demo_info['current_price'] * 1.35},
                    {'method': 'P/E', 'low': demo_info['current_price'] * 0.9, 'mid': demo_info['current_price'] * 1.08, 'high': demo_info['current_price'] * 1.25},
                    {'method': 'EV/EBITDA', 'low': demo_info['current_price'] * 0.88, 'mid': demo_info['current_price'] * 1.05, 'high': demo_info['current_price'] * 1.22},
                ],
                'analysis_summary': f'[DEMO 模式] {demo_info["company_name"]} 是一家領先的{demo_info["industry"]}公司。基於 DCF 和相對估值分析，目標價為 ${demo_info["current_price"] * 1.15:.2f}，相對當前價格有 15% 的上漲空間。',
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
