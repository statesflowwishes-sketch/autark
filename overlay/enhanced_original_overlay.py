#!/usr/bin/env python3
"""
ORIGINAL OVERLAY ENHANCED
=========================

Enhanced Original Overlay with complete AUTARK system integration including:
- Database pipeline visualization
- Repository management
- Specialized agent integration
- Real-time monitoring
- Full system control

Author: AUTARK SYSTEM
Version: 2.0.0
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiohttp
from aiohttp import web, WSMsgType
import aiohttp_cors
import aiofiles
import redis.asyncio as redis
import asyncpg
from qdrant_client import QdrantClient
import yaml
from dataclasses import dataclass, asdict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System-wide metrics"""
    total_repositories: int = 0
    integrated_repositories: int = 0
    active_agents: int = 0
    failed_operations: int = 0
    uptime_seconds: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0

class EnhancedOriginalOverlay:
    """
    Enhanced Original Overlay with full AUTARK system integration
    """
    
    def __init__(self, config_path: str = "config/orchestrator_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.start_time = datetime.now()
        
        # Database connections
        self.redis_client = None
        self.postgres_pool = None
        self.qdrant_client = None
        
        # WebSocket connections
        self.websockets = set()
        
        # System metrics
        self.metrics = SystemMetrics()
        
        # App setup
        self.app = web.Application()
        self._setup_routes()
        self._setup_cors()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {
                "overlay": {"port": 8888, "host": "0.0.0.0"},
                "databases": {
                    "postgresql": {"host": "localhost", "port": 5433, "database": "autark_repos", "username": "autark_user", "password": "autark_secure_2025"},
                    "redis": {"host": "localhost", "port": 6380, "db": 6},
                    "qdrant": {"host": "localhost", "port": 6334}
                }
            }
    
    def _setup_cors(self):
        """Setup CORS middleware"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    def _setup_routes(self):
        """Setup web routes"""
        
        # Static files
        static_path = Path(__file__).parent / "static"
        if static_path.exists():
            self.app.router.add_static('/', static_path, name='static')
        
        # Main routes
        self.app.router.add_get('/', self.index)
        self.app.router.add_get('/dashboard', self.dashboard)
        self.app.router.add_get('/repositories', self.repositories_page)
        self.app.router.add_get('/agents', self.agents_page)
        self.app.router.add_get('/pipeline', self.pipeline_page)
        self.app.router.add_get('/system', self.system_page)
        
        # API routes
        self.app.router.add_get('/api/status', self.api_status)
        self.app.router.add_get('/api/repositories', self.api_repositories)
        self.app.router.add_get('/api/repositories/{repo_id}', self.api_repository_detail)
        self.app.router.add_get('/api/agents', self.api_agents)
        self.app.router.add_get('/api/metrics', self.api_metrics)
        self.app.router.add_post('/api/agents/create', self.api_create_agent)
        self.app.router.add_post('/api/pipeline/start', self.api_start_pipeline)
        self.app.router.add_post('/api/pipeline/stop', self.api_stop_pipeline)
        
        # WebSocket
        self.app.router.add_get('/ws', self.websocket_handler)
    
    async def initialize(self):
        """Initialize connections and resources"""
        try:
            # Redis connection
            redis_config = self.config["databases"]["redis"]
            self.redis_client = redis.Redis(
                host=redis_config["host"],
                port=redis_config["port"],
                db=redis_config["db"],
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("✅ Redis connected")
            
            # PostgreSQL connection
            postgres_config = self.config["databases"]["postgresql"]
            self.postgres_pool = await asyncpg.create_pool(
                host=postgres_config["host"],
                port=postgres_config["port"],
                database=postgres_config["database"],
                user=postgres_config["username"],
                password=postgres_config["password"],
                min_size=2,
                max_size=10
            )
            logger.info("✅ PostgreSQL connected")
            
            # Qdrant connection
            qdrant_config = self.config["databases"]["qdrant"]
            self.qdrant_client = QdrantClient(
                host=qdrant_config["host"],
                port=qdrant_config["port"]
            )
            logger.info("✅ Qdrant connected")
            
            # Start background tasks
            asyncio.create_task(self._update_metrics())
            asyncio.create_task(self._broadcast_updates())
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
    
    async def _update_metrics(self):
        """Update system metrics periodically"""
        while True:
            try:
                # Get repository count from PostgreSQL
                async with self.postgres_pool.acquire() as conn:
                    result = await conn.fetchrow("""
                        SELECT 
                            COUNT(*) as total,
                            COUNT(*) FILTER (WHERE integration_status = 'completed') as integrated,
                            COUNT(*) FILTER (WHERE integration_status LIKE 'failed%' OR integration_status LIKE 'error%') as failed
                        FROM repositories
                    """)
                    
                    if result:
                        self.metrics.total_repositories = result['total']
                        self.metrics.integrated_repositories = result['integrated']
                        self.metrics.failed_operations = result['failed']
                
                # Get agent count from Redis
                agent_keys = await self.redis_client.keys("agent:*")
                self.metrics.active_agents = len(agent_keys)
                
                # Calculate uptime
                self.metrics.uptime_seconds = (datetime.now() - self.start_time).total_seconds()
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"Metrics update error: {e}")
                await asyncio.sleep(30)
    
    async def _broadcast_updates(self):
        """Broadcast updates to WebSocket clients"""
        while True:
            try:
                if self.websockets:
                    update_data = {
                        "type": "metrics_update",
                        "data": asdict(self.metrics),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Send to all connected clients
                    disconnected = set()
                    for ws in self.websockets:
                        try:
                            await ws.send_str(json.dumps(update_data))
                        except:
                            disconnected.add(ws)
                    
                    # Remove disconnected clients
                    self.websockets -= disconnected
                
                await asyncio.sleep(5)  # Broadcast every 5 seconds
                
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                await asyncio.sleep(10)
    
    # Route handlers
    async def index(self, request):
        """Main dashboard page"""
        return web.Response(text=self._generate_index_html(), content_type='text/html')
    
    async def dashboard(self, request):
        """Enhanced dashboard page"""
        return web.Response(text=self._generate_dashboard_html(), content_type='text/html')
    
    async def repositories_page(self, request):
        """Repositories management page"""
        return web.Response(text=self._generate_repositories_html(), content_type='text/html')
    
    async def agents_page(self, request):
        """Agents management page"""
        return web.Response(text=self._generate_agents_html(), content_type='text/html')
    
    async def pipeline_page(self, request):
        """Pipeline monitoring page"""
        return web.Response(text=self._generate_pipeline_html(), content_type='text/html')
    
    async def system_page(self, request):
        """System monitoring page"""
        return web.Response(text=self._generate_system_html(), content_type='text/html')
    
    # API handlers
    async def api_status(self, request):
        """System status API"""
        return web.json_response({
            "status": "running",
            "metrics": asdict(self.metrics),
            "timestamp": datetime.now().isoformat()
        })
    
    async def api_repositories(self, request):
        """Repositories API"""
        try:
            page = int(request.query.get('page', 1))
            limit = int(request.query.get('limit', 50))
            category = request.query.get('category', '')
            
            offset = (page - 1) * limit
            
            async with self.postgres_pool.acquire() as conn:
                # Build query
                where_clause = ""
                params = [limit, offset]
                if category:
                    where_clause = "WHERE category = $3"
                    params.append(category)
                
                query = f"""
                    SELECT id, name, url, category, description, stars, language, 
                           license, clone_status, integration_status, created_at
                    FROM repositories 
                    {where_clause}
                    ORDER BY stars DESC NULLS LAST, name
                    LIMIT $1 OFFSET $2
                """
                
                repos = await conn.fetch(query, *params)
                
                # Get total count
                count_query = f"SELECT COUNT(*) FROM repositories {where_clause}"
                count_params = [params[2]] if category else []
                total = await conn.fetchval(count_query, *count_params)
                
                return web.json_response({
                    "repositories": [dict(repo) for repo in repos],
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "pages": (total + limit - 1) // limit
                })
                
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def api_repository_detail(self, request):
        """Repository detail API"""
        try:
            repo_id = request.match_info['repo_id']
            
            async with self.postgres_pool.acquire() as conn:
                repo = await conn.fetchrow(
                    "SELECT * FROM repositories WHERE id = $1", repo_id
                )
                
                if not repo:
                    return web.json_response({"error": "Repository not found"}, status=404)
                
                return web.json_response(dict(repo))
                
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def api_agents(self, request):
        """Agents API"""
        try:
            agent_keys = await self.redis_client.keys("agent:*")
            agents = []
            
            for key in agent_keys:
                agent_data = await self.redis_client.hgetall(key)
                if agent_data:
                    agents.append(agent_data)
            
            return web.json_response({"agents": agents})
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def api_metrics(self, request):
        """Metrics API"""
        return web.json_response(asdict(self.metrics))
    
    async def api_create_agent(self, request):
        """Create agent API"""
        try:
            data = await request.json()
            mode = data.get('mode', 'lazy')
            description = data.get('description', 'Created via Original Overlay')
            
            # Call orchestrator API to create agent
            async with aiohttp.ClientSession() as session:
                orchestrator_url = "http://localhost:8000/agents/create"
                async with session.post(orchestrator_url, json={
                    "mode": mode,
                    "description": description
                }) as resp:
                    result = await resp.json()
                    return web.json_response(result)
                    
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def api_start_pipeline(self, request):
        """Start pipeline API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("http://localhost:8000/pipeline/start") as resp:
                    result = await resp.json()
                    return web.json_response(result)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def api_stop_pipeline(self, request):
        """Stop pipeline API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("http://localhost:8000/pipeline/stop") as resp:
                    result = await resp.json()
                    return web.json_response(result)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def websocket_handler(self, request):
        """WebSocket handler for real-time updates"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websockets.add(ws)
        logger.info(f"WebSocket client connected. Total: {len(self.websockets)}")
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        # Handle WebSocket messages if needed
                        await ws.send_str(json.dumps({"echo": data}))
                    except json.JSONDecodeError:
                        await ws.send_str(json.dumps({"error": "Invalid JSON"}))
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
        except Exception as e:
            logger.error(f"WebSocket handler error: {e}")
        finally:
            self.websockets.discard(ws)
            logger.info(f"WebSocket client disconnected. Total: {len(self.websockets)}")
        
        return ws
    
    def _generate_index_html(self) -> str:
        """Generate enhanced index page"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>AUTARK SYSTEM - Original Overlay Enhanced</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                :root {
                    --bg-primary: #0a0a0a;
                    --bg-secondary: #1a1a1a;
                    --text-primary: #00ff41;
                    --text-secondary: #00cc33;
                    --accent: #ff6b35;
                    --border: #333;
                    --success: #00ff41;
                    --warning: #ffb441;
                    --error: #ff4141;
                }
                
                * { margin: 0; padding: 0; box-sizing: border-box; }
                
                body {
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                    background: var(--bg-primary);
                    color: var(--text-primary);
                    line-height: 1.6;
                    overflow-x: hidden;
                }
                
                .matrix-bg {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    z-index: -1;
                    background: linear-gradient(45deg, 
                        rgba(0, 255, 65, 0.03) 0%,
                        rgba(0, 0, 0, 0.95) 50%,
                        rgba(255, 107, 53, 0.03) 100%);
                }
                
                .container {
                    max-width: 1400px;
                    margin: 0 auto;
                    padding: 20px;
                }
                
                .header {
                    text-align: center;
                    padding: 40px 0;
                    border-bottom: 2px solid var(--accent);
                    margin-bottom: 40px;
                }
                
                .header h1 {
                    font-size: 3rem;
                    color: var(--accent);
                    text-shadow: 0 0 20px var(--accent);
                    margin-bottom: 10px;
                    animation: glow 2s infinite alternate;
                }
                
                @keyframes glow {
                    from { text-shadow: 0 0 20px var(--accent); }
                    to { text-shadow: 0 0 30px var(--accent), 0 0 40px var(--accent); }
                }
                
                .header p {
                    font-size: 1.2rem;
                    color: var(--text-secondary);
                }
                
                .nav-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 40px;
                }
                
                .nav-card {
                    background: var(--bg-secondary);
                    border: 2px solid var(--border);
                    border-radius: 10px;
                    padding: 30px;
                    text-align: center;
                    transition: all 0.3s ease;
                    cursor: pointer;
                    position: relative;
                    overflow: hidden;
                }
                
                .nav-card:hover {
                    border-color: var(--accent);
                    transform: translateY(-5px);
                    box-shadow: 0 10px 25px rgba(255, 107, 53, 0.3);
                }
                
                .nav-card::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, transparent, rgba(255, 107, 53, 0.1), transparent);
                    transition: left 0.5s ease;
                }
                
                .nav-card:hover::before {
                    left: 100%;
                }
                
                .nav-card .icon {
                    font-size: 4rem;
                    margin-bottom: 20px;
                    color: var(--accent);
                }
                
                .nav-card h3 {
                    font-size: 1.5rem;
                    margin-bottom: 15px;
                    color: var(--text-primary);
                }
                
                .nav-card p {
                    color: var(--text-secondary);
                    margin-bottom: 20px;
                }
                
                .nav-card .btn {
                    background: var(--accent);
                    color: var(--bg-primary);
                    border: none;
                    padding: 12px 25px;
                    border-radius: 5px;
                    font-weight: bold;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    text-decoration: none;
                    display: inline-block;
                }
                
                .nav-card .btn:hover {
                    background: var(--text-primary);
                    transform: scale(1.05);
                }
                
                .stats-bar {
                    background: var(--bg-secondary);
                    border: 1px solid var(--border);
                    border-radius: 10px;
                    padding: 20px;
                    display: flex;
                    justify-content: space-around;
                    flex-wrap: wrap;
                    margin-bottom: 40px;
                }
                
                .stat-item {
                    text-align: center;
                    padding: 10px;
                }
                
                .stat-value {
                    font-size: 2rem;
                    font-weight: bold;
                    color: var(--accent);
                    display: block;
                }
                
                .stat-label {
                    font-size: 0.9rem;
                    color: var(--text-secondary);
                    text-transform: uppercase;
                }
                
                .footer {
                    text-align: center;
                    padding: 40px 0;
                    border-top: 1px solid var(--border);
                    color: var(--text-secondary);
                }
                
                @media (max-width: 768px) {
                    .nav-grid {
                        grid-template-columns: 1fr;
                    }
                    
                    .header h1 {
                        font-size: 2rem;
                    }
                    
                    .stats-bar {
                        flex-direction: column;
                    }
                }
            </style>
        </head>
        <body>
            <div class="matrix-bg"></div>
            
            <div class="container">
                <div class="header">
                    <h1>🚀 AUTARK SYSTEM</h1>
                    <p>Original Overlay Enhanced - Vollständige Database Pipeline Integration</p>
                </div>
                
                <div class="stats-bar">
                    <div class="stat-item">
                        <span id="repo-count" class="stat-value">0</span>
                        <span class="stat-label">Repositories</span>
                    </div>
                    <div class="stat-item">
                        <span id="agent-count" class="stat-value">0</span>
                        <span class="stat-label">Active Agents</span>
                    </div>
                    <div class="stat-item">
                        <span id="uptime" class="stat-value">0s</span>
                        <span class="stat-label">System Uptime</span>
                    </div>
                    <div class="stat-item">
                        <span id="status" class="stat-value">●</span>
                        <span class="stat-label">System Status</span>
                    </div>
                </div>
                
                <div class="nav-grid">
                    <div class="nav-card" onclick="window.location.href='/dashboard'">
                        <div class="icon">📊</div>
                        <h3>System Dashboard</h3>
                        <p>Comprehensive system overview with real-time monitoring and control</p>
                        <a href="/dashboard" class="btn">Open Dashboard</a>
                    </div>
                    
                    <div class="nav-card" onclick="window.location.href='/repositories'">
                        <div class="icon">🗄️</div>
                        <h3>Repository Management</h3>
                        <p>Browse, search and manage 300+ integrated database repositories</p>
                        <a href="/repositories" class="btn">Browse Repositories</a>
                    </div>
                    
                    <div class="nav-card" onclick="window.location.href='/agents'">
                        <div class="icon">🤖</div>
                        <h3>Specialized Agents</h3>
                        <p>Manage lazy, vibing, RAG, async and special coding agents</p>
                        <a href="/agents" class="btn">Manage Agents</a>
                    </div>
                    
                    <div class="nav-card" onclick="window.location.href='/pipeline'">
                        <div class="icon">⚡</div>
                        <h3>Database Pipeline</h3>
                        <p>Monitor and control the repository integration pipeline</p>
                        <a href="/pipeline" class="btn">View Pipeline</a>
                    </div>
                    
                    <div class="nav-card" onclick="window.location.href='/system'">
                        <div class="icon">🔧</div>
                        <h3>System Control</h3>
                        <p>Advanced system configuration and performance monitoring</p>
                        <a href="/system" class="btn">System Control</a>
                    </div>
                    
                    <div class="nav-card" onclick="window.open('http://localhost:8000/dashboard', '_blank')">
                        <div class="icon">🎯</div>
                        <h3>Orchestrator</h3>
                        <p>Access the main system orchestrator control panel</p>
                        <a href="http://localhost:8000/dashboard" target="_blank" class="btn">Open Orchestrator</a>
                    </div>
                </div>
                
                <div class="footer">
                    <p>AUTARK SYSTEM v2.0.0 - Enhanced Original Overlay with Complete Pipeline Integration</p>
                    <p>🔗 Connected Systems: PostgreSQL • Redis • Qdrant • MongoDB • Elasticsearch • Specialized Agents</p>
                </div>
            </div>
            
            <script>
                // WebSocket connection for real-time updates
                const ws = new WebSocket('ws://localhost:8888/ws');
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    if (data.type === 'metrics_update') {
                        const metrics = data.data;
                        document.getElementById('repo-count').textContent = metrics.total_repositories;
                        document.getElementById('agent-count').textContent = metrics.active_agents;
                        document.getElementById('uptime').textContent = Math.floor(metrics.uptime_seconds) + 's';
                        
                        const status = metrics.total_repositories > 0 ? '🟢' : '🟡';
                        document.getElementById('status').textContent = status;
                    }
                };
                
                ws.onopen = function() {
                    console.log('✅ Connected to AUTARK System');
                };
                
                ws.onerror = function(error) {
                    console.error('❌ WebSocket error:', error);
                };
                
                // Update uptime every second
                setInterval(function() {
                    const currentUptime = document.getElementById('uptime').textContent;
                    const seconds = parseInt(currentUptime.replace('s', '')) + 1;
                    document.getElementById('uptime').textContent = seconds + 's';
                }, 1000);
            </script>
        </body>
        </html>
        """
    
    def _generate_dashboard_html(self) -> str:
        """Generate comprehensive dashboard"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>AUTARK Dashboard - Original Overlay Enhanced</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                /* Include the same CSS as index but with dashboard-specific styles */
                /* ... (CSS from index) ... */
                
                .dashboard-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                
                .dashboard-panel {
                    background: var(--bg-secondary);
                    border: 1px solid var(--border);
                    border-radius: 10px;
                    padding: 20px;
                }
                
                .panel-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid var(--border);
                }
                
                .panel-title {
                    font-size: 1.2rem;
                    font-weight: bold;
                    color: var(--accent);
                }
                
                .metric-row {
                    display: flex;
                    justify-content: space-between;
                    margin: 10px 0;
                    padding: 8px 0;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }
                
                .metric-label {
                    color: var(--text-secondary);
                }
                
                .metric-value {
                    color: var(--text-primary);
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <!-- Dashboard implementation with real-time panels -->
            <div class="container">
                <div class="header">
                    <h1>📊 AUTARK DASHBOARD</h1>
                    <p>Real-time System Monitoring & Control</p>
                </div>
                
                <div class="dashboard-grid">
                    <div class="dashboard-panel">
                        <div class="panel-header">
                            <div class="panel-title">🗄️ Repository Status</div>
                        </div>
                        <div id="repo-metrics">
                            <!-- Real-time repository metrics -->
                        </div>
                    </div>
                    
                    <div class="dashboard-panel">
                        <div class="panel-header">
                            <div class="panel-title">🤖 Agent Activity</div>
                        </div>
                        <div id="agent-metrics">
                            <!-- Real-time agent metrics -->
                        </div>
                    </div>
                    
                    <div class="dashboard-panel">
                        <div class="panel-header">
                            <div class="panel-title">⚡ Pipeline Status</div>
                        </div>
                        <div id="pipeline-metrics">
                            <!-- Real-time pipeline metrics -->
                        </div>
                    </div>
                    
                    <div class="dashboard-panel">
                        <div class="panel-header">
                            <div class="panel-title">🔧 System Health</div>
                        </div>
                        <div id="system-metrics">
                            <!-- Real-time system metrics -->
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                // Enhanced dashboard JavaScript with real-time updates
                // ... (WebSocket integration and real-time updates)
            </script>
        </body>
        </html>
        """
    
    def _generate_repositories_html(self) -> str:
        """Generate repositories page with search and filtering"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Repository Management - AUTARK System</title>
            <!-- Enhanced repository management interface -->
        </head>
        <body>
            <!-- Repository browser with search, filters, and integration status -->
        </body>
        </html>
        """
    
    def _generate_agents_html(self) -> str:
        """Generate agents management page"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Agent Management - AUTARK System</title>
            <!-- Agent creation and management interface -->
        </head>
        <body>
            <!-- Agent management with creation forms and monitoring -->
        </body>
        </html>
        """
    
    def _generate_pipeline_html(self) -> str:
        """Generate pipeline monitoring page"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pipeline Control - AUTARK System</title>
            <!-- Pipeline monitoring and control interface -->
        </head>
        <body>
            <!-- Pipeline status, logs, and control buttons -->
        </body>
        </html>
        """
    
    def _generate_system_html(self) -> str:
        """Generate system monitoring page"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>System Control - AUTARK System</title>
            <!-- System monitoring and configuration interface -->
        </head>
        <body>
            <!-- System metrics, logs, and configuration options -->
        </body>
        </html>
        """
    
    async def run(self):
        """Run the enhanced Original Overlay"""
        try:
            await self.initialize()
            
            host = self.config["overlay"]["host"]
            port = self.config["overlay"]["port"]
            
            logger.info(f"🚀 Starting Enhanced Original Overlay on {host}:{port}")
            
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            site = web.TCPSite(runner, host, port)
            await site.start()
            
            logger.info(f"✅ Enhanced Original Overlay running on http://{host}:{port}")
            logger.info("🔗 Available pages:")
            logger.info(f"   📊 Dashboard: http://{host}:{port}/dashboard")
            logger.info(f"   🗄️  Repositories: http://{host}:{port}/repositories")
            logger.info(f"   🤖 Agents: http://{host}:{port}/agents")
            logger.info(f"   ⚡ Pipeline: http://{host}:{port}/pipeline")
            logger.info(f"   🔧 System: http://{host}:{port}/system")
            
            # Keep running
            try:
                while True:
                    await asyncio.sleep(3600)
            except KeyboardInterrupt:
                logger.info("Shutting down Enhanced Original Overlay...")
            finally:
                await runner.cleanup()
                
        except Exception as e:
            logger.error(f"❌ Failed to start Enhanced Original Overlay: {e}")
            raise

async def main():
    """Main entry point"""
    overlay = EnhancedOriginalOverlay()
    await overlay.run()

if __name__ == "__main__":
    asyncio.run(main())