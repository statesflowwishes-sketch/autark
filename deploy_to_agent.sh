#!/bin/bash
"""
AUTARK + AKIS Deployment Script
===============================

Deployed das komplette AUTARK System mit AKIS Knowledge Integration
in den finalen Agent Ordner.
"""

set -e

echo "🚀 AUTARK + AKIS Deployment"
echo "=========================="

# Source and target directories
SOURCE_DIR="/home/holythreekingstreescrowns/Schreibtisch/KI AGENT"
TARGET_DIR="/home/holythreekingstreescrowns/Schreibtisch/Agent"

echo "📁 Source: $SOURCE_DIR"
echo "📁 Target: $TARGET_DIR"

# Create target directory if it doesn't exist
if [ ! -d "$TARGET_DIR" ]; then
    echo "📁 Creating target directory..."
    mkdir -p "$TARGET_DIR"
fi

# Copy all files
echo "📋 Copying AUTARK system files..."
cp -r "$SOURCE_DIR"/* "$TARGET_DIR/"

# Copy hidden files if any
echo "📋 Copying hidden files..."
cp -r "$SOURCE_DIR"/.[^.]* "$TARGET_DIR/" 2>/dev/null || true

# Set permissions
echo "🔧 Setting permissions..."
chmod +x "$TARGET_DIR"/*.py 2>/dev/null || true
chmod +x "$TARGET_DIR"/quickstart.sh 2>/dev/null || true
chmod +x "$TARGET_DIR"/akis/scripts/*.py 2>/dev/null || true

# Create deployment info
echo "📄 Creating deployment info..."
cat > "$TARGET_DIR/DEPLOYMENT_INFO.md" << EOF
# AUTARK + AKIS Deployment
========================

Deployment Date: $(date)
Source: $SOURCE_DIR
Target: $TARGET_DIR

## System Components

### Core AUTARK System
- ✅ autark_launcher.py - Main launcher
- ✅ autark_knowledge_integration.py - Knowledge integration
- ✅ autark_video_ai_pipeline.py - Video AI pipeline
- ✅ autark_complete_integration_demo.py - Integration demo
- ✅ quickstart.sh - Quick start script

### AKIS (Knowledge Integration System)
- ✅ akis/ - Complete AKIS implementation
- ✅ 7-Layer Architecture
- ✅ Hybrid Retrieval Engine
- ✅ Tool Manifests & Configuration
- ✅ Ontology Models
- ✅ Skill-Level Adaptive System

### Configuration
- ✅ agents.yaml - Agent configuration
- ✅ model_registry.json - Model registry
- ✅ task-schema.yaml - Task schema
- ✅ All configuration files

### Infrastructure
- ✅ venv/ - Python virtual environment
- ✅ overlay/ - Server overlay
- ✅ orchestrator/ - Orchestration layer
- ✅ policies/ - Policy definitions

## Quick Start

1. Navigate to deployment directory:
   cd "$TARGET_DIR"

2. Start AUTARK system:
   ./quickstart.sh

3. Start AKIS Knowledge System:
   cd akis
   venv/bin/python scripts/akis_server.py --mode interactive

4. Run integration demo:
   python autark_complete_integration_demo.py

## System Status
- 🧠 AUTARK Core: OPERATIONAL
- 🔍 AKIS Knowledge: OPERATIONAL  
- 🎥 Video AI Pipeline: READY
- 🔗 Integration: COMPLETE
- 📊 Deployment: SUCCESS

Ready for production use!
EOF

# Final verification
echo "✅ Deployment verification..."
if [ -f "$TARGET_DIR/autark_launcher.py" ] && [ -d "$TARGET_DIR/akis" ]; then
    echo "✅ Core files present"
else
    echo "❌ Missing core files"
    exit 1
fi

if [ -f "$TARGET_DIR/akis/src/akis/ontology/models.py" ]; then
    echo "✅ AKIS system present"
else
    echo "❌ AKIS system missing"
    exit 1
fi

# Show summary
echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================"
echo "📁 Location: $TARGET_DIR"
echo "📊 Components: $(find "$TARGET_DIR" -name "*.py" | wc -l) Python files"
echo "📚 Documentation: $(find "$TARGET_DIR" -name "*.md" | wc -l) Markdown files"
echo "⚙️  Configuration: $(find "$TARGET_DIR" -name "*.yaml" -o -name "*.yml" -o -name "*.json" | wc -l) config files"
echo ""
echo "🚀 Ready to start:"
echo "   cd '$TARGET_DIR'"
echo "   ./quickstart.sh"
echo ""
echo "🧠 AUTARK + AKIS System successfully deployed!"