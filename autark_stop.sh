#!/bin/bash

echo "🛑 ============================================== 🛑"
echo "        Stopping AUTARK SYSTEM"
echo "🛑 ============================================== 🛑"
echo

# Stop processes by PID
if [ -f ".autark_orchestrator.pid" ]; then
    ORCH_PID=$(cat .autark_orchestrator.pid)
    echo "🔄 Stopping Orchestrator (PID: $ORCH_PID)..."
    if kill -TERM "$ORCH_PID" 2>/dev/null; then
        echo "✅ Orchestrator stopped"
    else
        echo "⚠️  Orchestrator already stopped or not found"
    fi
    rm -f .autark_orchestrator.pid
fi

if [ -f ".autark_overlay.pid" ]; then
    OVERLAY_PID=$(cat .autark_overlay.pid)
    echo "🔄 Stopping Overlay Dashboard (PID: $OVERLAY_PID)..."
    if kill -TERM "$OVERLAY_PID" 2>/dev/null; then
        echo "✅ Overlay Dashboard stopped"
    else
        echo "⚠️  Overlay Dashboard already stopped or not found"
    fi
    rm -f .autark_overlay.pid
fi

# Stop any remaining Python processes related to our system
echo "🔄 Cleaning up remaining processes..."
pkill -f "orchestrator/simple_main.py" 2>/dev/null
pkill -f "overlay/start_overlay.py" 2>/dev/null

# Optionally stop containers (uncomment if needed)
# echo "🐳 Stopping database containers..."
# docker-compose -f docker-compose.dev.yml stop

echo
echo "✅ AUTARK SYSTEM completely stopped"
echo "   All processes have been terminated"
echo
echo "To restart: ./autark_launch.sh"
echo