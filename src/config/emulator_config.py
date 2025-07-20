"""
Emulator Configuration
"""
from typing import Dict, Any, List
import json
from pathlib import Path

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class EmulatorConfig:
    """
    Configuration manager for the emulator
    """

    def __init__(self, config_path: str = "config/emulator_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_default_config()
        self._load_config()

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            "simulation": {
                "start_time": None,  # Will be set from data
                "time_step_minutes": 1,
                "auto_save_interval": 60,  # seconds
                "enable_logging": True,
                "log_level": "INFO"
            },
            "trading": {
                "default_leverage": 10,
                "max_leverage": 100,
                "commission_rate": 0.0007,
                "min_commission": 0.04,
                "enable_slippage": True,
                "slippage_config": {
                    "0": 0.0001,
                    "100": 0.0005,
                    "1000": 0.001,
                    "10000": 0.002
                }
            },
            "data": {
                "klines_data_path": "klines_data",
                "state_data_path": "data",
                "enable_caching": True,
                "cache_size": 1000
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "enable_cors": True,
                "rate_limit": 1000  # requests per minute
            },
            "risk_management": {
                "max_position_size": 10000,  # USDT
                "max_daily_loss": 1000,  # USDT
                "enable_position_limits": True,
                "max_positions_per_symbol": 1
            },
            "supported_symbols": [
                "ADA-USDT", "AAVE-USDT", "APT-USDT", "ARB-USDT", "ATOM-USDT",
                "AVAX-USDT", "BNB-USDT", "BTC-USDT", "DOGE-USDT", "1000CAT-USDT",
                "1000CHEEMS-USDT", "1000PEPE-USDT"
            ]
        }

    def _load_config(self):
        """Load configuration from file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    file_config = json.load(f)

                # Merge with defaults
                self._merge_config(self.config, file_config)
                logger.info(f"Configuration loaded from {self.config_path}")
            else:
                self._save_config()
                logger.info(f"Default configuration saved to {self.config_path}")

        except Exception as e:
            logger.error(f"Error loading configuration: {e}")

    def _merge_config(self, default: Dict, override: Dict):
        """Recursively merge configuration dictionaries"""
        for key, value in override.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value

    def _save_config(self):
        """Save current configuration to file"""
        try:
            self.config_path.parent.mkdir(exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2, default=str)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

    def get(self, key_path: str, default=None):
        """
        Get configuration value by dot-separated path

        Args:
            key_path: e.g., "trading.default_leverage"
            default: Default value if not found

        Returns:
            Configuration value
        """
        try:
            keys = key_path.split('.')
            value = self.config

            for key in keys:
                value = value[key]

            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value):
        """
        Set configuration value by dot-separated path

        Args:
            key_path: e.g., "trading.default_leverage"
            value: Value to set
        """
        try:
            keys = key_path.split('.')
            config = self.config

            # Navigate to parent of target
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]

            # Set the value
            config[keys[-1]] = value
            logger.info(f"Configuration updated: {key_path} = {value}")

        except Exception as e:
            logger.error(f"Error setting configuration {key_path}: {e}")

    def save(self):
        """Save current configuration to file"""
        self._save_config()

    def reload(self):
        """Reload configuration from file"""
        self._load_config()

    def get_trading_config(self) -> Dict[str, Any]:
        """Get trading configuration"""
        return self.config.get("trading", {})

    def get_simulation_config(self) -> Dict[str, Any]:
        """Get simulation configuration"""
        return self.config.get("simulation", {})

    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration"""
        return self.config.get("api", {})

    def get_supported_symbols(self) -> List[str]:
        """Get list of supported trading symbols"""
        return self.config.get("supported_symbols", [])

    def is_symbol_supported(self, symbol: str) -> bool:
        """Check if symbol is supported"""
        return symbol in self.get_supported_symbols()

# Global configuration instance
emulator_config = EmulatorConfig()