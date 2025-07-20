"""
Balance Manager for handling account balances and leverage
"""
from typing import Dict, Optional, List
from datetime import datetime

from src.trading.models import Balance, Position
from src.utils.logger import setup_logger
from src.config.settings import settings

logger = setup_logger(__name__)

class BalanceManager:
    """
    Manages account balances, positions, and leverage calculations
    """

    def __init__(self, initial_balance: float = None):
        """
        Initialize BalanceManager

        Args:
            initial_balance: Initial USDT balance (defaults to settings)
        """
        self.initial_balance = initial_balance or settings.DEFAULT_BALANCE
        self.balances: Dict[str, Balance] = {
            "USDT": Balance(asset="USDT", free=self.initial_balance, total=self.initial_balance)
        }
        self.positions: Dict[str, Position] = {}  # symbol -> Position
        self.total_pnl = 0.0

    def get_balance(self, asset: str = "USDT") -> Optional[Balance]:
        """Get balance for specific asset"""
        return self.balances.get(asset)

    def get_all_balances(self) -> List[Balance]:
        """Get all balances"""
        return list(self.balances.values())

    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for specific symbol"""
        return self.positions.get(symbol)

    def get_all_positions(self) -> List[Position]:
        """Get all positions"""
        return list(self.positions.values())

    def calculate_commission(self, order_value: float) -> float:
        """
        Calculate commission for order

        Args:
            order_value: Order value in USDT

        Returns:
            Commission amount in USDT
        """
        commission = order_value * settings.COMMISSION_RATE
        return max(commission, settings.MIN_COMMISSION)

    def calculate_slippage(self, order_value: float, current_price: float) -> float:
        """
        Calculate slippage for order

        Args:
            order_value: Order value in USDT
            current_price: Current market price

        Returns:
            Slippage percentage
        """
        slippage_pct = settings.get_slippage(order_value)
        return current_price * slippage_pct

    def can_place_order(self, symbol: str, side: str, quantity: float,
                       price: float, leverage: int = None) -> tuple[bool, str]:
        """
        Check if order can be placed

        Args:
            symbol: Trading pair
            side: BUY or SELL
            quantity: Order quantity
            price: Order price
            leverage: Leverage (defaults to settings)

        Returns:
            (can_place, error_message)
        """
        leverage = leverage or settings.DEFAULT_LEVERAGE
        order_value = quantity * price
        required_margin = order_value / leverage
        commission = self.calculate_commission(order_value)

        usdt_balance = self.balances.get("USDT")
        if not usdt_balance:
            return False, "No USDT balance"

        total_required = required_margin + commission

        if usdt_balance.free < total_required:
            return False, f"Insufficient balance. Required: {total_required:.2f} USDT, Available: {usdt_balance.free:.2f} USDT"

        return True, ""

    def execute_order(self, order, executed_price: float, executed_quantity: float) -> bool:
        """
        Execute an order and update balances/positions

        Args:
            order: Order object
            executed_price: Execution price
            executed_quantity: Executed quantity

        Returns:
            True if successful
        """
        try:
            order_value = executed_quantity * executed_price
            commission = self.calculate_commission(order_value)
            required_margin = order_value / order.leverage if hasattr(order, 'leverage') else order_value / settings.DEFAULT_LEVERAGE

            # Update USDT balance
            usdt_balance = self.balances["USDT"]
            usdt_balance.free -= (required_margin + commission)
            usdt_balance.total = usdt_balance.free + usdt_balance.locked

            # Update or create position
            position_key = f"{order.symbol}_{order.position_side.value}"

            if position_key in self.positions:
                # Update existing position
                position = self.positions[position_key]
                if order.side.value == order.position_side.value:
                    # Adding to position
                    total_quantity = position.quantity + executed_quantity
                    total_value = (position.quantity * position.entry_price) + (executed_quantity * executed_price)
                    position.entry_price = total_value / total_quantity
                    position.quantity = total_quantity
                else:
                    # Reducing position
                    position.quantity -= executed_quantity
                    if position.quantity <= 0:
                        # Position closed
                        realized_pnl = (executed_price - position.entry_price) * executed_quantity
                        if order.position_side.value == "SHORT":
                            realized_pnl = -realized_pnl

                        position.realized_pnl += realized_pnl
                        self.total_pnl += realized_pnl

                        # Return margin to balance
                        usdt_balance.free += position.margin
                        usdt_balance.total = usdt_balance.free + usdt_balance.locked

                        # Remove position if fully closed
                        if position.quantity <= 0:
                            del self.positions[position_key]
            else:
                # Create new position
                position = Position(
                    symbol=order.symbol,
                    side=order.position_side,
                    quantity=executed_quantity,
                    entry_price=executed_price,
                    current_price=executed_price,
                    leverage=settings.DEFAULT_LEVERAGE,
                    margin=required_margin,
                    take_profit_price=order.take_profit_price,
                    stop_loss_price=order.stop_loss_price
                )
                self.positions[position_key] = position

            # Update order
            order.executed_price = executed_price
            order.executed_quantity = executed_quantity
            order.commission = commission
            order.status = "FILLED"
            order.executed_time = datetime.now()

            logger.info(f"Order executed: {order.symbol} {order.side.value} {executed_quantity} @ {executed_price}")
            return True

        except Exception as e:
            logger.error(f"Error executing order: {e}")
            return False

    def update_position_prices(self, symbol: str, current_price: float):
        """
        Update position prices and calculate unrealized PnL

        Args:
            symbol: Trading pair
            current_price: Current market price
        """
        for position_key, position in self.positions.items():
            if position.symbol == symbol:
                position.current_price = current_price

                # Calculate unrealized PnL
                if position.side.value == "LONG":
                    position.unrealized_pnl = (current_price - position.entry_price) * position.quantity
                else:  # SHORT
                    position.unrealized_pnl = (position.entry_price - current_price) * position.quantity

    def check_tp_sl(self, symbol: str, current_price: float, high: float, low: float) -> List[Position]:
        """
        Check if TP/SL conditions are met

        Args:
            symbol: Trading pair
            current_price: Current price
            high: Candle high
            low: Candle low

        Returns:
            List of positions that should be closed
        """
        positions_to_close = []

        for position_key, position in list(self.positions.items()):
            if position.symbol != symbol:
                continue

            should_close = False

            # Check take profit
            if position.take_profit_price:
                if position.side.value == "LONG" and high >= position.take_profit_price:
                    should_close = True
                elif position.side.value == "SHORT" and low <= position.take_profit_price:
                    should_close = True

            # Check stop loss
            if position.stop_loss_price:
                if position.side.value == "LONG" and low <= position.stop_loss_price:
                    should_close = True
                elif position.side.value == "SHORT" and high >= position.stop_loss_price:
                    should_close = True

            if should_close:
                positions_to_close.append(position)

        return positions_to_close

    def get_account_summary(self) -> Dict:
        """Get account summary for API response"""
        total_balance = sum(balance.total for balance in self.balances.values())
        total_unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())

        return {
            "totalBalance": str(total_balance),
            "totalUnrealizedPnl": str(total_unrealized_pnl),
            "totalRealizedPnl": str(self.total_pnl),
            "totalPnl": str(self.total_pnl + total_unrealized_pnl)
        }