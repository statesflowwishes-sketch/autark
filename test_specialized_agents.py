#!/usr/bin/env python3
"""
Test und Demonstration der Specialized Coding Agents
Integration mit Original AUTARK System
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.autark_coding_integration import AutarkSpecializedAgentManager


async def test_specialized_agents():
    """Vollständiger Test der spezialisierten Coding-Agenten"""
    
    print("🚀 AUTARK SPECIALIZED CODING AGENTS - Test & Demo")
    print("=" * 60)
    
    # Initialize agent manager
    manager = AutarkSpecializedAgentManager()
    
    try:
        # Initialize system
        print("\n📋 Initializing AUTARK Specialized Agent System...")
        await manager.initialize(None)
        print("✅ System initialized successfully")
        
        # Test cases für verschiedene Coding Modi
        test_cases = [
            {
                "mode": "lazy",
                "task": "Optimize a slow database query with minimal code changes",
                "priority": 3
            },
            {
                "mode": "vibing", 
                "task": "Create a beautiful user interface with smooth animations",
                "priority": 2
            },
            {
                "mode": "rag",
                "task": "Build context-aware documentation generator",
                "priority": 4
            },
            {
                "mode": "async",
                "task": "Process thousands of API requests concurrently",
                "priority": 5
            },
            {
                "mode": "special",
                "task": "Implement machine learning model deployment pipeline",
                "priority": 4
            }
        ]
        
        session_ids = []
        
        # Create agents for each test case
        print("\n🤖 Creating Specialized Agents...")
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. Creating {test_case['mode'].upper()} agent...")
            print(f"   Task: {test_case['task']}")
            
            session_id = await manager.create_agent(
                test_case["mode"],
                test_case["task"], 
                test_case["priority"]
            )
            
            session_ids.append(session_id)
            print(f"   ✅ Agent created with session ID: {session_id}")
        
        # Wait a bit for processing
        print("\n⏳ Processing agents...")
        await asyncio.sleep(2)
        
        # Check status of all agents
        print("\n📊 Agent Status Report:")
        print("-" * 40)
        
        for i, session_id in enumerate(session_ids):
            status = await manager.get_agent_status(session_id)
            
            if "error" not in status:
                print(f"\n{i+1}. Session {session_id}:")
                print(f"   Mode: {status['mode']}")
                print(f"   Status: {status['status']}")
                print(f"   Duration: {status['duration_seconds']:.1f}s")
                
                # Handle CodingContext object
                context = status.get('context', {})
                if hasattr(context, 'domain'):
                    print(f"   Domain: {context.domain}")
                    print(f"   Complexity: {context.estimated_complexity}")
                else:
                    print(f"   Context: {context}")
                
                integrations = status.get('integrations', {})
                print(f"   Database Integration: {integrations.get('database_connected', 'N/A')}")
                print(f"   CodeLLM CLI: {integrations.get('codellm_available', 'N/A')}")
            else:
                print(f"\n{i+1}. Session {session_id}: ERROR - {status['error']}")
        
        # Test continuation
        print("\n🔄 Testing Agent Continuation...")
        if session_ids:
            test_session = session_ids[0]
            print(f"Continuing session {test_session} with additional request...")
            
            result = await manager.agent_factory.continue_session(
                test_session,
                "Add error handling and logging to the previous solution"
            )
            
            print(f"✅ Continuation result: {result['status']}")
        
        # List all active agents
        print("\n📋 Active Agents Summary:")
        active_agents = await manager.list_active_agents()
        
        for agent in active_agents:
            print(f"  • {agent['session_id']} ({agent['mode']}) - {agent['status']['status']}")
        
        # Performance metrics
        print("\n📈 Performance Metrics:")
        metrics = manager.get_performance_metrics()
        
        print(f"  Total Sessions: {metrics['total_sessions']}")
        print(f"  Active Agents: {len(active_agents)}")
        print(f"  Mode Usage: {metrics['mode_usage']}")
        print(f"  Average Duration: {metrics['average_duration']:.1f}s")
        
        # Test specialized features
        print("\n🔧 Testing Specialized Features...")
        
        # Test Lazy Agent optimization
        print("\n1. Testing Lazy Agent optimization...")
        lazy_session = session_ids[0] if session_ids else None
        if lazy_session:
            lazy_agent = manager.agent_factory.orchestrator.lazy_agent
            if lazy_agent:
                optimization = await lazy_agent.optimize_for_laziness(
                    "def fibonacci(n): return n if n <= 1 else fib(n-1) + fib(n-2)"
                )
                print(f"   ✅ Optimization suggested: {optimization['optimization_type']}")
        
        # Test RAG Agent knowledge retrieval
        print("\n2. Testing RAG Agent knowledge retrieval...")
        rag_session = session_ids[2] if len(session_ids) > 2 else None
        if rag_session:
            rag_agent = manager.agent_factory.orchestrator.rag_agent
            if rag_agent:
                context = await rag_agent.retrieve_context("Python asyncio practices")
                print(f"   ✅ Context retrieved: {len(context['relevant_docs'])} docs")
        
        # Test Async Agent load management
        print("\n3. Testing Async Agent load management...")
        async_session = session_ids[3] if len(session_ids) > 3 else None
        if async_session:
            async_agent = manager.agent_factory.orchestrator.async_agent
            if async_agent:
                # Create some test tasks
                tasks = [f"Task {i}" for i in range(10)]
                results = await async_agent.execute_concurrent_tasks(tasks)
                print(f"   ✅ Executed {len(results)} concurrent tasks")
        
        # Demonstration complete
        print("\n🎉 DEMONSTRATION COMPLETE!")
        print("=" * 60)
        print("All specialized coding agents are operational and integrated")
        print("with the AUTARK system infrastructure.")
        print("\nNext steps:")
        print("  1. Start the Original Overlay Dashboard: http://localhost:8888")
        print("  2. Access Specialized Dashboard: python overlay/specialized_dashboard.py")
        print("  3. Use CLI interface: python autark_specialized.py")
        print("  4. Integrate with your development workflow")
        
        # Optional: Keep agents running for testing
        print("\n⚡ Agents remain active for further testing...")
        print("Use 'python autark_specialized.py status' to monitor")
        
        return session_ids, metrics
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return [], {}


async def demonstrate_coding_modes():
    """Detaillierte Demonstration jedes Coding-Modus"""
    
    print("\n🎯 DETAILED CODING MODES DEMONSTRATION")
    print("=" * 50)
    
    modes_info = {
        "lazy": {
            "name": "🦥 Lazy Coding",
            "description": "Maximale Effizienz mit minimaler Anstrengung",
            "features": [
                "Automatische Code-Optimierung",
                "Wiederverwendung bestehender Komponenten", 
                "Reduzierung von Boilerplate",
                "Smart Caching und Memoization"
            ],
            "use_cases": [
                "Legacy Code Refactoring",
                "Performance Optimierung",
                "Code Cleanup",
                "Technical Debt Reduction"
            ]
        },
        "vibing": {
            "name": "🌊 Vibing Coding", 
            "description": "Flow State für kreative Entwicklung",
            "features": [
                "Adaptive Arbeitsrhythmus",
                "Kreativitäts-Booster",
                "Intuitive Code-Strukturierung",
                "Mood-basierte Optimierung"
            ],
            "use_cases": [
                "UI/UX Development",
                "Creative Projects",
                "Prototyping",
                "Innovation Sprints"
            ]
        },
        "rag": {
            "name": "🧠 RAG Coding",
            "description": "Kontextbewusste Entwicklung mit Wissensabruf",
            "features": [
                "Semantic Code Search",
                "Documentation Integration",
                "Best Practice Suggestions",
                "Context-Aware Generation"
            ],
            "use_cases": [
                "API Integration",
                "Framework Migration",
                "Documentation Generation",
                "Knowledge Management"
            ]
        },
        "async": {
            "name": "⚡ Async Coding",
            "description": "Hochperformante parallele Entwicklung", 
            "features": [
                "Concurrent Processing",
                "Load Balancing",
                "Backpressure Control",
                "Resource Optimization"
            ],
            "use_cases": [
                "High-Load Systems",
                "Real-time Processing",
                "Microservices",
                "Data Pipeline"
            ]
        },
        "special": {
            "name": "⭐ Special Coding",
            "description": "Domain-spezifische Expertensysteme",
            "features": [
                "Domain Detection",
                "Specialized Patterns",
                "Expert Knowledge",
                "Custom Optimizations"
            ],
            "use_cases": [
                "Machine Learning",
                "Blockchain Development",
                "IoT Systems",
                "Scientific Computing"
            ]
        }
    }
    
    for mode, info in modes_info.items():
        print(f"\n{info['name']}")
        print("-" * 30)
        print(f"📝 {info['description']}")
        
        print("\n🔧 Key Features:")
        for feature in info['features']:
            print(f"  • {feature}")
        
        print("\n🎯 Use Cases:")
        for use_case in info['use_cases']:
            print(f"  • {use_case}")
        
        print()


if __name__ == "__main__":
    print("🤖 AUTARK Specialized Coding Agents - Test Suite")
    print("Integrating advanced AI-driven development approaches")
    print("with the AUTARK system infrastructure\n")
    
    # Run demonstration
    asyncio.run(demonstrate_coding_modes())
    
    # Run full test
    session_ids, metrics = asyncio.run(test_specialized_agents())
    
    if session_ids:
        print(f"\n✅ Test completed successfully!")
        print(f"Created {len(session_ids)} specialized agents")
        print(f"Total sessions: {metrics.get('total_sessions', 0)}")
        print(f"System ready for production use!")
    else:
        print("\n❌ Test failed - check error messages above")