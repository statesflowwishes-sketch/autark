#!/bin/bash
# Quick Start Script für das KI Agent System
# Erstelle Python Virtual Environment und starte System

cd "$(dirname "$0")"

# Farbige Ausgabe
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}🔄 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║              🚀 KI Agent System Quick Start 🚀              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Überprüfe ob Container laufen
print_step "Überprüfe Container Status..."
if ! docker ps | grep -q "ki-agent-postgres-dev"; then
    print_error "Container sind nicht gestartet!"
    echo "Starte Container mit: docker-compose -f docker-compose.dev.yml up -d"
    exit 1
fi

# Erstelle Python Virtual Environment
if [[ ! -d "venv" ]]; then
    print_step "Erstelle Python Virtual Environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    print_step "Installiere Python Dependencies..."
    pip install --upgrade pip
    pip install fastapi uvicorn redis psycopg2-binary pymongo elasticsearch
    pip install pydantic sqlalchemy python-multipart aiofiles aioredis
    pip install qdrant-client sentence-transformers openai anthropic
    pip install pytest pytest-asyncio python-dotenv pyyaml prometheus-client
    pip install requests httpx asyncio-mqtt
    
    print_success "Python Environment eingerichtet"
else
    print_step "Aktiviere vorhandenes Python Environment..."
    source venv/bin/activate
fi

# Erstelle .env falls nicht vorhanden
if [[ ! -f ".env" ]]; then
    print_step "Erstelle Environment-Konfiguration..."
    cat > .env << 'EOF'
# KI Agent System Configuration
POSTGRES_URL=postgresql://ki_agent:SecureKIAgent2025!@localhost:5433/ki_agent_db
REDIS_URL=redis://:SecureKIAgent2025!@localhost:6380
QDRANT_URL=http://localhost:6334
MONGO_URL=mongodb://ki_agent:SecureKIAgent2025!@localhost:27018/ki_agent
ELASTICSEARCH_URL=http://localhost:9201

# System Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
SECURE_MODE=true
COST_BUDGET_DEFAULT_USD=5.0
MAX_ITERATIONS_DEFAULT=8
EOF
    print_success "Environment-Konfiguration erstellt"
fi

# Teste Datenbankverbindungen
print_step "Teste Datenbankverbindungen..."
errors=0

if ! timeout 5 bash -c "</dev/tcp/localhost/5433" >/dev/null 2>&1; then
    print_error "PostgreSQL nicht erreichbar (Port 5433)"
    ((errors++))
fi

if ! timeout 5 bash -c "</dev/tcp/localhost/6380" >/dev/null 2>&1; then
    print_error "Redis nicht erreichbar (Port 6380)"
    ((errors++))
fi

if ! curl -f http://localhost:6334/ >/dev/null 2>&1; then
    print_error "Qdrant nicht erreichbar (Port 6334)"
    ((errors++))
fi

if ! timeout 5 bash -c "</dev/tcp/localhost/27018" >/dev/null 2>&1; then
    print_error "MongoDB nicht erreichbar (Port 27018)"
    ((errors++))
fi

if ! curl -f http://localhost:9201/_cluster/health >/dev/null 2>&1; then
    print_error "Elasticsearch nicht erreichbar (Port 9201)"
    ((errors++))
fi

if [[ $errors -eq 0 ]]; then
    print_success "Alle Datenbanken sind erreichbar"
else
    print_error "$errors Datenbankverbindungen fehlgeschlagen"
    echo "Überprüfe Container mit: docker ps"
    exit 1
fi

# Erstelle Basis-Orchestrator wenn nicht vorhanden
if [[ ! -f "orchestrator/simple_main.py" ]]; then
    print_step "Erstelle Basis-Orchestrator..."
    mkdir -p orchestrator logs

    cat > orchestrator/simple_main.py << 'EOF'
#!/usr/bin/env python3
"""
KI Agent Orchestrator - Einfacher Startpunkt
Basis-Implementation für das autarke Multi-Agent System
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class SimpleKIAgentOrchestrator:
    """Einfacher KI Agent Orchestrator für Basis-Funktionalität"""
    
    def __init__(self):
        self.running = False
        self.task_counter = 0
        
    async def initialize(self):
        """Initialisiere Orchestrator"""
        logger.info("🚀 Initialisiere KI Agent Orchestrator...")
        
        # Teste Datenbankverbindungen
        await self._test_connections()
        
        logger.info("✅ Orchestrator erfolgreich initialisiert")
    
    async def _test_connections(self):
        """Teste alle Datenbankverbindungen"""
        import redis
        import psycopg2
        import requests
        
        try:
            # Redis Test
            r = redis.Redis(host='localhost', port=6380, password='SecureKIAgent2025!', decode_responses=True)
            r.ping()
            logger.info("✅ Redis Verbindung erfolgreich")
            
            # PostgreSQL Test
            conn = psycopg2.connect(
                host='localhost',
                port=5433,
                user='ki_agent',
                password='SecureKIAgent2025!',
                database='ki_agent_db'
            )
            conn.close()
            logger.info("✅ PostgreSQL Verbindung erfolgreich")
            
            # Qdrant Test
            response = requests.get('http://localhost:6334/')
            if response.status_code == 200:
                logger.info("✅ Qdrant Verbindung erfolgreich")
            
            # Elasticsearch Test
            response = requests.get('http://localhost:9201/_cluster/health')
            if response.status_code == 200:
                logger.info("✅ Elasticsearch Verbindung erfolgreich")
                
        except Exception as e:
            logger.error(f"❌ Datenbankverbindungsfehler: {e}")
            raise
    
    async def start(self):
        """Starte Orchestrator Hauptschleife"""
        logger.info("🔄 Starte KI Agent Orchestrator...")
        
        self.running = True
        
        while self.running:
            try:
                # Simuliere Task Processing
                self.task_counter += 1
                logger.info(f"🔄 Heartbeat #{self.task_counter} - System läuft...")
                
                # Hier würde die eigentliche Agent-Orchestrierung stattfinden
                await self._process_pending_tasks()
                
                # Warte 30 Sekunden
                await asyncio.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("⚠️  Interrupt empfangen, fahre herunter...")
                break
            except Exception as e:
                logger.error(f"❌ Fehler in Hauptschleife: {e}")
                await asyncio.sleep(10)
    
    async def _process_pending_tasks(self):
        """Verarbeite ausstehende Tasks"""
        # Placeholder für echte Task-Verarbeitung
        
        # Beispiel: Logge System Status
        if self.task_counter % 10 == 0:  # Alle 5 Minuten
            logger.info("📊 System Status Check...")
            logger.info(f"   • Laufzeit: {self.task_counter * 30} Sekunden")
            logger.info(f"   • Status: Aktiv")
            logger.info(f"   • Timestamp: {datetime.now().isoformat()}")
    
    async def stop(self):
        """Stoppe Orchestrator"""
        logger.info("🛑 Stoppe KI Agent Orchestrator...")
        self.running = False

async def main():
    """Hauptfunktion"""
    orchestrator = SimpleKIAgentOrchestrator()
    
    try:
        await orchestrator.initialize()
        await orchestrator.start()
    except KeyboardInterrupt:
        logger.info("Shutdown signal empfangen...")
    except Exception as e:
        logger.error(f"Kritischer Fehler: {e}")
        sys.exit(1)
    finally:
        await orchestrator.stop()

if __name__ == "__main__":
    # Erstelle logs Verzeichnis
    Path("./logs").mkdir(exist_ok=True)
    
    logger.info("🤖 KI Agent System - Einfacher Modus")
    logger.info("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 System heruntergefahren")
EOF

    chmod +x orchestrator/simple_main.py
    print_success "Basis-Orchestrator erstellt"
fi

print_success "KI Agent System bereit!"
echo ""
echo -e "${YELLOW}🚀 System starten:${NC}"
echo "   python orchestrator/simple_main.py"
echo ""
echo -e "${YELLOW}🛠️  Management:${NC}"
echo "   ./manage.sh status    # System Status"
echo "   ./manage.sh logs      # Logs anzeigen"
echo "   ./manage.sh monitor   # Live Monitoring"
echo ""
echo -e "${YELLOW}🌐 Web Interfaces:${NC}"
echo "   Qdrant Dashboard: http://localhost:6334/dashboard"
echo "   Elasticsearch:    http://localhost:9201"
echo ""
echo -e "${YELLOW}📊 Datenbank Ports:${NC}"
echo "   PostgreSQL: localhost:5433"
echo "   Redis:      localhost:6380"
echo "   MongoDB:    localhost:27018"
echo "   Qdrant:     localhost:6334"
echo "   Elasticsearch: localhost:9201"