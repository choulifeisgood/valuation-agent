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

# CORS 配置 - 允許 Vercel 前端域名
cors_origins = os.environ.get('CORS_ORIGINS', '*').split(',')
CORS(app, origins=cors_origins, supports_credentials=True)

# 初始化 Agents
data_agent = DataAgent()
forensic_agent = ForensicAgent()
valuation_agent = ValuationAgent()
synthesis_agent = SynthesisAgent()


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({'status': 'healthy', 'message': 'Valuation Agent API is running'})


@app.route('/api/analyze', methods=['POST'])
def analyze_stock():
    """
    主要估值分析端點
    接收股票代碼，回傳完整估值報告
    """
    try:
        data = request.get_json()
        ticker = data.get('ticker', '').upper().strip()

        if not ticker:
            return jsonify({'error': '請提供股票代碼'}), 400

        # Step 1: 數據獲取 (Data Agent)
        stock_data = data_agent.fetch_stock_data(ticker)
        if stock_data.get('error'):
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
