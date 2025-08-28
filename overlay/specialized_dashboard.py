#!/usr/bin/env python3
"""
Original Overlay Dashboard Erweiterung für spezialisierte Coding-Agenten
Erweitert das bestehende dashboard.html um Specialized Coding Agent Controls
"""

import asyncio
import json
import aiohttp
from aiohttp import web
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SpecializedCodingDashboard:
    """Dashboard Extension für spezialisierte Coding-Agenten"""
    
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup API Routes für Dashboard"""
        self.app.router.add_get('/api/specialized/agents', self.get_agents)
        self.app.router.add_post('/api/specialized/create', self.create_agent)
        self.app.router.add_get('/api/specialized/status/{session_id}', self.get_agent_status)
        self.app.router.add_post('/api/specialized/continue/{session_id}', self.continue_agent)
        self.app.router.add_delete('/api/specialized/terminate/{session_id}', self.terminate_agent)
        self.app.router.add_get('/api/specialized/metrics', self.get_metrics)
        self.app.router.add_get('/specialized/dashboard', self.dashboard_page)
        
        # CORS für Frontend
        self.app.middlewares.append(self.cors_middleware)
    
    async def cors_middleware(self, request, handler):
        """CORS Middleware"""
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    async def get_agents(self, request):
        """API: Liste aller aktiven Agenten"""
        try:
            agents = await self.agent_manager.list_active_agents()
            return web.json_response({
                "success": True,
                "agents": agents,
                "count": len(agents)
            })
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def create_agent(self, request):
        """API: Neuen Agenten erstellen"""
        try:
            data = await request.json()
            mode = data.get('mode', 'auto')
            task = data.get('task', '')
            priority = data.get('priority', 1)
            
            if not task:
                return web.json_response({
                    "success": False,
                    "error": "Task description required"
                }, status=400)
            
            session_id = await self.agent_manager.create_agent(mode, task, priority)
            
            return web.json_response({
                "success": True,
                "session_id": session_id,
                "mode": mode,
                "task": task
            })
            
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def get_agent_status(self, request):
        """API: Status eines Agenten"""
        try:
            session_id = request.match_info['session_id']
            status = await self.agent_manager.get_agent_status(session_id)
            
            if "error" in status:
                return web.json_response({
                    "success": False,
                    "error": status["error"]
                }, status=404)
            
            return web.json_response({
                "success": True,
                "status": status
            })
            
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def continue_agent(self, request):
        """API: Agent Session fortsetzen"""
        try:
            session_id = request.match_info['session_id']
            data = await request.json()
            additional_request = data.get('request', '')
            
            if not additional_request:
                return web.json_response({
                    "success": False,
                    "error": "Additional request required"
                }, status=400)
            
            result = await self.agent_manager.agent_factory.continue_session(
                session_id, additional_request
            )
            
            return web.json_response({
                "success": True,
                "result": result
            })
            
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def terminate_agent(self, request):
        """API: Agent beenden"""
        try:
            session_id = request.match_info['session_id']
            result = await self.agent_manager.agent_factory.terminate_session(session_id)
            
            return web.json_response({
                "success": True,
                "result": result
            })
            
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def get_metrics(self, request):
        """API: Performance Metriken"""
        try:
            metrics = self.agent_manager.get_performance_metrics()
            return web.json_response({
                "success": True,
                "metrics": metrics
            })
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def dashboard_page(self, request):
        """Specialized Coding Dashboard HTML"""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AUTARK Specialized Coding Agents</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            font-family: 'Consolas', monospace;
            color: #00ff00;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .dashboard-container {
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            border: 2px solid #00ff00;
            border-radius: 10px;
            background: rgba(0, 255, 0, 0.1);
        }
        
        .title {
            font-size: 2.5em;
            text-shadow: 0 0 20px #00ff00;
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from { text-shadow: 0 0 20px #00ff00; }
            to { text-shadow: 0 0 30px #00ff00, 0 0 40px #00ff00; }
        }
        
        .control-panel {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .create-agent {
            padding: 20px;
            border: 1px solid #00ff00;
            border-radius: 8px;
            background: rgba(0, 255, 0, 0.05);
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            color: #00ff00;
        }
        
        select, input, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #00ff00;
            background: rgba(0, 0, 0, 0.7);
            color: #00ff00;
            border-radius: 4px;
        }
        
        button {
            background: linear-gradient(45deg, #00ff00, #00cc00);
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 15px #00ff00;
        }
        
        .agents-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .agent-card {
            border: 1px solid #00ff00;
            border-radius: 8px;
            padding: 20px;
            background: rgba(0, 255, 0, 0.05);
            position: relative;
            overflow: hidden;
        }
        
        .agent-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, #00ff00, transparent);
            animation: scan 3s linear infinite;
        }
        
        @keyframes scan {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        .agent-mode {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .mode-lazy { background: #ff6b00; color: #000; }
        .mode-vibing { background: #ff0080; color: #fff; }
        .mode-rag { background: #0080ff; color: #fff; }
        .mode-async { background: #8000ff; color: #fff; }
        .mode-special { background: #ffff00; color: #000; }
        
        .agent-actions {
            margin-top: 15px;
        }
        
        .agent-actions button {
            margin-right: 10px;
            margin-bottom: 5px;
            padding: 5px 10px;
            font-size: 0.8em;
        }
        
        .metrics-panel {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .metric-card {
            text-align: center;
            padding: 20px;
            border: 1px solid #00ff00;
            border-radius: 8px;
            background: rgba(0, 255, 0, 0.05);
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #00ff00;
        }
        
        .metric-label {
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        
        .status-active { background: #00ff00; animation: pulse 1s infinite; }
        .status-idle { background: #ffff00; }
        .status-error { background: #ff0000; }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .log-output {
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #00ff00;
            border-radius: 4px;
            padding: 10px;
            max-height: 200px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.8em;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header">
            <h1 class="title">🤖 AUTARK SPECIALIZED CODING AGENTS</h1>
            <p>Advanced AI-Powered Development Modes | CodeLLM CLI Integration</p>
        </div>
        
        <div class="control-panel">
            <div class="create-agent">
                <h3>🚀 Create Specialized Agent</h3>
                <form id="createAgentForm">
                    <div class="form-group">
                        <label for="mode">Coding Mode:</label>
                        <select id="mode" name="mode">
                            <option value="auto">🎯 Auto (Smart Detection)</option>
                            <option value="lazy">🦥 Lazy (Productive Faulheit)</option>
                            <option value="vibing">🌊 Vibing (Flow State)</option>
                            <option value="rag">🧠 RAG (Context-Aware)</option>
                            <option value="async">⚡ Async (Concurrent)</option>
                            <option value="special">⭐ Special (Domain Expert)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="task">Task Description:</label>
                        <textarea id="task" name="task" rows="3" placeholder="Describe your coding task..."></textarea>
                    </div>
                    <div class="form-group">
                        <label for="priority">Priority (1-10):</label>
                        <input type="number" id="priority" name="priority" min="1" max="10" value="5">
                    </div>
                    <button type="submit">Create Agent</button>
                </form>
            </div>
            
            <div class="create-agent">
                <h3>📊 System Status</h3>
                <div id="systemStatus">
                    <div class="status-indicator status-active"></div> AUTARK System: Active<br>
                    <div class="status-indicator status-active"></div> CodeLLM CLI: Connected<br>
                    <div class="status-indicator status-active"></div> Original Overlay: Running<br>
                    <div class="status-indicator status-active"></div> Database Cluster: Healthy<br>
                </div>
                <div class="log-output" id="systemLog">
                    [INFO] AUTARK Specialized Agents ready<br>
                    [INFO] All database connections established<br>
                    [INFO] CodeLLM CLI integration active<br>
                    [INFO] Waiting for agent creation requests...
                </div>
            </div>
        </div>
        
        <div id="activeAgents">
            <h3>🔧 Active Specialized Agents</h3>
            <div class="agents-grid" id="agentsGrid">
                <!-- Agents will be populated here -->
            </div>
        </div>
        
        <div class="metrics-panel" id="metricsPanel">
            <div class="metric-card">
                <div class="metric-value" id="totalSessions">0</div>
                <div class="metric-label">Total Sessions</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="activeAgents">0</div>
                <div class="metric-label">Active Agents</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="mostUsedMode">-</div>
                <div class="metric-label">Most Used Mode</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="avgDuration">0s</div>
                <div class="metric-label">Avg Duration</div>
            </div>
        </div>
    </div>
    
    <script>
        // Dashboard JavaScript functionality
        let agents = [];
        let metrics = {};
        
        // Create Agent Form Handler
        document.getElementById('createAgentForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = {
                mode: formData.get('mode'),
                task: formData.get('task'),
                priority: parseInt(formData.get('priority'))
            };
            
            try {
                const response = await fetch('/api/specialized/create', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    logMessage(`Agent created: ${result.session_id} (${result.mode})`);
                    loadAgents();
                    e.target.reset();
                } else {
                    logMessage(`Error: ${result.error}`, 'error');
                }
            } catch (error) {
                logMessage(`Network error: ${error.message}`, 'error');
            }
        });
        
        // Load and display agents
        async function loadAgents() {
            try {
                const response = await fetch('/api/specialized/agents');
                const result = await response.json();
                
                if (result.success) {
                    agents = result.agents;
                    renderAgents();
                }
            } catch (error) {
                console.error('Failed to load agents:', error);
            }
        }
        
        // Render agents grid
        function renderAgents() {
            const grid = document.getElementById('agentsGrid');
            
            if (agents.length === 0) {
                grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; opacity: 0.6;">No active agents</p>';
                return;
            }
            
            grid.innerHTML = agents.map(agent => `
                <div class="agent-card">
                    <div class="agent-mode mode-${agent.mode}">${agent.mode.toUpperCase()}</div>
                    <h4>Session: ${agent.session_id}</h4>
                    <p><strong>Duration:</strong> ${agent.status.duration_seconds.toFixed(1)}s</p>
                    <p><strong>Domain:</strong> ${agent.status.context.domain}</p>
                    <p><strong>Complexity:</strong> ${agent.status.context.estimated_complexity}</p>
                    
                    <div class="agent-actions">
                        <button onclick="continueAgent('${agent.session_id}')">Continue</button>
                        <button onclick="viewStatus('${agent.session_id}')">Status</button>
                        <button onclick="terminateAgent('${agent.session_id}')" style="background: #ff4444;">Terminate</button>
                    </div>
                </div>
            `).join('');
        }
        
        // Agent action handlers
        async function continueAgent(sessionId) {
            const request = prompt('Enter additional request:');
            if (!request) return;
            
            try {
                const response = await fetch(`/api/specialized/continue/${sessionId}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({request})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    logMessage(`Agent ${sessionId} continued with: ${request}`);
                    loadAgents();
                } else {
                    logMessage(`Error: ${result.error}`, 'error');
                }
            } catch (error) {
                logMessage(`Network error: ${error.message}`, 'error');
            }
        }
        
        async function viewStatus(sessionId) {
            try {
                const response = await fetch(`/api/specialized/status/${sessionId}`);
                const result = await response.json();
                
                if (result.success) {
                    alert(JSON.stringify(result.status, null, 2));
                } else {
                    alert(`Error: ${result.error}`);
                }
            } catch (error) {
                alert(`Network error: ${error.message}`);
            }
        }
        
        async function terminateAgent(sessionId) {
            if (!confirm(`Terminate agent ${sessionId}?`)) return;
            
            try {
                const response = await fetch(`/api/specialized/terminate/${sessionId}`, {
                    method: 'DELETE'
                });
                
                const result = await response.json();
                
                if (result.success) {
                    logMessage(`Agent ${sessionId} terminated`);
                    loadAgents();
                } else {
                    logMessage(`Error: ${result.error}`, 'error');
                }
            } catch (error) {
                logMessage(`Network error: ${error.message}`, 'error');
            }
        }
        
        // Load metrics
        async function loadMetrics() {
            try {
                const response = await fetch('/api/specialized/metrics');
                const result = await response.json();
                
                if (result.success) {
                    updateMetrics(result.metrics);
                }
            } catch (error) {
                console.error('Failed to load metrics:', error);
            }
        }
        
        // Update metrics display
        function updateMetrics(metricsData) {
            document.getElementById('totalSessions').textContent = metricsData.total_sessions || 0;
            document.getElementById('activeAgents').textContent = agents.length;
            
            const modeUsage = metricsData.mode_usage || {};
            const mostUsed = Object.keys(modeUsage).reduce((a, b) => 
                modeUsage[a] > modeUsage[b] ? a : b, 'none');
            document.getElementById('mostUsedMode').textContent = mostUsed;
        }
        
        // Log messages
        function logMessage(message, type = 'info') {
            const log = document.getElementById('systemLog');
            const timestamp = new Date().toLocaleTimeString();
            const prefix = type === 'error' ? '[ERROR]' : '[INFO]';
            
            log.innerHTML += `<br>${timestamp} ${prefix} ${message}`;
            log.scrollTop = log.scrollHeight;
        }
        
        // Auto-refresh
        setInterval(() => {
            loadAgents();
            loadMetrics();
        }, 5000);
        
        // Initial load
        loadAgents();
        loadMetrics();
    </script>
</body>
</html>
        """
        
        return web.Response(text=html_content, content_type='text/html')


# Integration in bestehende Overlay
async def extend_overlay_dashboard(agent_manager, port=8889):
    """Startet erweiterte Dashboard auf separatem Port"""
    
    dashboard = SpecializedCodingDashboard(agent_manager)
    
    runner = web.AppRunner(dashboard.app)
    await runner.setup()
    
    site = web.TCPSite(runner, 'localhost', port)
    await site.start()
    
    logger.info(f"Specialized Coding Dashboard started on http://localhost:{port}")
    logger.info("Dashboard paths:")
    logger.info(f"  - Main: http://localhost:{port}/specialized/dashboard")
    logger.info(f"  - API:  http://localhost:{port}/api/specialized/*")
    
    return runner


if __name__ == "__main__":
    # Standalone test
    async def test_dashboard():
        from agents.autark_coding_integration import specialized_agent_manager
        
        # Initialize manager
        await specialized_agent_manager.initialize(None)
        
        # Start dashboard
        runner = await extend_overlay_dashboard(specialized_agent_manager)
        
        print("Dashboard running on http://localhost:8889/specialized/dashboard")
        print("Press Ctrl+C to stop")
        
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            await runner.cleanup()
    
    asyncio.run(test_dashboard())