#!/bin/bash
# KI Agent System Deployment & Setup Script
# Komplette Vorbereitung und Start des autarken KI Agent Systems

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KI_AGENT_HOME="/opt/ki-agent"
SERVICE_USER="ki-agent"

echo "🚀 KI Agent System Deployment gestartet..."
echo "📍 Script Directory: $SCRIPT_DIR"
echo "🏠 Installation Directory: $KI_AGENT_HOME"

# Funktion für farbige Ausgabe
print_status() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

# Überprüfung der Voraussetzungen
check_prerequisites() {
    print_status "Überprüfe Systemvoraussetzungen..."
    
    # Docker installiert?
    if ! command -v docker &> /dev/null; then
        print_error "Docker ist nicht installiert. Bitte installiere Docker zuerst."
        exit 1
    fi
    
    # Docker läuft?
    if ! docker info &> /dev/null; then
        print_error "Docker läuft nicht. Bitte starte Docker zuerst."
        exit 1
    fi
    
    # Python 3.9+ installiert?
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 ist nicht installiert."
        exit 1
    fi
    
    # systemd verfügbar?
    if ! command -v systemctl &> /dev/null; then
        print_error "systemd ist nicht verfügbar."
        exit 1
    fi
    
    # Genug Speicherplatz? (mindestens 10GB)
    available_space=$(df /opt 2>/dev/null | awk 'NR==2 {print $4}' || echo "0")
    if [ "$available_space" -lt 10485760 ]; then  # 10GB in KB
        print_warning "Weniger als 10GB freier Speicherplatz verfügbar."
    fi
    
    print_success "Alle Voraussetzungen erfüllt."
}

# System-Setup
setup_system() {
    print_status "Richte System ein..."
    
    # Erstelle Service User
    if ! id "$SERVICE_USER" &>/dev/null; then
        sudo useradd -r -s /bin/bash -d "$KI_AGENT_HOME" "$SERVICE_USER"
        print_success "Service User '$SERVICE_USER' erstellt."
    else
        print_status "Service User '$SERVICE_USER' existiert bereits."
    fi
    
    # Erstelle Verzeichnisstruktur
    sudo mkdir -p "$KI_AGENT_HOME"/{data,logs,configs,venv,src}
    sudo mkdir -p "$KI_AGENT_HOME"/data/{postgres,redis,qdrant,mongo,elasticsearch}
    sudo mkdir -p /etc/systemd/system
    
    # Setze Berechtigungen
    sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$KI_AGENT_HOME"
    sudo chmod 755 "$KI_AGENT_HOME"
    
    print_success "System-Setup abgeschlossen."
}

# Kopiere Dateien
deploy_files() {
    print_status "Kopiere Projektdateien..."
    
    # Kopiere gesamtes Projekt
    sudo cp -r "$SCRIPT_DIR"/* "$KI_AGENT_HOME"/src/
    
    # Kopiere Konfigurationsdateien
    sudo cp "$SCRIPT_DIR"/database/postgres.conf "$KI_AGENT_HOME"/configs/
    sudo cp "$SCRIPT_DIR"/database/redis.conf "$KI_AGENT_HOME"/configs/
    
    # Kopiere systemd Services
    sudo cp "$SCRIPT_DIR"/systemd/*.service /etc/systemd/system/
    
    # Setze Berechtigungen
    sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$KI_AGENT_HOME"/src
    sudo chmod +x "$KI_AGENT_HOME"/src/database/setup_databases.sh
    
    print_success "Dateien erfolgreich kopiert."
}

# Python Environment Setup
setup_python_environment() {
    print_status "Richte Python Environment ein..."
    
    # Virtual Environment erstellen
    sudo -u "$SERVICE_USER" python3 -m venv "$KI_AGENT_HOME"/venv
    
    # Aktiviere venv und installiere Abhängigkeiten
    sudo -u "$SERVICE_USER" bash -c "
        source '$KI_AGENT_HOME/venv/bin/activate'
        pip install --upgrade pip
        pip install fastapi uvicorn redis psycopg2-binary pymongo elasticsearch
        pip install pydantic sqlalchemy alembic python-multipart
        pip install qdrant-client sentence-transformers
        pip install openai anthropic
        pip install pytest pytest-asyncio
        pip install python-dotenv pyyaml
        pip install aiofiles aioredis
        pip install prometheus-client
    "
    
    print_success "Python Environment eingerichtet."
}

# Datenbanken Setup
setup_databases() {
    print_status "Richte Datenbanken ein..."
    
    # Führe Database Setup Skript aus
    bash "$KI_AGENT_HOME"/src/database/setup_databases.sh
    
    # Warte auf Datenbankinitialisierung
    print_status "Warte auf Datenbankinitialisierung..."
    sleep 45
    
    # Initialisiere PostgreSQL Schema
    export PGPASSWORD="SecureKIAgent2025!"
    psql -h localhost -p 5433 -U ki_agent -d ki_agent_db -f "$KI_AGENT_HOME"/src/database/init_schema.sql
    
    print_success "Datenbanken erfolgreich eingerichtet."
}

# systemd Services Setup
setup_systemd_services() {
    print_status "Richte systemd Services ein..."
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Aktiviere und starte Database Services
    for service in ki-agent-postgres ki-agent-redis ki-agent-qdrant ki-agent-mongo ki-agent-elasticsearch; do
        print_status "Aktiviere Service: $service"
        sudo systemctl enable "$service"
        sudo systemctl start "$service"
        
        # Warte kurz und überprüfe Status
        sleep 5
        if sudo systemctl is-active --quiet "$service"; then
            print_success "Service $service erfolgreich gestartet."
        else
            print_error "Service $service konnte nicht gestartet werden."
            sudo systemctl status "$service" --no-pager
        fi
    done
    
    # Hauptservice aktivieren (aber noch nicht starten)
    sudo systemctl enable ki-agent-orchestrator
    
    print_success "systemd Services eingerichtet."
}

# Gesundheitscheck der Services
health_check() {
    print_status "Führe Gesundheitscheck durch..."
    
    # PostgreSQL
    if pg_isready -h localhost -p 5433 >/dev/null 2>&1; then
        print_success "PostgreSQL ist erreichbar."
    else
        print_error "PostgreSQL ist nicht erreichbar."
        return 1
    fi
    
    # Redis
    if redis-cli -h localhost -p 6380 -a SecureKIAgent2025! ping >/dev/null 2>&1; then
        print_success "Redis ist erreichbar."
    else
        print_error "Redis ist nicht erreichbar."
        return 1
    fi
    
    # Qdrant
    if curl -f http://localhost:6334/health >/dev/null 2>&1; then
        print_success "Qdrant ist erreichbar."
    else
        print_error "Qdrant ist nicht erreichbar."
        return 1
    fi
    
    # MongoDB
    if mongosh --host localhost:27018 --eval "db.runCommand('ping')" >/dev/null 2>&1; then
        print_success "MongoDB ist erreichbar."
    else
        print_error "MongoDB ist nicht erreichbar."
        return 1
    fi
    
    # Elasticsearch
    if curl -f http://localhost:9201/_cluster/health >/dev/null 2>&1; then
        print_success "Elasticsearch ist erreichbar."
    else
        print_error "Elasticsearch ist nicht erreichbar."
        return 1
    fi
    
    print_success "Alle Services sind gesund!"
}

# Orchestrator vorbereiten
prepare_orchestrator() {
    print_status "Bereite KI Agent Orchestrator vor..."
    
    # Erstelle Haupt-Python-Modul
    sudo -u "$SERVICE_USER" cat > "$KI_AGENT_HOME"/src/orchestrator/main.py << 'EOF'
#!/usr/bin/env python3
"""
KI Agent Orchestrator - Haupteinstiegspunkt
Startet das autarke Multi-Agent System
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path

# Füge Projektverzeichnis zu Python Path hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from orchestrator.state_machine import OrchestrationStateMachine
from orchestrator.agent_factory import AgentFactory
from integration.leap_client import LeapClient

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/ki-agent/logs/orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class KIAgentOrchestrator:
    def __init__(self):
        self.running = False
        self.state_machine = None
        self.agent_factory = None
        
    async def initialize(self):
        """Initialisiere alle Komponenten"""
        logger.info("🚀 Initialisiere KI Agent Orchestrator...")
        
        try:
            # Agent Factory initialisieren
            self.agent_factory = AgentFactory()
            await self.agent_factory.initialize()
            
            # State Machine initialisieren
            self.state_machine = OrchestrationStateMachine()
            await self.state_machine.initialize()
            
            logger.info("✅ Orchestrator erfolgreich initialisiert")
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Initialisierung: {e}")
            raise
    
    async def start(self):
        """Starte den Orchestrator"""
        logger.info("🔄 Starte KI Agent Orchestrator...")
        
        self.running = True
        
        # Hauptschleife
        while self.running:
            try:
                # Überprüfe auf neue Tasks
                await self.state_machine.process_pending_tasks()
                
                # Kurze Pause
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ Fehler in Hauptschleife: {e}")
                await asyncio.sleep(10)
    
    async def stop(self):
        """Stoppe den Orchestrator gracefully"""
        logger.info("🛑 Stoppe KI Agent Orchestrator...")
        self.running = False
        
        if self.state_machine:
            await self.state_machine.shutdown()
        
        if self.agent_factory:
            await self.agent_factory.shutdown()
        
        logger.info("✅ Orchestrator gestoppt")

async def main():
    orchestrator = KIAgentOrchestrator()
    
    # Signal Handler für graceful shutdown
    def signal_handler(sig, frame):
        logger.info(f"Signal {sig} empfangen, fahre herunter...")
        asyncio.create_task(orchestrator.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await orchestrator.initialize()
        await orchestrator.start()
    except KeyboardInterrupt:
        logger.info("Interrupt empfangen, fahre herunter...")
    except Exception as e:
        logger.error(f"Kritischer Fehler: {e}")
        sys.exit(1)
    finally:
        await orchestrator.stop()

if __name__ == "__main__":
    asyncio.run(main())
EOF
    
    sudo chown "$SERVICE_USER:$SERVICE_USER" "$KI_AGENT_HOME"/src/orchestrator/main.py
    sudo chmod +x "$KI_AGENT_HOME"/src/orchestrator/main.py
    
    print_success "Orchestrator vorbereitet."
}

# Hauptfunktion
main() {
    print_status "🚀 KI Agent System Deployment gestartet..."
    
    check_prerequisites
    setup_system
    deploy_files
    setup_python_environment
    setup_databases
    setup_systemd_services
    prepare_orchestrator
    health_check
    
    print_success "🎉 KI Agent System erfolgreich eingerichtet!"
    echo ""
    echo "📋 Nächste Schritte:"
    echo "1. Starte den Hauptservice: sudo systemctl start ki-agent-orchestrator"
    echo "2. Überprüfe den Status: sudo systemctl status ki-agent-orchestrator"
    echo "3. Zeige Logs an: journalctl -fu ki-agent-orchestrator"
    echo ""
    echo "🔧 Verfügbare Services:"
    echo "  - PostgreSQL: localhost:5433"
    echo "  - Redis: localhost:6380"
    echo "  - Qdrant: localhost:6334"
    echo "  - MongoDB: localhost:27018"
    echo "  - Elasticsearch: localhost:9201"
    echo ""
    echo "📂 Logs: /opt/ki-agent/logs/"
    echo "⚙️  Config: /opt/ki-agent/configs/"
    echo "💾 Data: /opt/ki-agent/data/"
}

# Script ausführen
main "$@"