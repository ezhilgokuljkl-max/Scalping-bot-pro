"""
Notification manager.

Centralizes all notifications including Telegram, Email, and Logging.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from scalping_bot.notifications.telegram_bot import TelegramBot

logger = logging.getLogger(__name__)


class Notifier:
    """Centralized notification manager.

    Handles all notifications through multiple channels:
    - Telegram
    - Email (optional)
    - Logging
    """

    def __init__(self, telegram_enabled: bool = True):
        """Initialize notifier.

        Args:
            telegram_enabled: Enable Telegram notifications
        """
        self.telegram = TelegramBot(enabled=telegram_enabled)
        self.logger = logging.getLogger(f"{__name__}.Notifier")

    async def notify_trade_opened(self, trade_info: Dict[str, Any]) -> None:
        """Notify when trade is opened.

        Args:
            trade_info: Trade information
        """
        self.logger.info(f"Trade opened: {trade_info}")
        await self.telegram.send_trade_alert(trade_info)

    async def notify_trade_closed(self, trade_info: Dict[str, Any]) -> None:
        """Notify when trade is closed.

        Args:
            trade_info: Trade information
        """
        pnl = trade_info.get('pnl', 0)
        status = "✅ WIN" if pnl >= 0 else "❌ LOSS"

        message = (
            f"{status} Trade Closed\n"
            f"Symbol: {trade_info.get('symbol')}\n"
            f"Entry: {trade_info.get('entry_price')}\n"
            f"Exit: {trade_info.get('exit_price')}\n"
            f"P&L: ₹{pnl:.2f}\n"
            f"Duration: {trade_info.get('duration_seconds', 0):.0f}s"
        )

        self.logger.info(f"Trade closed: {message}")
        await self.telegram.send_message(message)

    async def notify_stop_loss_hit(self, trade_info: Dict[str, Any]) -> None:
        """Notify when stop loss is hit.

        Args:
            trade_info: Trade information
        """
        message = (
            f"🛑 Stop Loss Hit\n"
            f"Symbol: {trade_info.get('symbol')}\n"
            f"Entry: {trade_info.get('entry_price')}\n"
            f"SL Level: {trade_info.get('stop_loss')}\n"
            f"Loss: ₹{trade_info.get('loss', 0):.2f}"
        )

        self.logger.warning(message)
        await self.telegram.send_message(message)

    async def notify_target_hit(self, trade_info: Dict[str, Any]) -> None:
        """Notify when target is hit.

        Args:
            trade_info: Trade information
        """
        message = (
            f"🎯 Target Hit\n"
            f"Symbol: {trade_info.get('symbol')}\n"
            f"Entry: {trade_info.get('entry_price')}\n"
            f"Target: {trade_info.get('target')}\n"
            f"Profit: ₹{trade_info.get('profit', 0):.2f}"
        )

        self.logger.info(message)
        await self.telegram.send_message(message)

    async def notify_risk_warning(self, warning_info: Dict[str, Any]) -> None:
        """Notify risk warnings.

        Args:
            warning_info: Warning information
        """
        message = (
            f"⚠️ Risk Warning\n"
            f"Type: {warning_info.get('type')}\n"
            f"Message: {warning_info.get('message')}\n"
            f"Current Value: {warning_info.get('current_value')}\n"
            f"Limit: {warning_info.get('limit')}"
        )

        self.logger.warning(message)
        await self.telegram.send_message(message)

    async def notify_error(self, error_info: Dict[str, Any]) -> None:
        """Notify errors.

        Args:
            error_info: Error information
        """
        message = (
            f"❌ Error\n"
            f"Type: {error_info.get('type')}\n"
            f"Message: {error_info.get('message')}\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')}"
        )

        self.logger.error(message)
        await self.telegram.send_message(message)

    async def notify_status(self, status_info: Dict[str, Any]) -> None:
        """Notify bot status.

        Args:
            status_info: Status information
        """
        self.logger.info(f"Bot status: {status_info}")
        await self.telegram.send_status(status_info)

    async def notify_daily_report(self, report_info: Dict[str, Any]) -> None:
        """Send daily report.

        Args:
            report_info: Report information
        """
        self.logger.info(f"Daily report: {report_info}")
        await self.telegram.send_daily_report(report_info)
