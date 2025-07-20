"""
Trade Logger for detailed trading operation logging
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from src.utils.logger import setup_logger
from src.config.settings import settings

logger = setup_logger(__name__)

class TradeLogger:
    """
    Specialized logger for trading operations
    """

    def __init__(self, log_path: str = None):
        """
        Initialize TradeLogger

        Args:
            log_path: Path to trade logs directory
        """
        self.log_path = Path(log_path or settings.STATE_DATA_PATH) / "logs"
        self.log_path.mkdir(exist_ok=True)

        # Log files
        self.trades_file = self.log_path / "trades.jsonl"
        self.executions_file = self.log_path / "executions.jsonl"
        self.errors_file = self.log_path / "errors.jsonl"

    def log_order_created(self, order, current_time: datetime):
        """Log order creation"""
        log_entry = {
            "timestamp": current_time.isoformat(),
            "type": "order_created",
            "order_id": order.id,
            "symbol": order.symbol,
            "side": order.side.value if hasattr(order.side, 'value') else str(order.side),
            "quantity": order.quantity,
            "price": order.price,
            "order_type": order.order_type.value if hasattr(order.order_type, 'value') else str(order.order_type),
            "take_profit": order.take_profit_price,
            "stop_loss": order.stop_loss_price
        }

        self._write_log(self.trades_file, log_entry)
        logger.info(f"Order created: {order.id} - {order.symbol} {order.side} {order.quantity}")

    def log_order_executed(self, order, execution_price: float, execution_time: datetime):
        """Log order execution"""
        log_entry = {
            "timestamp": execution_time.isoformat(),
            "type": "order_executed",
            "order_id": order.id,
            "symbol": order.symbol,
            "side": order.side.value if hasattr(order.side, 'value') else str(order.side),
            "quantity": order.executed_quantity,
            "execution_price": execution_price,
            "commission": order.commission,
            "slippage": abs(execution_price - order.price) if order.price > 0 else 0
        }

        self._write_log(self.executions_file, log_entry)
        logger.info(f"Order executed: {order.id} - {order.symbol} {order.side} "
                   f"{order.executed_quantity} @ {execution_price}")

    def log_position_opened(self, position, current_time: datetime):
        """Log position opening"""
        log_entry = {
            "timestamp": current_time.isoformat(),
            "type": "position_opened",
            "symbol": position.symbol,
            "side": position.side.value if hasattr(position.side, 'value') else str(position.side),
            "quantity": position.quantity,
            "entry_price": position.entry_price,
            "leverage": position.leverage,
            "margin": position.margin
        }

        self._write_log(self.trades_file, log_entry)
        logger.info(f"Position opened: {position.symbol} {position.side} "
                   f"{position.quantity} @ {position.entry_price}")

    def log_position_closed(self, position, close_price: float, pnl: float, current_time: datetime):
        """Log position closing"""
        log_entry = {
            "timestamp": current_time.isoformat(),
            "type": "position_closed",
            "symbol": position.symbol,
            "side": position.side.value if hasattr(position.side, 'value') else str(position.side),
            "quantity": position.quantity,
            "entry_price": position.entry_price,
            "close_price": close_price,
            "pnl": pnl,
            "leverage": position.leverage
        }

        self._write_log(self.trades_file, log_entry)
        logger.info(f"Position closed: {position.symbol} {position.side} "
                   f"{position.quantity} @ {close_price}, PnL: {pnl:.2f}")

    def log_tp_sl_triggered(self, position, trigger_type: str, trigger_price: float, current_time: datetime):
        """Log TP/SL trigger"""
        log_entry = {
            "timestamp": current_time.isoformat(),
            "type": f"{trigger_type}_triggered",
            "symbol": position.symbol,
            "side": position.side.value if hasattr(position.side, 'value') else str(position.side),
            "quantity": position.quantity,
            "entry_price": position.entry_price,
            "trigger_price": trigger_price,
            "trigger_type": trigger_type
        }

        self._write_log(self.trades_file, log_entry)
        logger.info(f"{trigger_type.upper()} triggered: {position.symbol} {position.side} "
                   f"@ {trigger_price}")

    def log_error(self, error_type: str, error_msg: str, context: Dict[str, Any] = None):
        """Log trading errors"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "error",
            "error_type": error_type,
            "error_msg": error_msg,
            "context": context or {}
        }

        self._write_log(self.errors_file, log_entry)
        logger.error(f"Trading error ({error_type}): {error_msg}")

    def log_balance_update(self, asset: str, old_balance: float, new_balance: float,
                          change_reason: str, current_time: datetime):
        """Log balance changes"""
        log_entry = {
            "timestamp": current_time.isoformat(),
            "type": "balance_update",
            "asset": asset,
            "old_balance": old_balance,
            "new_balance": new_balance,
            "change": new_balance - old_balance,
            "change_reason": change_reason
        }

        self._write_log(self.trades_file, log_entry)
        logger.info(f"Balance updated: {asset} {old_balance:.2f} -> {new_balance:.2f} "
                   f"({change_reason})")

    def _write_log(self, file_path: Path, log_entry: Dict[str, Any]):
        """Write log entry to file"""
        try:
            with open(file_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Error writing to log file {file_path}: {e}")

    def get_trade_summary(self, start_time: datetime = None, end_time: datetime = None) -> Dict[str, Any]:
        """Get trading summary from logs"""
        try:
            summary = {
                "total_orders": 0,
                "total_executions": 0,
                "total_positions_opened": 0,
                "total_positions_closed": 0,
                "total_volume": 0.0,
                "total_commission": 0.0,
                "total_pnl": 0.0,
                "errors": 0
            }

            # Read trades log
            if self.trades_file.exists():
                with open(self.trades_file, 'r') as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            entry_time = datetime.fromisoformat(entry['timestamp'])

                            if start_time and entry_time < start_time:
                                continue
                            if end_time and entry_time > end_time:
                                continue

                            if entry['type'] == 'order_created':
                                summary['total_orders'] += 1
                            elif entry['type'] == 'position_opened':
                                summary['total_positions_opened'] += 1
                            elif entry['type'] == 'position_closed':
                                summary['total_positions_closed'] += 1
                                summary['total_pnl'] += entry.get('pnl', 0)

                        except Exception as e:
                            logger.error(f"Error parsing trade log entry: {e}")

            # Read executions log
            if self.executions_file.exists():
                with open(self.executions_file, 'r') as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            entry_time = datetime.fromisoformat(entry['timestamp'])

                            if start_time and entry_time < start_time:
                                continue
                            if end_time and entry_time > end_time:
                                continue

                            summary['total_executions'] += 1
                            summary['total_volume'] += entry.get('quantity', 0) * entry.get('execution_price', 0)
                            summary['total_commission'] += entry.get('commission', 0)

                        except Exception as e:
                            logger.error(f"Error parsing execution log entry: {e}")

            # Read errors log
            if self.errors_file.exists():
                with open(self.errors_file, 'r') as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            entry_time = datetime.fromisoformat(entry['timestamp'])

                            if start_time and entry_time < start_time:
                                continue
                            if end_time and entry_time > end_time:
                                continue

                            summary['errors'] += 1

                        except Exception as e:
                            logger.error(f"Error parsing error log entry: {e}")

            return summary

        except Exception as e:
            logger.error(f"Error generating trade summary: {e}")
            return {}