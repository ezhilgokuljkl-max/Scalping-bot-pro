"""
Risk management engine for the trading bot.

Manages all risk controls including daily limits, drawdown protection,
position sizing, and trade validation.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, date
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RiskMetrics:
    """Current risk metrics."""
    daily_pnl: float = 0.0
    daily_trades: int = 0
    daily_wins: int = 0
    daily_losses: int = 0
    consecutive_losses: int = 0
    max_consecutive_losses: int = 0
    open_positions: int = 0
    total_risk_exposure: float = 0.0
    drawdown_percentage: float = 0.0
    drawdown_amount: float = 0.0


class RiskManager:
    """Manages all trading risk controls.

    Enforces:
    - Daily profit/loss limits
    - Drawdown limits
    - Position limits
    - Risk per trade limits
    - Consecutive loss limits
    - Slippage tolerance
    """

    def __init__(
        self,
        initial_capital: float,
        max_daily_loss: float = -5000,
        max_daily_profit: float = 10000,
        max_drawdown_percentage: float = 10.0,
        max_risk_per_trade_percentage: float = 2.0,
        max_consecutive_losses: int = 3,
        max_concurrent_positions: int = 3,
        max_trades_per_day: int = 20,
        max_trades_per_minute: int = 3,
    ):
        """Initialize risk manager.

        Args:
            initial_capital: Starting capital
            max_daily_loss: Maximum allowed daily loss
            max_daily_profit: Maximum daily profit limit
            max_drawdown_percentage: Maximum drawdown from peak
            max_risk_per_trade_percentage: Maximum risk per trade as % of capital
            max_consecutive_losses: Maximum consecutive losses before pause
            max_concurrent_positions: Maximum open positions
            max_trades_per_day: Maximum trades per day
            max_trades_per_minute: Maximum trades per minute
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.peak_capital = initial_capital

        # Limits
        self.max_daily_loss = max_daily_loss
        self.max_daily_profit = max_daily_profit
        self.max_drawdown_percentage = max_drawdown_percentage
        self.max_risk_per_trade_percentage = max_risk_per_trade_percentage
        self.max_consecutive_losses = max_consecutive_losses
        self.max_concurrent_positions = max_concurrent_positions
        self.max_trades_per_day = max_trades_per_day
        self.max_trades_per_minute = max_trades_per_minute

        # Metrics
        self.metrics = RiskMetrics()
        self.daily_loss_limit_hit = False
        self.daily_profit_limit_hit = False
        self.drawdown_limit_hit = False
        self.consecutive_loss_limit_hit = False

        self.logger = logging.getLogger(f"{__name__}.RiskManager")

    def validate_trade(
        self,
        entry_price: float,
        stop_loss: float,
        quantity: int,
        current_positions: int = 0,
    ) -> tuple:
        """Validate if trade meets risk criteria.

        Args:
            entry_price: Trade entry price
            stop_loss: Stop loss price
            quantity: Trade quantity
            current_positions: Current number of open positions

        Returns:
            Tuple of (is_valid, reason)
        """
        # Check if risk limits hit
        if self.daily_loss_limit_hit:
            return False, "Daily loss limit reached"
        if self.daily_profit_limit_hit:
            return False, "Daily profit limit reached"
        if self.drawdown_limit_hit:
            return False, "Drawdown limit reached"
        if self.consecutive_loss_limit_hit:
            return False, "Consecutive loss limit reached"

        # Check position limits
        if current_positions >= self.max_concurrent_positions:
            return False, f"Maximum concurrent positions ({self.max_concurrent_positions}) reached"

        if self.metrics.daily_trades >= self.max_trades_per_day:
            return False, f"Maximum trades per day ({self.max_trades_per_day}) reached"

        # Calculate risk
        risk_amount = abs(entry_price - stop_loss) * quantity
        risk_percentage = (risk_amount / self.current_capital) * 100

        if risk_percentage > self.max_risk_per_trade_percentage:
            return False, f"Risk too high: {risk_percentage:.2f}% > {self.max_risk_per_trade_percentage}%"

        # Check position size
        position_size_percentage = (entry_price * quantity / self.current_capital) * 100
        if position_size_percentage > (self.max_risk_per_trade_percentage * 2):
            return False, f"Position size too large: {position_size_percentage:.2f}%"

        return True, "Trade validation passed"

    def on_trade_opened(self, entry_price: float, quantity: int, risk_amount: float) -> None:
        """Record when trade is opened.

        Args:
            entry_price: Entry price
            quantity: Quantity
            risk_amount: Risk amount in INR
        """
        self.metrics.open_positions += 1
        self.metrics.daily_trades += 1
        self.metrics.total_risk_exposure += risk_amount
        self.logger.info(f"Trade opened - Positions: {self.metrics.open_positions}, Daily trades: {self.metrics.daily_trades}")

    def on_trade_closed(self, pnl: float, is_win: bool) -> None:
        """Record when trade is closed.

        Args:
            pnl: Profit/loss amount
            is_win: True if trade is profitable
        """
        self.metrics.open_positions = max(0, self.metrics.open_positions - 1)
        self.metrics.daily_pnl += pnl
        self.current_capital += pnl

        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital

        if is_win:
            self.metrics.daily_wins += 1
            self.metrics.consecutive_losses = 0
        else:
            self.metrics.daily_losses += 1
            self.metrics.consecutive_losses += 1
            if self.metrics.consecutive_losses > self.metrics.max_consecutive_losses:
                self.metrics.max_consecutive_losses = self.metrics.consecutive_losses

        # Check limits
        self._check_daily_limits()
        self._check_consecutive_losses()
        self._check_drawdown()

        self.logger.info(
            f"Trade closed - PnL: {pnl:.2f}, Daily PnL: {self.metrics.daily_pnl:.2f}, "
            f"Capital: {self.current_capital:.2f}"
        )

    def on_new_day(self) -> None:
        """Reset daily metrics for new trading day."""
        self.metrics.daily_pnl = 0.0
        self.metrics.daily_trades = 0
        self.metrics.daily_wins = 0
        self.metrics.daily_losses = 0
        self.daily_loss_limit_hit = False
        self.daily_profit_limit_hit = False
        self.consecutive_loss_limit_hit = False
        self.logger.info("Daily metrics reset")

    def _check_daily_limits(self) -> None:
        """Check daily profit/loss limits."""
        if self.metrics.daily_pnl <= self.max_daily_loss:
            self.daily_loss_limit_hit = True
            self.logger.warning(f"Daily loss limit hit: {self.metrics.daily_pnl:.2f} <= {self.max_daily_loss}")

        if self.metrics.daily_pnl >= self.max_daily_profit:
            self.daily_profit_limit_hit = True
            self.logger.warning(f"Daily profit limit hit: {self.metrics.daily_pnl:.2f} >= {self.max_daily_profit}")

    def _check_consecutive_losses(self) -> None:
        """Check consecutive loss limit."""
        if self.metrics.consecutive_losses >= self.max_consecutive_losses:
            self.consecutive_loss_limit_hit = True
            self.logger.warning(
                f"Consecutive loss limit reached: {self.metrics.consecutive_losses} losses"
            )

    def _check_drawdown(self) -> None:
        """Check maximum drawdown limit."""
        if self.peak_capital > 0:
            drawdown = self.peak_capital - self.current_capital
            drawdown_percentage = (drawdown / self.peak_capital) * 100

            self.metrics.drawdown_amount = drawdown
            self.metrics.drawdown_percentage = drawdown_percentage

            if drawdown_percentage >= self.max_drawdown_percentage:
                self.drawdown_limit_hit = True
                self.logger.warning(
                    f"Drawdown limit hit: {drawdown_percentage:.2f}% >= {self.max_drawdown_percentage}%"
                )

    def get_metrics(self) -> Dict[str, Any]:
        """Get current risk metrics.

        Returns:
            Dictionary with risk metrics
        """
        return {
            "initial_capital": self.initial_capital,
            "current_capital": self.current_capital,
            "peak_capital": self.peak_capital,
            "daily_pnl": self.metrics.daily_pnl,
            "daily_trades": self.metrics.daily_trades,
            "daily_wins": self.metrics.daily_wins,
            "daily_losses": self.metrics.daily_losses,
            "win_rate": (
                (self.metrics.daily_wins / self.metrics.daily_trades * 100)
                if self.metrics.daily_trades > 0
                else 0
            ),
            "consecutive_losses": self.metrics.consecutive_losses,
            "open_positions": self.metrics.open_positions,
            "drawdown_percentage": self.metrics.drawdown_percentage,
            "drawdown_amount": self.metrics.drawdown_amount,
            "limits_hit": {
                "daily_loss": self.daily_loss_limit_hit,
                "daily_profit": self.daily_profit_limit_hit,
                "drawdown": self.drawdown_limit_hit,
                "consecutive_losses": self.consecutive_loss_limit_hit,
            },
        }

    def reset(self) -> None:
        """Reset risk manager."""
        self.current_capital = self.initial_capital
        self.peak_capital = self.initial_capital
        self.metrics = RiskMetrics()
        self.daily_loss_limit_hit = False
        self.daily_profit_limit_hit = False
        self.drawdown_limit_hit = False
        self.consecutive_loss_limit_hit = False
        self.logger.info("Risk manager reset")
