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
        "uptime_seconds": 0,  # Calculate from start time
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
            # Send status every 2 seconds
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
    <title>🤖 Scalping Bot Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
            color: #e0e0e0;
            padding: 20px;
            min-height: 100vh;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        .header h1 {
            font-size: 2.5em;
            font-weight: bold;
        }

        .status-badge {
            padding: 10px 20px;
            border-radius: 50px;
            font-weight: bold;
            font-size: 1.1em;
            animation: pulse 2s infinite;
        }

        .status-badge.running {
            background: #10b981;
            color: white;
        }

        .status-badge.stopped {
            background: #ef4444;
            color: white;
        }

        .status-badge.paused {
            background: #f59e0b;
            color: white;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        .control-panel {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }

        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn-start {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
        }

        .btn-stop {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
        }

        .btn-pause {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
        }

        .btn-emergency {
            background: linear-gradient(135deg, #dc2626 0%, #7f1d1d 100%);
            color: white;
            animation: danger-pulse 1s infinite;
        }

        @keyframes danger-pulse {
            0%, 100% { box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); }
            50% { box-shadow: 0 4px 25px rgba(220, 38, 38, 0.4); }
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            border: 2px solid rgba(102, 126, 234, 0.3);
            padding: 25px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            border-color: rgba(102, 126, 234, 0.6);
            transform: translateY(-5px);
        }

        .stat-label {
            font-size: 0.9em;
            color: #a0a0a0;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }

        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }

        .stat-value.positive {
            color: #10b981;
        }

        .stat-value.negative {
            color: #ef4444;
        }

        .section {
            background: linear-gradient(135deg, rgba(45, 45, 68, 0.8) 0%, rgba(65, 65, 85, 0.8) 100%);
            border: 2px solid rgba(102, 126, 234, 0.2);
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 25px;
            backdrop-filter: blur(10px);
        }

        .section h2 {
            margin-bottom: 20px;
            font-size: 1.5em;
            color: #667eea;
            border-bottom: 2px solid rgba(102, 126, 234, 0.5);
            padding-bottom: 10px;
        }

        .positions-table {
            width: 100%;
            border-collapse: collapse;
            overflow-x: auto;
        }

        .positions-table thead {
            background: rgba(102, 126, 234, 0.2);
        }

        .positions-table th {
            padding: 15px;
            text-align: left;
            font-weight: bold;
            color: #667eea;
            border-bottom: 2px solid rgba(102, 126, 234, 0.5);
        }

        .positions-table td {
            padding: 15px;
            border-bottom: 1px solid rgba(102, 126, 234, 0.2);
        }

        .positions-table tr:hover {
            background: rgba(102, 126, 234, 0.1);
        }

        .badge {
            padding: 6px 12px;
            border-radius: 50px;
            font-size: 0.85em;
            font-weight: bold;
        }

        .badge-buy {
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
        }

        .badge-sell {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
        }

        .badge-pending {
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
        }

        .pnl-positive {
            color: #10b981;
            font-weight: bold;
        }

        .pnl-negative {
            color: #ef4444;
            font-weight: bold;
        }

        .exit-btn {
            padding: 6px 12px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85em;
            transition: all 0.2s ease;
        }

        .exit-btn:hover {
            background: #764ba2;
            transform: scale(1.05);
        }

        .empty-state {
            text-align: center;
            padding: 40px;
            color: #707070;
        }

        .empty-state svg {
            width: 60px;
            height: 60px;
            margin-bottom: 15px;
            opacity: 0.5;
        }

        .chart-container {
            position: relative;
            height: 300px;
            margin-bottom: 30px;
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(102, 126, 234, 0.3);
            border-radius: 50%;
            border-top-color: #667eea;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                gap: 15px;
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

            .positions-table th, .positions-table td {
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div>
                <h1>🤖 Scalping Bot</h1>
                <p style="color: rgba(255,255,255,0.8); margin-top: 5px;">Real-Time Trading Dashboard</p>
            </div>
            <div class="status-badge running" id="statusBadge">🔴 INITIALIZING</div>
        </div>

        <!-- Control Panel -->
        <div class="control-panel">
            <button class="btn btn-start" onclick="startBot()">▶️ START</button>
            <button class="btn btn-pause" onclick="pauseBot()">⏸️ PAUSE</button>
            <button class="btn btn-stop" onclick="stopBot()">⏹️ STOP</button>
            <button class="btn btn-emergency" onclick="emergencyStop()">🚨 EMERGENCY</button>
        </div>

        <!-- Statistics -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Account Balance</div>
                <div class="stat-value" id="statBalance">₹ 0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Available Balance</div>
                <div class="stat-value" id="statAvailable">₹ 0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Today's P&L</div>
                <div class="stat-value positive" id="statTodayPnL">₹ 0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total P&L</div>
                <div class="stat-value positive" id="statTotalPnL">₹ 0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Open Positions</div>
                <div class="stat-value" id="statOpenPositions">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Trades</div>
                <div class="stat-value" id="statTotalTrades">0</div>
            </div>
        </div>

        <!-- Open Positions -->
        <div class="section">
            <h2>📊 Open Positions</h2>
            <div id="positionsContainer">
                <div class="empty-state">
                    <div class="loading"></div>
                    <p>Loading positions...</p>
                </div>
            </div>
        </div>

        <!-- Performance Metrics -->
        <div class="section">
            <h2>📈 Performance Metrics</h2>
            <div class="chart-container">
                <canvas id="performanceChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let performanceChart = null;

        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                updateDashboard(data);
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
            badge.textContent = status.status === 'RUNNING' ? '🟢 RUNNING' : '🔴 STOPPED';
            badge.className = `status-badge ${status.status.toLowerCase()}`;

            // Update stats
            document.getElementById('statBalance').textContent = `₹ ${status.account.balance.toLocaleString()}`;
            document.getElementById('statAvailable').textContent = `₹ ${status.account.available.toLocaleString()}`;
            
            const todayPnLElement = document.getElementById('statTodayPnL');
            todayPnLElement.textContent = `₹ ${status.account.today_pnl.toLocaleString()}`;
            todayPnLElement.className = status.account.today_pnl >= 0 ? 'stat-value positive' : 'stat-value negative';

            const totalPnLElement = document.getElementById('statTotalPnL');
            totalPnLElement.textContent = `₹ ${status.account.total_pnl.toLocaleString()}`;
            totalPnLElement.className = status.account.total_pnl >= 0 ? 'stat-value positive' : 'stat-value negative';

            document.getElementById('statOpenPositions').textContent = positions.count;
            document.getElementById('statTotalTrades').textContent = status.account.total_trades;

            // Update positions table
            updatePositionsTable(positions.positions);
        }

        function updatePositionsTable(positions) {
            const container = document.getElementById('positionsContainer');
            
            if (!positions || positions.length === 0) {
                container.innerHTML = '<div class="empty-state"><p>📭 No open positions</p></div>';
                return;
            }

            let html = `
                <table class="positions-table">
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Side</th>
                            <th>Entry Price</th>
                            <th>Current Price</th>
                            <th>Qty</th>
                            <th>P&L</th>
                            <th>Return %</th>
                            <th>Stop Loss</th>
                            <th>Target</th>
                            <th>Time</th>
                            <th>Action</th>
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
                        <td>₹ ${pos.entry_price.toFixed(2)}</td>
                        <td>₹ ${pos.current_price.toFixed(2)}</td>
                        <td>${pos.quantity}</td>
                        <td class="${pnlClass}">₹ ${pos.pnl.toFixed(2)}</td>
                        <td class="${pnlClass}">${pos.pnl_percent.toFixed(2)}%</td>
                        <td>₹ ${pos.stop_loss.toFixed(2)}</td>
                        <td>₹ ${pos.target_1.toFixed(2)}</td>
                        <td>${durationMin}m</td>
                        <td><button class="exit-btn" onclick="exitTrade('${pos.trade_id}')">EXIT</button></td>
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
                alert(`✅ ${data.message || data.status}`);
            } catch (error) {
                alert(`❌ Error: ${error.message}`);
            }
        }

        function startBot() {
            apiCall('/api/commands/start', 'POST');
        }

        function stopBot() {
            if (confirm('⚠️ Stop the bot and close all positions?')) {
                apiCall('/api/commands/stop', 'POST');
            }
        }

        function pauseBot() {
            apiCall('/api/commands/pause', 'POST');
        }

        function emergencyStop() {
            if (confirm('🚨 EMERGENCY STOP - This will close ALL positions immediately! Continue?')) {
                apiCall('/api/commands/emergency_stop', 'POST');
            }
        }

        function exitTrade(tradeId) {
            if (confirm('Exit this trade?')) {
                apiCall(`/api/commands/exit/${tradeId}`, 'POST');
            }
        }

        // Initialize
        window.addEventListener('DOMContentLoaded', () => {
            connectWebSocket();
            setInterval(() => {
                if (ws.readyState !== WebSocket.OPEN) {
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
