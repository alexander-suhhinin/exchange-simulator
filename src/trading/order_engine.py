"""
Order Engine for executing trading orders
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from src.trading.models import Order, OrderSide, OrderType, PositionSide, OrderStatus
from src.trading.balance_manager import BalanceManager
from src.utils.logger import setup_logger
from src.config.settings import settings

logger = setup_logger(__name__)

class OrderEngine:
    """
    Handles order creation, execution, and management
    """

    def __init__(self, balance_manager: BalanceManager):
        """
        Initialize OrderEngine

        Args:
            balance_manager: BalanceManager instance
        """
        self.balance_manager = balance_manager
        self.orders: Dict[str, Order] = {}  # order_id -> Order
        self.order_history: List[Order] = []

    def create_order(self, symbol: str, side: str, quantity: float,
                    order_type: str = "MARKET", price: float = 0.0,
                    take_profit: Optional[float] = None,
                    stop_loss: Optional[float] = None,
                    leverage: int = None) -> Tuple[bool, str, Optional[Order]]:
        """
        Create a new order

        Args:
            symbol: Trading pair
            side: BUY or SELL
            quantity: Order quantity
            order_type: Order type (MARKET, LIMIT)
            price: Order price (for limit orders)
            take_profit: Take profit price
            stop_loss: Stop loss price
            leverage: Leverage

        Returns:
            (success, message, order)
        """
        try:
            # Validate parameters
            if side not in ["BUY", "SELL"]:
                return False, "Invalid side", None

            if order_type not in ["MARKET", "LIMIT"]:
                return False, "Invalid order type", None

            if quantity <= 0:
                return False, "Invalid quantity", None

            # Determine position side
            position_side = PositionSide.LONG if side == "BUY" else PositionSide.SHORT

            # Set leverage
            leverage = leverage or settings.DEFAULT_LEVERAGE

            # Get current price for market orders
            if order_type == "MARKET":
                # This will be set during execution
                execution_price = 0.0
            else:
                execution_price = price

            # Create order
            order = Order(
                symbol=symbol,
                side=OrderSide(side),
                position_side=position_side,
                order_type=OrderType(order_type),
                quantity=quantity,
                price=price,
                take_profit_price=take_profit,
                stop_loss_price=stop_loss
            )

            # Add leverage attribute
            order.leverage = leverage

            # Check if order can be placed
            can_place, error_msg = self.balance_manager.can_place_order(
                symbol, side, quantity, execution_price, leverage
            )

            if not can_place:
                return False, error_msg, None

            # Store order
            self.orders[order.id] = order

            logger.info(f"Order created: {order.id} - {symbol} {side} {quantity}")

            return True, "Order created successfully", order

        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return False, f"Error creating order: {str(e)}", None

    def execute_market_order(self, order: Order, current_price: float,
                           high: float, low: float) -> bool:
        """
        Execute a market order

        Args:
            order: Order to execute
            current_price: Current market price
            high: Candle high
            low: Candle low

        Returns:
            True if successful
        """
        try:
            # Calculate execution price with slippage
            order_value = order.quantity * current_price
            slippage = self.balance_manager.calculate_slippage(order_value, current_price)

            if order.side == OrderSide.BUY:
                # Buy orders execute at ask (higher price)
                execution_price = current_price + slippage
            else:
                # Sell orders execute at bid (lower price)
                execution_price = current_price - slippage

            # Execute order
            success = self.balance_manager.execute_order(
                order, execution_price, order.quantity
            )

            if success:
                # Move to history
                self.order_history.append(order)
                if order.id in self.orders:
                    del self.orders[order.id]

                logger.info(f"Market order executed: {order.symbol} {order.side.value} "
                          f"{order.quantity} @ {execution_price}")

            return success

        except Exception as e:
            logger.error(f"Error executing market order: {e}")
            return False

    def process_candle(self, symbol: str, open_price: float, high: float,
                      low: float, close: float, volume: float):
        """
        Process a new candle and check for order execution

        Args:
            symbol: Trading pair
            open_price: Candle open price
            high: Candle high
            low: Candle low
            close: Candle close
            volume: Candle volume
        """
        try:
            # Update position prices
            self.balance_manager.update_position_prices(symbol, close)

            # Check TP/SL conditions with improved logic
            positions_to_close = self._check_tp_sl_improved(symbol, open_price, high, low, close)

            for position, trigger_type, trigger_price in positions_to_close:
                # Create closing order
                closing_side = "SELL" if position.side.value == "LONG" else "BUY"

                success, msg, order = self.create_order(
                    symbol=symbol,
                    side=closing_side,
                    quantity=position.quantity,
                    order_type="MARKET"
                )

                if success and order:
                    # Execute immediately at trigger price
                    self.execute_market_order(order, trigger_price, high, low)
                    logger.info(f"{trigger_type} triggered for {symbol}: {position.side.value} "
                              f"position closed at {trigger_price}")

            # Execute pending market orders
            pending_orders = [
                order for order in self.orders.values()
                if order.symbol == symbol and order.order_type == OrderType.MARKET
            ]

            for order in pending_orders:
                self.execute_market_order(order, close, high, low)

        except Exception as e:
            logger.error(f"Error processing candle for {symbol}: {e}")

    def _check_tp_sl_improved(self, symbol: str, open_price: float, high: float,
                             low: float, close: float) -> List[tuple]:
        """
        Improved TP/SL checking with more precise logic

        Args:
            symbol: Trading pair
            open_price: Candle open price
            high: Candle high
            low: Candle low
            close: Candle close

        Returns:
            List of (position, trigger_type, trigger_price) tuples
        """
        positions_to_close = []

        for position_key, position in list(self.balance_manager.positions.items()):
            if position.symbol != symbol:
                continue

            # Check take profit
            if position.take_profit_price:
                if position.side.value == "LONG" and high >= position.take_profit_price:
                    # TP triggered for long position
                    positions_to_close.append((position, "TP", position.take_profit_price))
                elif position.side.value == "SHORT" and low <= position.take_profit_price:
                    # TP triggered for short position
                    positions_to_close.append((position, "TP", position.take_profit_price))

            # Check stop loss
            if position.stop_loss_price:
                if position.side.value == "LONG" and low <= position.stop_loss_price:
                    # SL triggered for long position
                    positions_to_close.append((position, "SL", position.stop_loss_price))
                elif position.side.value == "SHORT" and high >= position.stop_loss_price:
                    # SL triggered for short position
                    positions_to_close.append((position, "SL", position.stop_loss_price))

        return positions_to_close

    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        return self.orders.get(order_id)

    def get_open_orders(self, symbol: str = None) -> List[Order]:
        """Get open orders"""
        orders = list(self.orders.values())
        if symbol:
            orders = [order for order in orders if order.symbol == symbol]
        return orders

    def get_order_history(self, symbol: str = None, limit: int = 100) -> List[Order]:
        """Get order history"""
        history = self.order_history[-limit:] if limit else self.order_history
        if symbol:
            history = [order for order in history if order.symbol == symbol]
        return history

    def cancel_order(self, order_id: str) -> Tuple[bool, str]:
        """
        Cancel an order

        Args:
            order_id: Order ID to cancel

        Returns:
            (success, message)
        """
        if order_id not in self.orders:
            return False, "Order not found"

        order = self.orders[order_id]
        order.status = OrderStatus.CANCELLED

        # Move to history
        self.order_history.append(order)
        del self.orders[order_id]

        logger.info(f"Order cancelled: {order_id}")
        return True, "Order cancelled successfully"