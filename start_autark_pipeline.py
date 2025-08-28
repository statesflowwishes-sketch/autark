#!/usr/bin/env python3
"""
AUTARK SYSTEM STARTUP SCRIPT
============================

Complete startup orchestration for the AUTARK system including:
- Database pipeline
- Specialized coding agents
- Original Overlay Enhanced
- System orchestrator
- Health monitoring

Author: AUTARK SYSTEM
Version: 1.0.0
"""

import asyncio
import logging
import signal
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import subprocess
import json
import yaml
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutarkSystemStartup:
    """
    Complete AUTARK system startup and management
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_path = self.base_dir / "config" / "orchestrator_config.yaml"
        self.processes: Dict[str, subprocess.Popen] = {}
        self.shutdown_requested = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"🛑 Received signal {signum}, initiating shutdown...")
        self.shutdown_requested = True
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available"""
        logger.info("🔍 Checking system dependencies...")
        
        required_packages = [
            "aiohttp", "asyncpg", "redis", "qdrant-client", 
            "pymongo", "elasticsearch", "fastapi", "uvicorn",
            "yaml", "git", "sentence-transformers", "numpy"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"❌ Missing packages: {missing_packages}")
            logger.info("💡 Install with: pip install " + " ".join(missing_packages))
            return False
        
        logger.info("✅ All dependencies available")
        return True
    
    def check_docker_services(self) -> bool:
        """Check if Docker services are running"""
        logger.info("🐳 Checking Docker services...")
        
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                check=True
            )
            
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        containers.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            
            required_ports = [5433, 6380, 6334, 27018, 9201]
            running_ports = []
            
            for container in containers:
                ports = container.get("Ports", "")
                for port in required_ports:
                    if f":{port}->" in ports:
                        running_ports.append(port)
            
            missing_ports = set(required_ports) - set(running_ports)
            
            if missing_ports:
                logger.warning(f"⚠️ Missing Docker services on ports: {missing_ports}")
                logger.info("🚀 Starting Docker services...")
                return self.start_docker_services()
            
            logger.info("✅ All required Docker services are running")
            return True
            
        except subprocess.CalledProcessError:
            logger.error("❌ Docker not available or not running")
            return False
        except FileNotFoundError:
            logger.error("❌ Docker command not found")
            return False
    
    def start_docker_services(self) -> bool:
        """Start required Docker services"""
        try:
            compose_file = self.base_dir / "docker-compose.dev.yml"
            
            if compose_file.exists():
                logger.info("🚀 Starting Docker Compose services...")
                result = subprocess.run(
                    ["docker-compose", "-f", str(compose_file), "up", "-d"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                if result.returncode == 0:
                    logger.info("✅ Docker services started successfully")
                    time.sleep(10)  # Wait for services to be ready
                    return True
                else:
                    logger.error(f"❌ Failed to start Docker services: {result.stderr}")
                    return False
            else:
                logger.error(f"❌ Docker Compose file not found: {compose_file}")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Docker Compose failed: {e}")
            return False
        except FileNotFoundError:
            logger.error("❌ docker-compose command not found")
            return False
    
    def start_service(self, name: str, script_path: str, args: List[str] = None) -> bool:
        """Start a service process"""
        try:
            if name in self.processes:
                logger.warning(f"⚠️ Service {name} already running")
                return True
            
            full_path = self.base_dir / script_path
            if not full_path.exists():
                logger.error(f"❌ Script not found: {full_path}")
                return False
            
            cmd = [sys.executable, str(full_path)]
            if args:
                cmd.extend(args)
            
            logger.info(f"🚀 Starting {name}...")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.base_dir),
                env=dict(os.environ, PYTHONPATH=str(self.base_dir))
            )
            
            self.processes[name] = process
            logger.info(f"✅ {name} started (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start {name}: {e}")
            return False
    
    def check_service_health(self, name: str, url: str) -> bool:
        """Check if a service is healthy"""
        try:
            import requests
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def monitor_services(self):
        """Monitor running services"""
        while not self.shutdown_requested:
            try:
                # Check process health
                dead_services = []
                for name, process in self.processes.items():
                    if process.poll() is not None:
                        dead_services.append(name)
                        logger.error(f"💀 Service {name} died (exit code: {process.returncode})")
                
                # Remove dead services
                for name in dead_services:
                    del self.processes[name]
                
                # Sleep before next check
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                time.sleep(10)
    
    def shutdown_services(self):
        """Shutdown all services gracefully"""
        logger.info("🛑 Shutting down all services...")
        
        # Shutdown order (reverse of startup)
        shutdown_order = [
            "enhanced_overlay",
            "specialized_dashboard", 
            "orchestrator",
            "database_pipeline"
        ]
        
        for name in shutdown_order:
            if name in self.processes:
                process = self.processes[name]
                logger.info(f"🛑 Stopping {name}...")
                
                try:
                    # Try graceful shutdown first
                    process.terminate()
                    process.wait(timeout=10)
                    logger.info(f"✅ {name} stopped gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if necessary
                    logger.warning(f"⚠️ Force killing {name}")
                    process.kill()
                    process.wait()
                except Exception as e:
                    logger.error(f"❌ Error stopping {name}: {e}")
        
        self.processes.clear()
        logger.info("✅ All services stopped")
    
    def display_startup_banner(self):
        """Display startup banner"""
        banner = """
        ╔══════════════════════════════════════════════════════════╗
        ║                    AUTARK SYSTEM                         ║
        ║              Complete Pipeline Startup                   ║
        ╠══════════════════════════════════════════════════════════╣
        ║  🚀 Database Pipeline Integration                        ║
        ║  🤖 Specialized Coding Agents                           ║
        ║  📊 Original Overlay Enhanced                            ║
        ║  ⚡ System Orchestrator                                 ║
        ║  🔗 300+ Database Repository Management                  ║
        ╚══════════════════════════════════════════════════════════╝
        """
        print(banner)
        logger.info("🎯 AUTARK System v2.0.0 - Complete Pipeline Edition")
    
    def display_service_urls(self):
        """Display service URLs"""
        logger.info("\n🔗 Service URLs:")
        logger.info("   📊 Original Overlay Enhanced:  http://localhost:8888")
        logger.info("   🤖 Specialized Dashboard:      http://localhost:8889")
        logger.info("   ⚡ System Orchestrator:        http://localhost:8000")
        logger.info("   📈 Orchestrator Dashboard:     http://localhost:8000/dashboard")
        logger.info("\n📱 WebSocket Endpoints:")
        logger.info("   🔄 Real-time Updates:          ws://localhost:8888/ws")
        logger.info("   📊 System Status:              ws://localhost:8000/ws/status")
        logger.info("\n🗄️ Database Services:")
        logger.info("   🐘 PostgreSQL:                 localhost:5433")
        logger.info("   🔴 Redis:                       localhost:6380")
        logger.info("   🎯 Qdrant:                      localhost:6334")
        logger.info("   🍃 MongoDB:                     localhost:27018")
        logger.info("   🔍 Elasticsearch:               localhost:9201")
    
    def run(self):
        """Run the complete AUTARK system"""
        try:
            self.display_startup_banner()
            
            # Pre-flight checks
            logger.info("🔍 Running pre-flight checks...")
            
            if not self.check_dependencies():
                logger.error("❌ Dependency check failed")
                return False
            
            if not self.check_docker_services():
                logger.error("❌ Docker services check failed")
                return False
            
            logger.info("✅ Pre-flight checks passed")
            
            # Start services in order
            startup_sequence = [
                ("orchestrator", "pipeline/autark_orchestrator.py"),
                ("enhanced_overlay", "overlay/enhanced_original_overlay.py"),
                ("specialized_dashboard", "overlay/specialized_dashboard.py")
            ]
            
            failed_services = []
            for name, script in startup_sequence:
                if not self.start_service(name, script):
                    failed_services.append(name)
                else:
                    time.sleep(3)  # Wait between service starts
            
            if failed_services:
                logger.error(f"❌ Failed to start services: {failed_services}")
                self.shutdown_services()
                return False
            
            # Wait for services to be ready
            logger.info("⏳ Waiting for services to be ready...")
            time.sleep(10)
            
            # Display service information
            self.display_service_urls()
            
            logger.info("🎉 AUTARK System startup complete!")
            logger.info("💡 Press Ctrl+C to shutdown the system")
            
            # Start monitoring
            self.monitor_services()
            
            return True
            
        except KeyboardInterrupt:
            logger.info("⚠️ Received keyboard interrupt")
        except Exception as e:
            logger.error(f"❌ Startup failed: {e}")
        finally:
            self.shutdown_services()
        
        return False

def main():
    """Main entry point"""
    startup = AutarkSystemStartup()
    
    try:
        success = startup.run()
        exit_code = 0 if success else 1
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        exit_code = 1
    
    logger.info(f"👋 AUTARK System shutdown complete (exit code: {exit_code})")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()