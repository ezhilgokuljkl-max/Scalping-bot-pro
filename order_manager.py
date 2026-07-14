"""
Order management engine.

Handles order lifecycle including placement, tracking, cancellation,
and execution validation.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from collections import deque

from scalping_bot.order_management.models import (
    Order,
    OrderRequest,
    OrderSide,
    OrderType,
    OrderStatus,
)

logger = logging.getLogger(__name__)


class OrderManager:
    """Manages order lifecycle.

    Handles:
    - Order placement
    - Order tracking
    - Order cancellation
    - Duplicate prevention
    - Order history
    """

    def __init__(self, max_history_size: int = 1000):
        """Initialize order manager.

        Args:
            max_history_size: Maximum size of order history
        """
        self.orders: Dict[str, Order] = {}
        self.order_history: deque = deque(maxlen=max_history_size)
        self.duplicate_check_window_seconds = 5
        self.logger = logging.getLogger(f"{__name__}.OrderManager")

    def create_order(self, request: OrderRequest) -> Optional[Order]:
        """Create a new order.

        Args:
            request: OrderRequest object

        Returns:
            Created Order object
        """
        # Check for duplicates
        if self._is_duplicate(request):
            self.logger.warning(f"Duplicate order detected: {request.symbol} {request.side}")
            return None

        # Create order
        order = Order(
            order_id=f"ORD_{uuid.uuid4().hex[:8]}",
            symbol=request.symbol,
            side=request.side,
            quantity=request.quantity,
            order_type=request.order_type,
            price=request.price,
            stop_price=request.stop_price,
            status=OrderStatus.PENDING,
            metadata=request.metadata,
        )

        self.orders[order.order_id] = order
        self.logger.info(f"Order created: {order.order_id}")
        return order

    def place_order(self, order: Order) -> bool:
        """Place an order.

        Args:
            order: Order to place

        Returns:
            True if successful
        """
        if order.order_id not in self.orders:
            self.logger.error(f"Order not found: {order.order_id}")
            return False

        order.status = OrderStatus.PLACED
        order.updated_at = datetime.now()
        self.logger.info(f"Order placed: {order.order_id}")
        return True

    def execute_order(self, order_id: str, filled_quantity: int, average_price: float) -> Optional[Order]:
        """Mark order as executed.

        Args:
            order_id: Order ID
            filled_quantity: Quantity filled
            average_price: Average execution price

        Returns:
            Updated Order object
        """
        if order_id not in self.orders:
            self.logger.warning(f"Order not found: {order_id}")
            return None

        order = self.orders[order_id]
        order.filled_quantity = filled_quantity
        order.average_price = average_price

        if filled_quantity == order.quantity:
            order.status = OrderStatus.EXECUTED
        elif filled_quantity > 0:
            order.status = OrderStatus.PARTIALLY_EXECUTED

        order.updated_at = datetime.now()
        self.logger.info(
            f"Order executed: {order_id} - {filled_quantity}/{order.quantity} @ {average_price}"
        )
        return order

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order.

        Args:
            order_id: Order ID to cancel

        Returns:
            True if successful
        """
        if order_id not in self.orders:
            self.logger.warning(f"Order not found: {order_id}")
            return False

        order = self.orders[order_id]
        if not order.is_open():
            self.logger.warning(f"Order cannot be cancelled: {order_id}")
            return False

        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now()
        self.logger.info(f"Order cancelled: {order_id}")
        return True

    def reject_order(self, order_id: str, reason: str = "") -> bool:
        """Reject an order.

        Args:
            order_id: Order ID
            reason: Rejection reason

        Returns:
            True if successful
        """
        if order_id not in self.orders:
            return False

        order = self.orders[order_id]
        order.status = OrderStatus.REJECTED
        order.updated_at = datetime.now()
        if reason:
            order.metadata["rejection_reason"] = reason
        self.logger.warning(f"Order rejected: {order_id} - {reason}")
        return True

    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID.

        Args:
            order_id: Order ID

        Returns:
            Order object
        """
        return self.orders.get(order_id)

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get all open orders.

        Args:
            symbol: Optional symbol filter

        Returns:
            List of open orders
        """
        orders = [o for o in self.orders.values() if o.is_open()]
        if symbol:
            orders = [o for o in orders if o.symbol == symbol]
        return orders

    def get_order_history(self, symbol: Optional[str] = None, limit: int = 50) -> List[Order]:
        """Get order history.

        Args:
            symbol: Optional symbol filter
            limit: Maximum number of orders to return

        Returns:
            List of orders from history
        """
        history = list(self.order_history)[-limit:]
        if symbol:
            history = [o for o in history if o.symbol == symbol]
        return history

    def archive_order(self, order_id: str) -> bool:
        """Archive completed order to history.

        Args:
            order_id: Order ID to archive

        Returns:
            True if successful
        """
        if order_id not in self.orders:
            return False

        order = self.orders.pop(order_id)
        self.order_history.append(order)
        self.logger.info(f"Order archived: {order_id}")
        return True

    def _is_duplicate(self, request: OrderRequest) -> bool:
        """Check if order request is a duplicate.

        Args:
            request: OrderRequest to check

        Returns:
            True if duplicate found
        """
        now = datetime.now()
        for order in self.orders.values():
            if (
                order.symbol == request.symbol
                and order.side == request.side
                and order.is_open()
                and (now - order.created_at).total_seconds() < self.duplicate_check_window_seconds
            ):
                return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """Get order statistics.

        Returns:
            Dictionary with stats
        """
        total_orders = len(self.orders) + len(self.order_history)
        open_orders = len([o for o in self.orders.values() if o.is_open()])
        executed_orders = len([o for o in self.order_history if o.status == OrderStatus.EXECUTED])
        cancelled_orders = len([o for o in self.order_history if o.status == OrderStatus.CANCELLED])
        rejected_orders = len([o for o in self.order_history if o.status == OrderStatus.REJECTED])

        return {
            "total_orders": total_orders,
            "open_orders": open_orders,
            "executed_orders": executed_orders,
            "cancelled_orders": cancelled_orders,
            "rejected_orders": rejected_orders,
            "execution_rate": (
                (executed_orders / total_orders * 100) if total_orders > 0 else 0
            ),
        }

    def reset(self) -> None:
        """Reset order manager."""
        self.orders.clear()
        self.order_history.clear()
        self.logger.info("Order manager reset")
