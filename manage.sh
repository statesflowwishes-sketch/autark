#!/bin/bash
# KI Agent System Management Script
# Verwalte alle Aspekte des KI Agent Systems

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KI_AGENT_HOME="/opt/ki-agent"

# Farbige Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}    KI Agent System Manager     ${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Zeige Systemstatus
show_status() {
    print_header
    echo "System Status:"
    echo ""
    
    # Überprüfe alle Services
    services=(
        "ki-agent-postgres"
        "ki-agent-redis" 
        "ki-agent-qdrant"
        "ki-agent-mongo"
        "ki-agent-elasticsearch"
        "ki-agent-orchestrator"
    )
    
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service"; then
            echo -e "  ${GREEN}●${NC} $service - aktiv"
        elif systemctl is-enabled --quiet "$service"; then
            echo -e "  ${YELLOW}●${NC} $service - inaktiv (aktiviert)"
        else
            echo -e "  ${RED}●${NC} $service - inaktiv (deaktiviert)"
        fi
    done
    
    echo ""
    echo "Datenbank Verbindungen:"
    
    # PostgreSQL Check
    if pg_isready -h localhost -p 5433 >/dev/null 2>&1; then
        echo -e "  ${GREEN}●${NC} PostgreSQL (Port 5433) - erreichbar"
    else
        echo -e "  ${RED}●${NC} PostgreSQL (Port 5433) - nicht erreichbar"
    fi
    
    # Redis Check
    if redis-cli -h localhost -p 6380 -a SecureKIAgent2025! ping >/dev/null 2>&1; then
        echo -e "  ${GREEN}●${NC} Redis (Port 6380) - erreichbar"
    else
        echo -e "  ${RED}●${NC} Redis (Port 6380) - nicht erreichbar"
    fi
    
    # Qdrant Check
    if curl -f http://localhost:6334/health >/dev/null 2>&1; then
        echo -e "  ${GREEN}●${NC} Qdrant (Port 6334) - erreichbar"
    else
        echo -e "  ${RED}●${NC} Qdrant (Port 6334) - nicht erreichbar"
    fi
    
    # MongoDB Check
    if timeout 5 bash -c "</dev/tcp/localhost/27018" >/dev/null 2>&1; then
        echo -e "  ${GREEN}●${NC} MongoDB (Port 27018) - erreichbar"
    else
        echo -e "  ${RED}●${NC} MongoDB (Port 27018) - nicht erreichbar"
    fi
    
    # Elasticsearch Check
    if curl -f http://localhost:9201/_cluster/health >/dev/null 2>&1; then
        echo -e "  ${GREEN}●${NC} Elasticsearch (Port 9201) - erreichbar"
    else
        echo -e "  ${RED}●${NC} Elasticsearch (Port 9201) - nicht erreichbar"
    fi
    
    echo ""
    echo "System Ressourcen:"
    echo "  CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)% verwendet"
    echo "  RAM: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
    echo "  Disk (/opt): $(df -h /opt | awk 'NR==2{printf "%s/%s (%s verwendet)", $3,$2,$5}')"
}

# Starte alle Services
start_all() {
    print_status "Starte alle KI Agent Services..."
    
    # Datenbank Services zuerst
    for service in ki-agent-postgres ki-agent-redis ki-agent-qdrant ki-agent-mongo ki-agent-elasticsearch; do
        print_status "Starte $service..."
        sudo systemctl start "$service"
        sleep 5
    done
    
    # Warte auf Datenbankinitialisierung
    print_status "Warte auf Datenbankinitialisierung..."
    sleep 20
    
    # Hauptservice starten
    print_status "Starte ki-agent-orchestrator..."
    sudo systemctl start ki-agent-orchestrator
    
    print_success "Alle Services gestartet!"
}

# Stoppe alle Services
stop_all() {
    print_status "Stoppe alle KI Agent Services..."
    
    # Hauptservice zuerst stoppen
    sudo systemctl stop ki-agent-orchestrator || true
    
    # Dann Datenbank Services
    for service in ki-agent-elasticsearch ki-agent-mongo ki-agent-qdrant ki-agent-redis ki-agent-postgres; do
        print_status "Stoppe $service..."
        sudo systemctl stop "$service" || true
    done
    
    print_success "Alle Services gestoppt!"
}

# Neustarten aller Services
restart_all() {
    print_status "Starte alle KI Agent Services neu..."
    stop_all
    sleep 10
    start_all
}

# Zeige Logs
show_logs() {
    service="${1:-ki-agent-orchestrator}"
    lines="${2:-50}"
    
    print_status "Zeige Logs für $service (letzte $lines Zeilen)..."
    sudo journalctl -u "$service" -n "$lines" --no-pager
    
    echo ""
    print_status "Folge Live-Logs mit: journalctl -fu $service"
}

# Backup erstellen
backup_data() {
    backup_dir="/opt/ki-agent/backups/$(date +%Y%m%d_%H%M%S)"
    
    print_status "Erstelle Backup in $backup_dir..."
    
    sudo mkdir -p "$backup_dir"
    
    # PostgreSQL Dump
    print_status "Sichere PostgreSQL Datenbank..."
    sudo -u postgres pg_dump -h localhost -p 5433 -U ki_agent -d ki_agent_db > "$backup_dir/postgres_dump.sql"
    
    # Redis Dump
    print_status "Sichere Redis Daten..."
    sudo cp /opt/ki-agent/data/redis/dump.rdb "$backup_dir/" 2>/dev/null || true
    
    # Qdrant Daten
    print_status "Sichere Qdrant Daten..."
    sudo tar -czf "$backup_dir/qdrant_data.tar.gz" -C /opt/ki-agent/data/qdrant . 2>/dev/null || true
    
    # MongoDB Dump
    print_status "Sichere MongoDB Datenbank..."
    mongodump --host localhost:27018 --username ki_agent --password SecureKIAgent2025! --out "$backup_dir/mongo_dump" 2>/dev/null || true
    
    # Konfigurationsdateien
    print_status "Sichere Konfigurationsdateien..."
    sudo tar -czf "$backup_dir/configs.tar.gz" -C /opt/ki-agent configs
    
    # Logs
    print_status "Sichere aktuelle Logs..."
    sudo tar -czf "$backup_dir/logs.tar.gz" -C /opt/ki-agent logs
    
    sudo chown -R ki-agent:ki-agent "$backup_dir"
    
    print_success "Backup erstellt: $backup_dir"
}

# System Monitoring
monitor() {
    print_status "Starte kontinuierliches Monitoring (Strg+C zum Beenden)..."
    
    while true; do
        clear
        show_status
        echo ""
        echo "Aktualisiert alle 30 Sekunden... (Strg+C zum Beenden)"
        sleep 30
    done
}

# System Health Check
health_check() {
    print_status "Führe umfangreichen Health Check durch..."
    
    errors=0
    
    # Service Status Check
    services=(
        "ki-agent-postgres"
        "ki-agent-redis" 
        "ki-agent-qdrant"
        "ki-agent-mongo"
        "ki-agent-elasticsearch"
        "ki-agent-orchestrator"
    )
    
    for service in "${services[@]}"; do
        if ! systemctl is-active --quiet "$service"; then
            print_error "Service $service ist nicht aktiv"
            ((errors++))
        fi
    done
    
    # Datenbank Connectivity Check
    if ! pg_isready -h localhost -p 5433 >/dev/null 2>&1; then
        print_error "PostgreSQL ist nicht erreichbar"
        ((errors++))
    fi
    
    if ! redis-cli -h localhost -p 6380 -a SecureKIAgent2025! ping >/dev/null 2>&1; then
        print_error "Redis ist nicht erreichbar"
        ((errors++))
    fi
    
    if ! curl -f http://localhost:6334/health >/dev/null 2>&1; then
        print_error "Qdrant ist nicht erreichbar"
        ((errors++))
    fi
    
    # Disk Space Check
    available=$(df /opt | awk 'NR==2 {print $4}')
    if [ "$available" -lt 1048576 ]; then  # < 1GB
        print_warning "Weniger als 1GB freier Speicherplatz verfügbar"
        ((errors++))
    fi
    
    # Memory Check
    mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ "$mem_usage" -gt 90 ]; then
        print_warning "Speicherverbrauch über 90%: ${mem_usage}%"
    fi
    
    if [ $errors -eq 0 ]; then
        print_success "Health Check erfolgreich - alle Systeme funktional!"
    else
        print_error "Health Check fehlgeschlagen - $errors Probleme gefunden"
        return 1
    fi
}

# Zeige Hilfe
show_help() {
    print_header
    echo "Verfügbare Befehle:"
    echo ""
    echo "  status          - Zeige Systemstatus"
    echo "  start           - Starte alle Services"
    echo "  stop            - Stoppe alle Services"
    echo "  restart         - Starte alle Services neu"
    echo "  logs [service] [lines] - Zeige Logs (Standard: orchestrator, 50 Zeilen)"
    echo "  backup          - Erstelle vollständiges Backup"
    echo "  monitor         - Kontinuierliches Monitoring"
    echo "  health          - Umfangreicher Health Check"
    echo "  help            - Zeige diese Hilfe"
    echo ""
    echo "Beispiele:"
    echo "  $0 status"
    echo "  $0 logs ki-agent-postgres 100"
    echo "  $0 backup"
}

# Hauptlogik
case "${1:-help}" in
    "status")
        show_status
        ;;
    "start")
        start_all
        ;;
    "stop")
        stop_all
        ;;
    "restart")
        restart_all
        ;;
    "logs")
        show_logs "$2" "$3"
        ;;
    "backup")
        backup_data
        ;;
    "monitor")
        monitor
        ;;
    "health")
        health_check
        ;;
    "help"|*)
        show_help
        ;;
esac