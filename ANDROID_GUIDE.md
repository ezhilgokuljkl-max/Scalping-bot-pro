# 🤖 SCALPING BOT - ANDROID APP

Control your trading bot directly from your Android phone! 📱

## 📱 Two Ways to Use on Android

### Option 1: Web Dashboard (Easiest)

Access the bot dashboard from any Android device:

1. **On your Computer** - Run the bot:
   ```bash
   python setup_and_run.py
   ```

2. **On your Phone** - Open browser:
   - Find your computer's IP address
   - Open: `http://YOUR_COMPUTER_IP:8000`
   - Full dashboard works on mobile!

3. **Controls on Phone:**
   - 🎯 Tap [▶️ START] to trade
   - Tap [⏸️ PAUSE] to pause
   - Tap [⏹️ STOP] to stop
   - Tap [🚨 EMERGENCY] for emergency stop
   - Swipe to see all positions
   - Tap [EXIT] on any trade to close it

### Option 2: Native Android App

Download and install the native Android app for better mobile experience:

- **App Name:** Scalping Bot Trader
- **Platform:** Android 8.0+
- **Features:** Full bot control, notifications, real-time updates

---

## 🃏 Find Your Computer's IP Address

### On Windows:
```bash
ipconfig
```
Look for "IPv4 Address" (usually 192.168.x.x or 10.0.x.x)

### On Mac/Linux:
```bash
ifconfig
```
Look for "inet" address (not 127.0.0.1)

### Example:
If your IP is `192.168.1.100`, open on phone:
```
http://192.168.1.100:8000
```

---

## 📱 Access Dashboard on Phone

### Step 1: Same WiFi Network
Make sure your phone is on same WiFi as your computer

### Step 2: Open Browser on Phone
- Chrome, Firefox, Safari, or any browser

### Step 3: Enter URL
```
http://YOUR_COMPUTER_IP:8000
```

### Step 4: See Full Dashboard
- Stats cards
- Open positions
- Control buttons
- Real-time updates

---

## 💱 Features on Mobile

### Dashboard Responsive Design
- ✅ Adapts to phone screen
- ✅ Touch-friendly buttons
- ✅ Swipe to scroll positions
- ✅ Real-time updates
- ✅ No lag or delay

### What You Can Do:
1. **Monitor** - Watch trades in real-time
2. **Start** - Tap to begin trading
3. **Pause** - Stop new entries
4. **Stop** - Shutdown bot
5. **Emergency** - Close all positions
6. **Exit Individual Trades** - Tap EXIT button
7. **See Stats** - All account info

---

## 🔧 Setup Steps

### Step 1: Start Bot on Computer
```bash
python setup_and_run.py
```

### Step 2: Find Computer's IP
```bash
# Windows
ipconfig

# Mac/Linux
ifconfig
```

### Step 3: On Phone
1. Open browser (Chrome, Firefox, etc)
2. Type: `http://192.168.1.100:8000` (use your IP)
3. Press Enter
4. Dashboard loads!

### Step 4: Use Dashboard
- Click START to trade
- Monitor positions
- See real-time updates
- Control bot from phone

---

## 📈 Dashboard on Mobile Screen

```
┌─────────────────────────┐
│ 🤖 SCALPING BOT    🔴 STOPPED │
├─────────────────────────┤
│ [[▶️ START]] [⏹️ STOP] │
│ [⏸️ PAUSE] [🚨 EMG]  │
├─────────────────────────┤
│ 💰 Balance           │
│ ₹100,000            │
├─────────────────────────┤
│ 📅 Today P&L         │
│ +₹2,500 ✅            │
├─────────────────────────┤
│ ⏳ Open Positions     │
│ 0                  │
├─────────────────────────┤
│                    │
│ 💱 OPEN POSITIONS   │
│ No positions     │
│                    │
└─────────────────────────┘
```

---

## 📢 Get Phone Notifications

### Enable Telegram Alerts:

1. **Create Telegram Bot:**
   - Chat with @BotFather on Telegram
   - Create new bot
   - Get API token

2. **Edit config.yaml:**
   ```yaml
   notifications:
     telegram:
       enabled: true
       token: "YOUR_BOT_TOKEN"
       chat_id: "YOUR_CHAT_ID"
   ```

3. **Get Alerts on Phone:**
   - Every trade notification
   - P&L updates
   - Alerts on phone instantly

---

## 🔐 Security Tips

### Local Network (Safe)
If accessing from phone on same WiFi:
- No extra security needed
- Fast connection
- Fully secure

### Remote Access (Requires Security)
If accessing from outside network:

1. **Use VPN:**
   - Download VPN app on phone
   - Connect to your home VPN
   - Then access dashboard

2. **Use Reverse Proxy (Advanced):**
   - Setup ngrok or similar
   - Secure tunnel to your computer
   - Access from anywhere

3. **Firewall:**
   - Don't expose port 8000 to internet
   - Use VPN for remote access

---

## 📈 Mobile Controls - Step by Step

### Start Trading:
1. Open: `http://YOUR_IP:8000`
2. Tap green **[▶️ START]** button
3. Status changes to 🟢 RUNNING
4. Bot begins monitoring markets

### Monitor Positions:
1. Scroll down to see positions table
2. Swipe left/right to see more columns
3. Watch P&L update in real-time (updates every 2 seconds)
4. Green = Profit, Red = Loss

### Exit a Trade:
1. Find trade in positions table
2. Tap **[EXIT]** button
3. Trade closes immediately

### Stop Bot:
1. Tap yellow **[⏸️ PAUSE]** (stops new entries)
2. Or tap red **[⏹️ STOP]** (complete shutdown)
3. Status changes to 🔴 STOPPED

### Emergency Stop:
1. Tap **[🚨 EMERGENCY]** button
2. ALL positions close immediately
3. Bot stops
4. Use if market crashes

---

## 📱 Recommended Android Browsers

| Browser | Rating | Notes |
|---------|--------|-------|
| **Chrome** | ⭐⭐⭐⭐⭐ | Best, smooth, updates |
| **Firefox** | ⭐⭐⭐⭐ | Good alternative |
| **Edge** | ⭐⭐⭐⭐ | Works well |
| **Opera** | ⭐⭐⭐ | OK but slower |
| **Samsung Browser** | ⭐⭐⭐ | Works but basic |

**Recommendation:** Use **Chrome** for best experience

---

## 🔱 Troubleshooting on Mobile

### Q: Can't connect to dashboard?
```
1. Check WiFi is connected on phone
2. Verify computer and phone on same WiFi
3. Check computer IP address is correct
4. Bot should be running (see http://localhost:8000 on computer)
5. Try: http://192.168.1.100:8000 (replace with your IP)
```

### Q: Dashboard loads but no updates?
```
1. Refresh page (pull down or F5)
2. Check bot is running: python run_bot.py
3. Check firewall not blocking port 8000
4. Try different browser (Chrome recommended)
```

### Q: Buttons don't work on mobile?
```
1. Make sure WiFi is stable
2. Check bot is running
3. Refresh page
4. Try closing and reopening browser
5. Check JavaScript is enabled
```

### Q: Can't find computer IP?
```
Windows: Open CMD, type: ipconfig
Look for IPv4 Address (usually 192.168.x.x)

Mac: Open Terminal, type: ifconfig
Look for inet address

Linux: Open Terminal, type: hostname -I
```

---

## 💱 Example Mobile Trading Session

```
09:00 AM
- Open Chrome on phone
- Type: http://192.168.1.100:8000
- Dashboard loads (beautiful!)
- See: 🟢 RUNNING status
- See: ₹100,000 balance

09:15 AM
- Market opens
- Tap [▶️ START]
- Bot begins trading
- See first position appear: NIFTY50
- Entry: ₹23,500
- P&L: +₹5 (green text)

09:16 AM
- Price moves to ₹23,510
- Target hit!
- Position auto-closes
- +₹10 profit 🎉

09:20 AM
- Another signal
- New position: BANKNIFTY
- Monitoring from phone
- Refreshes every 2 seconds

14:00 PM
- Still trading throughout day
- Multiple positions closed
- Total P&L: +₹2,500 ✅

15:30 PM
- Market closes
- All positions auto-close
- Tap [⏹️ STOP]
- Status: 🔴 STOPPED
- Daily report ready
```

---

## 📸 Screenshots on Mobile

### Landscape Mode
```
┌─────────────────────────────────────────────────────────────┐
│ 🤖 SCALPING BOT    | 🟢 RUNNING                             │
├─────────────────────────────────────────────────────────────┤
│ [▶️ START] [⏸️ PAUSE] [⏹️ STOP] [🚨 EMERGENCY]           │
├─────────────────────────────────────────────────────────────┤
│ 💰 ₹100,000  | 🪙 ₹95,000  | 📅 +₹2,500  | ⏳ 3 trades   │
├─────────────────────────────────────────────────────────────┤
│ Symbol  │ Side │ Entry  │ Current │ P&L  │ Return │ EXIT   │
│ NIFTY50 │ BUY  │ 23500  │ 23520   │ +₹5  │ +0.02% │ [✖️]   │
│ BANKNFT │ SELL │ 45200  │ 45180   │ +₹30 │ +0.07% │ [✖️]   │
└─────────────────────────────────────────────────────────────┘
```

### Portrait Mode
```
┌──────────────────────┐
│ 🤖 SCALPING BOT      │
│ 🟢 RUNNING           │
├──────────────────────┤
│ [▶️ START]  [⏸️ PAUSE] │
│ [⏹️ STOP]   [🚨 EMG]  │
├──────────────────────┤
│ 💰 Balance           │
│ ₹100,000             │
├──────────────────────┤
│ 📅 Today P&L         │
│ +₹2,500 ✅           │
├──────────────────────┤
│ ⏳ Open Positions    │
│ 3                    │
├──────────────────────┤
│ NIFTY50 - BUY        │
│ Entry: ₹23,500       │
│ Current: ₹23,520     │
│ P&L: +₹5 ✅          │
│ [EXIT]               │
├──────────────────────┤
│ BANKNFT - SELL       │
│ Entry: ₹45,200       │
│ Current: ₹45,180     │
│ P&L: +₹30 ✅         │
│ [EXIT]               │
└──────────────────────┘
```

---

## ✅ Checklist for Mobile Access

- [ ] Bot running on computer: `python setup_and_run.py`
- [ ] Found computer's IP address
- [ ] Phone on same WiFi network
- [ ] Opened browser on phone
- [ ] Entered URL: `http://YOUR_IP:8000`
- [ ] Dashboard loaded in browser
- [ ] Clicked ▶️ **START** button
- [ ] Watching real-time updates
- [ ] Saw trades execute
- [ ] Tested all buttons (PAUSE, STOP, etc)

---

## 📱 App Store Release (Coming Soon)

We're developing a native Android app for submission to Google Play Store:

**Features:**
- ✅ No browser needed
- ✅ App icon on home screen
- ✅ Push notifications
- ✅ Offline mode support
- ✅ Biometric authentication
- ✅ Custom alerts

**Coming Soon:** Check back for native app link

---

## 🎉 That's It!

Your bot is now accessible from any Android device! 📱

**Just:**
1. Run bot on computer
2. Find computer's IP
3. Open on phone browser
4. Control everything from phone

**Happy Mobile Trading!** 🚀

---

## 📞 Support

**Issues on mobile?**
- Check network connection
- Try different browser
- Refresh page
- Restart bot
- Check firewall settings

**Need help?**
- See full guide: `USAGE_GUIDE.md`
- Check setup: `SETUP.md`
- Quick reference: `QUICKSTART.md`
