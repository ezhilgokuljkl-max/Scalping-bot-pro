#!/usr/bin/env python3
"""
🤖 SCALPING BOT - ONE-CLICK SETUP & RUN

This script handles everything automatically:
✅ Check Python version
✅ Create virtual environment
✅ Install dependencies
✅ Download requirements
✅ Setup configuration
✅ Start the bot
✅ Launch dashboard

Just run: python setup_and_run.py
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from time import sleep

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header():
    """Print welcome header"""
    print(f"""
{Colors.BOLD}{Colors.CYAN}
╔═══════════════════════════════════════════════════════════════╗
║          🤖 SCALPING BOT - AUTOMATED SETUP & RUN 🤖          ║
║                                                               ║
║  This script will set up everything you need automatically   ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.ENDC}
    """)

def check_python_version():
    """Verify Python 3.12+ is installed"""
    print(f"{Colors.BLUE}📋 Step 1: Checking Python version...{Colors.ENDC}")
    
    if sys.version_info < (3, 12):
        print(f"{Colors.RED}❌ ERROR: Python 3.12+ required, but you have {sys.version}{Colors.ENDC}")
        print(f"{Colors.YELLOW}📥 Download Python 3.12+ from: https://www.python.org/downloads/{Colors.ENDC}")
        sys.exit(1)
    
    print(f"{Colors.GREEN}✅ Python {sys.version.split()[0]} detected - OK!{Colors.ENDC}\n")

def create_virtual_env():
    """Create Python virtual environment"""
    print(f"{Colors.BLUE}📋 Step 2: Creating virtual environment...{Colors.ENDC}")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print(f"{Colors.YELLOW}⚠️  Virtual environment already exists!{Colors.ENDC}")
        choice = input(f"{Colors.CYAN}Recreate it? (y/n): {Colors.ENDC}").strip().lower()
        if choice == 'y':
            shutil.rmtree(venv_path)
            print(f"{Colors.YELLOW}🗑️  Removed old environment...{Colors.ENDC}")
        else:
            print(f"{Colors.GREEN}✅ Using existing virtual environment{Colors.ENDC}\n")
            return get_python_executable()
    
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", "venv"],
            check=True,
            capture_output=True
        )
        print(f"{Colors.GREEN}✅ Virtual environment created!{Colors.ENDC}\n")
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Failed to create virtual environment: {e}{Colors.ENDC}")
        sys.exit(1)
    
    return get_python_executable()

def get_python_executable():
    """Get path to Python executable in virtual environment"""
    if platform.system() == "Windows":
        return Path("venv/Scripts/python.exe")
    return Path("venv/bin/python")

def install_dependencies(python_path):
    """Install required packages"""
    print(f"{Colors.BLUE}📋 Step 3: Installing dependencies...{Colors.ENDC}")
    print(f"{Colors.CYAN}This may take 2-5 minutes...{Colors.ENDC}")
    
    try:
        subprocess.run(
            [str(python_path), "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True
        )
        
        subprocess.run(
            [str(python_path), "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
            capture_output=False
        )
        
        print(f"{Colors.GREEN}✅ All dependencies installed!{Colors.ENDC}\n")
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Failed to install dependencies: {e}{Colors.ENDC}")
        sys.exit(1)

def verify_config():
    """Check if config.yaml exists"""
    print(f"{Colors.BLUE}📋 Step 4: Verifying configuration...{Colors.ENDC}")
    
    config_file = Path("config.yaml")
    if not config_file.exists():
        print(f"{Colors.RED}❌ config.yaml not found!{Colors.ENDC}")
        print(f"{Colors.YELLOW}📝 Creating default config...{Colors.ENDC}")
        create_default_config()
    
    print(f"{Colors.GREEN}✅ Configuration file exists{Colors.ENDC}\n")

def create_default_config():
    """Create a default config.yaml if it doesn't exist"""
    config_content = """# Scalping Bot Configuration

trading:
  mode: paper              # 'paper' or 'live'
  symbols:
    - NIFTY50
    - BANKNIFTY
  
  quantity: 1              # Lot size
  cooldown_seconds: 30     # Wait between trades
  
  trading_hours:
    start: "09:15"
    end: "15:30"
  
  max_trades_per_day: 20
  max_concurrent_trades: 3

risk:
  max_daily_loss: -5000
  max_daily_profit: 10000
  max_drawdown: 0.10
  max_risk_per_trade: 0.02
  trailing_stop: true
  break_even_on_target: 50

broker:
  provider: "paper"
  paper_starting_capital: 100000

notifications:
  telegram:
    enabled: false
    token: ""
    chat_id: ""

database:
  type: "sqlite"
  sqlite_db: "trading_bot.db"

logging:
  level: "INFO"
  file: "logs/scalping_bot.log"
  max_file_size: 10485760
  backup_count: 5
"""
    
    with open("config.yaml", "w") as f:
        f.write(config_content)
    print(f"{Colors.GREEN}✅ Default config.yaml created{Colors.ENDC}")

def create_launcher_script():
    """Create run_bot.py launcher script"""
    print(f"{Colors.BLUE}📋 Step 5: Creating launcher script...{Colors.ENDC}")
    
    launcher_content = '''#!/usr/bin/env python3
"""
Scalping Bot Launcher
Starts the bot with dashboard
"""

import asyncio
import threading
import yaml
import sys
from pathlib import Path

try:
    from main import ScalpingBot
    from dashboard import set_bot_instance, start_dashboard_server
    from paper_trading import PaperTradingBroker
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print(f"Make sure you installed dependencies: pip install -r requirements.txt")
    sys.exit(1)

def main():
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Load configuration
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ config.yaml not found!")
        sys.exit(1)
    
    # Initialize broker
    broker = PaperTradingBroker(
        starting_capital=config['broker']['paper_starting_capital']
    )
    
    # Create bot instance
    bot = ScalpingBot(config, broker, mode='paper')
    set_bot_instance(bot)
    
    # Start dashboard server in background
    dashboard_thread = threading.Thread(
        target=lambda: start_dashboard_server('0.0.0.0', 8000),
        daemon=True
    )
    dashboard_thread.start()
    
    # Wait for dashboard to start
    import time
    time.sleep(1)
    
    # Print startup info
    print(f"""
╔════════════════════════════════════════════════════════════╗
║           🤖 SCALPING BOT STARTED SUCCESSFULLY 🤖        ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  📊 Dashboard: http://localhost:8000                      ║
║  🎮 Mode: PAPER TRADING (Virtual Money)                   ║
║  💰 Starting Capital: ₹{config['broker']['paper_starting_capital']:,}                ║
║                                                            ║
║  CONTROLS:                                                 ║
║  • Click [▶️  START] to begin trading                      ║
║  • Click [⏸️  PAUSE] to stop new entries                   ║
║  • Click [⏹️  STOP] to shutdown                            ║
║  • Click [🚨 EMERGENCY] to close all trades               ║
║                                                            ║
║  Press CTRL+C to stop the bot                             ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Start bot
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        print("\n✅ Bot stopped gracefully")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    with open("run_bot.py", "w") as f:
        f.write(launcher_content)
    
    # Make executable on Unix
    if platform.system() != "Windows":
        os.chmod("run_bot.py", 0o755)
    
    print(f"{Colors.GREEN}✅ Launcher script created (run_bot.py){Colors.ENDC}\n")

def verify_installation(python_path):
    """Verify all dependencies are installed"""
    print(f"{Colors.BLUE}📋 Step 6: Verifying installation...{Colors.ENDC}")
    
    packages = [
        "fastapi",
        "uvicorn",
        "pandas",
        "pydantic",
        "pyyaml",
        "aiohttp",
    ]
    
    try:
        for package in packages:
            subprocess.run(
                [str(python_path), "-c", f"import {package.replace('-', '_')}"],
                check=True,
                capture_output=True
            )
        print(f"{Colors.GREEN}✅ All dependencies verified!{Colors.ENDC}\n")
        return True
    except subprocess.CalledProcessError:
        print(f"{Colors.RED}❌ Some dependencies are missing!{Colors.ENDC}")
        return False

def create_quickstart_guide():
    """Create a quick reference guide"""
    guide_content = """# 🚀 QUICK START GUIDE

## Already Installed? Start Here:

### 1. Activate Virtual Environment
```bash
# Windows
venv\\Scripts\\activate

# Mac/Linux
source venv/bin/activate
```

### 2. Run the Bot
```bash
python run_bot.py
```

### 3. Open Dashboard
Go to: http://localhost:8000

### 4. Click START Button
Bot will begin trading!

---

## Dashboard Controls

| Button | Action |
|--------|--------|
| **▶️ START** | Activate trading |
| **⏸️ PAUSE** | Stop new entries |
| **⏹️ STOP** | Shutdown |
| **🚨 EMERGENCY** | Close all positions |

---

## Monitoring

- **Live Updates**: Dashboard refreshes every 2 seconds
- **P&L Tracking**: Green = Profit, Red = Loss
- **Positions Table**: See all active trades
- **Statistics**: Real-time account info

---

## Logs

Watch bot logs:
```bash
tail -f logs/scalping_bot.log
```

---

## Configuration

Edit trading settings:
```bash
# Edit this file
config.yaml

# Change these to customize:
# - Symbols to trade
# - Stop loss & profit targets
# - Risk limits
# - Trading hours
```

---

## Common Issues

### Dashboard won't load?
```bash
# Restart bot
# Make sure it says "http://localhost:8000"
```

### No trades executing?
```bash
# 1. Check if within trading hours (09:15 - 15:30)
# 2. Click START button
# 3. Check logs: tail -f logs/scalping_bot.log
```

### Bot crashed?
```bash
# Restart with:
python run_bot.py
```

---

## Next Steps

1. ✅ Run bot in paper mode for 1-2 weeks
2. ✅ Monitor performance on dashboard
3. ✅ Analyze results and optimize
4. ✅ When ready, switch to live trading

---

## Support Files

- **USAGE_GUIDE.md** - Detailed documentation
- **config.yaml** - Configuration settings
- **logs/scalping_bot.log** - Trading logs
- **trading_bot.db** - Trade history database

---

## Happy Trading! 🚀
"""
    
    with open("QUICKSTART.md", "w") as f:
        f.write(guide_content)
    print(f"{Colors.GREEN}✅ Quick start guide created (QUICKSTART.md){Colors.ENDC}")

def run_bot(python_path):
    """Start the bot"""
    print(f"{Colors.BLUE}📋 Step 7: Starting bot...{Colors.ENDC}\n")
    
    try:
        subprocess.run(
            [str(python_path), "run_bot.py"],
            check=False
        )
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Bot stopped by user{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}❌ Error running bot: {e}{Colors.ENDC}")
        sys.exit(1)

def main():
    """Main setup and run flow"""
    print_header()
    
    try:
        # Step 1: Check Python version
        check_python_version()
        
        # Step 2: Create virtual environment
        python_path = create_virtual_env()
        
        # Step 3: Install dependencies
        install_dependencies(python_path)
        
        # Step 4: Verify configuration
        verify_config()
        
        # Step 5: Create launcher script
        create_launcher_script()
        
        # Step 6: Verify installation
        if not verify_installation(python_path):
            print(f"{Colors.YELLOW}⚠️  Some dependencies might be missing{Colors.ENDC}")
            print(f"{Colors.CYAN}Trying to install again...{Colors.ENDC}")
            install_dependencies(python_path)
        
        # Step 7: Create quick start guide
        create_quickstart_guide()
        
        # Step 8: Ask to run
        print(f"{Colors.BOLD}{Colors.GREEN}\n🎉 SETUP COMPLETE!{Colors.ENDC}")
        print(f"{Colors.CYAN}\nAll files created and dependencies installed.\n{Colors.ENDC}")
        
        start_bot = input(f"{Colors.CYAN}Start the bot now? (y/n): {Colors.ENDC}").strip().lower()
        
        if start_bot == 'y':
            print(f"\n{Colors.GREEN}Launching bot...{Colors.ENDC}\n")
            run_bot(python_path)
        else:
            print(f"""
{Colors.GREEN}✅ Setup complete! To start bot later:{Colors.ENDC}

{Colors.CYAN}1. Activate virtual environment:{Colors.ENDC}
   {Colors.YELLOW}source venv/bin/activate  # Mac/Linux{Colors.ENDC}
   {Colors.YELLOW}venv\\Scripts\\activate   # Windows{Colors.ENDC}

{Colors.CYAN}2. Run the bot:{Colors.ENDC}
   {Colors.YELLOW}python run_bot.py{Colors.ENDC}

{Colors.CYAN}3. Open dashboard:{Colors.ENDC}
   {Colors.YELLOW}http://localhost:8000{Colors.ENDC}

{Colors.GREEN}Happy Trading! 🚀{Colors.ENDC}
            """)
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Setup cancelled by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Setup failed: {e}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
