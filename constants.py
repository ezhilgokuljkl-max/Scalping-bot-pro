"""
Application-wide constants and enumerations.
"""

from enum import Enum
from typing import Final


class OrderStatus(str, Enum):
    """Order status enumeration."""

    PENDING = "PENDING"
    PLACED = "PLACED"
    EXECUTED = "EXECUTED"
    PARTIALLY_EXECUTED = "PARTIALLY_EXECUTED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class OrderType(str, Enum):
    """Order type enumeration."""

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"


class OrderSide(str, Enum):
    """Order side (direction) enumeration."""

    BUY = "BUY"
    SELL = "SELL"


class TradeStatus(str, Enum):
    """Trade status enumeration."""

    OPEN = "OPEN"
    PARTIALLY_CLOSED = "PARTIALLY_CLOSED"
    CLOSED = "CLOSED"
    STOPPED_OUT = "STOPPED_OUT"
    PROFIT_BOOKED = "PROFIT_BOOKED"
    REVERSED = "REVERSED"


class BotStatus(str, Enum):
    """Bot status enumeration."""

    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    ERROR = "ERROR"
    EMERGENCY_STOP = "EMERGENCY_STOP"


class TimeFrames(str, Enum):
    """Supported timeframes."""

    ONE_MIN = "1m"
    FIVE_MIN = "5m"
    FIFTEEN_MIN = "15m"
    THIRTY_MIN = "30m"
    ONE_HOUR = "1h"
    FOUR_HOUR = "4h"
    DAILY = "1d"


# Trading Constants
MIN_PROFIT_TARGET: Final[int] = 1  # Minimum 1 point
MAX_PROFIT_TARGET: Final[int] = 100  # Maximum 100 points
MIN_STOP_LOSS: Final[int] = 1  # Minimum 1 point
MAX_STOP_LOSS: Final[int] = 100  # Maximum 100 points
MIN_QUANTITY: Final[int] = 1
MAX_QUANTITY: Final[int] = 100

# Risk Management Constants
MIN_RISK_PERCENTAGE: Final[float] = 0.1  # 0.1%
MAX_RISK_PERCENTAGE: Final[float] = 10.0  # 10%
MIN_DAILY_LOSS: Final[int] = -100000  # -1 lakh
MAX_DAILY_PROFIT: Final[int] = 100000  # 1 lakh

# API Constants
API_TIMEOUT_SECONDS: Final[int] = 30
API_MAX_RETRIES: Final[int] = 3
API_RETRY_DELAY_SECONDS: Final[int] = 2

# Time Constants
MIN_HOLDING_TIME_SECONDS: Final[int] = 10
MAX_HOLDING_TIME_SECONDS: Final[int] = 600  # 10 minutes
COOLDOWN_MIN_SECONDS: Final[int] = 5
COOLDOWN_MAX_SECONDS: Final[int] = 300

# Broker Constants
DHAN_BASE_URL: Final[str] = "https://api.dhan.co"
ZERODHA_BASE_URL: Final[str] = "https://api.kite.trade"

# Exchange Codes
EXCHANGE_NSE: Final[str] = "NSE"
EXCHANGE_BSE: Final[str] = "BSE"
EXCHANGE_NFO: Final[str] = "NFO"
EXCHANGE_MCX: Final[str] = "MCX"

# Segment Codes
SEGMENT_EQUITY: Final[str] = "EQ"
SEGMENT_FO: Final[str] = "FO"
SEGMENT_COMMODITY: Final[str] = "COM"

# Slippage Constants
DEFAULT_SLIPPAGE_PERCENTAGE: Final[float] = 0.1  # 0.1%
MAX_SLIPPAGE_PERCENTAGE: Final[float] = 5.0  # 5%

# Database Constants
DEFAULT_DB_ECHO: Final[bool] = False
DEFAULT_POOL_SIZE: Final[int] = 10
DEFAULT_MAX_OVERFLOW: Final[int] = 20

# Cache Constants
CACHE_TTL_SECONDS: Final[int] = 300  # 5 minutes

# Webhook Constants
WEBHOOK_TIMEOUT_SECONDS: Final[int] = 10
WEBHOOK_MAX_RETRIES: Final[int] = 3
