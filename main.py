"""
Main entry point for the Scalping Trading Bot.

This is the core bot loop that:
- Continuously fetches market data
- Analyzes signals using the scalping strategy
- Executes orders in real-time
- Manages positions and risk
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime, time
from typing import Optional

from scalping import ScalpingStrategy
from position_manager import PositionManager
from order_manager import OrderManager
from risk_manager import RiskManager
from notifier import Notifier
from logger import setup_logger

logger = setup_logger("ScalpingBot")


class ScalpingBot:
    """Main trading bot class."""

    def __init__(self, config: dict, broker, mode: str = "paper"):
        """Initialize bot.
        
        Args:
            config: Configuration dictionary
            broker: Broker instance (DhanBroker, ZerodhaBroker, or PaperBroker)
            mode: 'paper' or 'live'
        """
        self.config = config
        self.broker = broker
        self.mode = mode
        self.running = False
        
        # Initialize components
        self.strategy = ScalpingStrategy()
        self.position_manager = PositionManager()
        self.order_manager = OrderManager()
        self.risk_manager = RiskManager(config.get("risk", {}))
        self.notifier = Notifier(config.get("notifications", {}))
        
        # Trading parameters
        self.symbols = config.get("trading", {}).get("symbols", ["NIFTY50"])
        self.cooldown_seconds = config.get("trading", {}).get("cooldown_seconds", 30)
        self.last_trade_time = {}
        
        logger.info(f"Bot initialized in {mode} mode")

    async def start(self):
        """Start the bot."""
        logger.info("Starting trading bot...")
        
        # Connect to broker
        connected = await self.broker.connect()
        if not connected:
            logger.error("Failed to connect to broker")
            return False
        
        self.running = True
        
        try:
            await self.notifier.notify(
                f"🤖 Scalping Bot Started - {self.mode.upper()} MODE",
                "Bot is now active and monitoring markets"
            )
            
            # Start main bot loop
            await self._main_loop()
            
        except KeyboardInterrupt:
            logger.info("Bot interrupted by user")
        except Exception as e:
            logger.error(f"Bot error: {e}", exc_info=True)
        finally:
            await self.stop()

    async def stop(self):
        """Stop the bot gracefully."""
        logger.info("Stopping trading bot...")
        self.running = False
        
        # Close all open positions
        await self._close_all_positions()
        
        # Disconnect broker
        await self.broker.disconnect()
        
        await self.notifier.notify(
            "🛑 Scalping Bot Stopped",
            "Bot has been shut down"
        )
        logger.info("Bot stopped")

    async def _main_loop(self):
        """Main bot trading loop - runs continuously."""
        logger.info("Entering main trading loop...")
        
        while self.running:
            try:
                # Check if it's trading hours
                if not self._is_trading_hours():
                    await asyncio.sleep(30)
                    continue
                
                # Get account info
                account = await self.broker.get_account_info()
                if account:
                    logger.debug(f"Account balance: {account.available_balance}")
                
                # Process each symbol
                for symbol in self.symbols:
                    if not self.running:
                        break
                    
                    await self._process_symbol(symbol)
                
                # Check existing positions
                await self._check_open_positions()
                
                # Small delay before next iteration
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                await asyncio.sleep(5)

    async def _process_symbol(self, symbol: str):
        """Process a single symbol for trading signals.
        
        Args:
            symbol: Trading symbol (e.g., 'NIFTY50', 'BANKNIFTY')
        """
        try:
            # Check cooldown
            if self._is_in_cooldown(symbol):
                return
            
            # Get real-time market data
            market_data = await self.broker.get_market_data(symbol)
            if not market_data:
                logger.warning(f"No market data for {symbol}")
                return
            
            logger.debug(f"Market data for {symbol}: {market_data}")
            
            # Analyze for trading signal
            signal = self.strategy.analyze(symbol, market_data)
            if not signal:
                return
            
            logger.info(f"Trading signal generated for {symbol}: {signal.side}")
            
            # Validate signal
            if not self.strategy.validate_signal(signal):
                logger.warning(f"Signal validation failed for {symbol}")
                return
            
            # Pre-trade validation (risk checks)
            if not self.risk_manager.validate_trade(signal):
                logger.warning(f"Risk validation failed for {symbol}")
                return
            
            # Place order
            success = await self._place_order(signal)
            if success:
                self.last_trade_time[symbol] = datetime.now()
                await self.notifier.notify(
                    f"📊 Trade Signal: {signal.side.value} {symbol}",
                    f"Entry: {signal.entry_price}\nSL: {signal.stop_loss}\nTarget: {signal.target_1}"
                )
            
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}", exc_info=True)

    async def _place_order(self, signal) -> bool:
        """Place an order based on signal.
        
        Args:
            signal: Trading signal
            
        Returns:
            True if order placed successfully
        """
        try:
            # Place main entry order
            order = await self.broker.place_order(
                symbol=signal.symbol,
                side=signal.side,
                quantity=signal.quantity,
                order_type="MARKET",  # Use market order for scalping
                price=signal.entry_price
            )
            
            if not order:
                logger.error(f"Failed to place order for {signal.symbol}")
                return False
            
            logger.info(f"Order placed: {order.order_id}")
            
            # Track position
            self.position_manager.add_trade(
                trade_id=order.order_id,
                symbol=signal.symbol,
                side=signal.side.value,
                entry_price=signal.entry_price,
                quantity=signal.quantity,
                stop_loss=signal.stop_loss,
                target_1=signal.target_1,
                target_2=signal.target_2,
                target_3=signal.target_3,
                metadata={"order_id": order.order_id, "entered_at": datetime.now()}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return False

    async def _check_open_positions(self):
        """Check and manage open positions."""
        try:
            positions = self.position_manager.get_open_trades()
            
            for position in positions:
                # Get current market data
                market_data = await self.broker.get_market_data(position.symbol)
                if not market_data:
                    continue
                
                current_price = market_data.get("close")
                
                # Update position price
                self.position_manager.update_trade_price(position.trade_id, current_price)
                
                # Check for exit conditions
                should_exit = self._check_exit_conditions(position, current_price)
                if should_exit:
                    await self._exit_position(position, current_price)
                    
        except Exception as e:
            logger.error(f"Error checking positions: {e}")

    def _check_exit_conditions(self, position, current_price: float) -> bool:
        """Check if position should be exited.
        
        Args:
            position: Position data
            current_price: Current market price
            
        Returns:
            True if position should be exited
        """
        try:
            # Stop loss hit
            if position.side == "BUY" and current_price <= position.stop_loss:
                logger.warning(f"Stop loss hit for {position.symbol}")
                return True
            elif position.side == "SELL" and current_price >= position.stop_loss:
                logger.warning(f"Stop loss hit for {position.symbol}")
                return True
            
            # Take profit at target
            if position.side == "BUY" and current_price >= position.target_1:
                logger.info(f"Target hit for {position.symbol}")
                return True
            elif position.side == "SELL" and current_price <= position.target_1:
                logger.info(f"Target hit for {position.symbol}")
                return True
            
            # Time-based exit (5 minutes for scalping)
            time_in_trade = (datetime.now() - position.entry_time).total_seconds()
            if time_in_trade > 300:  # 5 minutes
                logger.info(f"Time-based exit for {position.symbol}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking exit conditions: {e}")
            return False

    async def _exit_position(self, position, exit_price: float):
        """Exit a position.
        
        Args:
            position: Position data
            exit_price: Exit price
        """
        try:
            # Close position on broker
            order = await self.broker.close_position(position.trade_id)
            if order:
                logger.info(f"Position closed: {position.symbol}")
                
                # Close position in manager
                summary = self.position_manager.close_trade(position.trade_id, exit_price)
                
                if summary:
                    await self.notifier.notify(
                        f"💰 Trade Closed: {position.symbol}",
                        f"Exit Price: {exit_price}\nP&L: ₹{summary['pnl']}\nReturn: {summary['pnl_percentage']:.2f}%"
                    )
            
        except Exception as e:
            logger.error(f"Error exiting position: {e}")

    async def _close_all_positions(self):
        """Close all open positions."""
        positions = self.position_manager.get_open_trades()
        for position in list(positions):  # Create a copy as we're modifying
            try:
                market_data = await self.broker.get_market_data(position.symbol)
                if market_data:
                    current_price = market_data.get("close")
                    await self._exit_position(position, current_price)
            except Exception as e:
                logger.error(f"Error closing position: {e}")

    def _is_trading_hours(self) -> bool:
        """Check if current time is within trading hours.
        
        Returns:
            True if within trading hours
        """
        config_hours = self.config.get("trading", {}).get("trading_hours", {})
        start_time = self._parse_time(config_hours.get("start", "09:15"))
        end_time = self._parse_time(config_hours.get("end", "15:30"))
        
        current_time = datetime.now().time()
        return start_time <= current_time <= end_time

    def _is_in_cooldown(self, symbol: str) -> bool:
        """Check if symbol is in cooldown period.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            True if in cooldown
        """
        if symbol not in self.last_trade_time:
            return False
        
        elapsed = (datetime.now() - self.last_trade_time[symbol]).total_seconds()
        return elapsed < self.cooldown_seconds

    @staticmethod
    def _parse_time(time_str: str) -> time:
        """Parse time string (HH:MM format).
        
        Args:
            time_str: Time string
            
        Returns:
            time object
        """
        parts = time_str.split(":")
        return time(int(parts[0]), int(parts[1]))


async def main():
    """Main entry point."""
    import yaml
    from dhan import DhanBroker
    from paper_trading import PaperTradingBroker
    
    # Load configuration
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)
    
    # Initialize broker based on configuration
    broker_config = config.get("broker", {})
    broker_type = broker_config.get("provider", "paper").lower()
    
    if broker_type == "dhan":
        broker = DhanBroker()
    elif broker_type == "zerodha":
        from zerodha import ZerodhaBroker
        broker = ZerodhaBroker()
    else:
        broker = PaperTradingBroker(
            starting_capital=broker_config.get("paper_starting_capital", 100000)
        )
    
    # Determine mode
    mode = config.get("trading", {}).get("mode", "paper")
    
    # Create and start bot
    bot = ScalpingBot(config, broker, mode=mode)
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        asyncio.create_task(bot.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start bot
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
