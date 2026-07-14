"""
Configuration management using Pydantic Settings.

Loads configuration from YAML file and environment variables.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field, validator
import yaml


class TradingSettings(BaseSettings):
    """Trading configuration settings."""

    mode: str = Field(default="paper", description="Trading mode: paper or live")
    profit_target: float = Field(default=5, description="Profit target in points")
    stop_loss: float = Field(default=10, description="Stop loss in points")
    quantity: int = Field(default=1, description="Trade quantity")
    max_concurrent_trades: int = Field(default=3, description="Max open trades")
    max_trades_per_day: int = Field(default=20, description="Max trades per day")
    cooldown_seconds: int = Field(default=30, description="Cooldown between trades")
    symbols: List[str] = Field(default=["NIFTY50"], description="Trading symbols")


class RiskSettings(BaseSettings):
    """Risk management settings."""

    max_daily_loss: float = Field(default=-5000, description="Max daily loss in INR")
    max_daily_profit: float = Field(default=10000, description="Max daily profit in INR")
    max_drawdown_percentage: float = Field(default=10.0, description="Max drawdown %")
    max_risk_per_trade_percentage: float = Field(default=2.0, description="Max risk per trade %")
    max_consecutive_losses: int = Field(default=3, description="Max consecutive losses")
    trailing_stop_enabled: bool = Field(default=True, description="Enable trailing stop")
    break_even_enabled: bool = Field(default=True, description="Enable break-even stops")


class BrokerSettings(BaseSettings):
    """Broker configuration settings."""

    primary: str = Field(default="paper", description="Primary broker: paper, dhan, zerodha")
    dhan_client_id: Optional[str] = Field(default=None, description="Dhan client ID")
    dhan_access_token: Optional[str] = Field(default=None, description="Dhan access token")
    zerodha_api_key: Optional[str] = Field(default=None, description="Zerodha API key")
    zerodha_api_secret: Optional[str] = Field(default=None, description="Zerodha API secret")
    paper_starting_capital: float = Field(default=100000, description="Paper trading capital")


class NotificationSettings(BaseSettings):
    """Notification configuration settings."""

    telegram_enabled: bool = Field(default=False, description="Enable Telegram")
    telegram_token: Optional[str] = Field(default=None, description="Telegram bot token")
    telegram_chat_id: Optional[str] = Field(default=None, description="Telegram chat ID")
    email_enabled: bool = Field(default=False, description="Enable email")
    smtp_server: Optional[str] = Field(default=None, description="SMTP server")
    smtp_port: int = Field(default=587, description="SMTP port")
    sender_email: Optional[str] = Field(default=None, description="Sender email")
    sender_password: Optional[str] = Field(default=None, description="Sender password")


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    type: str = Field(default="sqlite", description="Database type: sqlite or postgresql")
    sqlite_db: str = Field(default="trading_bot.db", description="SQLite database file")
    postgresql_url: Optional[str] = Field(default=None, description="PostgreSQL connection URL")


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""

    level: str = Field(default="INFO", description="Log level")
    file_path: str = Field(default="logs/scalping_bot.log", description="Log file path")
    max_file_size: int = Field(default=10485760, description="Max log file size in bytes")
    backup_count: int = Field(default=5, description="Number of backup log files")


class Settings(BaseSettings):
    """Main application settings."""

    # API Settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=4, description="Number of API workers")

    # Sub-settings
    trading: TradingSettings = Field(default_factory=TradingSettings)
    risk: RiskSettings = Field(default_factory=RiskSettings)
    broker: BrokerSettings = Field(default_factory=BrokerSettings)
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("trading", pre=True, always=True)
    def load_trading_config(cls, v):
        """Load trading configuration."""
        if isinstance(v, dict):
            return TradingSettings(**v)
        return v or TradingSettings()

    @validator("risk", pre=True, always=True)
    def load_risk_config(cls, v):
        """Load risk configuration."""
        if isinstance(v, dict):
            return RiskSettings(**v)
        return v or RiskSettings()

    @validator("broker", pre=True, always=True)
    def load_broker_config(cls, v):
        """Load broker configuration."""
        if isinstance(v, dict):
            return BrokerSettings(**v)
        return v or BrokerSettings()

    @validator("notifications", pre=True, always=True)
    def load_notification_config(cls, v):
        """Load notification configuration."""
        if isinstance(v, dict):
            return NotificationSettings(**v)
        return v or NotificationSettings()

    @validator("database", pre=True, always=True)
    def load_database_config(cls, v):
        """Load database configuration."""
        if isinstance(v, dict):
            return DatabaseSettings(**v)
        return v or DatabaseSettings()

    @validator("logging", pre=True, always=True)
    def load_logging_config(cls, v):
        """Load logging configuration."""
        if isinstance(v, dict):
            return LoggingSettings(**v)
        return v or LoggingSettings()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings instance

    Example:
        >>> settings = get_settings()
        >>> print(settings.trading.profit_target)
    """
    config_path = Path("config.yaml")

    # Load from YAML if exists
    if config_path.exists():
        with open(config_path, "r") as f:
            config_dict = yaml.safe_load(f) or {}
        return Settings(**config_dict)

    # Fall back to environment variables
    return Settings()
