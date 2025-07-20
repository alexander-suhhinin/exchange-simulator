"""
Trading data models
"""
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass, field
import uuid

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"

class PositionSide(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"

@dataclass
class Order:
    """Trading order model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    side: OrderSide = OrderSide.BUY
    position_side: PositionSide = PositionSide.LONG
    order_type: OrderType = OrderType.MARKET
    quantity: float = 0.0
    price: float = 0.0
    executed_price: float = 0.0
    executed_quantity: float = 0.0
    status: OrderStatus = OrderStatus.PENDING
    take_profit_price: Optional[float] = None
    stop_loss_price: Optional[float] = None
    commission: float = 0.0
    created_time: datetime = field(default_factory=datetime.now)
    executed_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "orderId": self.id,
            "symbol": self.symbol,
            "side": self.side.value if hasattr(self.side, 'value') else str(self.side),
            "positionSide": self.position_side.value if hasattr(self.position_side, 'value') else str(self.position_side),
            "type": self.order_type.value if hasattr(self.order_type, 'value') else str(self.order_type),
            "quantity": str(self.quantity),
            "price": str(self.price),
            "executedPrice": str(self.executed_price),
            "executedQty": str(self.executed_quantity),
            "status": self.status.value if hasattr(self.status, 'value') else str(self.status),
            "takeProfit": str(self.take_profit_price) if self.take_profit_price else None,
            "stopLoss": str(self.stop_loss_price) if self.stop_loss_price else None,
            "commission": str(self.commission),
            "createTime": int(self.created_time.timestamp() * 1000),
            "updateTime": int(self.executed_time.timestamp() * 1000) if self.executed_time else int(self.created_time.timestamp() * 1000)
        }

@dataclass
class Position:
    """Position model"""
    symbol: str = ""
    side: PositionSide = PositionSide.LONG
    quantity: float = 0.0
    entry_price: float = 0.0
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    leverage: int = 10
    margin: float = 0.0
    take_profit_price: Optional[float] = None
    stop_loss_price: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "symbol": self.symbol,
            "side": self.side.value,
            "quantity": str(self.quantity),
            "entryPrice": str(self.entry_price),
            "markPrice": str(self.current_price),
            "unrealizedPnl": str(self.unrealized_pnl),
            "realizedPnl": str(self.realized_pnl),
            "leverage": str(self.leverage),
            "margin": str(self.margin),
            "takeProfit": str(self.take_profit_price) if self.take_profit_price else None,
            "stopLoss": str(self.stop_loss_price) if self.stop_loss_price else None
        }

@dataclass
class Balance:
    """Balance model"""
    asset: str = "USDT"
    free: float = 0.0
    locked: float = 0.0
    total: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "asset": self.asset,
            "free": str(self.free),
            "locked": str(self.locked),
            "total": str(self.total)
        }