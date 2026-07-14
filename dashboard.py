"""
Interactive Web Dashboard for Scalping Bot

Provides a beautiful, real-time UI with:
- Live trading status
- Open positions tracker
- Trade history
- Performance metrics
- Control buttons (Start/Stop/Pause)
- Live charts and statistics
"""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Scalping Bot Dashboard")

# Global bot instance (will be set from main.py)
bot_instance = None
connected_clients = set()


@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the main dashboard HTML."""
    return HTML_DASHBOARD


@app.get("/api/status")
async def get_bot_status():
    """Get current bot status."""
    if not bot_instance:
        return {"error": "Bot not initialized"}
    
    account = await bot_instance.broker.get_account_info()
    positions = bot_instance.position_manager.get_open_trades()
    
    return {
        "status": "RUNNING" if bot_instance.running else "STOPPED",
        "mode": bot_instance.mode.upper(),
        "uptime_seconds": 0,
        "account": {
            "balance": account.balance if account else 0,
            "available": account.available_balance if account else 0,
            "used_margin": account.used_margin if account else 0,
            "total_trades": account.total_trades if account else 0,
            "today_pnl": account.today_pnl if account else 0,
            "total_pnl": account.total_pnl if account else 0,
        },
        "positions": {
            "open": len(positions),
            "total_pnl": sum([p.current_pnl for p in positions]) if positions else 0,
        },
        "symbols_monitored": bot_instance.symbols,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/positions")
async def get_open_positions():
    """Get all open positions."""
    if not bot_instance:
        return {"error": "Bot not initialized"}
    
    positions = bot_instance.position_manager.get_open_trades()
    
    return {
        "positions": [
            {
                "trade_id": p.trade_id,
                "symbol": p.symbol,
                "side": p.side,
                "entry_price": p.entry_price,
                "current_price": p.current_price,
                "quantity": p.entry_quantity,
                "stop_loss": p.stop_loss,
                "target_1": p.target_1,
                "target_2": p.target_2,
                "target_3": p.target_3,
                "pnl": p.current_pnl,
                "pnl_percent": p.current_pnl_percentage,
                "entry_time": p.entry_time.isoformat(),
                "duration_seconds": (datetime.now() - p.entry_time).total_seconds(),
            }
            for p in positions
        ],
        "total_pnl": sum([p.current_pnl for p in positions]) if positions else 0,
        "count": len(positions),
    }


@app.get("/api/history")
async def get_trade_history(limit: int = 50):
    """Get recent closed trades."""
    if not bot_instance:
        return {"error": "Bot not initialized"}
    
    closed_trades = bot_instance.broker.get_closed_trades() if hasattr(bot_instance.broker, 'get_closed_trades') else []
    
    return {
        "trades": closed_trades[-limit:],
        "total_count": len(closed_trades),
    }


@app.post("/api/commands/start")
async def start_bot():
    """Start the bot."""
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot not initialized")
    
    if bot_instance.running:
        return {"status": "already_running"}
    
    bot_instance.running = True
    return {"status": "started", "message": "Bot started successfully"}


@app.post("/api/commands/stop")
async def stop_bot():
    """Stop the bot."""
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot not initialized")
    
    if not bot_instance.running:
        return {"status": "already_stopped"}
    
    await bot_instance.stop()
    return {"status": "stopped", "message": "Bot stopped successfully"}


@app.post("/api/commands/pause")
async def pause_bot():
    """Pause new entries (keep monitoring)."""
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot not initialized")
    
    bot_instance.running = False
    return {"status": "paused", "message": "Bot paused - no new entries"}


@app.post("/api/commands/emergency_stop")
async def emergency_stop():
    """Emergency stop - close all positions immediately."""
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot not initialized")
    
    await bot_instance._close_all_positions()
    bot_instance.running = False
    return {"status": "emergency_stopped", "message": "All positions closed"}


@app.post("/api/commands/exit/{trade_id}")
async def exit_trade(trade_id: str):
    """Exit a specific trade."""
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot not initialized")
    
    position = bot_instance.position_manager.get_trade(trade_id)
    if not position:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    market_data = await bot_instance.broker.get_market_data(position.symbol)
    if market_data:
        exit_price = market_data.get("close", position.current_price)
        await bot_instance._exit_position(position, exit_price)
        return {"status": "exited", "trade_id": trade_id}
    
    return {"error": "Could not get market data"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for live updates."""
    await websocket.accept()
    connected_clients.add(websocket)
    
    try:
        while True:
            await asyncio.sleep(2)
            status = await get_bot_status()
            positions = await get_open_positions()
            
            await websocket.send_json({
                "type": "update",
                "status": status,
                "positions": positions,
                "timestamp": datetime.now().isoformat(),
            })
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        connected_clients.discard(websocket)


HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scalping Bot Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #667eea;
            --secondary: #764ba2;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --dark: #0f172a;
            --darker: #1e293b;
            --light: #f1f5f9;
            --border: #334155;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, var(--dark) 0%, var(--darker) 100%);
            color: #e2e8f0;
            overflow-x: hidden;
            min-height: 100vh;
        }

        .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            width: 280px;
            height: 100vh;
            background: linear-gradient(180deg, #1a1f35 0%, #0f172a 100%);
            border-right: 1px solid var(--border);
            overflow-y: auto;
            z-index: 1000;
            display: flex;
            flex-direction: column;
        }

        .sidebar-header {
            padding: 30px 20px;
            text-align: center;
            border-bottom: 2px solid var(--border);
        }

        .sidebar-header h1 {
            font-size: 1.5em;
            color: var(--primary);
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .sidebar-header i {
            font-size: 1.8em;
        }

        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--danger);
            margin-right: 8px;
            animation: pulse 2s infinite;
        }

        .status-indicator.active {
            background: var(--success);
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .nav-buttons {
            flex: 1;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .nav-btn {
            padding: 15px 20px;
            border: 2px solid transparent;
            border-radius: 10px;
            background: rgba(102, 126, 234, 0.1);
            color: #e2e8f0;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.95em;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .nav-btn:hover {
            background: rgba(102, 126, 234, 0.2);
            border-color: var(--primary);
            transform: translateX(5px);
        }

        .nav-btn i {
            font-size: 1.2em;
        }

        .main {
            margin-left: 280px;
            padding: 30px;
            min-height: 100vh;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 40px;
            padding: 30px;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
            border: 2px solid var(--border);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }

        .header h1 {
            font-size: 2em;
            color: var(--light);
        }

        .header p {
            color: #94a3b8;
            font-size: 0.95em;
        }

        .status-badge {
            padding: 12px 24px;
            border-radius: 50px;
            font-weight: bold;
            font-size: 1em;
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(239, 68, 68, 0.2);
            color: var(--danger);
            border: 2px solid var(--danger);
        }

        .status-badge.running {
            background: rgba(16, 185, 129, 0.2);
            color: var(--success);
            border-color: var(--success);
        }

        .control-panel {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 15px;
            margin-bottom: 40px;
        }

        .btn-action {
            padding: 16px 24px;
            border: none;
            border-radius: 12px;
            font-size: 0.95em;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            letter-spacing: 0.5px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        }

        .btn-action:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
        }

        .btn-action i {
            font-size: 1.2em;
        }

        .btn-start {
            background: linear-gradient(135deg, var(--success) 0%, #059669 100%);
            color: white;
        }

        .btn-stop {
            background: linear-gradient(135deg, var(--danger) 0%, #dc2626 100%);
            color: white;
        }

        .btn-pause {
            background: linear-gradient(135deg, var(--warning) 0%, #d97706 100%);
            color: white;
        }

        .btn-emergency {
            background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
            color: white;
            animation: danger-glow 2s infinite;
        }

        @keyframes danger-glow {
            0%, 100% { box-shadow: 0 8px 16px rgba(220, 38, 38, 0.2); }
            50% { box-shadow: 0 8px 24px rgba(220, 38, 38, 0.4); }
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .stat-card {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            border: 2px solid var(--border);
            padding: 25px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
        }

        .stat-card:hover {
            border-color: var(--primary);
            transform: translateY(-8px);
            box-shadow: 0 16px 40px rgba(102, 126, 234, 0.2);
        }

        .stat-label {
            font-size: 0.85em;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .stat-label i {
            color: var(--primary);
            font-size: 1.1em;
        }

        .stat-value {
            font-size: 2.2em;
            font-weight: 800;
            color: var(--light);
            font-family: 'Courier New', monospace;
        }

        .stat-value.positive {
            color: var(--success);
        }

        .stat-value.negative {
            color: var(--danger);
        }

        .section {
            background: linear-gradient(135deg, rgba(45, 45, 68, 0.5) 0%, rgba(65, 65, 85, 0.5) 100%);
            border: 2px solid var(--border);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            margin-bottom: 30px;
        }

        .section h2 {
            margin-bottom: 25px;
            font-size: 1.6em;
            color: var(--light);
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 2px solid var(--border);
            padding-bottom: 15px;
        }

        .section h2 i {
            color: var(--primary);
            font-size: 1.4em;
        }

        .positions-table {
            width: 100%;
            border-collapse: collapse;
            border-spacing: 0;
        }

        .positions-table thead {
            background: rgba(102, 126, 234, 0.15);
            border-bottom: 2px solid var(--border);
        }

        .positions-table th {
            padding: 18px 15px;
            text-align: left;
            font-weight: 700;
            color: var(--primary);
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .positions-table td {
            padding: 18px 15px;
            border-bottom: 1px solid rgba(102, 126, 234, 0.1);
            font-size: 0.95em;
        }

        .positions-table tr:hover {
            background: rgba(102, 126, 234, 0.08);
        }

        .positions-table tr:last-child td {
            border-bottom: none;
        }

        .badge {
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 0.85em;
            font-weight: 700;
            display: inline-block;
            letter-spacing: 0.3px;
        }

        .badge-buy {
            background: rgba(16, 185, 129, 0.2);
            color: var(--success);
            border: 1px solid rgba(16, 185, 129, 0.4);
        }

        .badge-sell {
            background: rgba(239, 68, 68, 0.2);
            color: var(--danger);
            border: 1px solid rgba(239, 68, 68, 0.4);
        }

        .pnl-positive {
            color: var(--success);
            font-weight: 700;
            font-family: 'Courier New', monospace;
        }

        .pnl-negative {
            color: var(--danger);
            font-weight: 700;
            font-family: 'Courier New', monospace;
        }

        .exit-btn {
            padding: 10px 16px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.85em;
            font-weight: 700;
            transition: all 0.2s ease;
        }

        .exit-btn:hover {
            transform: scale(1.08);
            box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
        }

        .empty-state {
            text-align: center;
            padding: 60px 40px;
            color: #64748b;
        }

        .empty-state i {
            font-size: 3.5em;
            margin-bottom: 20px;
            color: var(--border);
        }

        .empty-state p {
            font-size: 1.1em;
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(102, 126, 234, 0.3);
            border-top-color: var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .price-up {
            color: var(--success);
            font-weight: 700;
        }

        .price-down {
            color: var(--danger);
            font-weight: 700;
        }

        @media (max-width: 768px) {
            .sidebar {
                width: 0;
                overflow: hidden;
            }

            .main {
                margin-left: 0;
                padding: 20px;
            }

            .header {
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }

            .control-panel {
                grid-template-columns: 1fr 1fr;
            }

            .stats-grid {
                grid-template-columns: 1fr;
            }

            .positions-table {
                font-size: 0.9em;
            }

            .positions-table th,
            .positions-table td {
                padding: 12px 10px;
            }
        }
    </style>
</head>
<body>
    <!-- Sidebar -->
    <div class="sidebar">
        <div class="sidebar-header">
            <h1><i class="fas fa-robot"></i>SCALPING BOT</h1>
            <p style="color: #94a3b8; font-size: 0.85em; margin-top: 8px;">Trading Dashboard</p>
        </div>
        <div class="nav-buttons">
            <button class="nav-btn" onclick="startBot()" style="background: rgba(16, 185, 129, 0.1);">
                <i class="fas fa-play"></i>START BOT
            </button>
            <button class="nav-btn" onclick="pauseBot()" style="background: rgba(245, 158, 11, 0.1);">
                <i class="fas fa-pause"></i>PAUSE BOT
            </button>
            <button class="nav-btn" onclick="stopBot()" style="background: rgba(239, 68, 68, 0.1);">
                <i class="fas fa-stop"></i>STOP BOT
            </button>
            <button class="nav-btn" onclick="emergencyStop()" style="background: rgba(139, 0, 0, 0.2); color: #ff6b6b; margin-top: auto;">
                <i class="fas fa-exclamation-triangle"></i>EMERGENCY
            </button>
        </div>
    </div>

    <!-- Main Content -->
    <div class="main">
        <!-- Header -->
        <div class="header">
            <div>
                <h1><i class="fas fa-chart-line" style="color: var(--primary);"></i>Trading Dashboard</h1>
                <p>Real-time bot performance and position tracking</p>
            </div>
            <div class="status-badge" id="statusBadge">
                <span class="status-indicator"></span>
                <span id="statusText">INITIALIZING</span>
            </div>
        </div>

        <!-- Control Panel -->
        <div class="control-panel">
            <button class="btn-action btn-start" onclick="startBot()" title="Start Trading">
                <i class="fas fa-play"></i>START
            </button>
            <button class="btn-action btn-pause" onclick="pauseBot()" title="Pause Trading">
                <i class="fas fa-pause"></i>PAUSE
            </button>
            <button class="btn-action btn-stop" onclick="stopBot()" title="Stop Bot">
                <i class="fas fa-square"></i>STOP
            </button>
            <button class="btn-action btn-emergency" onclick="emergencyStop()" title="Emergency Stop">
                <i class="fas fa-fire"></i>EMERGENCY
            </button>
        </div>

        <!-- Statistics Grid -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label"><i class="fas fa-wallet"></i>Account Balance</div>
                <div class="stat-value" id="statBalance">₹100,000</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><i class="fas fa-coins"></i>Available</div>
                <div class="stat-value" id="statAvailable">₹95,000</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><i class="fas fa-calendar-today"></i>Today's P&L</div>
                <div class="stat-value positive" id="statTodayPnL">+₹2,500</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><i class="fas fa-chart-pie"></i>Total P&L</div>
                <div class="stat-value positive" id="statTotalPnL">+₹5,200</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><i class="fas fa-hourglass-half"></i>Open Positions</div>
                <div class="stat-value" id="statOpenPositions" style="color: var(--primary);">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><i class="fas fa-exchange-alt"></i>Total Trades</div>
                <div class="stat-value" id="statTotalTrades" style="color: var(--primary);">0</div>
            </div>
        </div>

        <!-- Open Positions Section -->
        <div class="section">
            <h2><i class="fas fa-list"></i>Open Positions</h2>
            <div id="positionsContainer">
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <p>No open positions</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;

        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    updateDashboard(data);
                } catch (e) {
                    console.error('Error parsing message:', e);
                }
            };

            ws.onerror = () => {
                console.error('WebSocket error');
                setTimeout(connectWebSocket, 3000);
            };
        }

        function updateDashboard(data) {
            const status = data.status;
            const positions = data.positions;

            // Update status badge
            const badge = document.getElementById('statusBadge');
            const indicator = badge.querySelector('.status-indicator');
            const statusText = document.getElementById('statusText');
            
            if (status.status === 'RUNNING') {
                badge.classList.add('running');
                indicator.classList.add('active');
                statusText.textContent = 'RUNNING';
            } else {
                badge.classList.remove('running');
                indicator.classList.remove('active');
                statusText.textContent = 'STOPPED';
            }

            // Update stats
            updateStatCard('statBalance', `₹${status.account.balance.toLocaleString()}`);
            updateStatCard('statAvailable', `₹${status.account.available.toLocaleString()}`);
            
            updatePnLCard('statTodayPnL', status.account.today_pnl);
            updatePnLCard('statTotalPnL', status.account.total_pnl);
            
            updateStatCard('statOpenPositions', positions.count);
            updateStatCard('statTotalTrades', status.account.total_trades);

            // Update positions table
            updatePositionsTable(positions.positions);
        }

        function updateStatCard(id, value) {
            document.getElementById(id).textContent = value;
        }

        function updatePnLCard(id, value) {
            const element = document.getElementById(id);
            const formattedValue = `${value >= 0 ? '+' : ''}₹${value.toLocaleString()}`;
            element.textContent = formattedValue;
            element.className = value >= 0 ? 'stat-value positive' : 'stat-value negative';
        }

        function updatePositionsTable(positions) {
            const container = document.getElementById('positionsContainer');
            
            if (!positions || positions.length === 0) {
                container.innerHTML = '<div class="empty-state"><i class="fas fa-inbox"></i><p>No open positions</p></div>';
                return;
            }

            let html = `
                <table class="positions-table">
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Side</th>
                            <th>Entry</th>
                            <th>Current</th>
                            <th>Qty</th>
                            <th>P&L</th>
                            <th>Return</th>
                            <th>SL</th>
                            <th>Target</th>
                            <th>Time</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            positions.forEach(pos => {
                const sideClass = pos.side.toUpperCase() === 'BUY' ? 'badge-buy' : 'badge-sell';
                const pnlClass = pos.pnl >= 0 ? 'pnl-positive' : 'pnl-negative';
                const durationMin = Math.floor(pos.duration_seconds / 60);
                
                html += `
                    <tr>
                        <td><strong>${pos.symbol}</strong></td>
                        <td><span class="badge ${sideClass}">${pos.side}</span></td>
                        <td>₹${pos.entry_price.toFixed(2)}</td>
                        <td>₹${pos.current_price.toFixed(2)}</td>
                        <td>${pos.quantity}</td>
                        <td class="${pnlClass}">₹${Math.abs(pos.pnl).toFixed(2)}</td>
                        <td class="${pnlClass}">${(pos.pnl_percent >= 0 ? '+' : '')}${pos.pnl_percent.toFixed(2)}%</td>
                        <td>₹${pos.stop_loss.toFixed(2)}</td>
                        <td>₹${pos.target_1.toFixed(2)}</td>
                        <td>${durationMin}m</td>
                        <td><button class="exit-btn" onclick="exitTrade('${pos.trade_id}')"><i class="fas fa-sign-out-alt"></i></button></td>
                    </tr>
                `;
            });

            html += '</tbody></table>';
            container.innerHTML = html;
        }

        async function apiCall(endpoint, method = 'GET') {
            try {
                const response = await fetch(endpoint, { method });
                const data = await response.json();
            } catch (error) {
                console.error('API Error:', error);
            }
        }

        function startBot() { apiCall('/api/commands/start', 'POST'); }
        function stopBot() { if (confirm('Stop bot and close positions?')) apiCall('/api/commands/stop', 'POST'); }
        function pauseBot() { apiCall('/api/commands/pause', 'POST'); }
        function emergencyStop() { if (confirm('EMERGENCY STOP - Close ALL positions?')) apiCall('/api/commands/emergency_stop', 'POST'); }
        function exitTrade(tradeId) { if (confirm('Exit this trade?')) apiCall(`/api/commands/exit/${tradeId}`, 'POST'); }

        // Initialize
        window.addEventListener('DOMContentLoaded', () => {
            connectWebSocket();
            setInterval(() => {
                if (ws && ws.readyState !== WebSocket.OPEN) {
                    connectWebSocket();
                }
            }, 5000);
        });
    </script>
</body>
</html>
"""

def set_bot_instance(bot):
    """Set the bot instance for the dashboard."""
    global bot_instance
    bot_instance = bot

def start_dashboard_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the dashboard FastAPI server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)
