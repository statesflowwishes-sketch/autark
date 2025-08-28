"""
KI Agent Factory - Erweiterte Multi-Agent Orchestrierung
Erstellt und verwaltet verschiedene KI-Agents für autarke Codeentwicklung
"""

import asyncio
import logging
import json
import yaml
from typing import Dict, List, Any, Optional, Type, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Adapter Imports
from adapters.codellm import CodeLLMAdapter
from adapters.aider import AiderAdapter
from adapters.opendevin import OpenDevinAdapter
from adapters.swe_agent import SWEAgentAdapter

# Integration Imports
from integration.leap_client import LeapClient
from integration.leap_embedding_provider import LeapEmbeddingProvider

# Provider Imports
from orchestrator.providers.model_router import ModelRouter

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Verfügbare Agent-Typen"""
    CODELLM_CLI = "codellm_cli"
    AIDER_CLI = "aider_cli"
    HTTP_API = "http_api"
    PYTHON_MODULE = "python_module"
    LEAP_ORCHESTRATOR = "leap_orchestrator"
    MULTI_MODEL_ENSEMBLE = "multi_model_ensemble"
    PLANNER_AGENT = "planner_agent"
    EXECUTOR_AGENT = "executor_agent"
    REVIEWER_AGENT = "reviewer_agent"
    SECURITY_AGENT = "security_agent"

class AgentCapability(Enum):
    """Agent-Fähigkeiten"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DEBUGGING = "debugging"
    REFACTORING = "refactoring"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    SECURITY_ANALYSIS = "security_analysis"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    ARCHITECTURE_DESIGN = "architecture_design"
    PROJECT_PLANNING = "project_planning"

@dataclass
class AgentConfig:
    """Konfiguration für einen Agent"""
    agent_id: str
    agent_type: AgentType
    capabilities: List[AgentCapability]
    model_config: Dict[str, Any]
    sandbox_tier: str = "medium"
    cost_budget_usd: float = 5.0
    time_budget_minutes: int = 60
    max_iterations: int = 8
    priority: int = 100
    enabled: bool = True
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class AgentInstance:
    """Instanz eines aktiven Agents"""
    config: AgentConfig
    adapter: Any
    status: str = "initialized"
    current_task: Optional[str] = None
    cost_spent: float = 0.0
    time_spent: int = 0
    iterations_done: int = 0
    last_activity: Optional[str] = None
    metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}

class AgentFactory:
    """Erweiterte Agent Factory für Multi-Agent Orchestrierung"""
    
    def __init__(self, config_path: str = "/opt/ki-agent/src/agents.yaml"):
        self.config_path = Path(config_path)
        self.agents_config: Dict[str, Any] = {}
        self.active_agents: Dict[str, AgentInstance] = {}
        self.model_router: Optional[ModelRouter] = None
        self.leap_client: Optional[LeapClient] = None
        self.embedding_provider: Optional[LeapEmbeddingProvider] = None
        
        # Agent Class Registry
        self.agent_classes = {
            AgentType.CODELLM_CLI: CodeLLMAdapter,
            AgentType.AIDER_CLI: AiderAdapter,
            AgentType.HTTP_API: OpenDevinAdapter,
            AgentType.PYTHON_MODULE: SWEAgentAdapter,
            AgentType.LEAP_ORCHESTRATOR: self._create_leap_orchestrator,
            AgentType.MULTI_MODEL_ENSEMBLE: self._create_ensemble_agent,
            AgentType.PLANNER_AGENT: self._create_planner_agent,
            AgentType.EXECUTOR_AGENT: self._create_executor_agent,
            AgentType.REVIEWER_AGENT: self._create_reviewer_agent,
            AgentType.SECURITY_AGENT: self._create_security_agent
        }
    
    async def initialize(self):
        """Initialisiere die Agent Factory"""
        logger.info("🔧 Initialisiere Agent Factory...")
        
        try:
            # Lade Konfiguration
            await self._load_config()
            
            # Initialisiere Model Router
            self.model_router = ModelRouter()
            await self.model_router.initialize()
            
            # Initialisiere LEAP Integration
            self.leap_client = LeapClient()
            await self.leap_client.initialize()
            
            self.embedding_provider = LeapEmbeddingProvider()
            await self.embedding_provider.initialize()
            
            # Lade Standard-Agents
            await self._initialize_default_agents()
            
            logger.info("✅ Agent Factory erfolgreich initialisiert")
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Agent Factory Initialisierung: {e}")
            raise
    
    async def _load_config(self):
        """Lade Agent-Konfiguration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.agents_config = yaml.safe_load(f)
                logger.info(f"✅ Konfiguration geladen: {self.config_path}")
            else:
                logger.warning(f"⚠️  Konfigurationsdatei nicht gefunden: {self.config_path}")
                self.agents_config = self._get_default_config()
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Konfiguration: {e}")
            self.agents_config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Standard-Konfiguration falls keine Datei vorhanden"""
        return {
            "agents": {
                "primary_codellm": {
                    "type": "codellm_cli",
                    "binary": "/usr/local/bin/codellm",
                    "capabilities": ["code_generation", "debugging", "refactoring"],
                    "sandbox_tier": "medium",
                    "cost_budget_usd": 10.0,
                    "priority": 100
                },
                "secondary_aider": {
                    "type": "aider_cli", 
                    "binary": "/usr/local/bin/aider",
                    "capabilities": ["code_review", "documentation"],
                    "sandbox_tier": "low",
                    "cost_budget_usd": 5.0,
                    "priority": 80
                },
                "leap_orchestrator": {
                    "type": "leap_orchestrator",
                    "capabilities": ["project_planning", "architecture_design"],
                    "sandbox_tier": "high",
                    "cost_budget_usd": 15.0,
                    "priority": 90
                }
            }
        }
    
    async def _initialize_default_agents(self):
        """Initialisiere Standard-Agents"""
        agents_config = self.agents_config.get("agents", {})
        
        for agent_id, config in agents_config.items():
            try:
                await self.create_agent(agent_id, config)
                logger.info(f"✅ Agent '{agent_id}' erfolgreich erstellt")
            except Exception as e:
                logger.error(f"❌ Fehler beim Erstellen von Agent '{agent_id}': {e}")
    
    async def create_agent(self, agent_id: str, config: Dict[str, Any]) -> AgentInstance:
        """Erstelle einen neuen Agent"""
        try:
            # Parse Agent Type
            agent_type_str = config.get("type", "codellm_cli")
            agent_type = AgentType(agent_type_str)
            
            # Parse Capabilities
            capabilities_str = config.get("capabilities", ["code_generation"])
            capabilities = [AgentCapability(cap) for cap in capabilities_str]
            
            # Erstelle Agent Config
            agent_config = AgentConfig(
                agent_id=agent_id,
                agent_type=agent_type,
                capabilities=capabilities,
                model_config=config.get("model_config", {}),
                sandbox_tier=config.get("sandbox_tier", "medium"),
                cost_budget_usd=config.get("cost_budget_usd", 5.0),
                time_budget_minutes=config.get("time_budget_minutes", 60),
                max_iterations=config.get("max_iterations", 8),
                priority=config.get("priority", 100),
                enabled=config.get("enabled", True),
                metadata=config.get("metadata", {})
            )
            
            # Erstelle Agent Adapter
            adapter = await self._create_agent_adapter(agent_config, config)
            
            # Erstelle Agent Instance
            agent_instance = AgentInstance(
                config=agent_config,
                adapter=adapter
            )
            
            # Registriere Agent
            self.active_agents[agent_id] = agent_instance
            
            logger.info(f"✅ Agent '{agent_id}' vom Typ '{agent_type.value}' erstellt")
            return agent_instance
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Erstellen von Agent '{agent_id}': {e}")
            raise
    
    async def _create_agent_adapter(self, agent_config: AgentConfig, config: Dict[str, Any]):
        """Erstelle den entsprechenden Agent Adapter"""
        agent_type = agent_config.agent_type
        
        if agent_type == AgentType.CODELLM_CLI:
            return CodeLLMAdapter(config.get("binary", "/usr/local/bin/codellm"))
        
        elif agent_type == AgentType.AIDER_CLI:
            return AiderAdapter(config.get("binary", "/usr/local/bin/aider"))
        
        elif agent_type == AgentType.HTTP_API:
            return OpenDevinAdapter(config.get("endpoint", "http://localhost:8000"))
        
        elif agent_type == AgentType.PYTHON_MODULE:
            return SWEAgentAdapter(config.get("module", "swe_agent"))
        
        elif agent_type in self.agent_classes:
            # Verwende Custom Agent Creator
            creator_func = self.agent_classes[agent_type]
            if callable(creator_func):
                return await creator_func(agent_config, config)
        
        else:
            raise ValueError(f"Unbekannter Agent-Typ: {agent_type}")
    
    async def _create_leap_orchestrator(self, agent_config: AgentConfig, config: Dict[str, Any]):
        """Erstelle LEAP Orchestrator Agent"""
        from agents.leap_orchestrator_agent import LeapOrchestratorAgent
        return LeapOrchestratorAgent(
            leap_client=self.leap_client,
            embedding_provider=self.embedding_provider,
            config=agent_config
        )
    
    async def _create_ensemble_agent(self, agent_config: AgentConfig, config: Dict[str, Any]):
        """Erstelle Multi-Model Ensemble Agent"""
        from agents.ensemble_agent import EnsembleAgent
        return EnsembleAgent(
            model_router=self.model_router,
            config=agent_config
        )
    
    async def _create_planner_agent(self, agent_config: AgentConfig, config: Dict[str, Any]):
        """Erstelle Planner Agent"""
        from agents.planner_agent import PlannerAgent
        return PlannerAgent(config=agent_config)
    
    async def _create_executor_agent(self, agent_config: AgentConfig, config: Dict[str, Any]):
        """Erstelle Executor Agent"""
        from agents.executor_agent import ExecutorAgent
        return ExecutorAgent(config=agent_config)
    
    async def _create_reviewer_agent(self, agent_config: AgentConfig, config: Dict[str, Any]):
        """Erstelle Reviewer Agent"""
        from agents.reviewer_agent import ReviewerAgent
        return ReviewerAgent(config=agent_config)
    
    async def _create_security_agent(self, agent_config: AgentConfig, config: Dict[str, Any]):
        """Erstelle Security Agent"""
        from agents.security_agent import SecurityAgent
        return SecurityAgent(config=agent_config)
    
    async def get_agent(self, agent_id: str) -> Optional[AgentInstance]:
        """Hole einen Agent anhand seiner ID"""
        return self.active_agents.get(agent_id)
    
    async def get_agents_by_capability(self, capability: AgentCapability) -> List[AgentInstance]:
        """Hole alle Agents mit einer bestimmten Fähigkeit"""
        matching_agents = []
        for agent in self.active_agents.values():
            if capability in agent.config.capabilities and agent.config.enabled:
                matching_agents.append(agent)
        
        # Sortiere nach Priorität
        matching_agents.sort(key=lambda a: a.config.priority, reverse=True)
        return matching_agents
    
    async def select_best_agent(
        self, 
        task_type: str, 
        capabilities_needed: List[AgentCapability],
        budget_constraint: Optional[float] = None
    ) -> Optional[AgentInstance]:
        """Wähle den besten Agent für eine Aufgabe"""
        
        candidate_agents = []
        
        # Finde Agents mit benötigten Fähigkeiten
        for capability in capabilities_needed:
            agents = await self.get_agents_by_capability(capability)
            candidate_agents.extend(agents)
        
        if not candidate_agents:
            logger.warning(f"Keine Agents für Fähigkeiten gefunden: {capabilities_needed}")
            return None
        
        # Filtere nach Budget falls angegeben
        if budget_constraint:
            candidate_agents = [
                agent for agent in candidate_agents 
                if agent.config.cost_budget_usd >= budget_constraint
            ]
        
        # Filtere verfügbare Agents
        available_agents = [
            agent for agent in candidate_agents 
            if agent.status in ["initialized", "idle"] and agent.config.enabled
        ]
        
        if not available_agents:
            logger.warning("Keine verfügbaren Agents gefunden")
            return None
        
        # Wähle Agent mit höchster Priorität
        best_agent = max(available_agents, key=lambda a: a.config.priority)
        
        logger.info(f"✅ Agent '{best_agent.config.agent_id}' ausgewählt für Task: {task_type}")
        return best_agent
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Hole Status aller Agents"""
        status = {
            "total_agents": len(self.active_agents),
            "active_agents": sum(1 for a in self.active_agents.values() if a.status == "active"),
            "idle_agents": sum(1 for a in self.active_agents.values() if a.status == "idle"),
            "agents": {}
        }
        
        for agent_id, agent in self.active_agents.items():
            status["agents"][agent_id] = {
                "type": agent.config.agent_type.value,
                "status": agent.status,
                "capabilities": [cap.value for cap in agent.config.capabilities],
                "cost_spent": agent.cost_spent,
                "time_spent": agent.time_spent,
                "iterations_done": agent.iterations_done,
                "current_task": agent.current_task
            }
        
        return status
    
    async def shutdown(self):
        """Fahre alle Agents herunter"""
        logger.info("🛑 Fahre Agent Factory herunter...")
        
        for agent_id, agent in self.active_agents.items():
            try:
                if hasattr(agent.adapter, 'shutdown'):
                    await agent.adapter.shutdown()
                logger.info(f"✅ Agent '{agent_id}' heruntergefahren")
            except Exception as e:
                logger.error(f"❌ Fehler beim Herunterfahren von Agent '{agent_id}': {e}")
        
        self.active_agents.clear()
        
        if self.model_router:
            await self.model_router.shutdown()
        
        if self.leap_client:
            await self.leap_client.shutdown()
        
        logger.info("✅ Agent Factory heruntergefahren")

# Legacy Funktion für Rückwärtskompatibilität
def build(agent_cfg):
    """Legacy Builder Funktion"""
    logger.warning("⚠️  Legacy 'build()' Funktion verwendet - verwende AgentFactory.create_agent()")
    
    agent_type = agent_cfg.get("type", "codellm_cli")
    
    if agent_type == "codellm_cli":
        return CodeLLMAdapter(agent_cfg.get("binary", "/usr/local/bin/codellm"))
    elif agent_type == "aider_cli":
        return AiderAdapter(agent_cfg.get("binary", "/usr/local/bin/aider"))
    elif agent_type == "http_api":
        return OpenDevinAdapter(agent_cfg.get("endpoint", "http://localhost:8000"))
    elif agent_type == "python_module":
        return SWEAgentAdapter(agent_cfg.get("module", "swe_agent"))
    else:
        raise ValueError(f"Unbekannter Agent-Typ: {agent_type}")