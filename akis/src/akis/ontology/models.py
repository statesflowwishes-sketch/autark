"""
AKIS Ontology Models
===================

Datenmodelle für das AUTARK Knowledge Integration System.
Implementiert die 7-Schichten-Architektur mit Lernkurven-Integration.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union
from enum import Enum
import datetime
import uuid

class MaturityLevel(Enum):
    """Maturity Level für Tools und Capabilities"""
    AWARENESS = 0           # Bewusstsein
    BASIC_EXECUTION = 1     # Grundlegende Ausführung
    EFFICIENT_EXECUTION = 2 # Effiziente Ausführung
    ADAPTIVE_OPTIMIZATION = 3  # Adaptive Optimierung
    PREDICTIVE_PROACTIVE = 4   # Prädiktiv/Proaktiv
    AUTONOMOUS_SELF_TUNING = 5 # Autonome Selbstoptimierung

class RiskLevel(Enum):
    """Risiko-Level für Tools und Operationen"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceTag(Enum):
    """Compliance-Tags für Governance"""
    GDPR = "gdpr"
    ISO27001 = "iso27001"
    SOC2 = "soc2"
    PRIVACY = "privacy"
    EU_AI_ACT = "eu_ai_act"
    DATA_GOVERNANCE = "data_governance"
    CONTENT_POLICY = "content_policy"

@dataclass
class LearningCurveLevel:
    """Einzelner Level in einer Lernkurve"""
    level: MaturityLevel
    description: str
    expected_accuracy: float      # 0.0 - 1.0
    max_latency_ms: int          # Maximale Latenz in ms
    risk_factor: float           # 0.0 - 1.0 (niedriger = weniger Risiko)
    min_evidence_docs: int       # Mindestanzahl Evidenz-Dokumente
    required_capabilities: List[str] = field(default_factory=list)
    typical_errors: List[str] = field(default_factory=list)
    recovery_strategies: List[str] = field(default_factory=list)

@dataclass
class MaturityProfile:
    """Komplette Lernkurve für eine Capability"""
    profile_id: str
    name: str
    description: str
    levels: List[LearningCurveLevel] = field(default_factory=list)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    
    def get_level(self, level: MaturityLevel) -> Optional[LearningCurveLevel]:
        """Hole spezifischen Level aus der Lernkurve"""
        for curve_level in self.levels:
            if curve_level.level == level:
                return curve_level
        return None

@dataclass
class BenchmarkMetric:
    """Einzelne Benchmark-Metrik"""
    name: str
    target_value: Union[float, int, str]
    tolerance: float = 0.05
    unit: str = ""
    description: str = ""

@dataclass
class BenchmarkCase:
    """Test-Case für Capability-Validierung"""
    case_id: str
    capability_ref: str
    description: str
    input_data: Dict[str, Any]
    expected_outcome: Any
    target_metrics: List[BenchmarkMetric] = field(default_factory=list)
    success_criteria: str = ""
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    last_run: Optional[datetime.datetime] = None
    last_result: Optional[Dict[str, Any]] = None

@dataclass
class Capability:
    """Fähigkeit eines Tools oder Systems"""
    capability_id: str
    name: str
    description: str
    domain: str
    primary_concepts: List[str] = field(default_factory=list)
    required_inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    maturity_profile_id: str = ""
    maturity_profile: Optional[MaturityProfile] = None
    benchmarks: List[BenchmarkCase] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    def get_current_maturity_level(self) -> MaturityLevel:
        """Bestimme aktuelles Maturity Level basierend auf Benchmarks"""
        if not self.maturity_profile or not self.benchmarks:
            return MaturityLevel.AWARENESS
        
        # Vereinfachte Logik - kann erweitert werden
        successful_benchmarks = sum(1 for b in self.benchmarks if b.last_result and b.last_result.get('success', False))
        total_benchmarks = len(self.benchmarks)
        
        if total_benchmarks == 0:
            return MaturityLevel.AWARENESS
        
        success_rate = successful_benchmarks / total_benchmarks
        
        if success_rate >= 0.95:
            return MaturityLevel.AUTONOMOUS_SELF_TUNING
        elif success_rate >= 0.90:
            return MaturityLevel.PREDICTIVE_PROACTIVE
        elif success_rate >= 0.85:
            return MaturityLevel.ADAPTIVE_OPTIMIZATION
        elif success_rate >= 0.75:
            return MaturityLevel.EFFICIENT_EXECUTION
        elif success_rate >= 0.60:
            return MaturityLevel.BASIC_EXECUTION
        else:
            return MaturityLevel.AWARENESS

@dataclass
class Tool:
    """Tool oder System im AKIS"""
    tool_id: str
    name: str
    version: str
    vendor: str
    description: str = ""
    capabilities: List[str] = field(default_factory=list)  # Capability IDs
    compliance_tags: List[ComplianceTag] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.MEDIUM
    documentation_sources: List[Dict[str, str]] = field(default_factory=list)
    last_review: datetime.date = field(default_factory=datetime.date.today)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_compliant_with(self, required_tags: List[ComplianceTag]) -> bool:
        """Prüfe ob Tool alle erforderlichen Compliance-Tags hat"""
        return all(tag in self.compliance_tags for tag in required_tags)

@dataclass
class DocumentChunk:
    """Chunk eines verarbeiteten Dokuments"""
    chunk_id: str
    document_id: str
    content: str
    chunk_index: int
    tool_refs: List[str] = field(default_factory=list)
    capability_refs: List[str] = field(default_factory=list)
    concept_refs: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)

@dataclass
class Document:
    """Dokument im Knowledge Base"""
    document_id: str
    source_path: str
    source_type: str  # markdown, code, openapi, etc.
    title: str = ""
    content: str = ""
    chunks: List[DocumentChunk] = field(default_factory=list)
    tool_refs: List[str] = field(default_factory=list)
    capability_refs: List[str] = field(default_factory=list)
    compliance_classification: List[ComplianceTag] = field(default_factory=list)
    hash: str = ""
    version: str = "1.0"
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Concept:
    """Konzept in der Ontologie"""
    concept_id: str
    name: str
    description: str
    taxonomy_path: str  # z.B. "technology.ai.video.generation"
    synonyms: List[str] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)
    domain_tags: List[str] = field(default_factory=list)
    confidence_score: float = 1.0
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    
@dataclass
class Relation:
    """Relation zwischen Entitäten"""
    relation_id: str
    subject: str
    predicate: str
    object: str
    confidence: float = 1.0
    provenance: str = ""
    temporal_validity: Optional[Dict[str, datetime.datetime]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)

@dataclass
class PolicyRule:
    """Policy-Regel für Governance"""
    rule_id: str
    name: str
    description: str
    scope: str  # tool, capability, document, etc.
    rule_type: str  # access_control, redaction, compliance, etc.
    conditions: Dict[str, Any] = field(default_factory=dict)
    action: str = ""
    enforcement_level: str = "mandatory"  # mandatory, recommended, optional
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    active: bool = True

@dataclass
class KnowledgeSnapshot:
    """Snapshot der Knowledge Base"""
    snapshot_id: str
    created_at: datetime.datetime
    graph_hash: str
    vector_index_hash: str
    tool_versions: Dict[str, str] = field(default_factory=dict)
    coverage_metrics: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RetrievalContext:
    """Kontext für Knowledge Retrieval"""
    user_id: str = ""
    user_role: str = "default"
    capability_hint: str = ""
    required_maturity_level: MaturityLevel = MaturityLevel.BASIC_EXECUTION
    compliance_requirements: List[ComplianceTag] = field(default_factory=list)
    max_latency_ms: int = 5000
    min_confidence: float = 0.7
    max_results: int = 10
    include_code: bool = True
    include_examples: bool = True

def generate_id() -> str:
    """Generiere eindeutige ID"""
    return str(uuid.uuid4())

# Vordefinierte Maturity Profiles für häufige Use Cases
DEFAULT_MATURITY_PROFILES = {
    "video_generation_profile_v1": MaturityProfile(
        profile_id="video_generation_profile_v1",
        name="Video Generation Maturity",
        description="Lernkurve für AI Video Generation",
        levels=[
            LearningCurveLevel(
                level=MaturityLevel.AWARENESS,
                description="Bewusstsein für Video-AI Tools",
                expected_accuracy=0.6,
                max_latency_ms=30000,
                risk_factor=0.8,
                min_evidence_docs=5
            ),
            LearningCurveLevel(
                level=MaturityLevel.BASIC_EXECUTION,
                description="Grundlegende Videogenerierung",
                expected_accuracy=0.75,
                max_latency_ms=20000,
                risk_factor=0.6,
                min_evidence_docs=3
            ),
            LearningCurveLevel(
                level=MaturityLevel.EFFICIENT_EXECUTION,
                description="Effiziente Videoproduktion",
                expected_accuracy=0.85,
                max_latency_ms=15000,
                risk_factor=0.4,
                min_evidence_docs=2
            ),
            LearningCurveLevel(
                level=MaturityLevel.ADAPTIVE_OPTIMIZATION,
                description="Adaptive Optimierung",
                expected_accuracy=0.92,
                max_latency_ms=10000,
                risk_factor=0.3,
                min_evidence_docs=1
            ),
            LearningCurveLevel(
                level=MaturityLevel.PREDICTIVE_PROACTIVE,
                description="Prädiktive Videoproduktion",
                expected_accuracy=0.96,
                max_latency_ms=8000,
                risk_factor=0.2,
                min_evidence_docs=1
            ),
            LearningCurveLevel(
                level=MaturityLevel.AUTONOMOUS_SELF_TUNING,
                description="Autonome Selbstoptimierung",
                expected_accuracy=0.98,
                max_latency_ms=5000,
                risk_factor=0.1,
                min_evidence_docs=1
            )
        ]
    )
}