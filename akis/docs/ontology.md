# Ontologie Übersicht

## Kern-Entitäten

### Tool
- id, name, version, vendor
- capabilities[], maturity_profile_id
- compliance_tags[], risk_level
- last_review, documentation_sources[]

### Capability
- id, domain, tasks[]
- required_inputs, outputs
- perf_metrics, maturity_profile

### LearningCurve / MaturityProfile
- level (0-5), description
- expected_accuracy, latency_bound
- risk_factor, min_evidence_docs

### Document
- id, source_type, tool_refs[]
- semantic_vectors[], hash, version
- compliance_classification

### CodeAsset
- repo, path, language
- symbols, tool_refs[]
- complexity_metrics

### Concept
- id, taxonomy_path
- synonyms[], related_concepts[]
- domain_tags[]

### Relation
- subject, predicate, object
- confidence, provenance
- temporal_validity

### BenchmarkCase
- id, capability_ref
- input, expected_outcome
- metric_targets, success_criteria

### PolicyRule
- id, scope, rule_type
- conditions, action
- enforcement_level

## Maturity Level Definition

### Level 0: Awareness
- Grundverständnis vorhanden
- Kann Tool identifizieren
- Benötigt detaillierte Anleitung

### Level 1: Basic Execution
- Kann einfache Tasks ausführen
- Versteht grundlegende Parameter
- Braucht gelegentlich Hilfe

### Level 2: Efficient Execution
- Routinierte Nutzung
- Kennt Best Practices
- Kann Fehler selbst beheben

### Level 3: Adaptive Optimization
- Kann Tool für verschiedene Szenarien anpassen
- Optimiert Performance
- Integriert mit anderen Tools

### Level 4: Predictive/Proactive
- Antizipiert Probleme
- Automatisiert Workflows
- Mentoring anderer

### Level 5: Autonomous Self-Tuning
- Vollautomatische Optimierung
- Innovation und Verbesserung
- Expertise-Transfer

## Beispiel-Relationen

```
Tool (CRM) HAS_CAPABILITY ManageCustomerSegments
Capability ManageCustomerSegments GROUNDED_IN Concepts: Customer, Segment, Lifecycle
Capability ManageCustomerSegments ACHIEVES_AT Level2
Document doc123 DESCRIBES Capability ManageCustomerSegments
Tool CRM SUPERSEDED_BY CRM v2.1
User alice HAS_SKILL_LEVEL Level3 FOR_CAPABILITY ManageCustomerSegments
BenchmarkCase bench_seg_001 VALIDATES Capability ManageCustomerSegments
PolicyRule gdpr_rule APPLIES_TO Tool CRM
```

## Persistenz

### Graph DB (Neo4j / ArangoDB)
- Entitäten als Nodes
- Relationen als Edges
- Temporale Validität über Properties

### Vector Store (Qdrant / Milvus)
- Document Chunks
- Code Snippets
- Semantic Search

### Document Store (MongoDB / PostgreSQL)
- Tool Manifests
- Benchmark Cases
- Policy Rules
- Audit Logs