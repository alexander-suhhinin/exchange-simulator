"""
Configuration settings for BingX Emulator
"""
from typing import Dict, Any
import os

class Settings:
    # API Settings
    API_HOST = "0.0.0.0"
    API_PORT = 8000

    # Trading Settings
    DEFAULT_LEVERAGE = 10
    DEFAULT_BALANCE = 1000.0  # USDT
    COMMISSION_RATE = 0.0007  # 0.07%
    MIN_COMMISSION = 0.04  # USDT

    # Slippage settings (volume in USDT -> slippage percentage)
    SLIPPAGE_CONFIG = {
        0: 0.0001,      # 0.01% for small orders
        100: 0.0005,    # 0.05% for medium orders
        1000: 0.001,    # 0.1% for large orders
        10000: 0.002    # 0.2% for very large orders
    }

    # Data paths
    KLINES_DATA_PATH = "klines_data"
    STATE_DATA_PATH = "data"

    # Time settings
    DEFAULT_TIMEFRAME = "5m"
    BASE_TIMEFRAME = "1m"

    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def get_slippage(cls, volume_usdt: float) -> float:
        """Get slippage percentage based on order volume"""
        for threshold, slippage in sorted(cls.SLIPPAGE_CONFIG.items(), reverse=True):
            if volume_usdt >= threshold:
                return slippage
        return cls.SLIPPAGE_CONFIG[0]

# Global settings instance
settings = Settings()