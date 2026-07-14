"""
Order models and data structures.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class OrderSide(str, Enum):
    """Order side."""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Order type."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"


class OrderStatus(str, Enum):
    """Order status."""
    PENDING = "PENDING"
    PLACED = "PLACED"
    EXECUTED = "EXECUTED"
    PARTIALLY_EXECUTED = "PARTIALLY_EXECUTED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


@dataclass
class OrderRequest:
    """Order request from strategy."""
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType
    price: float
    stop_price: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Order:
    """Order object."""
    order_id: str
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType
    price: float
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = 0
    average_price: float = 0.0
    commission: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_open(self) -> bool:
        """Check if order is open."""
        return self.status in [
            OrderStatus.PENDING,
            OrderStatus.PLACED,
            OrderStatus.PARTIALLY_EXECUTED,
        ]

    def is_filled(self) -> bool:
        """Check if order is completely filled."""
        return self.filled_quantity == self.quantity

    def fill_percentage(self) -> float:
        """Get fill percentage."""
        if self.quantity == 0:
            return 0.0
        return (self.filled_quantity / self.quantity) * 100
