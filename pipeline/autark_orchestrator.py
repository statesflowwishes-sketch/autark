#!/usr/bin/env python3
"""
AUTARK SYSTEM PIPELINE ORCHESTRATOR
===================================

Orchestrates the complete AUTARK system with database pipeline integration,
specialized coding agents, and Original Overlay dashboard coordination.

Features:
- Database pipeline orchestration
- Specialized agent coordination
- Original Overlay integration
- Resource management
- Full system automation

Author: AUTARK SYSTEM
Version: 1.0.0
"""

import asyncio
import json
import logging
import os
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import yaml
import subprocess
from dataclasses import dataclass, asdict
import aiohttp
import uvicorn
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis

# Import our modules
sys.path.append(str(Path(__file__).parent.parent))
from agents.autark_coding_integration import AutarkSpecializedAgentManager
from pipeline.autark_database_pipeline import AutarkDatabasePipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SystemStatus:
    """System-wide status information"""
    database_pipeline: str = "stopped"
    specialized_agents: str = "stopped"
    original_overlay: str = "stopped"
    redis_status: str = "disconnected"
    postgres_status: str = "disconnected"
    qdrant_status: str = "disconnected"
    mongodb_status: str = "disconnected"
    elasticsearch_status: str = "disconnected"
    total_repositories: int = 0
    active_agents: int = 0
    system_uptime: float = 0.0


class AutarkSystemOrchestrator:
    """
    Main orchestrator for the complete AUTARK system
    """
    
    def __init__(self, config_path: str = "config/orchestrator_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.start_time = datetime.now()
        self.status = SystemStatus()
        
        # Components
        self.database_pipeline = None
        self.agent_manager = None
        self.web_server = None
        self.redis_client = None
        
        # FastAPI app for Original Overlay
        self.app = FastAPI(title="AUTARK System Orchestrator")
        self._setup_routes()
        
        # Background tasks
        self.background_tasks = set()
        self.shutdown_event = asyncio.Event()
        
        # Process management
        self.original_overlay_process = None
        self.specialized_dashboard_process = None
        
    def _load_config(self) -> Dict[str, Any]:
        """Load orchestrator configuration"""
        default_config = {
            "system": {
                "auto_start_pipeline": True,
                "auto_start_agents": True,
                "auto_start_overlay": True,
                "health_check_interval": 30,
                "status_update_interval": 10
            },
            "pipeline": {
                "enabled": True,
                "auto_restart": True,
                "max_retries": 3
            },
            "agents": {
                "enabled": True,
                "max_concurrent": 5,
                "cleanup_interval": 300
            },
            "overlay": {
                "enabled": True,
                "port": 8888,
                "auto_restart": True
            },
            "dashboard": {
                "enabled": True,
                "port": 8889,
                "auto_restart": True
            },
            "api": {
                "port": 8000,
                "host": "0.0.0.0",
                "reload": False
            }
        }
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                return {**default_config, **config}
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_path} not found")
            return default_config
    
    def _setup_routes(self):
        """Setup FastAPI routes for the orchestrator API"""
        
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @self.app.get("/")
        async def root():
            return {"message": "AUTARK System Orchestrator", "status": "running"}
        
        @self.app.get("/status")
        async def get_system_status():
            """Get complete system status"""
            await self._update_system_status()
            return asdict(self.status)
        
        @self.app.get("/repositories/stats")
        async def get_repository_stats():
            """Get repository statistics"""
            try:
                stats = await self._get_repository_stats()
                return stats
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/pipeline/start")
        async def start_pipeline():
            """Start the database pipeline"""
            try:
                await self.start_database_pipeline()
                return {"status": "started", "message": "Database pipeline started"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/pipeline/stop")
        async def stop_pipeline():
            """Stop the database pipeline"""
            try:
                await self.stop_database_pipeline()
                return {"status": "stopped", "message": "Database pipeline stopped"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/agents/start")
        async def start_agents():
            """Start specialized agents"""
            try:
                await self.start_specialized_agents()
                return {"status": "started", "message": "Specialized agents started"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/agents/stop")
        async def stop_agents():
            """Stop specialized agents"""
            try:
                await self.stop_specialized_agents()
                return {"status": "stopped", "message": "Specialized agents stopped"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/agents/list")
        async def list_agents():
            """List active agents"""
            try:
                if self.agent_manager:
                    agents = await self.agent_manager.list_agents()
                    return {"agents": agents}
                return {"agents": []}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/overlay/start")
        async def start_overlay():
            """Start Original Overlay"""
            try:
                await self.start_original_overlay()
                return {"status": "started", "message": "Original Overlay started"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/overlay/stop")
        async def stop_overlay():
            """Stop Original Overlay"""
            try:
                await self.stop_original_overlay()
                return {"status": "stopped", "message": "Original Overlay stopped"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/dashboard")
        async def get_dashboard():
            """Serve the orchestrator dashboard"""
            dashboard_path = Path(__file__).parent / "templates" / "orchestrator_dashboard.html"
            if dashboard_path.exists():
                return FileResponse(dashboard_path)
            return HTMLResponse(self._generate_dashboard_html())
        
        @self.app.websocket("/ws/status")
        async def websocket_status(websocket: WebSocket):
            """WebSocket for real-time status updates"""
            await websocket.accept()
            try:
                while not self.shutdown_event.is_set():
                    await self._update_system_status()
                    status_data = asdict(self.status)
                    await websocket.send_json(status_data)
                    await asyncio.sleep(self.config["system"]["status_update_interval"])
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            finally:
                await websocket.close()
    
    async def initialize(self):
        """Initialize the orchestrator"""
        try:
            logger.info("🚀 Initializing AUTARK System Orchestrator")
            
            # Initialize Redis client
            self.redis_client = redis.Redis(
                host="localhost",
                port=6380,
                db=6,
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("✅ Redis connection established")
            
            # Initialize components
            self.database_pipeline = AutarkDatabasePipeline()
            self.agent_manager = AutarkSpecializedAgentManager()
            
            # Update initial status
            await self._update_system_status()
            
            logger.info("✅ Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize orchestrator: {e}")
            raise
    
    async def start_database_pipeline(self):
        """Start the database pipeline"""
        try:
            if self.status.database_pipeline == "running":
                logger.info("📊 Database pipeline already running")
                return
            
            logger.info("🔄 Starting database pipeline...")
            self.status.database_pipeline = "starting"
            
            # Create background task for pipeline
            task = asyncio.create_task(self._run_database_pipeline())
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)
            
            self.status.database_pipeline = "running"
            logger.info("✅ Database pipeline started")
            
        except Exception as e:
            self.status.database_pipeline = "error"
            logger.error(f"❌ Failed to start database pipeline: {e}")
            raise
    
    async def _run_database_pipeline(self):
        """Run the database pipeline as background task"""
        try:
            metrics = await self.database_pipeline.run_pipeline()
            self.status.total_repositories = metrics.total_repos
            self.status.database_pipeline = "completed"
            
            # Store pipeline results
            await self.redis_client.set(
                "pipeline:last_run",
                json.dumps({
                    "metrics": asdict(metrics),
                    "timestamp": datetime.now().isoformat()
                })
            )
            
        except Exception as e:
            self.status.database_pipeline = "error"
            logger.error(f"Database pipeline error: {e}")
    
    async def stop_database_pipeline(self):
        """Stop the database pipeline"""
        try:
            # Cancel background tasks
            for task in self.background_tasks.copy():
                if not task.done():
                    task.cancel()
            
            self.status.database_pipeline = "stopped"
            logger.info("🛑 Database pipeline stopped")
            
        except Exception as e:
            logger.error(f"❌ Failed to stop database pipeline: {e}")
            raise
    
    async def start_specialized_agents(self):
        """Start specialized coding agents"""
        try:
            if self.status.specialized_agents == "running":
                logger.info("🤖 Specialized agents already running")
                return
            
            logger.info("🔄 Starting specialized agents...")
            self.status.specialized_agents = "starting"
            
            await self.agent_manager.initialize()
            
            # Start health monitoring task
            task = asyncio.create_task(self._monitor_agents())
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)
            
            self.status.specialized_agents = "running"
            logger.info("✅ Specialized agents started")
            
        except Exception as e:
            self.status.specialized_agents = "error"
            logger.error(f"❌ Failed to start specialized agents: {e}")
            raise
    
    async def _monitor_agents(self):
        """Monitor agent health and status"""
        try:
            while not self.shutdown_event.is_set():
                if self.agent_manager:
                    agents = await self.agent_manager.list_agents()
                    self.status.active_agents = len([
                        a for a in agents if a.get("status") == "active"
                    ])
                
                await asyncio.sleep(self.config["system"]["health_check_interval"])
                
        except Exception as e:
            logger.error(f"Agent monitoring error: {e}")
    
    async def stop_specialized_agents(self):
        """Stop specialized coding agents"""
        try:
            if self.agent_manager:
                await self.agent_manager.cleanup()
            
            self.status.specialized_agents = "stopped"
            self.status.active_agents = 0
            logger.info("🛑 Specialized agents stopped")
            
        except Exception as e:
            logger.error(f"❌ Failed to stop specialized agents: {e}")
            raise
    
    async def start_original_overlay(self):
        """Start the Original Overlay dashboard"""
        try:
            if self.status.original_overlay == "running":
                logger.info("📊 Original Overlay already running")
                return
            
            logger.info("🔄 Starting Original Overlay...")
            self.status.original_overlay = "starting"
            
            # Start Original Overlay server
            overlay_script = Path(__file__).parent.parent / "overlay" / "start_overlay.py"
            
            self.original_overlay_process = await asyncio.create_subprocess_exec(
                sys.executable, str(overlay_script),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Give it time to start
            await asyncio.sleep(3)
            
            if self.original_overlay_process.returncode is None:
                self.status.original_overlay = "running"
                logger.info("✅ Original Overlay started")
            else:
                self.status.original_overlay = "error"
                logger.error("❌ Original Overlay failed to start")
            
        except Exception as e:
            self.status.original_overlay = "error"
            logger.error(f"❌ Failed to start Original Overlay: {e}")
            raise
    
    async def stop_original_overlay(self):
        """Stop the Original Overlay dashboard"""
        try:
            if self.original_overlay_process:
                self.original_overlay_process.terminate()
                await self.original_overlay_process.wait()
            
            self.status.original_overlay = "stopped"
            logger.info("🛑 Original Overlay stopped")
            
        except Exception as e:
            logger.error(f"❌ Failed to stop Original Overlay: {e}")
            raise
    
    async def start_specialized_dashboard(self):
        """Start the specialized agents dashboard"""
        try:
            logger.info("🔄 Starting Specialized Dashboard...")
            
            dashboard_script = Path(__file__).parent.parent / "overlay" / "specialized_dashboard.py"
            
            self.specialized_dashboard_process = await asyncio.create_subprocess_exec(
                sys.executable, str(dashboard_script),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await asyncio.sleep(2)
            logger.info("✅ Specialized Dashboard started")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Specialized Dashboard: {e}")
    
    async def _update_system_status(self):
        """Update system-wide status"""
        try:
            # Calculate uptime
            self.status.system_uptime = (datetime.now() - self.start_time).total_seconds()
            
            # Check database connections
            try:
                await self.redis_client.ping()
                self.status.redis_status = "connected"
            except:
                self.status.redis_status = "disconnected"
            
            # Check other services
            # PostgreSQL, Qdrant, MongoDB, Elasticsearch status checks would go here
            
        except Exception as e:
            logger.error(f"Status update error: {e}")
    
    async def _get_repository_stats(self) -> Dict[str, Any]:
        """Get repository statistics from the pipeline"""
        try:
            # Get stats from Redis cache
            pipeline_data = await self.redis_client.get("pipeline:last_run")
            if pipeline_data:
                data = json.loads(pipeline_data)
                return data.get("metrics", {})
            
            return {
                "total_repos": 0,
                "cloned_repos": 0,
                "integrated_repos": 0,
                "failed_repos": 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get repository stats: {e}")
            return {}
    
    def _generate_dashboard_html(self) -> str:
        """Generate basic dashboard HTML"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>AUTARK System Orchestrator</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { 
                    font-family: 'Courier New', monospace; 
                    background: #0a0a0a; 
                    color: #00ff41; 
                    margin: 0; 
                    padding: 20px; 
                }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 30px; }
                .status-grid { 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                    gap: 20px; 
                }
                .status-card { 
                    background: #1a1a1a; 
                    border: 1px solid #00ff41; 
                    padding: 20px; 
                    border-radius: 5px; 
                }
                .status-title { color: #ff6b35; font-weight: bold; margin-bottom: 10px; }
                .status-item { margin: 5px 0; }
                .btn { 
                    background: #00ff41; 
                    color: #0a0a0a; 
                    border: none; 
                    padding: 10px 20px; 
                    margin: 5px; 
                    cursor: pointer; 
                    border-radius: 3px; 
                }
                .btn:hover { background: #00cc33; }
                .log { 
                    background: #000; 
                    padding: 10px; 
                    height: 200px; 
                    overflow-y: scroll; 
                    border: 1px solid #333; 
                    margin-top: 20px; 
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 AUTARK SYSTEM ORCHESTRATOR</h1>
                    <p>Comprehensive Database Pipeline & Specialized Agent Management</p>
                </div>
                
                <div class="status-grid">
                    <div class="status-card">
                        <div class="status-title">🗄️ Database Pipeline</div>
                        <div id="pipeline-status" class="status-item">Status: Loading...</div>
                        <div id="repo-count" class="status-item">Repositories: Loading...</div>
                        <button class="btn" onclick="startPipeline()">Start Pipeline</button>
                        <button class="btn" onclick="stopPipeline()">Stop Pipeline</button>
                    </div>
                    
                    <div class="status-card">
                        <div class="status-title">🤖 Specialized Agents</div>
                        <div id="agents-status" class="status-item">Status: Loading...</div>
                        <div id="active-agents" class="status-item">Active: Loading...</div>
                        <button class="btn" onclick="startAgents()">Start Agents</button>
                        <button class="btn" onclick="stopAgents()">Stop Agents</button>
                    </div>
                    
                    <div class="status-card">
                        <div class="status-title">📊 Original Overlay</div>
                        <div id="overlay-status" class="status-item">Status: Loading...</div>
                        <div class="status-item">Port: 8888</div>
                        <button class="btn" onclick="startOverlay()">Start Overlay</button>
                        <button class="btn" onclick="stopOverlay()">Stop Overlay</button>
                        <button class="btn" onclick="openOverlay()">Open Overlay</button>
                    </div>
                    
                    <div class="status-card">
                        <div class="status-title">⚡ System Status</div>
                        <div id="system-uptime" class="status-item">Uptime: Loading...</div>
                        <div id="redis-status" class="status-item">Redis: Loading...</div>
                        <div id="postgres-status" class="status-item">PostgreSQL: Loading...</div>
                    </div>
                </div>
                
                <div class="log" id="log">
                    <div>🔄 Connecting to system...</div>
                </div>
            </div>
            
            <script>
                const ws = new WebSocket('ws://localhost:8000/ws/status');
                const log = document.getElementById('log');
                
                function addLog(message) {
                    log.innerHTML += '<div>' + new Date().toLocaleTimeString() + ' - ' + message + '</div>';
                    log.scrollTop = log.scrollHeight;
                }
                
                ws.onmessage = function(event) {
                    const status = JSON.parse(event.data);
                    
                    document.getElementById('pipeline-status').innerText = 'Status: ' + status.database_pipeline;
                    document.getElementById('repo-count').innerText = 'Repositories: ' + status.total_repositories;
                    document.getElementById('agents-status').innerText = 'Status: ' + status.specialized_agents;
                    document.getElementById('active-agents').innerText = 'Active: ' + status.active_agents;
                    document.getElementById('overlay-status').innerText = 'Status: ' + status.original_overlay;
                    document.getElementById('system-uptime').innerText = 'Uptime: ' + Math.floor(status.system_uptime) + 's';
                    document.getElementById('redis-status').innerText = 'Redis: ' + status.redis_status;
                };
                
                ws.onopen = function() {
                    addLog('✅ Connected to AUTARK Orchestrator');
                };
                
                ws.onerror = function(error) {
                    addLog('❌ WebSocket error: ' + error);
                };
                
                async function apiCall(endpoint, method = 'POST') {
                    try {
                        const response = await fetch(endpoint, { method });
                        const result = await response.json();
                        addLog('✅ ' + result.message);
                    } catch (error) {
                        addLog('❌ ' + error.message);
                    }
                }
                
                function startPipeline() { apiCall('/pipeline/start'); }
                function stopPipeline() { apiCall('/pipeline/stop'); }
                function startAgents() { apiCall('/agents/start'); }
                function stopAgents() { apiCall('/agents/stop'); }
                function startOverlay() { apiCall('/overlay/start'); }
                function stopOverlay() { apiCall('/overlay/stop'); }
                function openOverlay() { window.open('http://localhost:8888', '_blank'); }
            </script>
        </body>
        </html>
        """
    
    async def auto_start_services(self):
        """Auto-start services based on configuration"""
        try:
            if self.config["pipeline"]["enabled"] and self.config["system"]["auto_start_pipeline"]:
                await self.start_database_pipeline()
            
            if self.config["agents"]["enabled"] and self.config["system"]["auto_start_agents"]:
                await self.start_specialized_agents()
            
            if self.config["overlay"]["enabled"] and self.config["system"]["auto_start_overlay"]:
                await self.start_original_overlay()
            
            if self.config["dashboard"]["enabled"]:
                await self.start_specialized_dashboard()
                
        except Exception as e:
            logger.error(f"Auto-start error: {e}")
    
    async def shutdown(self):
        """Graceful shutdown of all services"""
        try:
            logger.info("🛑 Shutting down AUTARK System Orchestrator...")
            
            # Set shutdown event
            self.shutdown_event.set()
            
            # Stop all services
            await self.stop_original_overlay()
            await self.stop_specialized_agents()
            await self.stop_database_pipeline()
            
            # Stop specialized dashboard
            if self.specialized_dashboard_process:
                self.specialized_dashboard_process.terminate()
                await self.specialized_dashboard_process.wait()
            
            # Cancel background tasks
            for task in self.background_tasks:
                task.cancel()
            
            # Close connections
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("✅ AUTARK System Orchestrator shutdown complete")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
    
    def run(self):
        """Run the orchestrator"""
        async def _run():
            try:
                # Setup signal handlers
                loop = asyncio.get_event_loop()
                for sig in [signal.SIGINT, signal.SIGTERM]:
                    loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))
                
                # Initialize
                await self.initialize()
                
                # Auto-start services
                await self.auto_start_services()
                
                logger.info("🎯 AUTARK System Orchestrator running")
                logger.info(f"📊 Dashboard: http://localhost:{self.config['api']['port']}/dashboard")
                logger.info(f"🔗 Original Overlay: http://localhost:{self.config['overlay']['port']}")
                logger.info(f"🤖 Specialized Dashboard: http://localhost:{self.config['dashboard']['port']}")
                
                # Start web server
                config = uvicorn.Config(
                    self.app,
                    host=self.config["api"]["host"],
                    port=self.config["api"]["port"],
                    reload=self.config["api"]["reload"],
                    log_level="info"
                )
                server = uvicorn.Server(config)
                await server.serve()
                
            except Exception as e:
                logger.error(f"Runtime error: {e}")
                await self.shutdown()
        
        try:
            asyncio.run(_run())
        except KeyboardInterrupt:
            logger.info("Orchestrator interrupted by user")


async def main():
    """Main entry point"""
    orchestrator = AutarkSystemOrchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()