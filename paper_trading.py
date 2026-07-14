"""
Paper trading broker implementation for backtesting and simulation.

Allows trading without real money using virtual capital.
Simulates market conditions including slippage and commissions.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from decimal import Decimal

from scalping_bot.brokers.base import (
    BaseBroker,
    Order,
    Position,
    BrokerAccount,
    OrderStatus,
    OrderType,
    OrderSide,
)

logger = logging.getLogger(__name__)


class PaperTradingBroker(BaseBroker):
    """Paper trading broker for simulation.

    Simulates trading without real money.
    Tracks all orders and positions in memory.
    """

    def __init__(
        self,
        starting_capital: float = 100000,
        commission_percentage: float = 0.02,  # 0.02% per trade
        slippage_percentage: float = 0.1,  # 0.1% slippage
        enable_slippage: bool = True,
    ):
        """Initialize paper trading broker.

        Args:
            starting_capital: Starting capital in INR
            commission_percentage: Commission per trade in %
            slippage_percentage: Slippage simulation in %
            enable_slippage: Enable slippage simulation
        """
        super().__init__(broker_name="PaperTrading")
        self.starting_capital = starting_capital
        self.commission_percentage = commission_percentage
        self.slippage_percentage = slippage_percentage
        self.enable_slippage = enable_slippage

        # Account state
        self.balance = starting_capital
        self.available_balance = starting_capital
        self.used_margin = 0.0

        # Storage
        self.orders: Dict[str, Order] = {}
        self.positions: Dict[str, Position] = {}
        self.closed_trades: List[Dict[str, Any]] = []

        # Counters
        self.total_trades = 0
        self.today_pnl = 0.0
        self.total_pnl = 0.0

    async def connect(self) -> bool:
        """Connect to paper trading broker.

        Returns:
            True (always successful for paper trading)
        """
        self.is_connected = True
        self.account = BrokerAccount(
            account_id="PAPER_" + str(uuid.uuid4())[:8],
            broker_name=self.broker_name,
            balance=self.balance,
            available_balance=self.available_balance,
            is_live=False,
        )
        self.logger.info("Paper trading broker connected")
        return True

    async def disconnect(self) -> bool:
        """Disconnect from paper trading broker.

        Returns:
            True (always successful)
        """
        self.is_connected = False
        self.logger.info("Paper trading broker disconnected")
        return True

    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: int,
        order_type: OrderType,
        price: float,
        stop_price: Optional[float] = None,
    ) -> Optional[Order]:
        """Place an order.

        Args:
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Order quantity
            order_type: Order type
            price: Limit price
            stop_price: Stop price

        Returns:
            Order object if successful
        """
        try:
            # Apply slippage to execution price
            execution_price = self._apply_slippage(price, side)

            # Calculate commission
            trade_value = execution_price * quantity
            commission = trade_value * (self.commission_percentage / 100)

            # Check if enough balance
            required_margin = trade_value + commission
            if required_margin > self.available_balance:
                self.logger.warning(f"Insufficient balance for order. Required: {required_margin}, Available: {self.available_balance}")
                return None

            # Create order
            order = Order(
                order_id="ORD_" + str(uuid.uuid4())[:8],
                symbol=symbol,
                side=side,
                quantity=quantity,
                order_type=order_type,
                price=execution_price,
                stop_price=stop_price,
                status=OrderStatus.EXECUTED,
                filled_quantity=quantity,
                average_price=execution_price,
                commission=commission,
            )

            # Store order
            self.orders[order.order_id] = order

            # Update balance
            if side == OrderSide.BUY:
                self.available_balance -= required_margin
                self.used_margin += trade_value
            else:  # SELL
                self.available_balance -= commission
                # For short selling in paper trading
                self.balance += (execution_price * quantity)

            # Create or update position
            self._update_position(symbol, side, quantity, execution_price)

            self.total_trades += 1
            self.logger.info(f"Order placed: {order.order_id} - {side} {quantity} {symbol} @ {execution_price}")

            return order

        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return None

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order.

        Args:
            order_id: Order ID

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
        self.logger.info(f"Order cancelled: {order_id}")
        return True

    async def modify_order(
        self,
        order_id: str,
        quantity: Optional[int] = None,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> Optional[Order]:
        """Modify an order.

        Args:
            order_id: Order ID
            quantity: New quantity
            price: New price
            stop_price: New stop price

        Returns:
            Modified order
        """
        if order_id not in self.orders:
            self.logger.warning(f"Order not found: {order_id}")
            return None

        order = self.orders[order_id]
        if quantity is not None:
            order.quantity = quantity
        if price is not None:
            order.price = price
        if stop_price is not None:
            order.stop_price = stop_price

        order.updated_at = datetime.now()
        self.logger.info(f"Order modified: {order_id}")
        return order

    async def get_order(self, order_id: str) -> Optional[Order]:
        """Get order details.

        Args:
            order_id: Order ID

        Returns:
            Order object
        """
        return self.orders.get(order_id)

    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get all open orders.

        Args:
            symbol: Optional symbol filter

        Returns:
            List of open orders
        """
        open_orders = [o for o in self.orders.values() if o.is_open()]
        if symbol:
            open_orders = [o for o in open_orders if o.symbol == symbol]
        return open_orders

    async def get_positions(self, symbol: Optional[str] = None) -> List[Position]:
        """Get all open positions.

        Args:
            symbol: Optional symbol filter

        Returns:
            List of positions
        """
        positions = list(self.positions.values())
        if symbol:
            positions = [p for p in positions if p.symbol == symbol]
        return positions

    async def get_account_info(self) -> Optional[BrokerAccount]:
        """Get account information.

        Returns:
            BrokerAccount object
        """
        if not self.account:
            return None

        self.account.balance = self.balance
        self.account.available_balance = self.available_balance
        self.account.used_margin = self.used_margin
        self.account.open_positions = len(self.positions)
        self.account.open_orders = len([o for o in self.orders.values() if o.is_open()])
        self.account.total_trades = self.total_trades
        self.account.today_pnl = self.today_pnl
        self.account.total_pnl = self.total_pnl
        self.account.updated_at = datetime.now()

        return self.account

    async def close_position(
        self, position_id: str, quantity: Optional[int] = None
    ) -> Optional[Order]:
        """Close a position.

        Args:
            position_id: Position ID
            quantity: Quantity to close

        Returns:
            Closing order
        """
        if position_id not in self.positions:
            self.logger.warning(f"Position not found: {position_id}")
            return None

        position = self.positions[position_id]
        close_qty = quantity or position.quantity

        # Opposite side to close
        close_side = OrderSide.SELL if position.side == OrderSide.BUY else OrderSide.BUY

        # Place closing order
        closing_order = await self.place_order(
            symbol=position.symbol,
            side=close_side,
            quantity=close_qty,
            order_type=OrderType.MARKET,
            price=position.current_price,
        )

        if closing_order:
            # Calculate P&L
            pnl, pnl_pct = position.calculate_pnl(closing_order.average_price)
            self.today_pnl += pnl
            self.total_pnl += pnl

            # Store closed trade
            self.closed_trades.append({
                "position_id": position_id,
                "symbol": position.symbol,
                "side": position.side.value,
                "entry_price": position.entry_price,
                "exit_price": closing_order.average_price,
                "quantity": close_qty,
                "pnl": pnl,
                "pnl_percentage": pnl_pct,
                "closed_at": datetime.now(),
            })

            # Remove or reduce position
            if close_qty >= position.quantity:
                del self.positions[position_id]
            else:
                position.quantity -= close_qty

            self.logger.info(f"Position closed: {position_id} - PnL: {pnl}")
            return closing_order

        return None

    async def get_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get market data (simulated for paper trading).

        Args:
            symbol: Trading symbol

        Returns:
            Market data dictionary
        """
        # In real implementation, this would fetch actual market data
        # For paper trading, return dummy data
        return {
            "symbol": symbol,
            "close": 100.0,
            "high": 101.0,
            "low": 99.0,
            "open": 99.5,
            "volume": 1000000,
            "timestamp": datetime.now(),
        }

    async def validate_connection(self) -> bool:
        """Validate connection.

        Returns:
            True if connected
        """
        return self.is_connected

    def _apply_slippage(self, price: float, side: OrderSide) -> float:
        """Apply slippage to execution price.

        Args:
            price: Original price
            side: BUY or SELL

        Returns:
            Price with slippage applied
        """
        if not self.enable_slippage:
            return price

        slippage = price * (self.slippage_percentage / 100)
        if side == OrderSide.BUY:
            return price + slippage
        else:  # SELL
            return price - slippage

    def _update_position(
        self, symbol: str, side: OrderSide, quantity: int, price: float
    ) -> None:
        """Update or create position.

        Args:
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Quantity
            price: Entry price
        """
        position_id = f"{symbol}_{side.value}"

        if position_id in self.positions:
            position = self.positions[position_id]
            # Average entry price
            total_quantity = position.quantity + quantity
            position.entry_price = (
                (position.entry_price * position.quantity) + (price * quantity)
            ) / total_quantity
            position.quantity = total_quantity
        else:
            self.positions[position_id] = Position(
                position_id=position_id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                entry_price=price,
                current_price=price,
            )

    def get_closed_trades(self) -> List[Dict[str, Any]]:
        """Get list of closed trades.

        Returns:
            List of closed trades
        """
        return self.closed_trades

    def reset(self) -> None:
        """Reset paper trading broker state."""
        self.balance = self.starting_capital
        self.available_balance = self.starting_capital
        self.used_margin = 0.0
        self.orders.clear()
        self.positions.clear()
        self.closed_trades.clear()
        self.total_trades = 0
        self.today_pnl = 0.0
        self.total_pnl = 0.0
        self.logger.info("Paper trading broker reset")
