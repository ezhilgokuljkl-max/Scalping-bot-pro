"""
Position and trade management.

Tracks open positions, calculates P&L, manages trailing stops,
and handles break-even stops.
"""

import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """Trade object."""
    trade_id: str
    symbol: str
    side: str  # BUY or SELL
    entry_price: float
    entry_quantity: int
    stop_loss: float
    target_1: float
    target_2: Optional[float] = None
    target_3: Optional[float] = None
    current_price: float = 0.0
    quantity_closed: int = 0
    entry_time: datetime = field(default_factory=datetime.now)
    current_pnl: float = 0.0
    current_pnl_percentage: float = 0.0
    trailing_stop_enabled: bool = False
    break_even_enabled: bool = False
    highest_price: float = 0.0  # For trailing stop
    lowest_price: float = 0.0  # For trailing stop (short)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def calculate_pnl(self) -> tuple:
        """Calculate current P&L.

        Returns:
            Tuple of (pnl, pnl_percentage)
        """
        open_qty = self.entry_quantity - self.quantity_closed
        if open_qty <= 0:
            return 0.0, 0.0

        if self.side == "BUY":
            pnl = (self.current_price - self.entry_price) * open_qty
            pnl_percentage = ((self.current_price - self.entry_price) / self.entry_price) * 100
        else:  # SELL
            pnl = (self.entry_price - self.current_price) * open_qty
            pnl_percentage = ((self.entry_price - self.current_price) / self.entry_price) * 100

        self.current_pnl = pnl
        self.current_pnl_percentage = pnl_percentage
        return pnl, pnl_percentage

    def update_current_price(self, price: float) -> None:
        """Update current market price.

        Args:
            price: Current price
        """
        self.current_price = price

        if self.side == "BUY":
            if price > self.highest_price:
                self.highest_price = price
        else:  # SELL
            if price < self.lowest_price or self.lowest_price == 0:
                self.lowest_price = price

        self.calculate_pnl()

    def is_open(self) -> bool:
        """Check if trade is still open.

        Returns:
            True if partially or fully open
        """
        return self.quantity_closed < self.entry_quantity

    def open_quantity(self) -> int:
        """Get open quantity.

        Returns:
            Number of open contracts
        """
        return self.entry_quantity - self.quantity_closed


class PositionManager:
    """Manages open positions and trades.

    Handles:
    - Position tracking
    - P&L calculation
    - Trailing stops
    - Break-even stops
    - Partial profit booking
    """

    def __init__(
        self,
        trailing_stop_enabled: bool = True,
        trailing_stop_percentage: float = 2.0,
        break_even_enabled: bool = True,
        break_even_trigger_percentage: float = 50.0,
    ):
        """Initialize position manager.

        Args:
            trailing_stop_enabled: Enable trailing stops
            trailing_stop_percentage: Trail by this percentage
            break_even_enabled: Enable break-even stops
            break_even_trigger_percentage: Trigger BE at this % of target
        """
        self.trailing_stop_enabled = trailing_stop_enabled
        self.trailing_stop_percentage = trailing_stop_percentage
        self.break_even_enabled = break_even_enabled
        self.break_even_trigger_percentage = break_even_trigger_percentage

        self.trades: Dict[str, Trade] = {}
        self.logger = logging.getLogger(f"{__name__}.PositionManager")

    def add_trade(
        self,
        trade_id: str,
        symbol: str,
        side: str,
        entry_price: float,
        quantity: int,
        stop_loss: float,
        target_1: float,
        target_2: Optional[float] = None,
        target_3: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Trade:
        """Add a new trade.

        Args:
            trade_id: Unique trade ID
            symbol: Trading symbol
            side: BUY or SELL
            entry_price: Entry price
            quantity: Entry quantity
            stop_loss: Stop loss price
            target_1: First target
            target_2: Second target (optional)
            target_3: Third target (optional)
            metadata: Additional metadata

        Returns:
            Created Trade object
        """
        trade = Trade(
            trade_id=trade_id,
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            entry_quantity=quantity,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
            target_3=target_3,
            current_price=entry_price,
            trailing_stop_enabled=self.trailing_stop_enabled,
            break_even_enabled=self.break_even_enabled,
            highest_price=entry_price if side == "BUY" else 0.0,
            lowest_price=entry_price if side == "SELL" else float('inf'),
            metadata=metadata or {},
        )

        self.trades[trade_id] = trade
        self.logger.info(f"Trade added: {trade_id} - {side} {quantity} {symbol} @ {entry_price}")
        return trade

    def update_trade_price(self, trade_id: str, current_price: float) -> Optional[Trade]:
        """Update trade current price.

        Args:
            trade_id: Trade ID
            current_price: Current market price

        Returns:
            Updated Trade object
        """
        if trade_id not in self.trades:
            self.logger.warning(f"Trade not found: {trade_id}")
            return None

        trade = self.trades[trade_id]
        trade.update_current_price(current_price)

        # Update trailing stop
        if trade.trailing_stop_enabled:
            self._update_trailing_stop(trade)

        # Check for break-even
        if trade.break_even_enabled:
            self._check_break_even(trade)

        return trade

    def close_trade(self, trade_id: str, close_price: float, quantity: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Close a trade.

        Args:
            trade_id: Trade ID
            close_price: Close price
            quantity: Quantity to close (None = close all)

        Returns:
            Trade summary dictionary
        """
        if trade_id not in self.trades:
            self.logger.warning(f"Trade not found: {trade_id}")
            return None

        trade = self.trades[trade_id]
        close_qty = quantity or trade.open_quantity()

        if close_qty > trade.open_quantity():
            self.logger.warning(f"Cannot close {close_qty}, only {trade.open_quantity()} open")
            return None

        # Calculate P&L
        if trade.side == "BUY":
            pnl = (close_price - trade.entry_price) * close_qty
        else:  # SELL
            pnl = (trade.entry_price - close_price) * close_qty

        trade.quantity_closed += close_qty

        summary = {
            "trade_id": trade_id,
            "symbol": trade.symbol,
            "side": trade.side,
            "entry_price": trade.entry_price,
            "exit_price": close_price,
            "quantity_closed": close_qty,
            "quantity_open": trade.open_quantity(),
            "pnl": pnl,
            "pnl_percentage": (pnl / (trade.entry_price * close_qty)) * 100 if trade.entry_price > 0 else 0,
            "duration_seconds": (datetime.now() - trade.entry_time).total_seconds(),
        }

        if not trade.is_open():
            del self.trades[trade_id]
            self.logger.info(f"Trade closed completely: {trade_id}")
        else:
            self.logger.info(f"Trade partially closed: {trade_id}, {close_qty} contracts")

        return summary

    def get_trade(self, trade_id: str) -> Optional[Trade]:
        """Get trade by ID.

        Args:
            trade_id: Trade ID

        Returns:
            Trade object
        """
        return self.trades.get(trade_id)

    def get_open_trades(self, symbol: Optional[str] = None) -> List[Trade]:
        """Get all open trades.

        Args:
            symbol: Optional symbol filter

        Returns:
            List of open trades
        """
        trades = [t for t in self.trades.values() if t.is_open()]
        if symbol:
            trades = [t for t in trades if t.symbol == symbol]
        return trades

    def get_portfolio_pnl(self) -> tuple:
        """Get total portfolio P&L.

        Returns:
            Tuple of (total_pnl, total_pnl_percentage)
        """
        total_pnl = 0.0
        total_entry_value = 0.0

        for trade in self.trades.values():
            if trade.is_open():
                pnl, _ = trade.calculate_pnl()
                total_pnl += pnl
                total_entry_value += trade.entry_price * trade.open_quantity()

        total_pnl_percentage = (
            (total_pnl / total_entry_value) * 100 if total_entry_value > 0 else 0
        )

        return total_pnl, total_pnl_percentage

    def _update_trailing_stop(self, trade: Trade) -> None:
        """Update trailing stop loss.

        Args:
            trade: Trade object
        """
        if trade.side == "BUY":
            # For long positions, trail from highest price
            trail_distance = trade.highest_price * (self.trailing_stop_percentage / 100)
            new_stop = trade.highest_price - trail_distance
            if new_stop > trade.stop_loss:
                trade.stop_loss = new_stop
        else:  # SELL
            # For short positions, trail from lowest price
            trail_distance = trade.lowest_price * (self.trailing_stop_percentage / 100)
            new_stop = trade.lowest_price + trail_distance
            if new_stop < trade.stop_loss:
                trade.stop_loss = new_stop

    def _check_break_even(self, trade: Trade) -> None:
        """Check if break-even stop should be moved.

        Args:
            trade: Trade object
        """
        if trade.side == "BUY":
            target_distance = trade.target_1 - trade.entry_price
            trigger_price = trade.entry_price + (target_distance * (self.break_even_trigger_percentage / 100))

            if trade.current_price >= trigger_price:
                # Move stop to entry
                if trade.entry_price > trade.stop_loss:
                    trade.stop_loss = trade.entry_price
        else:  # SELL
            target_distance = trade.entry_price - trade.target_1
            trigger_price = trade.entry_price - (target_distance * (self.break_even_trigger_percentage / 100))

            if trade.current_price <= trigger_price:
                # Move stop to entry
                if trade.entry_price < trade.stop_loss:
                    trade.stop_loss = trade.entry_price

    def reset(self) -> None:
        """Reset position manager."""
        self.trades.clear()
        self.logger.info("Position manager reset")
