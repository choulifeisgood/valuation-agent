"""
估值 Agent 配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask 設置
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')

    # API 設置
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')

    # 估值參數預設值
    DEFAULT_RISK_FREE_RATE = 0.045  # 10Y Treasury (4.5%)
    DEFAULT_MARKET_RISK_PREMIUM = 0.055  # 市場風險溢價 (5.5%)
    DEFAULT_TERMINAL_GROWTH_RATE = 0.025  # 終值成長率 (2.5%)
    DEFAULT_PROJECTION_YEARS = 5  # 預測年數

    # 風險評分閾值
    ALTMAN_Z_DISTRESS = 1.81  # 財務困境區
    ALTMAN_Z_SAFE = 2.99  # 安全區

    # WACC 調整係數
    WACC_DISTRESS_PREMIUM = 0.03  # 財務困境時增加 3%
