"""Strategy module for the trading bot."""

from scalping_bot.strategies.base import BaseStrategy
from scalping_bot.strategies.scalping import ScalpingStrategy

__all__ = [
    "BaseStrategy",
    "ScalpingStrategy",
]
