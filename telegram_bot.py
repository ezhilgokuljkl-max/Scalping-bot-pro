"""
Telegram bot integration for notifications and manual controls.

Provides:
- Trade alerts
- Bot status notifications
- Manual commands (START, STOP, BUY, SELL, EXIT, etc.)
- Daily reports
- Risk warnings
"""

import logging
from typing import Optional, Callable, Dict, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot for notifications and control.

    Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.
    """

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        enabled: bool = True,
    ):
        """Initialize Telegram bot.

        Args:
            bot_token: Telegram bot token (or from TELEGRAM_BOT_TOKEN env var)
            chat_id: Telegram chat ID (or from TELEGRAM_CHAT_ID env var)
            enabled: Enable/disable Telegram notifications
        """
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = enabled and bool(self.bot_token and self.chat_id)

        self.command_handlers: Dict[str, Callable] = {}
        self.logger = logging.getLogger(f"{__name__}.TelegramBot")

        if self.enabled:
            self.logger.info("Telegram bot enabled")
        else:
            self.logger.warning("Telegram bot disabled - credentials not provided")

    def register_command(self, command: str, handler: Callable) -> None:
        """Register a command handler.

        Args:
            command: Command name (e.g., 'start', 'stop')
            handler: Callable to handle the command
        """
        self.command_handlers[command.lower()] = handler
        self.logger.info(f"Registered command handler: {command}")

    async def send_message(self, message: str) -> bool:
        """Send a text message.

        Args:
            message: Message text

        Returns:
            True if successful
        """
        if not self.enabled:
            return False

        try:
            # In production, this would use telegram API
            # await bot.send_message(chat_id=self.chat_id, text=message)
            self.logger.info(f"Message sent: {message[:50]}...")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False

    async def send_trade_alert(self, trade_info: Dict[str, Any]) -> bool:
        """Send trade alert.

        Args:
            trade_info: Trade information

        Returns:
            True if successful
        """
        message = (
            f"🚀 *Trade Alert*\n"
            f"Symbol: {trade_info.get('symbol')}\n"
            f"Side: {trade_info.get('side')}\n"
            f"Entry: {trade_info.get('entry_price')}\n"
            f"SL: {trade_info.get('stop_loss')}\n"
            f"Target: {trade_info.get('target')}\n"
            f"Quantity: {trade_info.get('quantity')}\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')}"
        )
        return await self.send_message(message)

    async def send_status(self, status_info: Dict[str, Any]) -> bool:
        """Send bot status.

        Args:
            status_info: Status information

        Returns:
            True if successful
        """
        message = (
            f"📊 *Bot Status*\n"
            f"Status: {status_info.get('status')}\n"
            f"Capital: ₹{status_info.get('capital', 0):.2f}\n"
            f"Daily P&L: ₹{status_info.get('daily_pnl', 0):.2f}\n"
            f"Open Trades: {status_info.get('open_trades', 0)}\n"
            f"Win Rate: {status_info.get('win_rate', 0):.1f}%\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')}"
        )
        return await self.send_message(message)

    async def send_error(self, error_info: Dict[str, Any]) -> bool:
        """Send error alert.

        Args:
            error_info: Error information

        Returns:
            True if successful
        """
        message = (
            f"⚠️ *Error Alert*\n"
            f"Type: {error_info.get('type')}\n"
            f"Message: {error_info.get('message')}\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')}"
        )
        return await self.send_message(message)

    async def send_daily_report(self, report_info: Dict[str, Any]) -> bool:
        """Send daily trading report.

        Args:
            report_info: Report information

        Returns:
            True if successful
        """
        message = (
            f"📈 *Daily Report*\n"
            f"Trades: {report_info.get('total_trades')}\n"
            f"Wins: {report_info.get('wins')} | Losses: {report_info.get('losses')}\n"
            f"Win Rate: {report_info.get('win_rate', 0):.1f}%\n"
            f"P&L: ₹{report_info.get('daily_pnl', 0):.2f}\n"
            f"Capital: ₹{report_info.get('capital', 0):.2f}\n"
            f"Date: {datetime.now().strftime('%Y-%m-%d')}"
        )
        return await self.send_message(message)

    async def start_polling(self) -> None:
        """Start polling for commands.

        This is a placeholder. In production, use telegram.ext
        """
        if not self.enabled:
            self.logger.warning("Telegram bot not enabled")
            return

        self.logger.info("Starting Telegram bot polling...")
        # In production, start actual polling
        # await self.updater.start_polling()

    async def stop_polling(self) -> None:
        """Stop polling for commands."""
        self.logger.info("Stopping Telegram bot polling...")
        # In production, stop actual polling
        # await self.updater.stop()

    def get_info(self) -> Dict[str, Any]:
        """Get bot information.

        Returns:
            Dictionary with bot info
        """
        return {
            "enabled": self.enabled,
            "chat_id": self.chat_id if self.enabled else None,
            "commands": list(self.command_handlers.keys()),
        }
