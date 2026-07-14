"""
Technical indicators for strategy analysis.

Provides common indicators like RSI, MACD, Bollinger Bands, etc.
"""

from typing import Optional, Dict, Any, List
import logging
import numpy as np
from collections import deque

logger = logging.getLogger(__name__)


class IndicatorCalculator:
    """Calculate technical indicators from market data."""

    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
        """Calculate Relative Strength Index (RSI).

        Args:
            prices: List of closing prices
            period: RSI period (default 14)

        Returns:
            RSI value (0-100) or None if insufficient data
        """
        if len(prices) < period + 1:
            return None

        deltas = np.diff(prices)
        gains = deltas.copy()
        losses = deltas.copy()

        gains[gains < 0] = 0
        losses[losses > 0] = 0
        losses = abs(losses)

        avg_gain = gains[-period:].mean()
        avg_loss = losses[-period:].mean()

        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi)

    @staticmethod
    def calculate_macd(
        prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Optional[Dict[str, float]]:
        """Calculate MACD (Moving Average Convergence Divergence).

        Args:
            prices: List of closing prices
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period

        Returns:
            Dict with 'macd', 'signal', 'histogram' or None if insufficient data
        """
        if len(prices) < slow:
            return None

        prices_array = np.array(prices)

        # Calculate EMAs
        ema_fast = IndicatorCalculator._calculate_ema(prices_array, fast)
        ema_slow = IndicatorCalculator._calculate_ema(prices_array, slow)

        # MACD line
        macd_line = ema_fast[-1] - ema_slow[-1]

        # Signal line (EMA of MACD)
        macd_values = ema_fast - ema_slow
        signal_line = IndicatorCalculator._calculate_ema(macd_values, signal)[-1]

        # Histogram
        histogram = macd_line - signal_line

        return {"macd": float(macd_line), "signal": float(signal_line), "histogram": float(histogram)}

    @staticmethod
    def calculate_bollinger_bands(
        prices: List[float], period: int = 20, std_dev: float = 2.0
    ) -> Optional[Dict[str, float]]:
        """Calculate Bollinger Bands.

        Args:
            prices: List of closing prices
            period: Period for moving average
            std_dev: Number of standard deviations

        Returns:
            Dict with 'upper', 'middle', 'lower' or None if insufficient data
        """
        if len(prices) < period:
            return None

        prices_array = np.array(prices)
        sma = prices_array[-period:].mean()
        std = prices_array[-period:].std()

        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)

        return {"upper": float(upper), "middle": float(sma), "lower": float(lower)}

    @staticmethod
    def calculate_atr(high: List[float], low: List[float], close: List[float], period: int = 14) -> Optional[float]:
        """Calculate Average True Range (ATR).

        Args:
            high: List of high prices
            low: List of low prices
            close: List of close prices
            period: ATR period

        Returns:
            ATR value or None if insufficient data
        """
        if len(high) < period:
            return None

        tr_values = []
        for i in range(len(high)):
            tr = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]) if i > 0 else 0,
                abs(low[i] - close[i - 1]) if i > 0 else 0,
            )
            tr_values.append(tr)

        atr = np.mean(tr_values[-period:])
        return float(atr)

    @staticmethod
    def calculate_sma(prices: List[float], period: int = 20) -> Optional[float]:
        """Calculate Simple Moving Average (SMA).

        Args:
            prices: List of closing prices
            period: SMA period

        Returns:
            SMA value or None if insufficient data
        """
        if len(prices) < period:
            return None

        sma = np.mean(prices[-period:])
        return float(sma)

    @staticmethod
    def calculate_ema(prices: List[float], period: int = 20) -> Optional[float]:
        """Calculate Exponential Moving Average (EMA).

        Args:
            prices: List of closing prices
            period: EMA period

        Returns:
            EMA value or None if insufficient data
        """
        if len(prices) < period:
            return None

        ema = IndicatorCalculator._calculate_ema(np.array(prices), period)
        return float(ema[-1])

    @staticmethod
    def _calculate_ema(prices: np.ndarray, period: int) -> np.ndarray:
        """Internal method to calculate EMA array.

        Args:
            prices: Array of prices
            period: EMA period

        Returns:
            Array of EMA values
        """
        multiplier = 2 / (period + 1)
        ema = np.zeros(len(prices))
        ema[0] = prices[0]

        for i in range(1, len(prices)):
            ema[i] = (prices[i] * multiplier) + (ema[i - 1] * (1 - multiplier))

        return ema

    @staticmethod
    def calculate_stochastic(
        high: List[float], low: List[float], close: List[float], period: int = 14
    ) -> Optional[Dict[str, float]]:
        """Calculate Stochastic Oscillator.

        Args:
            high: List of high prices
            low: List of low prices
            close: List of close prices
            period: Stochastic period

        Returns:
            Dict with 'k' and 'd' values or None if insufficient data
        """
        if len(high) < period:
            return None

        high_array = np.array(high[-period:])
        low_array = np.array(low[-period:])
        close_val = close[-1]

        highest_high = high_array.max()
        lowest_low = low_array.min()

        if highest_high == lowest_low:
            k = 50.0
        else:
            k = ((close_val - lowest_low) / (highest_high - lowest_low)) * 100

        return {"k": float(k), "d": float(k)}  # Simplified, d should be SMA of k

    @staticmethod
    def calculate_obv(close: List[float], volume: List[float]) -> Optional[float]:
        """Calculate On-Balance Volume (OBV).

        Args:
            close: List of close prices
            volume: List of volumes

        Returns:
            OBV value or None if insufficient data
        """
        if len(close) != len(volume) or len(close) < 2:
            return None

        obv = 0
        for i in range(len(close)):
            if close[i] > close[i - 1] if i > 0 else False:
                obv += volume[i]
            elif close[i] < close[i - 1] if i > 0 else False:
                obv -= volume[i]

        return float(obv)


class IndicatorBuffer:
    """Maintain rolling buffers of price data for indicator calculation."""

    def __init__(self, max_size: int = 500):
        """Initialize indicator buffer.

        Args:
            max_size: Maximum buffer size
        """
        self.max_size = max_size
        self.closes = deque(maxlen=max_size)
        self.highs = deque(maxlen=max_size)
        self.lows = deque(maxlen=max_size)
        self.volumes = deque(maxlen=max_size)

    def add_candle(self, high: float, low: float, close: float, volume: float) -> None:
        """Add candle data to buffer.

        Args:
            high: High price
            low: Low price
            close: Close price
            volume: Volume
        """
        self.highs.append(high)
        self.lows.append(low)
        self.closes.append(close)
        self.volumes.append(volume)

    def get_rsi(self, period: int = 14) -> Optional[float]:
        """Get current RSI."""
        return IndicatorCalculator.calculate_rsi(list(self.closes), period)

    def get_macd(self) -> Optional[Dict[str, float]]:
        """Get current MACD."""
        return IndicatorCalculator.calculate_macd(list(self.closes))

    def get_bollinger_bands(self, period: int = 20) -> Optional[Dict[str, float]]:
        """Get current Bollinger Bands."""
        return IndicatorCalculator.calculate_bollinger_bands(list(self.closes), period)

    def get_atr(self, period: int = 14) -> Optional[float]:
        """Get current ATR."""
        return IndicatorCalculator.calculate_atr(
            list(self.highs), list(self.lows), list(self.closes), period
        )

    def is_ready(self, min_candles: int = 20) -> bool:
        """Check if buffer has sufficient data.

        Args:
            min_candles: Minimum required candles

        Returns:
            True if buffer has sufficient data
        """
        return len(self.closes) >= min_candles

    def clear(self) -> None:
        """Clear all buffers."""
        self.closes.clear()
        self.highs.clear()
        self.lows.clear()
        self.volumes.clear()
