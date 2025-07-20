"""
State Manager for persisting emulator state between runs
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from src.trading.models import Order, Position, Balance
from src.utils.logger import setup_logger
from src.config.settings import settings

logger = setup_logger(__name__)

class StateManager:
    """
    Manages persistence of emulator state
    """

    def __init__(self, state_path: str = None):
        """
        Initialize StateManager

        Args:
            state_path: Path to state directory
        """
        self.state_path = Path(state_path or settings.STATE_DATA_PATH)
        self.state_path.mkdir(exist_ok=True)

        # State files
        self.balances_file = self.state_path / "balances.json"
        self.positions_file = self.state_path / "positions.json"
        self.orders_file = self.state_path / "orders.json"
        self.order_history_file = self.state_path / "order_history.json"
        self.simulation_state_file = self.state_path / "simulation_state.json"

    def save_balances(self, balances: Dict[str, Balance]):
        """Save balances to file"""
        try:
            balances_data = {
                asset: balance.to_dict() for asset, balance in balances.items()
            }

            with open(self.balances_file, 'w') as f:
                json.dump(balances_data, f, indent=2, default=str)

            logger.info(f"Balances saved to {self.balances_file}")

        except Exception as e:
            logger.error(f"Error saving balances: {e}")

    def load_balances(self) -> Dict[str, Balance]:
        """Load balances from file"""
        try:
            if not self.balances_file.exists():
                logger.info("No saved balances found, using defaults")
                return {}

            with open(self.balances_file, 'r') as f:
                balances_data = json.load(f)

            balances = {}
            for asset, data in balances_data.items():
                balance = Balance(
                    asset=data['asset'],
                    free=float(data['free']),
                    locked=float(data['locked']),
                    total=float(data['total'])
                )
                balances[asset] = balance

            logger.info(f"Balances loaded from {self.balances_file}")
            return balances

        except Exception as e:
            logger.error(f"Error loading balances: {e}")
            return {}

    def save_positions(self, positions: Dict[str, Position]):
        """Save positions to file"""
        try:
            positions_data = {
                pos_key: position.to_dict() for pos_key, position in positions.items()
            }

            with open(self.positions_file, 'w') as f:
                json.dump(positions_data, f, indent=2, default=str)

            logger.info(f"Positions saved to {self.positions_file}")

        except Exception as e:
            logger.error(f"Error saving positions: {e}")

    def load_positions(self) -> Dict[str, Position]:
        """Load positions from file"""
        try:
            if not self.positions_file.exists():
                logger.info("No saved positions found")
                return {}

            with open(self.positions_file, 'r') as f:
                positions_data = json.load(f)

            positions = {}
            for pos_key, data in positions_data.items():
                from src.trading.models import PositionSide

                position = Position(
                    symbol=data['symbol'],
                    side=PositionSide(data['side']),
                    quantity=float(data['quantity']),
                    entry_price=float(data['entryPrice']),
                    current_price=float(data['markPrice']),
                    unrealized_pnl=float(data['unrealizedPnl']),
                    realized_pnl=float(data['realizedPnl']),
                    leverage=int(data['leverage']),
                    margin=float(data['margin']),
                    take_profit_price=float(data['takeProfit']) if data.get('takeProfit') else None,
                    stop_loss_price=float(data['stopLoss']) if data.get('stopLoss') else None
                )
                positions[pos_key] = position

            logger.info(f"Positions loaded from {self.positions_file}")
            return positions

        except Exception as e:
            logger.error(f"Error loading positions: {e}")
            return {}

    def save_orders(self, orders: Dict[str, Order]):
        """Save open orders to file"""
        try:
            orders_data = {
                order_id: order.to_dict() for order_id, order in orders.items()
            }

            with open(self.orders_file, 'w') as f:
                json.dump(orders_data, f, indent=2, default=str)

            logger.info(f"Orders saved to {self.orders_file}")

        except Exception as e:
            logger.error(f"Error saving orders: {e}")

    def load_orders(self) -> Dict[str, Order]:
        """Load open orders from file"""
        try:
            if not self.orders_file.exists():
                logger.info("No saved orders found")
                return {}

            with open(self.orders_file, 'r') as f:
                orders_data = json.load(f)

            orders = {}
            for order_id, data in orders_data.items():
                from src.trading.models import OrderSide, OrderType, PositionSide, OrderStatus

                order = Order(
                    id=data['orderId'],
                    symbol=data['symbol'],
                    side=OrderSide(data['side']),
                    position_side=PositionSide(data['positionSide']),
                    order_type=OrderType(data['type']),
                    quantity=float(data['quantity']),
                    price=float(data['price']),
                    executed_price=float(data['executedPrice']),
                    executed_quantity=float(data['executedQty']),
                    status=OrderStatus(data['status']),
                    take_profit_price=float(data['takeProfit']) if data.get('takeProfit') else None,
                    stop_loss_price=float(data['stopLoss']) if data.get('stopLoss') else None,
                    commission=float(data['commission']),
                    created_time=datetime.fromtimestamp(int(data['createTime']) / 1000),
                    executed_time=datetime.fromtimestamp(int(data['updateTime']) / 1000) if data.get('updateTime') else None
                )
                orders[order_id] = order

            logger.info(f"Orders loaded from {self.orders_file}")
            return orders

        except Exception as e:
            logger.error(f"Error loading orders: {e}")
            return {}

    def save_order_history(self, order_history: list):
        """Save order history to file"""
        try:
            history_data = [order.to_dict() for order in order_history]

            with open(self.order_history_file, 'w') as f:
                json.dump(history_data, f, indent=2, default=str)

            logger.info(f"Order history saved to {self.order_history_file}")

        except Exception as e:
            logger.error(f"Error saving order history: {e}")

    def load_order_history(self) -> list:
        """Load order history from file"""
        try:
            if not self.order_history_file.exists():
                logger.info("No saved order history found")
                return []

            with open(self.order_history_file, 'r') as f:
                history_data = json.load(f)

            order_history = []
            for data in history_data:
                from src.trading.models import OrderSide, OrderType, PositionSide, OrderStatus

                order = Order(
                    id=data['orderId'],
                    symbol=data['symbol'],
                    side=OrderSide(data['side']),
                    position_side=PositionSide(data['positionSide']),
                    order_type=OrderType(data['type']),
                    quantity=float(data['quantity']),
                    price=float(data['price']),
                    executed_price=float(data['executedPrice']),
                    executed_quantity=float(data['executedQty']),
                    status=OrderStatus(data['status']),
                    take_profit_price=float(data['takeProfit']) if data.get('takeProfit') else None,
                    stop_loss_price=float(data['stopLoss']) if data.get('stopLoss') else None,
                    commission=float(data['commission']),
                    created_time=datetime.fromtimestamp(int(data['createTime']) / 1000),
                    executed_time=datetime.fromtimestamp(int(data['updateTime']) / 1000) if data.get('updateTime') else None
                )
                order_history.append(order)

            logger.info(f"Order history loaded from {self.order_history_file}")
            return order_history

        except Exception as e:
            logger.error(f"Error loading order history: {e}")
            return []

    def save_simulation_state(self, current_time: datetime, total_pnl: float):
        """Save simulation state"""
        try:
            state_data = {
                "current_time": current_time.isoformat(),
                "total_pnl": total_pnl,
                "last_save": datetime.now().isoformat()
            }

            with open(self.simulation_state_file, 'w') as f:
                json.dump(state_data, f, indent=2, default=str)

            logger.info(f"Simulation state saved to {self.simulation_state_file}")

        except Exception as e:
            logger.error(f"Error saving simulation state: {e}")

    def load_simulation_state(self) -> tuple[Optional[datetime], float]:
        """Load simulation state"""
        try:
            if not self.simulation_state_file.exists():
                logger.info("No saved simulation state found")
                return None, 0.0

            with open(self.simulation_state_file, 'r') as f:
                state_data = json.load(f)

            current_time = datetime.fromisoformat(state_data['current_time'])
            total_pnl = float(state_data['total_pnl'])

            logger.info(f"Simulation state loaded from {self.simulation_state_file}")
            return current_time, total_pnl

        except Exception as e:
            logger.error(f"Error loading simulation state: {e}")
            return None, 0.0

    def save_all_state(self, balance_manager, order_engine, time_manager):
        """Save all state"""
        try:
            # Save balances
            self.save_balances(balance_manager.balances)

            # Save positions
            self.save_positions(balance_manager.positions)

            # Save orders
            self.save_orders(order_engine.orders)

            # Save order history
            self.save_order_history(order_engine.order_history)

            # Save simulation state
            self.save_simulation_state(time_manager.current_time, balance_manager.total_pnl)

            logger.info("All state saved successfully")

        except Exception as e:
            logger.error(f"Error saving all state: {e}")

    def load_all_state(self, balance_manager, order_engine, time_manager):
        """Load all state"""
        try:
            # Load balances
            balances = self.load_balances()
            if balances:
                balance_manager.balances = balances

            # Load positions
            positions = self.load_positions()
            if positions:
                balance_manager.positions = positions

            # Load orders
            orders = self.load_orders()
            if orders:
                order_engine.orders = orders

            # Load order history
            order_history = self.load_order_history()
            if order_history:
                order_engine.order_history = order_history

            # Load simulation state
            current_time, total_pnl = self.load_simulation_state()
            if current_time:
                time_manager.set_current_time(current_time)
                balance_manager.total_pnl = total_pnl

            logger.info("All state loaded successfully")

        except Exception as e:
            logger.error(f"Error loading all state: {e}")

    def clear_state(self):
        """Clear all saved state"""
        try:
            for file_path in [self.balances_file, self.positions_file, self.orders_file,
                            self.order_history_file, self.simulation_state_file]:
                if file_path.exists():
                    file_path.unlink()

            logger.info("All state cleared")

        except Exception as e:
            logger.error(f"Error clearing state: {e}")