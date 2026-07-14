#!/usr/bin/env python3
"""
📱 SCALPING BOT - ANDROID HELPER

Helps setup remote access from Android devices
Enables secure connection and local network sharing
"""

import os
import sys
import socket
import subprocess
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Print welcome header"""
    print(f"""
{Colors.BOLD}{Colors.CYAN}
╔═══════════════════════════════════════════════════════════════╗
║      📱 SCALPING BOT - ANDROID REMOTE ACCESS SETUP 📱       ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.ENDC}
    """)

def get_local_ip():
    """Get local network IP address"""
    try:
        # Create socket to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def generate_qr_code(url):
    """Generate QR code for easy scanning"""
    try:
        import subprocess
        # Try to install qrcode if not present
        try:
            import qrcode
        except ImportError:
            print(f"{Colors.YELLOW}📋 Installing QR code generator...{Colors.ENDC}")
            subprocess.run([sys.executable, "-m", "pip", "install", "qrcode", "pillow"], 
                         capture_output=True)
        
        import qrcode
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save("bot_dashboard_qr.png")
        return True
    except:
        return False

def main():
    print_header()
    
    # Get local IP
    local_ip = get_local_ip()
    port = 8000
    url = f"http://{local_ip}:{port}"
    
    print(f"{Colors.CYAN}📋 ANDROID REMOTE ACCESS SETUP{Colors.ENDC}\n")
    
    print(f"{Colors.BLUE}Step 1: Local Network Information{Colors.ENDC}")
    print(f"{Colors.GREEN}✅ Your computer's local IP: {Colors.BOLD}{local_ip}{Colors.ENDC}")
    print(f"{Colors.GREEN}✅ Dashboard port: {Colors.BOLD}{port}{Colors.ENDC}")
    print(f"{Colors.GREEN}✅ Full URL: {Colors.BOLD}{url}{Colors.ENDC}\n")
    
    print(f"{Colors.BLUE}Step 2: Instructions for Android Phone{Colors.ENDC}")
    print(f"""
{Colors.CYAN}1. Make sure your phone is on the SAME WiFi network{Colors.ENDC}
{Colors.CYAN}2. Open a browser on your Android phone (Chrome recommended){Colors.ENDC}
{Colors.CYAN}3. Type or copy this URL:{Colors.ENDC}
   {Colors.BOLD}{url}{Colors.ENDC}
{Colors.CYAN}4. Press Enter{Colors.ENDC}
{Colors.CYAN}5. Dashboard will load on your phone!{Colors.ENDC}
    """)
    
    # Try to generate QR code
    print(f"{Colors.BLUE}Step 3: Scan QR Code (Optional){Colors.ENDC}")
    if generate_qr_code(url):
        print(f"{Colors.GREEN}✅ QR code generated: bot_dashboard_qr.png{Colors.ENDC}")
        print(f"{Colors.CYAN}Show this QR code to your phone's camera app to open dashboard!{Colors.ENDC}\n")
    else:
        print(f"{Colors.YELLOW}⚠️  QR code generation skipped{Colors.ENDC}\n")
    
    print(f"{Colors.BLUE}Step 4: Start Bot (if not running){Colors.ENDC}")
    print(f"{Colors.CYAN}On your computer, run:{Colors.ENDC}")
    print(f"{Colors.BOLD}python setup_and_run.py{Colors.ENDC}\n")
    
    print(f"{Colors.BLUE}Step 5: Network Checklist{Colors.ENDC}")
    print(f"""
{Colors.CYAN}[ ] Bot is running on this computer{Colors.ENDC}
{Colors.CYAN}[ ] Phone is on same WiFi network{Colors.ENDC}
{Colors.CYAN}[ ] Phone can access {url}{Colors.ENDC}
{Colors.CYAN}[ ] Dashboard loads on phone browser{Colors.ENDC}
{Colors.CYAN}[ ] Click START button on phone{Colors.ENDC}
    """)
    
    print(f"{Colors.GREEN}{Colors.BOLD}🎉 Setup Complete!{Colors.ENDC}\n")
    
    print(f"""
{Colors.CYAN}QUICK REFERENCE:

Computer IP: {Colors.BOLD}{local_ip}{Colors.ENDC}
Dashboard URL: {Colors.BOLD}{url}{Colors.ENDC}

On Android Phone:
1. Open Chrome
2. Paste URL: {url}
3. Press Enter
4. Tap [START] to trade

Mobile Controls:
▶️  START - Begin trading
⏸️  PAUSE - Stop new entries  
⏹️  STOP - Shutdown
🚨 EMERGENCY - Close all
    """)
    
    print(f"{Colors.BOLD}{Colors.GREEN}Your bot is ready for Android access!{Colors.ENDC}")
    print(f"{Colors.GREEN}Open the URL above on your phone's browser.{Colors.ENDC}\n")
    
    # Save info to file
    info = f"""Scalping Bot - Remote Access Info

Computer IP: {local_ip}
Dashboard Port: {port}
Full URL: {url}

Android Setup:
1. Ensure phone is on same WiFi
2. Open Chrome browser
3. Paste URL: {url}
4. Dashboard loads!

Save this file for easy reference.
"""
    
    with open("ANDROID_ACCESS.txt", "w") as f:
        f.write(info)
    
    print(f"{Colors.GREEN}✅ Access info saved to: ANDROID_ACCESS.txt{Colors.ENDC}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Setup cancelled{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.ENDC}")

