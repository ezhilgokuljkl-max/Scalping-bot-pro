"""
Ultra-short scalping strategy implementation.

A fast scalping strategy designed for 30-second to 5-minute trades.
Focuses on quick profits with tight risk management.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import logging

from scalping_bot.strategies.base import BaseStrategy, SignalData
from scalping_bot.config.constants import OrderSide

logger = logging.getLogger(__name__)


class ScalpingStrategy(BaseStrategy):
    """Ultra-short scalping strategy.

    Entry signals:
    - Price breakout with volume confirmation
    - Support/resistance levels
    - Momentum shifts

    Exit signals:
    - Target reached (automatic close)
    - Stop loss hit (automatic exit)
    - Time-based exit (after 5 minutes)
    """

    def __init__(self):
        """Initialize scalping strategy."""
        super().__init__(
            name="Scalping Strategy",
            description="Ultra-short scalping strategy for 30sec-5min trades",
        )
        self.min_profit_target = 3  # Minimum 3 points
        self.max_profit_target = 10  # Maximum 10 points
        self.min_stop_loss = 2  # Minimum 2 points
        self.max_stop_loss = 15  # Maximum 15 points
        self.volume_threshold = 1.5  # Volume multiplier
        self.rsi_period = 14
        self.rsi_overbought = 70
        self.rsi_oversold = 30

    def analyze(
        self, symbol: str, market_data: Dict[str, Any]
    ) -> Optional[SignalData]:
        """Analyze market for scalping signal.

        Args:
            symbol: Trading symbol
            market_data: Market data including OHLCV and indicators

        Returns:
            SignalData if signal found, None otherwise
        """
        if not self.enabled:
            return None

        try:
            # Extract market data
            current_price = market_data.get("close")
            volume = market_data.get("volume", 0)
            avg_volume = market_data.get("avg_volume", 0)
            high = market_data.get("high")
            low = market_data.get("low")
            open_price = market_data.get("open")

            if not all([current_price, high, low, open_price]):
                self.logger.warning(f"Missing market data for {symbol}")
                return None

            # Volume check: Volume should be above average
            if avg_volume > 0 and volume < avg_volume * self.volume_threshold:
                return None

            # Get indicators
            rsi = market_data.get("rsi")
            macd = market_data.get("macd")
            bb_upper = market_data.get("bb_upper")
            bb_lower = market_data.get("bb_lower")

            # Check for BUY signal
            buy_signal = self._check_buy_signal(
                current_price, volume, avg_volume, rsi, macd, open_price, low
            )

            if buy_signal:
                return self._create_signal(
                    symbol=symbol,
                    side=OrderSide.BUY,
                    entry_price=current_price,
                    market_data=market_data,
                )

            # Check for SELL signal
            sell_signal = self._check_sell_signal(
                current_price, volume, avg_volume, rsi, macd, open_price, high
            )

            if sell_signal:
                return self._create_signal(
                    symbol=symbol,
                    side=OrderSide.SELL,
                    entry_price=current_price,
                    market_data=market_data,
                )

            return None

        except Exception as e:
            self.logger.error(f"Error analyzing market for {symbol}: {e}")
            return None

    def _check_buy_signal(
        self,
        current_price: float,
        volume: float,
        avg_volume: float,
        rsi: Optional[float],
        macd: Optional[Dict[str, float]],
        open_price: float,
        low: float,
    ) -> bool:
        """Check if BUY signal conditions are met.

        Args:
            current_price: Current price
            volume: Current volume
            avg_volume: Average volume
            rsi: RSI indicator value
            macd: MACD indicator values
            open_price: Open price
            low: Low price

        Returns:
            True if BUY signal conditions met
        """
        # Condition 1: Price above open (bullish candle starting)
        if current_price <= open_price:
            return False

        # Condition 2: Volume confirmation
        if volume < avg_volume * self.volume_threshold:
            return False

        # Condition 3: RSI below overbought
        if rsi is not None and rsi > self.rsi_overbought:
            return False

        # Condition 4: MACD bullish signal
        if macd is not None:
            macd_line = macd.get("macd")
            signal_line = macd.get("signal")
            if macd_line is not None and signal_line is not None:
                # MACD should be positive or just crossing above
                if macd_line < signal_line - 0.1:  # Not bullish enough
                    return False

        # Condition 5: Support level (low should not be too far from current)
        risk_points = current_price - low
        if risk_points > 15:  # Too much risk
            return False

        return True

    def _check_sell_signal(
        self,
        current_price: float,
        volume: float,
        avg_volume: float,
        rsi: Optional[float],
        macd: Optional[Dict[str, float]],
        open_price: float,
        high: float,
    ) -> bool:
        """Check if SELL signal conditions are met.

        Args:
            current_price: Current price
            volume: Current volume
            avg_volume: Average volume
            rsi: RSI indicator value
            macd: MACD indicator values
            open_price: Open price
            high: High price

        Returns:
            True if SELL signal conditions met
        """
        # Condition 1: Price below open (bearish candle starting)
        if current_price >= open_price:
            return False

        # Condition 2: Volume confirmation
        if volume < avg_volume * self.volume_threshold:
            return False

        # Condition 3: RSI below oversold
        if rsi is not None and rsi < self.rsi_oversold:
            return False

        # Condition 4: MACD bearish signal
        if macd is not None:
            macd_line = macd.get("macd")
            signal_line = macd.get("signal")
            if macd_line is not None and signal_line is not None:
                # MACD should be negative or just crossing below
                if macd_line > signal_line + 0.1:  # Not bearish enough
                    return False

        # Condition 5: Resistance level
        risk_points = high - current_price
        if risk_points > 15:  # Too much risk
            return False

        return True

    def _create_signal(
        self, symbol: str, side: OrderSide, entry_price: float, market_data: Dict[str, Any]
    ) -> SignalData:
        """Create trading signal.

        Args:
            symbol: Trading symbol
            side: BUY or SELL
            entry_price: Entry price
            market_data: Market data

        Returns:
            SignalData object
        """
        # Calculate stop loss
        stop_loss = self._calculate_stop_loss(entry_price, side, market_data)

        # Calculate targets
        target_1, target_2, target_3 = self._calculate_targets(
            entry_price, side, stop_loss
        )

        signal = SignalData(
            timestamp=datetime.now(),
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
            target_3=target_3,
            quantity=1,
            signal_type="automatic",
            signal_source="strategy",
            confidence=0.7,
            metadata={
                "volume": market_data.get("volume"),
                "rsi": market_data.get("rsi"),
                "macd": market_data.get("macd"),
            },
        )

        self.last_signal = signal
        self.signal_count += 1
        self.logger.info(f"Signal generated: {signal}")

        return signal

    def _calculate_stop_loss(self, entry_price: float, side: OrderSide, market_data: Dict[str, Any]) -> float:
        """Calculate stop loss level.

        Args:
            entry_price: Entry price
            side: BUY or SELL
            market_data: Market data

        Returns:
            Stop loss price
        """
        if side == OrderSide.BUY:
            low = market_data.get("low", entry_price)
            stop_loss_points = min(max(entry_price - low, self.min_stop_loss), self.max_stop_loss)
            return entry_price - stop_loss_points
        else:  # SELL
            high = market_data.get("high", entry_price)
            stop_loss_points = min(max(high - entry_price, self.min_stop_loss), self.max_stop_loss)
            return entry_price + stop_loss_points

    def _calculate_targets(self, entry_price: float, side: OrderSide, stop_loss: float) -> tuple:
        """Calculate profit target levels.

        Args:
            entry_price: Entry price
            side: BUY or SELL
            stop_loss: Stop loss price

        Returns:
            Tuple of (target_1, target_2, target_3)
        """
        if side == OrderSide.BUY:
            risk = entry_price - stop_loss
            target_1 = entry_price + risk * 1.0  # 1:1 risk-reward
            target_2 = entry_price + risk * 1.5  # 1:1.5 risk-reward
            target_3 = entry_price + risk * 2.0  # 1:2 risk-reward
        else:  # SELL
            risk = stop_loss - entry_price
            target_1 = entry_price - risk * 1.0
            target_2 = entry_price - risk * 1.5
            target_3 = entry_price - risk * 2.0

        return (target_1, target_2, target_3)

    def validate_signal(self, signal: SignalData) -> bool:
        """Validate signal before execution.

        Args:
            signal: Signal to validate

        Returns:
            True if signal is valid
        """
        try:
            # Check entry price
            if signal.entry_price <= 0:
                self.logger.warning("Invalid entry price")
                return False

            # Check stop loss
            if signal.side == OrderSide.BUY:
                if signal.stop_loss >= signal.entry_price:
                    self.logger.warning("Invalid stop loss for BUY")
                    return False
                if signal.entry_price - signal.stop_loss < self.min_stop_loss:
                    self.logger.warning("Stop loss too close")
                    return False
            else:  # SELL
                if signal.stop_loss <= signal.entry_price:
                    self.logger.warning("Invalid stop loss for SELL")
                    return False
                if signal.stop_loss - signal.entry_price < self.min_stop_loss:
                    self.logger.warning("Stop loss too close")
                    return False

            # Check target
            if signal.side == OrderSide.BUY:
                if signal.target_1 <= signal.entry_price:
                    self.logger.warning("Invalid target for BUY")
                    return False
            else:  # SELL
                if signal.target_1 >= signal.entry_price:
                    self.logger.warning("Invalid target for SELL")
                    return False

            # Check quantity
            if signal.quantity <= 0:
                self.logger.warning("Invalid quantity")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating signal: {e}")
            return False
