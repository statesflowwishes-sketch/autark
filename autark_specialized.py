#!/usr/bin/env python3
"""
AUTARK SYSTEM Launcher für spezialisierte Coding-Agenten
Erweitert das bestehende autark_launch.sh um neue Coding-Modi
"""

import asyncio
import sys
import json
from typing import Dict, Any
from agents.autark_coding_integration import specialized_agent_manager
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutarkSpecializedCLI:
    """CLI Interface für spezialisierte Coding-Agenten"""
    
    def __init__(self):
        self.manager = specialized_agent_manager
        self.commands = {
            "create": self.create_agent,
            "status": self.get_status, 
            "list": self.list_agents,
            "continue": self.continue_session,
            "terminate": self.terminate_agent,
            "metrics": self.show_metrics,
            "help": self.show_help
        }
    
    async def run(self, args: list):
        """Haupteinstiegspunkt für CLI"""
        if len(args) < 1:
            await self.show_help()
            return
        
        command = args[0]
        if command not in self.commands:
            print(f"Unknown command: {command}")
            await self.show_help()
            return
        
        try:
            await self.commands[command](args[1:])
        except Exception as e:
            logger.error(f"Error executing command {command}: {e}")
            print(f"Error: {e}")
    
    async def create_agent(self, args: list):
        """Erstellt neuen spezialisierten Agenten"""
        if len(args) < 2:
            print("Usage: create <mode> <task_description> [priority]")
            print("Modes: lazy, vibing, rag, async, special, auto")
            return
        
        mode = args[0]
        task = " ".join(args[1:-1]) if len(args) > 2 else args[1]
        priority = int(args[-1]) if args[-1].isdigit() else 1
        
        # Initialize manager if needed
        if not self.manager.agent_factory:
            await self.manager.initialize(None)  # Base orchestrator kommt später
        
        session_id = await self.manager.create_agent(mode, task, priority)
        
        print(f"""
🤖 AUTARK SPECIALIZED AGENT CREATED
=====================================
Session ID: {session_id}
Mode: {mode}
Task: {task}
Priority: {priority}
Status: Active

Access via Original Overlay: http://localhost:8888
        """)
    
    async def get_status(self, args: list):
        """Zeigt Status eines Agenten"""
        if len(args) < 1:
            print("Usage: status <session_id>")
            return
        
        session_id = args[0]
        status = await self.manager.get_agent_status(session_id)
        
        if "error" in status:
            print(f"Error: {status['error']}")
            return
        
        print(f"""
📊 AGENT STATUS
===============
Session ID: {session_id}
Mode: {status['mode']}
Status: {status['status']}
Duration: {status['duration_seconds']:.1f}s
Context: {status['context'].mode} | {status['context'].domain}
        """)
    
    async def list_agents(self, args: list):
        """Listet alle aktiven Agenten"""
        agents = await self.manager.list_active_agents()
        
        if not agents:
            print("No active agents")
            return
        
        print("\n🔍 ACTIVE SPECIALIZED AGENTS")
        print("=" * 40)
        
        for agent in agents:
            print(f"ID: {agent['session_id']}")
            print(f"Mode: {agent['mode']}")
            print(f"Duration: {agent['status']['duration_seconds']:.1f}s")
            print("-" * 30)
    
    async def continue_session(self, args: list):
        """Setzt Session mit neuem Request fort"""
        if len(args) < 2:
            print("Usage: continue <session_id> <additional_request>")
            return
        
        session_id = args[0]
        request = " ".join(args[1:])
        
        result = await self.manager.agent_factory.continue_session(
            session_id, request
        )
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return
        
        print(f"""
✅ SESSION CONTINUED
====================
Session ID: {session_id}
New Request: {request}
Status: {result['status']}
        """)
    
    async def terminate_agent(self, args: list):
        """Beendet einen Agenten"""
        if len(args) < 1:
            print("Usage: terminate <session_id>")
            return
        
        session_id = args[0]
        result = await self.manager.agent_factory.terminate_session(session_id)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return
        
        print(f"""
🛑 AGENT TERMINATED
===================
Session ID: {session_id}
Total Duration: {result['total_duration_seconds']:.1f}s
Status: {result['status']}
        """)
    
    async def show_metrics(self, args: list):
        """Zeigt Performance-Metriken"""
        metrics = self.manager.get_performance_metrics()
        
        print(f"""
📈 AUTARK SYSTEM PERFORMANCE METRICS
====================================
Total Sessions: {metrics['total_sessions']}

Mode Usage:
""")
        
        for mode, count in metrics['mode_usage'].items():
            print(f"  {mode}: {count}")
        
        print(f"""
Active Agents: {len(self.manager.active_agents)}
        """)
    
    async def show_help(self, args: list = None):
        """Zeigt Hilfe"""
        print("""
🚀 AUTARK SPECIALIZED CODING AGENTS CLI
=======================================

Commands:
  create <mode> <task> [priority]  - Create specialized agent
  status <session_id>              - Show agent status  
  list                             - List all active agents
  continue <session_id> <request>  - Continue session
  terminate <session_id>           - Terminate agent
  metrics                          - Show performance metrics
  help                             - Show this help

Modes:
  lazy     - Productive laziness & lazy evaluation
  vibing   - Flow state & creative development
  rag      - Retrieval-augmented generation
  async    - Asynchronous & concurrent programming  
  special  - Specialized domain patterns
  auto     - Automatic mode detection

Examples:
  python autark_specialized.py create lazy "data processing pipeline"
  python autark_specialized.py create rag "code with documentation context" 2
  python autark_specialized.py create async "parallel API calls"
  
Integration:
  Original Overlay: http://localhost:8888
  Databases: postgres:5433, redis:6380, qdrant:6334, mongo:27018, elasticsearch:9201
        """)


async def main():
    """Hauptfunktion"""
    cli = AutarkSpecializedCLI()
    await cli.run(sys.argv[1:])


if __name__ == "__main__":
    asyncio.run(main())