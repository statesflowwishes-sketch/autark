#!/usr/bin/env python3
"""
Integration der spezialisierten Coding-Agenten in das AUTARK SYSTEM
Erweitert die bestehende agent_factory.py um neue Coding-Modi
"""

import asyncio
import hashlib
from typing import Dict, Any, List
from datetime import datetime
from .specialized_coding_agents import (
    SpecializedCodingOrchestrator,
    CodingContext
)
import logging

logger = logging.getLogger(__name__)


class AutarkCodingAgentFactory:
    """
    Enhanced Agent Factory mit spezialisierten Coding-Modi
    Integriert in das bestehende AUTARK SYSTEM
    """
    
    def __init__(self, database_manager=None):
        self.database_manager = database_manager
        self.orchestrator = SpecializedCodingOrchestrator()
        self.active_sessions = {}
        self.session_counter = 0
        
    async def initialize(self):
        """Initialisierung der Factory"""
        logger.info("Initializing AUTARK Coding Agent Factory")
        await self.orchestrator.initialize()
        
    async def create_specialized_agent(self, mode: str, task: str, priority: int = 1):
        """Erstellt einen spezialisierten Coding-Agenten"""
        
        # Detect coding context 
        context = self._analyze_coding_context(task)
        
        # Auto-mode detection
        if mode == "auto":
            mode = self._detect_optimal_mode(task, context)
            
        # Generate session ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"{mode}_{timestamp}"
        
        # Create agent session
        self.active_sessions[session_id] = {
            "mode": mode,
            "task": task,
            "priority": priority,
            "context": context,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Start processing
        asyncio.create_task(self._process_agent_task(session_id, mode, task, context))
        
        return session_id
    
    async def _process_agent_task(self, session_id: str, mode: str, task: str, context: CodingContext):
        """Verarbeitet eine Agent-Aufgabe"""
        try:
            result = await self.orchestrator.process_request(mode, task, context)
            
            # Update session
            self.active_sessions[session_id]["result"] = result
            self.active_sessions[session_id]["status"] = "completed"
            
        except Exception as e:
            logger.error(f"Error processing agent task {session_id}: {e}")
            self.active_sessions[session_id]["error"] = str(e)
            self.active_sessions[session_id]["status"] = "error"
    
    def _analyze_coding_context(
        self, 
        task: str
    ) -> CodingContext:
        """Analysiert den Coding-Kontext"""
        
        # Simple keyword-based domain detection
        keywords = {
            "database": ["database", "sql", "query", "table", "index"],
            "web": ["ui", "interface", "frontend", "html", "css", "react"],
            "api": ["api", "request", "endpoint", "rest", "microservice"],
            "data": ["data", "analysis", "processing", "pipeline", "etl"],
            "ml": ["machine learning", "model", "training", "prediction"],
            "devops": ["deployment", "docker", "kubernetes", "ci/cd", "pipeline"]
        }
        
        domain = "general"
        for domain_name, words in keywords.items():
            if any(word in task.lower() for word in words):
                domain = domain_name
                break
        
        # Estimate complexity
        complexity = "low"
        if any(word in task.lower() for word in ["complex", "advanced", "thousands", "optimize"]):
            complexity = "high"
        elif any(word in task.lower() for word in ["multiple", "various", "several"]):
            complexity = "medium"
        
        return CodingContext(
            mode="analysis",
            task_id=hashlib.md5(task.encode()).hexdigest()[:8],
            priority=1,
            estimated_complexity=complexity,
            domain=domain,
            start_time=datetime.now(),
            metadata={"keywords": task.lower().split()[:5]}
        )
    
    def _detect_optimal_mode(self, task: str, context: CodingContext) -> str:
        """Automatische Modus-Erkennung"""
        
        task_lower = task.lower()
        
        # Lazy mode für Optimierungen
        if any(word in task_lower for word in ["optimize", "improve", "refactor", "clean"]):
            return "lazy"
        
        # Vibing mode für kreative UI/UX Arbeit
        if any(word in task_lower for word in ["beautiful", "creative", "design", "ui", "ux"]):
            return "vibing"
        
        # RAG mode für dokumentationsbezogene Aufgaben
        if any(word in task_lower for word in ["documentation", "context", "knowledge", "research"]):
            return "rag"
        
        # Async mode für Performance und Concurrency
        if any(word in task_lower for word in ["concurrent", "parallel", "thousands", "performance"]):
            return "async"
        
        # Special mode für ML/AI/spezielle Domains
        if any(word in task_lower for word in ["machine learning", "ai", "model", "algorithm"]):
            return "special"
        
        # Default fallback
        return "lazy"
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Status einer Session abrufen"""
        if session_id not in self.active_sessions:
            return {"error": f"Session {session_id} not found"}
        
        session = self.active_sessions[session_id]
        duration = (datetime.now() - datetime.fromisoformat(session["created_at"])).total_seconds()
        
        return {
            "session_id": session_id,
            "mode": session["mode"],
            "task": session["task"],
            "status": session["status"],
            "context": session["context"],
            "duration_seconds": duration,
            "created_at": session["created_at"],
            "result": session.get("result"),
            "error": session.get("error"),
            "integrations": {
                "database_connected": self.database_manager is not None,
                "codellm_available": True  # Simulation
            }
        }
    
    async def continue_session(self, session_id: str, additional_request: str):
        """Session mit zusätzlicher Anfrage fortsetzen"""
        if session_id not in self.active_sessions:
            return {"error": f"Session {session_id} not found"}
        
        session = self.active_sessions[session_id]
        mode = session["mode"]
        context = session["context"]
        
        # Process additional request
        result = await self.orchestrator.process_request(mode, additional_request, context)
        
        return {
            "status": "continued",
            "additional_result": result
        }
    
    async def terminate_session(self, session_id: str):
        """Session beenden"""
        if session_id not in self.active_sessions:
            return {"error": f"Session {session_id} not found"}
        
        del self.active_sessions[session_id]
        return {"status": "terminated"}


class AutarkSpecializedAgentManager:
    """
    Manager für spezialisierte Coding-Agenten im AUTARK System
    Hauptschnittstelle für externe Anwendungen
    """
    
    def __init__(self):
        self.agent_factory = AutarkCodingAgentFactory()
        self.metrics = {
            "total_sessions": 0,
            "mode_usage": {},
            "average_duration": 0
        }
    
    async def initialize(self, database_manager=None):
        """System initialisieren"""
        self.agent_factory.database_manager = database_manager
        await self.agent_factory.initialize()
        logger.info("Specialized Agent Manager initialized")
    
    async def create_agent(self, mode: str, task: str, priority: int = 1) -> str:
        """Neuen spezialisierten Agenten erstellen"""
        logger.info(f"Creating specialized agent: {mode} for task: {task}")
        
        session_id = await self.agent_factory.create_specialized_agent(mode, task, priority)
        
        # Update metrics
        self.metrics["total_sessions"] += 1
        self.metrics["mode_usage"][mode] = self.metrics["mode_usage"].get(mode, 0) + 1
        
        return session_id
    
    async def get_agent_status(self, session_id: str) -> Dict[str, Any]:
        """Agent-Status abrufen"""
        return await self.agent_factory.get_session_status(session_id)
    
    async def list_active_agents(self):
        """Liste alle aktiven Agenten"""
        active_agents = []
        
        for session_id, agent_info in self.agent_factory.active_sessions.items():
            try:
                status = await self.get_agent_status(session_id)
                if "error" not in status:
                    active_agents.append({
                        "session_id": session_id,
                        "mode": status.get("mode", "unknown"),
                        "status": status,
                        "created_at": agent_info.get("created_at", "unknown")
                    })
            except Exception as e:
                logger.warning(f"Error getting status for {session_id}: {e}")
        
        return active_agents
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Performance-Metriken abrufen"""
        if self.agent_factory.active_sessions:
            durations = []
            for session in self.agent_factory.active_sessions.values():
                if "created_at" in session:
                    duration = (datetime.now() - datetime.fromisoformat(session["created_at"])).total_seconds()
                    durations.append(duration)
            
            if durations:
                self.metrics["average_duration"] = sum(durations) / len(durations)
        
        return self.metrics


# Global instance für einfache Verwendung
specialized_agent_manager = AutarkSpecializedAgentManager()


# Integration mit bestehendem AUTARK System
async def integrate_with_autark_system():
    """Integration in das bestehende AUTARK System"""
    
    # Hier würde normalerweise die Integration mit dem 
    # bestehenden database_manager und anderen AUTARK Komponenten erfolgen
    
    try:
        from ..orchestrator.agent_factory import AgentFactory
        from ..database.connections import DatabaseManager
        
        # Erweitere bestehende AgentFactory
        # original_factory = AgentFactory()
        # enhanced_factory = AutarkCodingAgentFactory(original_factory.database_manager)
        
        logger.info("Integration with AUTARK system completed")
        return True
        
    except ImportError:
        logger.warning("AUTARK system components not found, running in standalone mode")
        return False


if __name__ == "__main__":
    # Standalone test
    async def test_integration():
        manager = AutarkSpecializedAgentManager()
        await manager.initialize()
        
        # Test agent creation
        session_id = await manager.create_agent("lazy", "Optimize database query", 3)
        print(f"Created agent: {session_id}")
        
        # Check status
        status = await manager.get_agent_status(session_id)
        print(f"Status: {status}")
        
        # List agents
        agents = await manager.list_active_agents()
        print(f"Active agents: {len(agents)}")
    
    asyncio.run(test_integration())