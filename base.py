"""
Base strategy class that all strategies should inherit from.

Defines the interface and common functionality for all trading strategies.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from scalping_bot.config.constants import OrderSide, OrderType

logger = logging.getLogger(__name__)


@dataclass
class SignalData:
    """Data class for trading signals."""

    timestamp: datetime
    symbol: str
    side: OrderSide  # BUY or SELL
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: Optional[float] = None
    target_3: Optional[float] = None
    quantity: int = 1
    signal_type: str = "automatic"  # automatic or manual
    signal_source: str = "strategy"  # strategy, tradingview, manual
    confidence: float = 0.5  # 0.0 to 1.0
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate signal data."""
        if self.entry_price <= 0:
            raise ValueError("Entry price must be positive")
        if self.stop_loss <= 0:
            raise ValueError("Stop loss must be positive")
        if self.target_1 <= 0:
            raise ValueError("Target must be positive")
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")


class BaseStrategy(ABC):
    """Base class for all trading strategies.

    Provides interface and common functionality for implementing
    trading strategies. All strategies should inherit from this class.
    """

    def __init__(self, name: str, description: str = ""):
        """Initialize strategy.

        Args:
            name: Strategy name
            description: Strategy description
        """
        self.name = name
        self.description = description
        self.enabled = True
        self.last_signal: Optional[SignalData] = None
        self.signal_count = 0
        self.logger = logging.getLogger(f"{__name__}.{name}")

    @abstractmethod
    def analyze(self, symbol: str, market_data: Dict[str, Any]) -> Optional[SignalData]:
        """Analyze market data and generate trading signal.

        Args:
            symbol: Trading symbol
            market_data: Current market data (OHLCV, indicators, etc.)

        Returns:
            SignalData if signal generated, None otherwise

        Raises:
            NotImplementedError: Subclass must implement this method
        """
        pass

    @abstractmethod
    def validate_signal(self, signal: SignalData) -> bool:
        """Validate trading signal before execution.

        Args:
            signal: Signal to validate

        Returns:
            True if signal is valid, False otherwise

        Raises:
            NotImplementedError: Subclass must implement this method
        """
        pass

    def on_trade_opened(self, trade_data: Dict[str, Any]) -> None:
        """Callback when trade is opened.

        Args:
            trade_data: Opened trade information
        """
        self.logger.info(f"Trade opened: {trade_data}")

    def on_trade_closed(self, trade_data: Dict[str, Any]) -> None:
        """Callback when trade is closed.

        Args:
            trade_data: Closed trade information
        """
        self.logger.info(f"Trade closed: {trade_data}")

    def on_stop_loss_hit(self, trade_data: Dict[str, Any]) -> None:
        """Callback when stop loss is hit.

        Args:
            trade_data: Trade information
        """
        self.logger.warning(f"Stop loss hit: {trade_data}")

    def on_target_hit(self, trade_data: Dict[str, Any]) -> None:
        """Callback when target is hit.

        Args:
            trade_data: Trade information
        """
        self.logger.info(f"Target hit: {trade_data}")

    def reset(self) -> None:
        """Reset strategy state."""
        self.last_signal = None
        self.signal_count = 0
        self.logger.info(f"Strategy {self.name} reset")

    def get_info(self) -> Dict[str, Any]:
        """Get strategy information.

        Returns:
            Dictionary with strategy info
        """
        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "signal_count": self.signal_count,
            "last_signal": self.last_signal,
        }
