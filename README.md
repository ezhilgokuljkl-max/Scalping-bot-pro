# Professional Scalping Trading Bot

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A production-ready, modular, and scalable scalping trading bot designed for Indian Futures & Options markets. Supports TradingView webhook alerts, Dhan and Zerodha broker APIs, with comprehensive risk management, manual controls, and automated trading.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Broker Integration](#broker-integration)
- [Risk Management](#risk-management)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Trading Features
- **Ultra-short scalping**: 30 seconds to 5 minutes holding periods
- **Configurable profit targets**: 3, 4, 5+ points
- **Manual and automatic trading modes**
- **Multiple strategy support**: Extensible strategy framework
- **TradingView integration**: Receive webhook alerts and execute trades
- **Multi-instrument support**: Trade multiple symbols simultaneously

### Manual Controls
- START/STOP bot
- BUY/SELL signals
- EXIT CURRENT TRADE / EXIT ALL TRADES
- PAUSE/RESUME new entries
- EMERGENCY STOP
- Available via CLI and Telegram bot

### Risk Management
- Fixed stop loss and targets
- Trailing stop loss
- Break-even stops
- Daily profit targets and loss limits
- Maximum drawdown limits
- Risk per trade limits
- Capital allocation limits
- Auto-disable after risk limits reached

### Trade Management
- Partial profit booking
- Trailing stop loss
- Break-even movement
- Auto and manual exits
- Time-based exits
- Position reversal

### Broker Integration
- **Dhan API** support
- **Zerodha API** support
- Extensible broker architecture
- Paper trading mode
- Live trading mode

### Notifications
- Telegram alerts
- Bot status changes
- Trade execution notifications
- Risk warnings
- Daily reports
- Error notifications

### Monitoring & Dashboard
- Live web dashboard (FastAPI)
- Real-time bot status
- Open trades monitoring
- P&L tracking
- Daily statistics
- API connection status
- CPU/Memory usage

### Logging & Analytics
- Detailed trade history
- Performance statistics
- Strategy performance analysis
- Risk event tracking
- API activity logs
- File and database logging

## Architecture

```
scalping-bot/
├── src/
│   ├── scalping_bot/
│   │   ├── __init__.py
│   │   ├── main.py                 # Application entry point
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── settings.py         # Configuration management
│   │   │   └── constants.py        # Application constants
│   │   ├── strategies/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Base strategy class
│   │   │   ├── scalping.py         # Scalping strategy implementation
│   │   │   └── indicators.py       # Technical indicators
│   │   ├── brokers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Base broker interface
│   │   │   ├── dhan.py             # Dhan broker implementation
│   │   │   ├── zerodha.py          # Zerodha broker implementation
│   │   │   └── paper_trading.py    # Paper trading broker
│   │   ├── risk_management/
│   │   │   ├── __init__.py
│   │   │   ├── risk_manager.py     # Risk management engine
│   │   │   ├── position_manager.py # Position tracking
│   │   │   └── validators.py       # Trade validation
│   │   ├── order_management/
│   │   │   ├── __init__.py
│   │   │   ├── order_manager.py    # Order lifecycle management
│   │   │   ├── models.py           # Order models
│   │   │   └── executor.py         # Order execution
│   │   ├── notifications/
│   │   │   ├── __init__.py
│   │   │   ├── telegram_bot.py     # Telegram integration
│   │   │   └── notifier.py         # Notification manager
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # SQLAlchemy models
│   │   │   ├── db.py               # Database connection
│   │   │   ├── crud.py             # CRUD operations
│   │   │   └── migrations/         # Alembic migrations
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── app.py              # FastAPI application
│   │   │   ├── routes.py           # API endpoints
│   │   │   ├── webhooks.py         # TradingView webhooks
│   │   │   ├── models.py           # Pydantic models
│   │   │   └── dependencies.py     # Dependency injection
│   │   ├── cli/
│   │   │   ├── __init__.py
│   │   │   └── commands.py         # CLI commands
│   │   ├── dashboard/
│   │   │   ├── __init__.py
│   │   │   └── templates/          # HTML templates
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── helpers.py          # Utility functions
│   │   │   ├── time_utils.py       # Time utilities
│   │   │   └── validators.py       # Input validators
│   │   └── logger.py               # Logging configuration
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py             # Pytest configuration
│       ├── test_strategies.py
│       ├── test_brokers.py
│       ├── test_risk_management.py
│       ├── test_order_management.py
│       └── test_integration.py
├── config.yaml                      # Configuration file
├── .env.example                     # Environment variables template
├── docker-compose.yml               # Docker setup
├── Dockerfile                       # Docker image
├── requirements.txt                 # Python dependencies
├── setup.py                         # Package setup
├── README.md                        # This file
├── INSTALLATION.md                  # Detailed installation guide
├── DEPLOYMENT.md                    # Deployment guide
├── TESTING.md                       # Testing guide
├── API.md                           # API documentation
└── LICENSE                          # MIT License
```

## Quick Start

### Prerequisites
- Python 3.12 or higher
- pip or conda
- PostgreSQL or SQLite (SQLite is default)
- Telegram bot token (optional)
- Broker API credentials (Dhan/Zerodha)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ezhilgokulabc-ship-it/Scalping-bot.git
cd Scalping-bot
```

2. **Create virtual environment**
```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Initialize database**
```bash
alembic upgrade head
```

6. **Configure the bot**
```bash
# Edit config.yaml with your trading parameters
vim config.yaml
```

### Quick Run

**Paper Trading (Simulation)**
```bash
python -m scalping_bot.main --mode paper
```

**Live Trading**
```bash
python -m scalping_bot.main --mode live
```

**CLI Mode**
```bash
python -m scalping_bot.cli
```

## Configuration

Edit `config.yaml` to customize:

```yaml
# Trading Parameters
trading:
  mode: paper  # 'paper' or 'live'
  profit_target: 5  # Points
  stop_loss: 10  # Points
  quantity: 1  # Lot size
  max_trades_per_day: 20
  max_concurrent_trades: 3
  trading_hours:
    start: "09:15"
    end: "15:30"
  cooldown_seconds: 30

# Risk Management
risk:
  max_daily_loss: -5000  # INR
  max_daily_profit: 10000  # INR
  max_drawdown: 0.10  # 10%
  max_risk_per_trade: 0.02  # 2% of capital
  trailing_stop: true
  break_even_on_target: 50  # Move SL to BE after 50% of target hit

# Broker Configuration
broker:
  provider: "dhan"  # 'dhan', 'zerodha', or 'paper'
  paper_starting_capital: 100000  # For paper trading
  symbols:
    - "NIFTY 50"
    - "BANKNIFTY"

# Notifications
notifications:
  telegram:
    enabled: true
    token: "YOUR_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"
  email:
    enabled: false
    smtp_server: "smtp.gmail.com"
    sender_email: "your_email@gmail.com"

# Database
database:
  type: "sqlite"  # 'sqlite' or 'postgresql'
  sqlite_db: "trading_bot.db"
  postgresql_url: "postgresql://user:password@localhost/scalping_bot"

# Logging
logging:
  level: "INFO"
  file: "logs/scalping_bot.log"
  max_file_size: 10485760  # 10MB
  backup_count: 5
```

## Usage

### Starting the Bot

**1. Paper Trading Mode** (Simulation - No real money)
```bash
python -m scalping_bot.main --mode paper --config config.yaml
```

**2. Live Trading Mode** (Real money - Use with caution!)
```bash
python -m scalping_bot.main --mode live --config config.yaml
```

### Manual Controls via CLI

```bash
# Start trading
> start

# Stop trading (closes new entries, manages existing positions)
> stop

# Place manual trade
> manual_buy 23500 23450 23550 1
# Format: manual_buy entry_price stop_loss target quantity

# Exit current trade
> exit

# Exit all trades
> exit_all

# Pause new entries (keeps monitoring)
> pause

# Resume entries
> resume

# Emergency stop
> emergency_stop

# Show status
> status

# Show trades
> trades
```

### Manual Controls via Telegram

```
/start - Start bot
/stop - Stop bot
/status - Show bot status
/trades - Show open trades
/buy <entry> <sl> <target> <qty> - Manual buy
/sell <entry> <sl> <target> <qty> - Manual sell
/exit - Exit current trade
/exit_all - Exit all trades
/pause - Pause new entries
/resume - Resume entries
/emergency - Emergency stop
/report - Daily report
```

### TradingView Webhook Integration

**1. Setup your bot webhook endpoint**
The API server runs on `http://localhost:8000` by default.

**2. Create TradingView alert**
In TradingView, create an alert and set webhook URL:
```
http://your_domain_or_ip:8000/webhook/tradingview
```

**3. Example webhook payload**
```json
{
  "strategy_name": "Scalping Strategy",
  "action": "buy",
  "symbol": "NIFTY50",
  "entry_price": 23500,
  "stop_loss": 23450,
  "target_1": 23520,
  "target_2": 23540,
  "target_3": 23560,
  "quantity": 1,
  "timeframe": "5m",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## API Documentation

The bot provides a FastAPI interface at `http://localhost:8000`

**Key Endpoints:**

- `GET /api/v1/status` - Bot status
- `GET /api/v1/trades` - Open trades
- `GET /api/v1/history` - Trade history
- `GET /api/v1/performance` - Performance metrics
- `POST /api/v1/commands/start` - Start bot
- `POST /api/v1/commands/stop` - Stop bot
- `POST /api/v1/commands/trade` - Manual trade
- `POST /webhook/tradingview` - TradingView alerts

Full API documentation available at `http://localhost:8000/docs`

## Broker Integration

### Dhan Broker

**Setup:**
1. Get API credentials from Dhan
2. Set in `.env` file:
```
DHAN_CLIENT_ID=your_client_id
DHAN_ACCESS_TOKEN=your_access_token
```

**Configuration:**
```yaml
broker:
  provider: "dhan"
```

### Zerodha Broker

**Setup:**
1. Get API credentials from Zerodha
2. Set in `.env` file:
```
ZERODHA_API_KEY=your_api_key
ZERODHA_API_SECRET=your_api_secret
```

**Configuration:**
```yaml
broker:
  provider: "zerodha"
```

### Paper Trading

No broker credentials needed. Simulates trading with virtual capital.

```yaml
broker:
  provider: "paper"
  paper_starting_capital: 100000
```

## Risk Management

The bot implements comprehensive risk controls:

1. **Pre-trade validation**: Ensures all trades meet risk criteria
2. **Position limits**: Prevents over-exposure
3. **Daily limits**: Stops trading if daily loss/profit limits hit
4. **Drawdown protection**: Monitors maximum drawdown
5. **Stop loss enforcement**: Automatically exits losing trades
6. **Profit booking**: Automatically closes at target
7. **Duplicate prevention**: Avoids duplicate orders
8. **Cooldown periods**: Prevents rapid re-entry

## Troubleshooting

### Bot not starting
```bash
# Check logs
tail -f logs/scalping_bot.log

# Verify configuration
python -c "from scalping_bot.config import settings; print(settings)"
```

### Broker connection issues
```bash
# Test broker connection
python -m scalping_bot.brokers.dhan --test
python -m scalping_bot.brokers.zerodha --test
```

### Database issues
```bash
# Reset database
rm trading_bot.db
alembic upgrade head
```

### Telegram not sending
```bash
# Verify token and chat ID in .env
# Test connection
python -c "from scalping_bot.notifications.telegram_bot import TelegramBot; TelegramBot().test()"
```

## Testing

**Run all tests:**
```bash
pytest tests/ -v
```

**Run specific test:**
```bash
pytest tests/test_strategies.py -v
```

**Run with coverage:**
```bash
pytest tests/ --cov=src/scalping_bot --cov-report=html
```

**Paper trading tests:**
```bash
python -m scalping_bot.main --mode paper --test
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment guide using:
- Docker
- Docker Compose
- Kubernetes
- Cloud providers

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Disclaimer

⚠️ **WARNING**: This trading bot is provided as-is. Trading in financial markets carries substantial risk of loss. Use at your own risk. The author assumes no responsibility for financial losses. Always:

- Test thoroughly in paper trading mode first
- Start with small amounts in live trading
- Use appropriate risk management
- Monitor the bot regularly
- Understand the strategy before using
- Follow all applicable laws and regulations

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review logs for error messages

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

**Built with ❤️ for quantitative traders**
