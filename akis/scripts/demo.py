#!/usr/bin/env python3
"""
AKIS Demo
=========

Demonstration des AUTARK Knowledge Integration Systems
"""

import sys
from pathlib import Path
import subprocess
import time
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def run_command(cmd, description="", check=True):
    """Execute command with pretty output"""
    print(f"\n🔧 {description}")
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        if result.stdout:
            print("✅ Output:")
            for line in result.stdout.strip().split('\n'):
                print(f"   {line}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return e
    except Exception as e:
        print(f"❌ Exception: {e}")
        return e

def demo_akis():
    """AKIS Demo Flow"""
    
    print("="*60)
    print("🧠 AUTARK Knowledge Integration System")
    print("🎯 Live Demonstration")
    print("="*60)
    
    base_dir = Path(__file__).parent.parent
    scripts_dir = base_dir / "scripts"
    
    # Step 1: Initialize AKIS
    print("\n📋 Step 1: AKIS Initialization")
    init_script = scripts_dir / "init_akis.py"
    
    if init_script.exists():
        run_command([
            sys.executable, str(init_script), 
            "--data-dir", str(base_dir / "data"),
            "--manifests-dir", str(base_dir / "manifests"),
            "--docs-dir", str(base_dir / "docs")
        ], "Initializing AKIS Knowledge Base")
    else:
        print("❌ init_akis.py not found")
        return
    
    time.sleep(2)
    
    # Step 2: Check Data Directory
    print("\n📁 Step 2: Data Directory Overview")
    data_dir = base_dir / "data"
    
    if data_dir.exists():
        print("✅ Data directory contents:")
        for item in data_dir.rglob("*"):
            if item.is_file():
                size = item.stat().st_size
                print(f"   📄 {item.relative_to(data_dir)} ({size} bytes)")
    else:
        print("❌ Data directory not found")
    
    # Step 3: Test Queries (Simulated)
    print("\n🔍 Step 3: Query Examples")
    
    sample_queries = [
        "How do I create a video with AI?",
        "What tools are available for video editing?",
        "Show me knowledge integration capabilities",
        "How do I deploy to production?",
        "What are the maturity levels?",
    ]
    
    print("📋 Sample Queries (would be processed by AKIS):")
    for i, query in enumerate(sample_queries, 1):
        print(f"   {i}. {query}")
        
        # Simulate query processing
        print(f"      🔄 Processing...")
        time.sleep(0.5)
        print(f"      ✅ Would return: Tool suggestions, documentation, examples")
    
    # Step 4: Show Architecture
    print("\n🏗️  Step 4: AKIS Architecture Overview")
    
    architecture_layers = [
        "Layer 1: Storage Primitives (SQLite)",
        "Layer 2: Ingestion & Normalization",
        "Layer 3: Ontology & Knowledge Graph",
        "Layer 4: Embeddings & Indices",
        "Layer 5: Reasoning Adapters",
        "Layer 6: Evaluation & Telemetrie",
        "Layer 7: Governance & Security",
        "Layer 8: Delivery"
    ]
    
    print("📊 AKIS 7-Layer Architecture:")
    for layer in architecture_layers:
        print(f"   🔹 {layer}")
    
    # Step 5: Show Features
    print("\n⭐ Step 5: Key Features")
    
    features = [
        "🔍 Hybrid Retrieval: Graph + Vector + Lexical",
        "🎯 Skill-Level Adaptive Responses",
        "📊 6-Level Maturity Progression",
        "🛡️  Governance & Compliance",
        "📱 Offline-First Architecture",
        "🔗 Cross-Domain Knowledge Linking",
        "📈 Performance Benchmarking",
        "🎛️  Tool Manifest Configuration"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    # Step 6: Integration Options
    print("\n🔌 Step 6: Integration Options")
    
    integrations = [
        "✅ Standalone Python Server",
        "✅ REST API Endpoint",
        "✅ CLI Tool Interface",
        "✅ Jupyter Notebook Integration",
        "🔄 VS Code Extension (Planned)",
        "🔄 Web Dashboard (Planned)",
        "🔄 Slack Bot (Planned)"
    ]
    
    for integration in integrations:
        print(f"   {integration}")
    
    # Step 7: Next Steps
    print("\n🚀 Step 7: Next Steps")
    
    next_steps = [
        "1. Run: python scripts/init_akis.py --data-dir ./data",
        "2. Test: python scripts/akis_server.py --mode interactive",
        "3. Integrate: Import AKIS into existing AUTARK system",
        "4. Configure: Add your tool manifests",
        "5. Scale: Deploy to production environment"
    ]
    
    for step in next_steps:
        print(f"   {step}")
    
    print("\n" + "="*60)
    print("🎉 AKIS Demo Complete!")
    print("🧠 Ready for Knowledge Integration")
    print("="*60)


def show_manifest_examples():
    """Show manifest examples"""
    
    print("\n📋 Tool Manifest Examples")
    
    base_dir = Path(__file__).parent.parent
    manifests_dir = base_dir / "manifests" / "tools"
    
    if manifests_dir.exists():
        for manifest_file in manifests_dir.glob("*.yml"):
            print(f"\n📄 {manifest_file.name}:")
            try:
                content = manifest_file.read_text()
                # Show first few lines
                lines = content.split('\n')[:10]
                for line in lines:
                    print(f"   {line}")
                if len(content.split('\n')) > 10:
                    print("   ...")
            except Exception as e:
                print(f"   ❌ Error reading: {e}")
    else:
        print("❌ Manifests directory not found")


def show_ontology_info():
    """Show ontology information"""
    
    print("\n🧬 Ontology Structure")
    
    entities = [
        "Tool: Represents external tools and their capabilities",
        "Capability: Specific functionality a tool provides",
        "Document: Knowledge artifacts (docs, examples, tutorials)",
        "Concept: Abstract knowledge units",
        "Relation: Connections between entities",
        "BenchmarkCase: Performance validation scenarios",
        "PolicyRule: Governance and compliance rules"
    ]
    
    print("📊 Core Entities:")
    for entity in entities:
        print(f"   🔹 {entity}")
    
    print("\n📈 Maturity Levels:")
    maturity_levels = [
        "1. AWARENESS_EXPLORATION: Discovery phase",
        "2. BASIC_EXECUTION: Simple task completion",
        "3. EFFICIENT_OPERATION: Optimized workflows",
        "4. ADAPTIVE_OPTIMIZATION: Dynamic adaptation",
        "5. PREDICTIVE_INTELLIGENCE: Proactive assistance",
        "6. AUTONOMOUS_MASTERY: Self-directed operation"
    ]
    
    for level in maturity_levels:
        print(f"   {level}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AKIS Demo Script")
    parser.add_argument(
        "--mode", 
        choices=['full', 'manifests', 'ontology'],
        default='full',
        help="Demo mode"
    )
    
    args = parser.parse_args()
    
    if args.mode == 'full':
        demo_akis()
    elif args.mode == 'manifests':
        show_manifest_examples()
    elif args.mode == 'ontology':
        show_ontology_info()


if __name__ == "__main__":
    main()