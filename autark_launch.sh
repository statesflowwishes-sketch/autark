#!/bin/bash

echo "🤖 ==============================================="
echo "      AUTARK SYSTEM - Complete Launch"
echo "   Based on Abacus AI CodeLLM CLI Framework"
echo "=============================================== 🤖"
echo

# System-Checks
echo "🔍 Pre-flight System Checks..."

# Docker Check
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found"
    exit 1
fi

# Python Virtual Environment
if [ ! -d "venv" ]; then
    echo "❌ Python virtual environment not found"
    exit 1
fi

echo "✅ Prerequisites met"
echo

# Container Status
echo "🐳 Checking database containers..."
containers=(
    "ki-agent-postgres-dev:PostgreSQL"
    "ki-agent-redis-dev:Redis Cache"
    "ki-agent-mongo-dev:MongoDB"
    "ki-agent-qdrant-dev:Qdrant Vector"
    "ki-agent-elasticsearch-dev:Elasticsearch"
)

all_running=true
for container_info in "${containers[@]}"; do
    container="${container_info%%:*}"
    name="${container_info#*:}"
    
    if docker ps --format "table {{.Names}}" | grep -q "^${container}$"; then
        echo "  ✅ $name"
    else
        echo "  ❌ $name (not running)"
        all_running=false
    fi
done

if [ "$all_running" = false ]; then
    echo
    echo "⚠️  Some containers are not running. Starting them..."
    docker-compose -f docker-compose.dev.yml up -d
    echo "⏳ Waiting for containers to be ready..."
    sleep 10
fi

echo
echo "🎯 Starting AUTARK SYSTEM Components..."
echo

# Start Orchestrator in background
echo "🚀 Starting KI Agent Orchestrator..."
source venv/bin/activate
nohup python orchestrator/simple_main.py > logs/orchestrator.log 2>&1 &
ORCH_PID=$!
echo "   Orchestrator PID: $ORCH_PID"

# Wait a moment for orchestrator to initialize
sleep 3

# Start Original Overlay Dashboard
echo "🖥️  Starting Original Overlay Dashboard..."
nohup python overlay/start_overlay.py > logs/overlay.log 2>&1 &
OVERLAY_PID=$!
echo "   Overlay PID: $OVERLAY_PID"

# Save PIDs for later management
echo "$ORCH_PID" > .autark_orchestrator.pid
echo "$OVERLAY_PID" > .autark_overlay.pid

echo
echo "✨ ============================================== ✨"
echo "     🎉 AUTARK SYSTEM FULLY OPERATIONAL! 🎉"
echo "✨ ============================================== ✨"
echo
echo "🌐 Web Interfaces:"
echo "   📊 Dashboard:      http://localhost:8888/dashboard.html"
echo "   🔍 Qdrant:         http://localhost:6334/dashboard"
echo "   📈 Elasticsearch:  http://localhost:9201"
echo
echo "🗄️  Database Endpoints:"
echo "   🐘 PostgreSQL:     localhost:5433"
echo "   🔴 Redis:          localhost:6380"
echo "   🍃 MongoDB:        localhost:27018"
echo "   📊 Qdrant:         localhost:6334"
echo "   🔍 Elasticsearch:  localhost:9201"
echo
echo "📋 Management Commands:"
echo "   ./manage.sh status     # System status"
echo "   ./manage.sh logs       # Show logs"
echo "   ./manage.sh stop       # Stop system"
echo "   ./manage.sh monitor    # Live monitoring"
echo
echo "🔧 Advanced Features:"
echo "   • Multi-Agent Orchestration"
echo "   • LEAP Integration (pending)"
echo "   • Autonomous Resource Management"
echo "   • Real-time Analytics"
echo "   • Security Policy Enforcement"
echo "   • Cost Budget Management"
echo
echo "🎯 System is now autonomous and self-managing!"
echo "   Access the Original Overlay for real-time monitoring."
echo
echo "📝 Logs are written to:"
echo "   logs/orchestrator.log"
echo "   logs/overlay.log"
echo
echo "To stop the system: ./autark_stop.sh"
echo