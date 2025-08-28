#!/bin/bash
# KI Agent System Initialization Script
# Startet das komplette autarke KI Agent System

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KI_AGENT_HOME="/opt/ki-agent"

# Farbige Ausgabe
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                   🤖 KI Agent System 🚀                     ║"
    echo "║              Autarke Multi-Agent Orchestrierung             ║"
    echo "║                                                              ║"
    echo "║  🎯 CodeLLM + LEAP + Multi-Model Integration                ║"
    echo "║  🔧 Vollständige Pipeline mit Datenbank-Infrastruktur       ║"
    echo "║  🛡️  Sicherheit + Monitoring + Governance                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}🔄 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Überprüfe Systemvoraussetzungen
check_system() {
    print_step "Überprüfe Systemvoraussetzungen..."
    
    # Docker Check
    if ! command -v docker &> /dev/null; then
        print_error "Docker ist nicht installiert!"
        echo "Installiere Docker mit: curl -fsSL https://get.docker.com | sh"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker läuft nicht!"
        echo "Starte Docker mit: sudo systemctl start docker"
        exit 1
    fi
    
    # Python Check
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 ist nicht installiert!"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    # Einfache Version Check ohne bc
    major=$(echo $python_version | cut -d'.' -f1)
    minor=$(echo $python_version | cut -d'.' -f2)
    if [[ $major -lt 3 ]] || [[ $major -eq 3 && $minor -lt 9 ]]; then
        print_error "Python 3.9+ ist erforderlich (gefunden: $python_version)"
        exit 1
    fi
    
    # systemd Check
    if ! command -v systemctl &> /dev/null; then
        print_error "systemd ist nicht verfügbar!"
        exit 1
    fi
    
    # Speicherplatz Check (mindestens 15GB) - ohne bc
    available_gb=$(df /opt 2>/dev/null | awk 'NR==2 {printf "%.0f", $4/1024/1024}' || echo "0")
    if [[ $available_gb -lt 15 ]]; then
        print_warning "Weniger als 15GB freier Speicherplatz verfügbar ($available_gb GB)"
        read -p "Trotzdem fortfahren? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    print_success "Alle Systemvoraussetzungen erfüllt"
}

# Setup Datenbanken
setup_databases() {
    print_step "Starte Datenbank-Infrastructure Setup..."
    
    # Erstelle Datenverzeichnisse
    sudo mkdir -p /opt/ki-agent/data/{postgres,redis,qdrant,mongo,elasticsearch}
    sudo mkdir -p /opt/ki-agent/logs
    sudo mkdir -p /opt/ki-agent/configs
    
    # Setze Berechtigungen
    sudo chown -R $USER:$USER /opt/ki-agent 2>/dev/null || true
    
    cd "$SCRIPT_DIR"
    
    # Starte Datenbank-Compose
    print_step "Starte Datenbanken mit Docker Compose..."
    docker-compose -f docker-compose.dev.yml up -d postgres redis qdrant mongo elasticsearch
    
    # Warte auf Datenbankinitialisierung
    print_step "Warte auf Datenbankinitialisierung..."
    
    # PostgreSQL Health Check - einfacher TCP Check
    for i in {1..30}; do
        if timeout 5 bash -c "</dev/tcp/localhost/5433" >/dev/null 2>&1; then
            print_success "PostgreSQL ist bereit"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    # Redis Health Check - mit Passwort
    for i in {1..15}; do
        if redis-cli -h localhost -p 6380 -a SecureKIAgent2025! ping >/dev/null 2>&1; then
            print_success "Redis ist bereit"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    # Qdrant Health Check - verwende korrekte URL
    for i in {1..20}; do
        if curl -f http://localhost:6334/ >/dev/null 2>&1; then
            print_success "Qdrant ist bereit"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    # MongoDB Health Check
    for i in {1..20}; do
        if timeout 5 bash -c "</dev/tcp/localhost/27018" >/dev/null 2>&1; then
            print_success "MongoDB ist bereit"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    # Elasticsearch Health Check
    for i in {1..30}; do
        if curl -f http://localhost:9201/_cluster/health >/dev/null 2>&1; then
            print_success "Elasticsearch ist bereit"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    print_success "Alle Datenbanken sind erfolgreich gestartet"
}

# Initialisiere Datenbank-Schemas
init_database_schemas() {
    print_step "Initialisiere Datenbank-Schemas..."
    
    # PostgreSQL Schema
    export PGPASSWORD="SecureKIAgent2025!"
    if timeout 10 bash -c "</dev/tcp/localhost/5433" >/dev/null 2>&1; then
        # Verwende Docker exec für PostgreSQL Zugriff
        docker exec ki-agent-postgres-dev psql -U ki_agent -d ki_agent_db << 'EOF'
-- Grundlegende Audit Tabelle
CREATE TABLE IF NOT EXISTS audits (
    id SERIAL PRIMARY KEY,
    task_id TEXT NOT NULL,
    state TEXT NOT NULL,
    previous_state TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT DEFAULT 'system',
    execution_time_ms INTEGER,
    cost_usd DECIMAL(10,4),
    error_details TEXT
);

CREATE INDEX IF NOT EXISTS idx_audits_task_id ON audits(task_id);
CREATE INDEX IF NOT EXISTS idx_audits_state ON audits(state);
CREATE INDEX IF NOT EXISTS idx_audits_created_at ON audits(created_at);

-- Task Executions Tabelle
CREATE TABLE IF NOT EXISTS task_executions (
    id SERIAL PRIMARY KEY,
    task_uuid UUID DEFAULT gen_random_uuid() UNIQUE,
    goal TEXT NOT NULL,
    repo_url TEXT,
    branch TEXT DEFAULT 'main',
    mode TEXT CHECK (mode IN ('refactor', 'new_feature', 'bugfix', 'app_generation')),
    status TEXT DEFAULT 'pending',
    iterations_count INTEGER DEFAULT 0,
    max_iterations INTEGER DEFAULT 8,
    cost_budget_usd DECIMAL(10,4) DEFAULT 5.0,
    cost_spent_usd DECIMAL(10,4) DEFAULT 0.0,
    time_budget_minutes INTEGER DEFAULT 60,
    time_spent_minutes INTEGER DEFAULT 0,
    acceptance_criteria JSONB DEFAULT '[]',
    constraints JSONB DEFAULT '{}',
    results JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    created_by TEXT DEFAULT 'system'
);

CREATE INDEX IF NOT EXISTS idx_task_executions_status ON task_executions(status);
CREATE INDEX IF NOT EXISTS idx_task_executions_mode ON task_executions(mode);
CREATE INDEX IF NOT EXISTS idx_task_executions_created_at ON task_executions(created_at);

-- System Config Tabelle
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key TEXT UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    config_type TEXT DEFAULT 'general',
    is_encrypted BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    updated_by TEXT DEFAULT 'system'
);

CREATE INDEX IF NOT EXISTS idx_system_config_key ON system_config(config_key);
CREATE INDEX IF NOT EXISTS idx_system_config_type ON system_config(config_type);

-- Basis-Konfigurationsdaten einfügen
INSERT INTO system_config (config_key, config_value, config_type) VALUES
('max_iterations_default', '8', 'execution'),
('cost_budget_default_usd', '5.0', 'cost'),
('time_budget_default_minutes', '60', 'execution'),
('secure_mode', 'true', 'security'),
('git_commit_signing', 'true', 'git'),
('embedding_strategy', '"semantic+symbol"', 'ai'),
('sandbox_tier_default', '"medium"', 'security'),
('system_initialized', 'true', 'system'),
('initialization_timestamp', concat('"', now(), '"'), 'system')
ON CONFLICT (config_key) DO UPDATE SET 
    config_value = EXCLUDED.config_value,
    last_updated = NOW();
EOF
        print_success "PostgreSQL Schema initialisiert"
    else
        print_error "PostgreSQL Verbindung fehlgeschlagen"
    fi
    
    # Redis Setup - Basis-Konfiguration
    if timeout 5 bash -c "</dev/tcp/localhost/6380" >/dev/null 2>&1; then
        docker exec ki-agent-redis-dev redis-cli -a SecureKIAgent2025! SET "ki-agent:system:status" "initialized"
        docker exec ki-agent-redis-dev redis-cli -a SecureKIAgent2025! SET "ki-agent:system:version" "1.0.0"
        docker exec ki-agent-redis-dev redis-cli -a SecureKIAgent2025! SET "ki-agent:system:startup_time" "$(date -Iseconds)"
        print_success "Redis konfiguriert"
    else
        print_error "Redis Verbindung fehlgeschlagen"
    fi
    
    # Qdrant Setup - Erstelle Collections
    if curl -f http://localhost:6334/health >/dev/null 2>&1; then
        # Erstelle Collection für Code Embeddings
        curl -X PUT "http://localhost:6334/collections/code_embeddings" \
            -H "Content-Type: application/json" \
            -d '{
                "vectors": {
                    "size": 768,
                    "distance": "Cosine"
                }
            }' >/dev/null 2>&1
        
        # Erstelle Collection für Task Embeddings
        curl -X PUT "http://localhost:6334/collections/task_embeddings" \
            -H "Content-Type: application/json" \
            -d '{
                "vectors": {
                    "size": 768,
                    "distance": "Cosine"
                }
            }' >/dev/null 2>&1
        
        print_success "Qdrant Collections erstellt"
    else
        print_error "Qdrant Verbindung fehlgeschlagen"
    fi
    
    # MongoDB Setup - Erstelle Collections
    if timeout 5 bash -c "</dev/tcp/localhost/27018" >/dev/null 2>&1; then
        docker exec ki-agent-mongo-dev mongosh --eval "
            use ki_agent;
            db.createCollection('logs');
            db.createCollection('metrics');
            db.createCollection('artifacts');
            db.logs.createIndex({timestamp: 1});
            db.metrics.createIndex({timestamp: 1, metric_type: 1});
            db.artifacts.createIndex({task_id: 1, created_at: 1});
        " >/dev/null 2>&1
        print_success "MongoDB Collections erstellt"
    else
        print_error "MongoDB Verbindung fehlgeschlagen"
    fi
}

# Python Environment Setup
setup_python_environment() {
    print_step "Richte Python Environment ein..."
    
    # Virtual Environment erstellen
    python3 -m venv "$SCRIPT_DIR/venv"
    source "$SCRIPT_DIR/venv/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Installiere Basis-Dependencies
    pip install fastapi uvicorn redis psycopg2-binary pymongo elasticsearch
    pip install pydantic sqlalchemy alembic python-multipart aiofiles aioredis
    pip install qdrant-client sentence-transformers openai anthropic
    pip install pytest pytest-asyncio python-dotenv pyyaml prometheus-client
    
    print_success "Python Environment eingerichtet"
}

# KI Agent Orchestrator Setup
setup_orchestrator() {
    print_step "Konfiguriere KI Agent Orchestrator..."
    
    # Erstelle Environment-Konfiguration
    cat > "$SCRIPT_DIR/.env" << EOF
# KI Agent System Environment Configuration
POSTGRES_URL=postgresql://ki_agent:SecureKIAgent2025!@localhost:5433/ki_agent_db
REDIS_URL=redis://localhost:6380
QDRANT_URL=http://localhost:6334
MONGO_URL=mongodb://localhost:27018/ki_agent
ELASTICSEARCH_URL=http://localhost:9201

# System Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
PYTHONPATH=$SCRIPT_DIR

# Security
SECURE_MODE=true
SANDBOX_TIER_DEFAULT=medium

# Budgets & Limits
COST_BUDGET_DEFAULT_USD=5.0
TIME_BUDGET_DEFAULT_MINUTES=60
MAX_ITERATIONS_DEFAULT=8

# Feature Flags
ENABLE_CODE_EXECUTION=true
ENABLE_EXTERNAL_APIS=true
ENABLE_GIT_OPERATIONS=true
ENABLE_MONITORING=true
EOF
    
    print_success "Orchestrator konfiguriert"
}

# Systemd Services Setup (Optional)
setup_systemd_services() {
    if [[ "$EUID" -eq 0 ]]; then
        print_step "Richte systemd Services ein..."
        
        # Kopiere Service-Dateien
        cp "$SCRIPT_DIR"/systemd/*.service /etc/systemd/system/
        
        # Reload systemd
        systemctl daemon-reload
        
        # Aktiviere Services (aber starte sie noch nicht)
        systemctl enable ki-agent-postgres ki-agent-redis ki-agent-qdrant ki-agent-mongo ki-agent-elasticsearch
        
        print_success "systemd Services eingerichtet"
        print_warning "Services sind aktiviert aber nicht gestartet. Nutze './manage.sh start' zum Starten."
    else
        print_warning "Keine Root-Berechtigung - systemd Services werden übersprungen"
        print_warning "Nutze Docker Compose für Service-Management"
    fi
}

# Validierung der Installation
validate_installation() {
    print_step "Validiere Installation..."
    
    errors=0
    
    # Database Connectivity
    if ! timeout 5 bash -c "</dev/tcp/localhost/5433" >/dev/null 2>&1; then
        print_error "PostgreSQL nicht erreichbar"
        ((errors++))
    fi
    
    if ! timeout 5 bash -c "</dev/tcp/localhost/6380" >/dev/null 2>&1; then
        print_error "Redis nicht erreichbar"
        ((errors++))
    fi
    
    if ! curl -f http://localhost:6334/ >/dev/null 2>&1; then
        print_error "Qdrant nicht erreichbar"
        ((errors++))
    fi
    
    if ! timeout 5 bash -c "</dev/tcp/localhost/27018" >/dev/null 2>&1; then
        print_error "MongoDB nicht erreichbar"
        ((errors++))
    fi
    
    if ! curl -f http://localhost:9201/_cluster/health >/dev/null 2>&1; then
        print_error "Elasticsearch nicht erreichbar"
        ((errors++))
    fi
    
    # Python Environment Check
    if [[ ! -d "$SCRIPT_DIR/venv" ]]; then
        print_error "Python Virtual Environment nicht gefunden"
        ((errors++))
    fi
    
    # Configuration Files Check
    if [[ ! -f "$SCRIPT_DIR/.env" ]]; then
        print_error "Environment-Konfiguration nicht gefunden"
        ((errors++))
    fi
    
    if [[ $errors -eq 0 ]]; then
        print_success "Installation erfolgreich validiert!"
        return 0
    else
        print_error "Installation-Validierung fehlgeschlagen ($errors Fehler)"
        return 1
    fi
}

# Zeige Systemübersicht
show_system_overview() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🎉 Installation Abgeschlossen! 🎉        ║"
    echo "╠══════════════════════════════════════════════════════════════╣"
    echo "║                                                              ║"
    echo "║  📊 Verfügbare Services:                                     ║"
    echo "║     • PostgreSQL: localhost:5433                            ║"
    echo "║     • Redis: localhost:6380                                  ║"
    echo "║     • Qdrant: localhost:6334                                 ║"
    echo "║     • MongoDB: localhost:27018                               ║"
    echo "║     • Elasticsearch: localhost:9201                         ║"
    echo "║                                                              ║"
    echo "║  🛠️  Management-Befehle:                                     ║"
    echo "║     • ./manage.sh status    - System Status                 ║"
    echo "║     • ./manage.sh start     - Alle Services starten         ║"
    echo "║     • ./manage.sh stop      - Alle Services stoppen         ║"
    echo "║     • ./manage.sh monitor   - Live Monitoring               ║"
    echo "║     • ./manage.sh backup    - Backup erstellen              ║"
    echo "║                                                              ║"
    echo "║  🚀 KI Agent starten:                                        ║"
    echo "║     source venv/bin/activate                                 ║"
    echo "║     python -m orchestrator.main                             ║"
    echo "║                                                              ║"
    echo "║  📝 Logs & Konfiguration:                                    ║"
    echo "║     • Logs: ./logs/                                          ║"
    echo "║     • Config: ./.env                                         ║"
    echo "║     • Agents Config: ./agents.yaml                          ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Hauptfunktion
main() {
    print_banner
    
    echo "Initialisiere KI Agent System..."
    echo "Aktuelles Verzeichnis: $SCRIPT_DIR"
    echo ""
    
    check_system
    setup_databases
    init_database_schemas
    setup_python_environment
    setup_orchestrator
    setup_systemd_services
    
    if validate_installation; then
        show_system_overview
        exit 0
    else
        print_error "Installation fehlgeschlagen!"
        exit 1
    fi
}

# Führe Hauptfunktion aus
main "$@"