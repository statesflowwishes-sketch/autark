# AUTARK Knowledge Integration System (AKIS)

Ziel: Vorinitialisierte, versionierbare, quer-referenzierte Wissensbasis für KI-Agenten.

## Kernfeatures
- 🧠 Ontologie + Knowledge Graph
- 📈 Lernkurven / Maturity Profiles
- 🔍 Hybrid Retrieval (Graph + Vector + Lexical)
- 🛡️ Governance & Compliance
- 📊 Benchmarking & Drift Detection
- ⚡ Offline-First mit vortrainierten Tool-Erfahrungen

## Architektur (7-Schichten-Modell)

### Layer 0: Storage Primitives
- Object Store, Git Repo, Document DB, Graph DB, Vector DB

### Layer 1: Ingestion & Normalisierung
- Parser, Extraktoren, Konverter → Unified Knowledge Units

### Layer 2: Ontologie & Knowledge Graph
- Entities, Relations, Skill Curves

### Layer 3: Embeddings & Indexe
- Dokument-, Chunk-, Relation-, Code-Embeddings
- Hybrid lexical + vector

### Layer 4: Reasoning Adapters
- Query Planner, Graph Traversal, RAG Composer, Skill Conditioning

### Layer 5: Evaluation & Telemetrie
- Metriken, Bias/Drift Detection

### Layer 6: Governance & Security
- Redaction, Access Control, Version Gate

### Layer 7: Delivery
- API, Agent SDK, LangChain Adapter, OpenAI ToolSpec, Streaming Interface

## Quick Start

```bash
# Initialize AKIS
python scripts/init_akis.py

# Load tool manifests
python scripts/load_manifests.py

# Build knowledge base
python scripts/build_kb.py

# Start AKIS server
python scripts/start_akis.py
```

Siehe docs/ für Details.