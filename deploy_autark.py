#!/usr/bin/env python3
"""
AUTARK SYSTEM DEPLOYMENT SCRIPT
================================

One-click deployment for the complete AUTARK system pipeline:
- Docker environment setup
- Database initialization  
- Service deployment
- System verification
- Health monitoring

Author: AUTARK SYSTEM
Version: 2.0.0
"""

import subprocess
import sys
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_cmd(cmd, description, check=True):
    """Execute command with logging"""
    logger.info(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=check, 
                              capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ {description} - Success")
            return True
        else:
            logger.error(f"❌ {description} - Failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"💥 {description} - Exception: {e}")
        return False


def deploy_autark_system():
    """Deploy complete AUTARK system"""
    
    logger.info("""
    ╔══════════════════════════════════════════════════════════╗
    ║                 AUTARK SYSTEM DEPLOY                     ║
    ║            🚀 Complete Pipeline Deployment               ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    base_dir = Path(__file__).parent
    
    # Step 1: Install dependencies
    logger.info("📦 Installing Python dependencies...")
    deps = [
        "aiohttp>=3.8.0",
        "asyncpg>=0.28.0", 
        "redis>=4.5.0",
        "qdrant-client>=1.6.0",
        "pymongo>=4.5.0",
        "elasticsearch>=8.0.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pyyaml>=6.0",
        "GitPython>=3.1.0",
        "sentence-transformers>=2.2.0",
        "numpy>=1.24.0",
        "requests>=2.31.0",
        "aiofiles>=23.0.0",
        "python-multipart>=0.0.6"
    ]
    
    for dep in deps:
        if not run_cmd(f"pip install {dep}", f"Installing {dep}"):
            logger.error(f"Failed to install {dep}")
    
    # Step 2: Setup Docker environment
    logger.info("🐳 Setting up Docker environment...")
    docker_compose = base_dir / "docker-compose.dev.yml"
    
    if docker_compose.exists():
        run_cmd("docker-compose -f docker-compose.dev.yml down", 
                "Stopping existing containers", check=False)
        run_cmd("docker-compose -f docker-compose.dev.yml up -d", 
                "Starting Docker services")
    else:
        logger.warning("⚠️ Docker compose file not found, using default setup")
        
        # Start individual containers
        containers = [
            ("postgres:15", "autark-postgres", 5433, 
             "-e POSTGRES_DB=autark -e POSTGRES_USER=autark -e POSTGRES_PASSWORD=autark123"),
            ("redis:7-alpine", "autark-redis", 6380, ""),
            ("qdrant/qdrant:latest", "autark-qdrant", 6334, ""),
            ("mongo:6", "autark-mongo", 27018, 
             "-e MONGO_INITDB_ROOT_USERNAME=autark -e MONGO_INITDB_ROOT_PASSWORD=autark123"),
            ("elasticsearch:8.10.0", "autark-elastic", 9201, 
             "-e discovery.type=single-node -e xpack.security.enabled=false")
        ]
        
        for image, name, port, env in containers:
            run_cmd(f"docker stop {name}", f"Stopping {name}", check=False)
            run_cmd(f"docker rm {name}", f"Removing {name}", check=False)
            run_cmd(f"docker run -d --name {name} -p {port}:5432 {env} {image}" 
                   if "postgres" in image else
                   f"docker run -d --name {name} -p {port}:6379 {env} {image}"
                   if "redis" in image else
                   f"docker run -d --name {name} -p {port}:6333 {env} {image}"
                   if "qdrant" in image else  
                   f"docker run -d --name {name} -p {port}:27017 {env} {image}"
                   if "mongo" in image else
                   f"docker run -d --name {name} -p {port}:9200 {env} {image}",
                   f"Starting {name}")
    
    # Step 3: Wait for services
    logger.info("⏳ Waiting for database services to be ready...")
    time.sleep(30)
    
    # Step 4: Create directories
    logger.info("📁 Creating required directories...")
    dirs_to_create = [
        "pipeline", "overlay", "config", "data", 
        "logs", "repositories", "temp"
    ]
    
    for dir_name in dirs_to_create:
        dir_path = base_dir / dir_name
        dir_path.mkdir(exist_ok=True)
        logger.info(f"✅ Created directory: {dir_path}")
    
    # Step 5: Start AUTARK system
    logger.info("🚀 Starting AUTARK system...")
    startup_script = base_dir / "start_autark_pipeline.py"
    
    if startup_script.exists():
        logger.info("🎯 Launching AUTARK system...")
        logger.info("📊 System will be available at:")
        logger.info("   - Original Overlay: http://localhost:8888")
        logger.info("   - System Dashboard: http://localhost:8000")
        logger.info("   - Orchestrator API: http://localhost:8000/docs")
        
        # Execute startup script
        try:
            subprocess.run([sys.executable, str(startup_script)], 
                          cwd=str(base_dir))
        except KeyboardInterrupt:
            logger.info("🛑 System shutdown requested")
        except Exception as e:
            logger.error(f"💥 System error: {e}")
    else:
        logger.error("❌ Startup script not found")
        return False
    
    return True


def main():
    """Main deployment function"""
    try:
        success = deploy_autark_system()
        if success:
            logger.info("🎉 AUTARK System deployment completed successfully!")
        else:
            logger.error("❌ AUTARK System deployment failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("⚠️ Deployment interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Deployment failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()