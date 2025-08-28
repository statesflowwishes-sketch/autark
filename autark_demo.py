#!/usr/bin/env python3
"""
AUTARK SYSTEM MINIMAL DEMO
==========================

Minimale Version des AUTARK Systems ohne externe Dependencies
für sofortige Demonstration der Pipeline-Funktionalität.

Author: AUTARK SYSTEM
Version: DEMO-1.0
"""

import os
import sys
import time
import json
import sqlite3
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import subprocess

class AutarkMinimalDemo:
    """
    Minimale AUTARK System Demo mit eingebauten Funktionen
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.db_path = self.base_dir / "autark_demo.db"
        self.repositories = []
        self.system_status = {
            "pipeline_active": False,
            "repositories_processed": 0,
            "agents_active": 0,
            "overlay_status": "running"
        }
        
        # Initialisiere Demo-Datenbank
        self.init_database()
        
        # Lade Demo-Daten
        self.load_demo_data()
    
    def init_database(self):
        """Initialisiere SQLite Demo-Datenbank"""
        print("🔧 Initializing Demo Database...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Erstelle Tabellen
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS repositories (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                description TEXT,
                language TEXT,
                stars INTEGER,
                status TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                status TEXT,
                tasks_completed INTEGER DEFAULT 0,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pipeline_metrics (
                id INTEGER PRIMARY KEY,
                metric_name TEXT,
                metric_value TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Demo Database initialized")
    
    def load_demo_data(self):
        """Lade Demo-Daten für Repositories und Agents"""
        print("📦 Loading Demo Data...")
        
        # Demo Repositories
        demo_repos = [
            ("tensorflow/tensorflow", "ML/AI", "Machine Learning Library", "Python", 185000, "processed"),
            ("microsoft/vscode", "Tools", "Code Editor", "TypeScript", 163000, "processing"),
            ("torvalds/linux", "System", "Operating System Kernel", "C", 178000, "queued"),
            ("facebook/react", "Frontend", "JavaScript Library", "JavaScript", 228000, "processed"),
            ("kubernetes/kubernetes", "DevOps", "Container Orchestration", "Go", 110000, "processing"),
            ("django/django", "Backend", "Web Framework", "Python", 79000, "processed"),
            ("nodejs/node", "Runtime", "JavaScript Runtime", "JavaScript", 107000, "processing"),
            ("microsoft/TypeScript", "Language", "Programming Language", "TypeScript", 100000, "queued"),
            ("angular/angular", "Frontend", "Web Framework", "TypeScript", 96000, "processed"),
            ("vuejs/vue", "Frontend", "Progressive Framework", "JavaScript", 207000, "processing")
        ]
        
        # Demo Agents
        demo_agents = [
            ("Lazy Coding Agent", "lazy", "active", 45),
            ("Vibing Agent", "vibing", "active", 32),
            ("RAG Agent", "rag", "active", 67),
            ("Async Coding Agent", "async", "active", 89),
            ("Database Pipeline Agent", "pipeline", "active", 156),
            ("Orchestrator Agent", "orchestrator", "active", 234)
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Lösche alte Daten
        cursor.execute("DELETE FROM repositories")
        cursor.execute("DELETE FROM agents")
        
        # Füge Demo Repositories hinzu
        for repo in demo_repos:
            cursor.execute(
                "INSERT INTO repositories (name, category, description, language, stars, status) VALUES (?, ?, ?, ?, ?, ?)",
                repo
            )
        
        # Füge Demo Agents hinzu
        for agent in demo_agents:
            cursor.execute(
                "INSERT INTO agents (name, type, status, tasks_completed) VALUES (?, ?, ?, ?)",
                agent
            )
        
        conn.commit()
        conn.close()
        print("✅ Demo Data loaded")
    
    def get_system_metrics(self):
        """Hole aktuelle System-Metriken"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Repository-Statistiken
        cursor.execute("SELECT status, COUNT(*) FROM repositories GROUP BY status")
        repo_stats = dict(cursor.fetchall())
        
        # Agent-Statistiken
        cursor.execute("SELECT status, COUNT(*) FROM agents GROUP BY status")
        agent_stats = dict(cursor.fetchall())
        
        # Gesamtstatistiken
        cursor.execute("SELECT COUNT(*) FROM repositories")
        total_repos = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(tasks_completed) FROM agents")
        total_tasks = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "repositories": {
                "total": total_repos,
                "by_status": repo_stats
            },
            "agents": {
                "by_status": agent_stats,
                "total_tasks_completed": total_tasks
            },
            "system": self.system_status
        }
    
    def start_pipeline_simulation(self):
        """Simuliere Pipeline-Aktivität"""
        self.system_status["pipeline_active"] = True
        
        def simulate():
            while self.system_status["pipeline_active"]:
                # Simuliere Repository-Verarbeitung
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Finde ein Repository zum "Verarbeiten"
                cursor.execute("SELECT id FROM repositories WHERE status = 'queued' LIMIT 1")
                result = cursor.fetchone()
                
                if result:
                    repo_id = result[0]
                    cursor.execute(
                        "UPDATE repositories SET status = 'processing' WHERE id = ?",
                        (repo_id,)
                    )
                    conn.commit()
                    
                    # Simuliere Verarbeitungszeit
                    time.sleep(5)
                    
                    cursor.execute(
                        "UPDATE repositories SET status = 'processed' WHERE id = ?",
                        (repo_id,)
                    )
                    conn.commit()
                    
                    self.system_status["repositories_processed"] += 1
                
                conn.close()
                time.sleep(2)
        
        # Starte Simulation in separatem Thread
        thread = threading.Thread(target=simulate, daemon=True)
        thread.start()
        print("🚀 Pipeline simulation started")


class AutarkDemoServer(BaseHTTPRequestHandler):
    """
    HTTP Server für AUTARK Demo Interface
    """
    
    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        
        if path == "/" or path == "/dashboard":
            self.serve_dashboard()
        elif path == "/api/metrics":
            self.serve_metrics()
        elif path == "/api/repositories":
            self.serve_repositories()
        elif path == "/api/agents":
            self.serve_agents()
        elif path == "/start-pipeline":
            self.start_pipeline()
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        """Serve main dashboard"""
        html = self.get_dashboard_html()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_metrics(self):
        """Serve system metrics as JSON"""
        metrics = demo.get_system_metrics()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(metrics).encode())
    
    def serve_repositories(self):
        """Serve repository data"""
        conn = sqlite3.connect(demo.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM repositories ORDER BY stars DESC")
        
        repositories = []
        for row in cursor.fetchall():
            repositories.append({
                "id": row[0], "name": row[1], "category": row[2],
                "description": row[3], "language": row[4], 
                "stars": row[5], "status": row[6]
            })
        
        conn.close()
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(repositories).encode())
    
    def serve_agents(self):
        """Serve agent data"""
        conn = sqlite3.connect(demo.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agents ORDER BY tasks_completed DESC")
        
        agents = []
        for row in cursor.fetchall():
            agents.append({
                "id": row[0], "name": row[1], "type": row[2],
                "status": row[3], "tasks_completed": row[4]
            })
        
        conn.close()
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(agents).encode())
    
    def start_pipeline(self):
        """Start pipeline simulation"""
        demo.start_pipeline_simulation()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "Pipeline started"}).encode())
    
    def get_dashboard_html(self):
        """Generate dashboard HTML"""
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>AUTARK System Demo Dashboard</title>
    <meta charset="UTF-8">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
            color: #00ff41;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .header {
            background: rgba(0, 255, 65, 0.1);
            border-bottom: 2px solid #00ff41;
            padding: 20px;
            text-align: center;
            position: relative;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, transparent, #00ff41, transparent);
            opacity: 0.1;
            animation: scan 3s linear infinite;
        }
        
        @keyframes scan {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        .header h1 {
            font-size: 2.5em;
            text-shadow: 0 0 20px #00ff41;
            letter-spacing: 3px;
        }
        
        .header p {
            margin-top: 10px;
            font-size: 1.2em;
            opacity: 0.8;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .panel {
            background: rgba(0, 255, 65, 0.05);
            border: 1px solid #00ff41;
            border-radius: 10px;
            padding: 20px;
            position: relative;
            overflow: hidden;
        }
        
        .panel::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #00ff41, transparent, #00ff41);
            border-radius: 12px;
            z-index: -1;
            opacity: 0.3;
        }
        
        .panel h2 {
            color: #00ff41;
            margin-bottom: 15px;
            font-size: 1.5em;
            text-shadow: 0 0 10px #00ff41;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 10px;
            background: rgba(0, 255, 65, 0.1);
            border-radius: 5px;
        }
        
        .metric-value {
            color: #00ff41;
            font-weight: bold;
        }
        
        .repository-list, .agent-list {
            max-height: 300px;
            overflow-y: auto;
            margin-top: 10px;
        }
        
        .repository-item, .agent-item {
            padding: 10px;
            margin: 5px 0;
            background: rgba(0, 255, 65, 0.1);
            border-radius: 5px;
            border-left: 3px solid #00ff41;
        }
        
        .status-active { border-left-color: #00ff41; }
        .status-processing { border-left-color: #ffff00; }
        .status-queued { border-left-color: #ff6600; }
        .status-processed { border-left-color: #00ff41; }
        
        .button {
            background: linear-gradient(45deg, #00ff41, #00cc33);
            color: #000;
            border: none;
            padding: 15px 30px;
            border-radius: 5px;
            cursor: pointer;
            font-family: inherit;
            font-weight: bold;
            text-transform: uppercase;
            margin: 10px 5px;
            transition: all 0.3s;
        }
        
        .button:hover {
            box-shadow: 0 0 20px #00ff41;
            transform: translateY(-2px);
        }
        
        .controls {
            text-align: center;
            margin: 20px 0;
        }
        
        .blink {
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0.3; }
        }
        
        .scroll-text {
            background: #000;
            color: #00ff41;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            overflow: hidden;
            white-space: nowrap;
        }
        
        .scroll-text span {
            display: inline-block;
            animation: scroll 15s linear infinite;
        }
        
        @keyframes scroll {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 AUTARK SYSTEM DEMO</h1>
        <p>Complete Pipeline • Database Integration • Specialized Agents • Original Overlay</p>
        <div class="scroll-text">
            <span>⚡ 300+ Repositories Integrated • 🤖 6 Specialized Agents Active • 📊 Real-time Monitoring • 🔄 Pipeline Processing • 🎯 System Orchestration</span>
        </div>
    </div>
    
    <div class="controls">
        <button class="button" onclick="startPipeline()">🚀 Start Pipeline</button>
        <button class="button" onclick="refreshData()">🔄 Refresh Data</button>
        <button class="button" onclick="showLogs()">📊 Show Logs</button>
    </div>
    
    <div class="dashboard">
        <div class="panel">
            <h2>📊 System Metrics</h2>
            <div id="system-metrics">
                <div class="metric">
                    <span>Pipeline Status:</span>
                    <span class="metric-value blink" id="pipeline-status">ACTIVE</span>
                </div>
                <div class="metric">
                    <span>Repositories Processed:</span>
                    <span class="metric-value" id="repos-processed">0</span>
                </div>
                <div class="metric">
                    <span>Active Agents:</span>
                    <span class="metric-value" id="active-agents">6</span>
                </div>
                <div class="metric">
                    <span>Total Tasks Completed:</span>
                    <span class="metric-value" id="total-tasks">0</span>
                </div>
            </div>
        </div>
        
        <div class="panel">
            <h2>🗄️ Repository Status</h2>
            <div id="repository-stats">
                <div class="metric">
                    <span>Total Repositories:</span>
                    <span class="metric-value" id="total-repos">0</span>
                </div>
                <div class="metric">
                    <span>Processing:</span>
                    <span class="metric-value" id="repos-processing">0</span>
                </div>
                <div class="metric">
                    <span>Completed:</span>
                    <span class="metric-value" id="repos-completed">0</span>
                </div>
                <div class="metric">
                    <span>Queued:</span>
                    <span class="metric-value" id="repos-queued">0</span>
                </div>
            </div>
        </div>
        
        <div class="panel">
            <h2>🗃️ Repositories</h2>
            <div class="repository-list" id="repository-list">
                Loading repositories...
            </div>
        </div>
        
        <div class="panel">
            <h2>🤖 Specialized Agents</h2>
            <div class="agent-list" id="agent-list">
                Loading agents...
            </div>
        </div>
        
        <div class="panel">
            <h2>📈 Pipeline Activity</h2>
            <div id="pipeline-activity">
                <div class="metric">
                    <span>Database Connections:</span>
                    <span class="metric-value">5/5 Active</span>
                </div>
                <div class="metric">
                    <span>Processing Queue:</span>
                    <span class="metric-value" id="queue-size">3</span>
                </div>
                <div class="metric">
                    <span>System Load:</span>
                    <span class="metric-value">Normal</span>
                </div>
                <div class="metric">
                    <span>Uptime:</span>
                    <span class="metric-value" id="uptime">00:00:00</span>
                </div>
            </div>
        </div>
        
        <div class="panel">
            <h2>🎯 Original Overlay</h2>
            <div id="overlay-status">
                <div class="metric">
                    <span>Overlay Status:</span>
                    <span class="metric-value">🟢 Online</span>
                </div>
                <div class="metric">
                    <span>Real-time Updates:</span>
                    <span class="metric-value blink">🔄 Active</span>
                </div>
                <div class="metric">
                    <span>Connected Clients:</span>
                    <span class="metric-value">1</span>
                </div>
                <div class="metric">
                    <span>Data Sync:</span>
                    <span class="metric-value">✅ Synchronized</span>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let startTime = Date.now();
        
        function updateUptime() {
            const elapsed = Date.now() - startTime;
            const hours = Math.floor(elapsed / 3600000).toString().padStart(2, '0');
            const minutes = Math.floor((elapsed % 3600000) / 60000).toString().padStart(2, '0');
            const seconds = Math.floor((elapsed % 60000) / 1000).toString().padStart(2, '0');
            document.getElementById('uptime').textContent = `${hours}:${minutes}:${seconds}`;
        }
        
        function loadMetrics() {
            fetch('/api/metrics')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-repos').textContent = data.repositories.total;
                    document.getElementById('repos-processing').textContent = data.repositories.by_status.processing || 0;
                    document.getElementById('repos-completed').textContent = data.repositories.by_status.processed || 0;
                    document.getElementById('repos-queued').textContent = data.repositories.by_status.queued || 0;
                    document.getElementById('repos-processed').textContent = data.system.repositories_processed;
                    document.getElementById('total-tasks').textContent = data.agents.total_tasks_completed;
                    document.getElementById('active-agents').textContent = Object.values(data.agents.by_status).reduce((a, b) => a + b, 0);
                });
        }
        
        function loadRepositories() {
            fetch('/api/repositories')
                .then(response => response.json())
                .then(data => {
                    const list = document.getElementById('repository-list');
                    list.innerHTML = data.map(repo => 
                        `<div class="repository-item status-${repo.status}">
                            <strong>${repo.name}</strong> (${repo.language})<br>
                            <small>${repo.description}</small><br>
                            ⭐ ${repo.stars.toLocaleString()} • Status: ${repo.status}
                        </div>`
                    ).join('');
                });
        }
        
        function loadAgents() {
            fetch('/api/agents')
                .then(response => response.json())
                .then(data => {
                    const list = document.getElementById('agent-list');
                    list.innerHTML = data.map(agent => 
                        `<div class="agent-item status-${agent.status}">
                            <strong>${agent.name}</strong><br>
                            Type: ${agent.type} • Tasks: ${agent.tasks_completed}<br>
                            Status: <span class="blink">🟢 ${agent.status}</span>
                        </div>`
                    ).join('');
                });
        }
        
        function startPipeline() {
            fetch('/start-pipeline')
                .then(response => response.json())
                .then(data => {
                    alert('Pipeline started! Check the status updates.');
                    loadMetrics();
                });
        }
        
        function refreshData() {
            loadMetrics();
            loadRepositories();
            loadAgents();
        }
        
        function showLogs() {
            alert('📊 System Logs:\\n\\n✅ Database Pipeline: Active\\n🤖 Agents: 6 Running\\n📊 Original Overlay: Online\\n🔄 Real-time Updates: Active\\n⚡ System: Operational');
        }
        
        // Initialize
        loadMetrics();
        loadRepositories();
        loadAgents();
        
        // Auto-refresh every 5 seconds
        setInterval(() => {
            loadMetrics();
            updateUptime();
        }, 5000);
        
        // Update uptime every second
        setInterval(updateUptime, 1000);
    </script>
</body>
</html>
        '''


def main():
    """Main function to run AUTARK Demo"""
    global demo
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                 AUTARK SYSTEM DEMO                       ║
    ║          🚀 Complete Pipeline Demonstration              ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Initialize demo system
    demo = AutarkMinimalDemo()
    
    # Start pipeline simulation
    demo.start_pipeline_simulation()
    
    # Start web server
    server_address = ('localhost', 8888)
    httpd = HTTPServer(server_address, AutarkDemoServer)
    
    print("🌐 AUTARK Demo System started!")
    print("📊 Dashboard: http://localhost:8888")
    print("🔗 API Endpoints:")
    print("   - /api/metrics")
    print("   - /api/repositories") 
    print("   - /api/agents")
    print("\n💡 Press Ctrl+C to stop the demo")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
        httpd.shutdown()


if __name__ == "__main__":
    main()