# 🤖 SCALPING BOT - Complete Setup & Usage Guide

## 📋 Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Running the Bot](#running-the-bot)
4. [Using the Dashboard](#using-the-dashboard)
5. [Trading Modes](#trading-modes)
6. [Monitoring & Control](#monitoring--control)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/ezhilgokuljkl-max/Scalping-bot-pro.git
cd Scalping-bot-pro
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation
```bash
python -c "import fastapi; import pandas; print('✅ All dependencies installed!')"
```

---

## ⚙️ Configuration

### Step 1: Review config.yaml
The bot comes with a pre-configured `config.yaml` file. Here's what each section means:

```yaml
# TRADING SETTINGS
trading:
  mode: paper              # 'paper' = simulation, 'live' = real money
  symbols:
    - NIFTY50            # Stock/index symbols to trade
    - BANKNIFTY
  
  profit_target: 5       # Take profit after 5 points
  stop_loss: 10          # Exit if loses 10 points
  quantity: 1            # Lot size per trade
  
  max_trades_per_day: 20 # Maximum trades in a day
  max_concurrent_trades: 3  # Max open positions at once
  
  cooldown_seconds: 30   # Wait 30 sec between trades on same symbol
  
  trading_hours:
    start: "09:15"       # Market open time
    end: "15:30"         # Market close time

# RISK MANAGEMENT
risk:
  max_daily_loss: -5000      # Stop trading if lost ₹5000 today
  max_daily_profit: 10000    # Stop trading if gained ₹10000 today
  max_drawdown: 0.10         # Max 10% portfolio drawdown
  max_risk_per_trade: 0.02   # Risk max 2% per trade
  trailing_stop: true        # Move stop loss to protect gains
  break_even_on_target: 50   # Move SL to entry after 50% profit

# BROKER CONFIGURATION
broker:
  provider: "paper"    # 'paper', 'dhan', or 'zerodha'
  paper_starting_capital: 100000  # Virtual capital for testing

# NOTIFICATIONS
notifications:
  telegram:
    enabled: false
    token: "YOUR_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"

# DATABASE
database:
  type: "sqlite"
  sqlite_db: "trading_bot.db"

# LOGGING
logging:
  level: "INFO"              # DEBUG, INFO, WARNING, ERROR
  file: "logs/scalping_bot.log"
  max_file_size: 10485760    # 10MB
  backup_count: 5
```

### Step 2: Edit Configuration (Optional)
For paper trading (recommended to start):
```bash
# Just use default config - it's already set to paper trading!
# No changes needed to get started
```

### Step 3: Enable Telegram Alerts (Optional)
If you want notifications:
1. Create Telegram bot: https://core.telegram.org/bots#botfather
2. Get your Chat ID: https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-chat-id-for-a-user
3. Update `config.yaml`:
```yaml
notifications:
  telegram:
    enabled: true
    token: "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefg"
    chat_id: "987654321"
```

---

## 🚀 Running the Bot

### Method 1: Simple Python Script (Recommended)

**Create `run_bot.py`:**
```python
import asyncio
import threading
import yaml
from main import ScalpingBot
from dashboard import set_bot_instance, start_dashboard_server
from paper_trading import PaperTradingBroker

def main():
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize broker (paper trading by default)
    broker = PaperTradingBroker(
        starting_capital=config['broker']['paper_starting_capital']
    )
    
    # Create bot instance
    bot = ScalpingBot(config, broker, mode='paper')
    set_bot_instance(bot)
    
    # Start dashboard server in background thread
    dashboard_thread = threading.Thread(
        target=lambda: start_dashboard_server('0.0.0.0', 8000),
        daemon=True
    )
    dashboard_thread.start()
    
    print("""
╔════════════════════════════════════════════════════════╗
║          🤖 SCALPING BOT STARTED                       ║
╠════════════════════════════════════════════════════════╣
║  Dashboard: http://localhost:8000                      ║
║  Mode: PAPER TRADING (Virtual Money)                  ║
║  Press CTRL+C to stop                                 ║
╚════════════════════════════════════════════════════════╝
    """)
    
    # Start trading bot
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        print("\n✅ Bot stopped gracefully")

if __name__ == "__main__":
    main()
```

**Run it:**
```bash
python run_bot.py
```

### Method 2: Command Line
```bash
# Paper trading (simulation)
python main.py

# With verbose output
python main.py --debug
```

---

## 📊 Using the Dashboard

### Step 1: Open Dashboard
Once bot is running, open your browser:
```
http://localhost:8000
```

### Step 2: Dashboard Overview

**Left Sidebar:**
- 🤖 **START BOT** - Activate trading
- ⏸️ **PAUSE BOT** - Stop new entries
- ⏹️ **STOP BOT** - Shutdown
- 🚨 **EMERGENCY** - Close all positions immediately

**Top Right: Status Badge**
- 🟢 **RUNNING** - Bot is trading
- 🔴 **STOPPED** - Bot is inactive

**Statistics Cards:**
- 💰 **Account Balance** - Total capital
- 🪙 **Available Balance** - Cash available to trade
- 📅 **Today's P&L** - Profit/Loss for today
- 📊 **Total P&L** - Overall profit/loss
- ⏳ **Open Positions** - Number of active trades
- 💱 **Total Trades** - Lifetime trades executed

**Positions Table:**
| Column | Meaning |
|--------|----------|
| Symbol | Stock/Index name |
| Side | BUY or SELL |
| Entry | Price where trade opened |
| Current | Current live price |
| Qty | Quantity of shares |
| P&L | Profit/Loss in rupees |
| Return | Profit/Loss percentage |
| SL | Stop loss price |
| Target | Take profit price |
| Time | Minutes in the trade |
| EXIT | Close this trade now |

### Step 3: Monitor Live Updates
- Dashboard updates every 2 seconds automatically
- No need to refresh page
- Watch prices update in real-time
- P&L changes color (Green = Profit, Red = Loss)

---

## 🎯 Trading Modes

### Mode 1: Paper Trading (RECOMMENDED FOR TESTING)
**Best for:** Learning, testing strategies, backtesting

**Features:**
- ✅ Virtual money (₹100,000 default)
- ✅ No real money at risk
- ✅ Simulates real market conditions
- ✅ Perfect for beginners
- ✅ Test before going live

**How to use:**
1. Ensure `config.yaml` has `mode: paper`
2. Run `python run_bot.py`
3. Trade with virtual capital
4. Monitor performance
5. When confident, switch to live

### Mode 2: Live Trading (AFTER TESTING)
**Best for:** Real money trading after validation

**Prerequisites:**
- ✅ Paper trading testing (at least 1-2 weeks)
- ✅ Broker account (Dhan or Zerodha)
- ✅ API credentials
- ✅ Confidence in strategy

**How to switch to live:**

**Step 1: Get Broker API Credentials**

**For Dhan:**
```bash
# Get from: https://dhantrade.in
# API Docs: https://api.dhan.co/docs
```

**For Zerodha:**
```bash
# Get from: https://kite.zerodha.com/account/apikeys
# API Docs: https://kite.trade/docs/connect/v3/
```

**Step 2: Set Environment Variables**
```bash
# For Dhan
export DHAN_CLIENT_ID="your_client_id"
export DHAN_ACCESS_TOKEN="your_access_token"

# For Zerodha
export ZERODHA_API_KEY="your_api_key"
export ZERODHA_API_SECRET="your_api_secret"
```

**Step 3: Update config.yaml**
```yaml
trading:
  mode: live          # CHANGE THIS

broker:
  provider: "dhan"   # or "zerodha"
```

**Step 4: Start Live Trading**
```bash
python run_bot.py
```

**⚠️ WARNING:** Start with small position sizes!

---

## 🎮 Monitoring & Control

### Real-Time Monitoring

**Via Dashboard:**
1. Open http://localhost:8000
2. Watch stats update every 2 seconds
3. See open positions in real-time
4. Monitor P&L continuously

**Via Telegram (if enabled):**
- Get alerts for every trade
- Receive P&L updates
- Notifications for exits

**Via Logs:**
```bash
# Watch live logs
tail -f logs/scalping_bot.log

# Or search for specific trades
grep "Order placed" logs/scalping_bot.log
```

### Control Buttons

**START BOT** 🟢
- Activates trading
- Starts monitoring symbols
- Begins placing orders

**PAUSE BOT** ⏸️
- Stops new entries
- Keeps monitoring open
- Useful for market breaks

**STOP BOT** 🛑
- Closes all positions
- Stops monitoring
- Graceful shutdown

**EMERGENCY 🚨**
- **IMMEDIATELY** closes all trades
- No confirmation
- Use if market crashes

### Individual Trade Controls

**In positions table:**
- Each trade has an **[EXIT]** button
- Click to close that specific trade
- Useful for manual profit-taking
- Useful if you want to exit early

---

## 📈 What the Bot Does Automatically

### Every Second:
1. ✅ Checks if within trading hours
2. ✅ Gets current market prices
3. ✅ Analyzes strategy signals
4. ✅ Checks risk limits
5. ✅ Places new orders if signal found
6. ✅ Updates open positions
7. ✅ Checks stop-loss levels
8. ✅ Checks profit targets
9. ✅ Exits trades if conditions met

### Automatic Exits:
- **Stop Loss Hit** - Exits to prevent huge losses
- **Profit Target Hit** - Exits to lock in gains
- **5 Minute Timeout** - Closes if trade is open too long
- **Time-Based Exit** - Ensures quick scalping

---

## 🐛 Troubleshooting

### Problem 1: Dashboard won't load
**Solution:**
```bash
# Check if server is running
curl http://localhost:8000

# If error, restart bot
# Press CTRL+C to stop
# Then: python run_bot.py
```

### Problem 2: "Bot not initialized" error
**Solution:**
```bash
# Make sure dashboard is connected to bot
# Restart with:
python run_bot.py

# Don't run main.py and dashboard separately
```

### Problem 3: No trades being placed
**Check:**
```bash
# 1. Is bot running? (Check dashboard)
# 2. Are we in trading hours? (09:15 - 15:30 IST)
# 3. Check logs for errors:
grep "ERROR" logs/scalping_bot.log

# 4. Verify market data:
python -c "from paper_trading import PaperTradingBroker; import asyncio; print(asyncio.run(PaperTradingBroker().get_market_data('NIFTY50')))"
```

### Problem 4: Dashboard shows "Initializing"
**Solution:**
```bash
# Wait 10 seconds for WebSocket connection
# Refresh page if needed
# Check browser console for errors (F12)
```

### Problem 5: "Insufficient balance" error
**Solution:**
```yaml
# Increase starting capital in config.yaml:
broker:
  paper_starting_capital: 500000  # Increase from 100000

# Or reduce position size:
trading:
  quantity: 1  # Reduce this
```

---

## 📊 Example Trading Session

### Session Start:
```
09:14 AM - Bot starts
09:15 AM - Market opens, bot begins scanning
09:16 AM - Signal found! Order placed
         - BUY NIFTY50 @ ₹23,500 (SL: ₹23,490, Target: ₹23,510)
         - Dashboard shows: 1 open position
         - Telegram alert sent

09:17 AM - Price moves to ₹23,505 (+₹5)
         - P&L updates to +₹5 (Green)
         - Still holding

09:18 AM - Price hits ₹23,510 (Target!)
         - Position closed automatically
         - +₹10 profit locked in
         - Dashboard shows: 0 open positions
         - Telegram alert: "Trade Closed +₹10"
         - Today P&L: +₹10

09:19 AM - Cooldown: Wait 30 seconds before next trade
09:50 AM - Another signal, new trade placed
         - SELL BANKNIFTY @ ₹45,200
         
10:00 AM - Price drops to ₹45,180 (-₹20)
         - P&L: -₹20
         - Still above stop loss
         - Holding...

10:05 AM - 5 minutes in position, time-based exit triggered
         - Position closed at ₹45,180
         - Loss: -₹20
         - Today P&L: +₹10 - ₹20 = -₹10

...(more trades throughout day)...

15:30 PM - Market closes
         - All remaining positions auto-closed
         - Final P&L calculated
         - Daily report generated
         - Bot ready for next day
```

---

## ✅ Checklist for First Use

- [ ] Installed Python 3.12+
- [ ] Created virtual environment
- [ ] Installed requirements.txt
- [ ] Reviewed config.yaml
- [ ] Created run_bot.py
- [ ] Started bot: `python run_bot.py`
- [ ] Opened http://localhost:8000
- [ ] Clicked "START BOT" button
- [ ] Monitored for 1-2 hours
- [ ] Watched trades execute
- [ ] Reviewed dashboard stats
- [ ] Checked logs for errors
- [ ] Closed bot with STOP button

---

## 🎓 Next Steps

1. **Test for 1-2 weeks** with paper trading
2. **Analyze results** - Check if strategy is profitable
3. **Optimize settings** - Adjust profit targets, stop loss
4. **Enable Telegram** - Get alerts on your phone
5. **Go live** - When confident, switch to real trading

---

## 📞 Support

**Issues or questions?**
- Check logs: `logs/scalping_bot.log`
- Review config: `config.yaml`
- Check GitHub issues: https://github.com/ezhilgokuljkl-max/Scalping-bot-pro/issues

---

## 🎉 You're Ready!

You now have a fully functional algorithmic scalping bot with:
- ✅ Real-time trading
- ✅ Beautiful dashboard
- ✅ Automatic risk management
- ✅ Paper & live trading modes
- ✅ Complete monitoring

**Happy Trading! 🚀**
