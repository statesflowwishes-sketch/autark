"""
AUTARK Knowledge Integration System (AKIS)
==========================================

Advanced Knowledge Management and Retrieval System for AUTARK.

AKIS provides:
- 7-Layer Architecture for Knowledge Management
- Hybrid Retrieval (Graph + Vector + Lexical)
- Skill-Level Adaptive Responses
- Tool Manifest Configuration
- Maturity Level Progression
- Governance & Compliance

Usage:
    from akis.retrieval.hybrid_retriever import AKISRetrievalEngine
    from akis.ontology.models import RetrievalContext, MaturityLevel
    
    engine = AKISRetrievalEngine(data_dir="./data")
    context = RetrievalContext(user_id="test")
    result = engine.query("How to create video?", context)

Architecture Layers:
    1. Storage Primitives
    2. Ingestion & Normalization  
    3. Ontology & Knowledge Graph
    4. Embeddings & Indices
    5. Reasoning Adapters
    6. Evaluation & Telemetrie
    7. Governance & Security
    8. Delivery
"""

__version__ = "0.1.0"
__author__ = "AUTARK Team"
__license__ = "MIT"

# Core imports
try:
    from .ontology.models import (
        MaturityLevel,
        Tool,
        Capability,
        Document,
        Concept,
        Relation,
        BenchmarkCase,
        PolicyRule,
        RetrievalContext,
        LearningCurveLevel
    )
    
    from .retrieval.hybrid_retriever import (
        AKISRetrievalEngine,
        KnowledgeGraph,
        VectorStore,
        LexicalSearch,
        SkillLevelAdaptiveRetriever
    )
    
    from .ingestion.pipeline import (
        IngestionPipeline,
        ToolManifestParser,
        DocumentProcessor,
        ConceptExtractor
    )
    
    # Make key classes available at package level
    __all__ = [
        # Core Models
        'MaturityLevel',
        'Tool',
        'Capability', 
        'Document',
        'Concept',
        'Relation',
        'BenchmarkCase',
        'PolicyRule',
        'RetrievalContext',
        'LearningCurveLevel',
        
        # Retrieval System
        'AKISRetrievalEngine',
        'KnowledgeGraph',
        'VectorStore', 
        'LexicalSearch',
        'SkillLevelAdaptiveRetriever',
        
        # Ingestion Pipeline
        'IngestionPipeline',
        'ToolManifestParser',
        'DocumentProcessor',
        'ConceptExtractor'
    ]
    
except ImportError as e:
    # Allow package to load even if dependencies missing
    import warnings
    warnings.warn(f"Some AKIS components unavailable: {e}")
    __all__ = []


def get_version():
    """Get AKIS version"""
    return __version__


def get_info():
    """Get AKIS information"""
    return {
        'name': 'AUTARK Knowledge Integration System',
        'version': __version__,
        'author': __author__,
        'license': __license__,
        'description': 'Advanced Knowledge Management for AUTARK',
        'features': [
            '7-Layer Architecture',
            'Hybrid Retrieval Engine', 
            'Skill-Level Adaptive Responses',
            'Tool Manifest Configuration',
            'Maturity Level Progression',
            'Governance & Compliance'
        ],
        'layers': [
            'Storage Primitives',
            'Ingestion & Normalization',
            'Ontology & Knowledge Graph', 
            'Embeddings & Indices',
            'Reasoning Adapters',
            'Evaluation & Telemetrie',
            'Governance & Security',
            'Delivery'
        ]
    }


def quick_start_guide():
    """Print quick start guide"""
    
    guide = """
🧠 AUTARK Knowledge Integration System (AKIS)
=============================================

🚀 Quick Start:

1. Initialize AKIS:
   python scripts/init_akis.py --data-dir ./data

2. Start Interactive Mode:
   python scripts/akis_server.py --mode interactive

3. Basic Usage:
   from akis import AKISRetrievalEngine, RetrievalContext
   
   engine = AKISRetrievalEngine("./data")
   context = RetrievalContext(user_id="test")
   result = engine.query("your question", context)

📚 Documentation:
   - README.md - Architecture overview
   - docs/ontology.md - Knowledge models
   - manifests/tools/ - Tool configurations

🎯 Key Features:
   ✅ Hybrid Search (Graph + Vector + Lexical)
   ✅ Skill-Level Adaptation
   ✅ 6-Level Maturity Progression
   ✅ Tool Manifest System
   ✅ Governance Framework
   ✅ Offline-First Design

🔗 Integration:
   - Standalone Python
   - REST API ready
   - CLI interface
   - Jupyter compatible
"""
    
    print(guide)


if __name__ == "__main__":
    # Show info when run directly
    import json
    info = get_info()
    print(json.dumps(info, indent=2))
    print("\n" + "="*50)
    quick_start_guide()