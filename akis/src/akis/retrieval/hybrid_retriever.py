"""
AKIS Hybrid Retrieval Engine
============================

Implementiert Hybrid Retrieval: Graph + Vector + Lexical Search
mit Skill-Level-Conditioning für optimale Knowledge-Antworten.
"""

import json
import sqlite3
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import asdict
from pathlib import Path
import logging

from ..ontology.models import (
    RetrievalContext, MaturityLevel, Tool, Capability, 
    Document, Concept, Relation, BenchmarkCase
)

logger = logging.getLogger(__name__)


class KnowledgeGraph:
    """Knowledge Graph für strukturierte Abfragen"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialisiere Graph-Datenbank (SQLite für Prototyp)"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Erstelle Tabellen
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS entities (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            name TEXT,
            data TEXT,  -- JSON serialized entity data
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS relations (
            id TEXT PRIMARY KEY,
            subject TEXT NOT NULL,
            predicate TEXT NOT NULL,
            object TEXT NOT NULL,
            confidence REAL DEFAULT 1.0,
            data TEXT,  -- JSON serialized relation data
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject) REFERENCES entities(id),
            FOREIGN KEY (object) REFERENCES entities(id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
        CREATE INDEX IF NOT EXISTS idx_relations_subject ON relations(subject);
        CREATE INDEX IF NOT EXISTS idx_relations_predicate ON relations(predicate);
        CREATE INDEX IF NOT EXISTS idx_relations_object ON relations(object);
        """)
        self.conn.commit()
    
    def upsert_entity(self, entity_id: str, entity_type: str, 
                     name: str, data: Dict[str, Any]):
        """Füge Entity hinzu oder aktualisiere sie"""
        self.conn.execute("""
        INSERT OR REPLACE INTO entities (id, type, name, data)
        VALUES (?, ?, ?, ?)
        """, (entity_id, entity_type, name, json.dumps(data)))
        self.conn.commit()
    
    def upsert_relation(self, relation_id: str, subject: str, 
                       predicate: str, obj: str, confidence: float = 1.0,
                       data: Dict[str, Any] = None):
        """Füge Relation hinzu oder aktualisiere sie"""
        data_json = json.dumps(data or {})
        self.conn.execute("""
        INSERT OR REPLACE INTO relations (id, subject, predicate, object, confidence, data)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (relation_id, subject, predicate, obj, confidence, data_json))
        self.conn.commit()
    
    def get_capabilities_for_tool(self, tool_id: str) -> List[str]:
        """Hole alle Capabilities eines Tools"""
        cursor = self.conn.execute("""
        SELECT object FROM relations 
        WHERE subject = ? AND predicate = 'HAS_CAPABILITY'
        """, (tool_id,))
        return [row['object'] for row in cursor.fetchall()]
    
    def get_concepts_for_capability(self, capability_id: str) -> List[str]:
        """Hole alle Concepts einer Capability"""
        cursor = self.conn.execute("""
        SELECT object FROM relations 
        WHERE subject = ? AND predicate IN ('GROUNDED_IN', 'RELATES_TO')
        """, (capability_id,))
        return [row['object'] for row in cursor.fetchall()]
    
    def get_tools_by_capability(self, capability_id: str) -> List[str]:
        """Hole alle Tools die eine bestimmte Capability haben"""
        cursor = self.conn.execute("""
        SELECT subject FROM relations 
        WHERE object = ? AND predicate = 'HAS_CAPABILITY'
        """, (capability_id,))
        return [row['subject'] for row in cursor.fetchall()]
    
    def expand_related_entities(self, entity_id: str, 
                               max_depth: int = 2) -> List[Tuple[str, str, float]]:
        """Expandiere verwandte Entitäten (BFS)"""
        visited = set()
        queue = [(entity_id, 0, 1.0)]  # (entity, depth, confidence)
        related = []
        
        while queue and len(related) < 50:  # Limit für Performance
            current_entity, depth, confidence = queue.pop(0)
            
            if current_entity in visited or depth >= max_depth:
                continue
                
            visited.add(current_entity)
            
            # Hole direkte Nachbarn
            cursor = self.conn.execute("""
            SELECT object, predicate, confidence FROM relations 
            WHERE subject = ?
            UNION
            SELECT subject, predicate, confidence FROM relations 
            WHERE object = ?
            """, (current_entity, current_entity))
            
            for row in cursor.fetchall():
                neighbor = row['object'] if row['object'] != current_entity else row['subject']
                predicate = row['predicate']
                rel_confidence = row['confidence'] * confidence
                
                if neighbor not in visited:
                    related.append((neighbor, predicate, rel_confidence))
                    queue.append((neighbor, depth + 1, rel_confidence))
        
        return sorted(related, key=lambda x: x[2], reverse=True)


class VectorStore:
    """Vector Store für semantische Suche"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialisiere Vector Store (SQLite mit JSON für Prototyp)"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS vectors (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            embedding TEXT,  -- JSON serialized vector
            metadata TEXT,   -- JSON serialized metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()
    
    def upsert_vector(self, doc_id: str, content: str, 
                     embedding: List[float], metadata: Dict[str, Any] = None):
        """Füge Vektor hinzu oder aktualisiere ihn"""
        self.conn.execute("""
        INSERT OR REPLACE INTO vectors (id, content, embedding, metadata)
        VALUES (?, ?, ?, ?)
        """, (doc_id, content, json.dumps(embedding), json.dumps(metadata or {})))
        self.conn.commit()
    
    def search(self, query_embedding: List[float], top_k: int = 10,
              metadata_filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Semantische Suche (vereinfachte Cosine Similarity)"""
        cursor = self.conn.execute("SELECT * FROM vectors")
        results = []
        
        query_vec = np.array(query_embedding)
        query_norm = np.linalg.norm(query_vec)
        
        for row in cursor.fetchall():
            try:
                doc_embedding = json.loads(row['embedding'])
                doc_vec = np.array(doc_embedding)
                
                # Cosine Similarity
                similarity = np.dot(query_vec, doc_vec) / (query_norm * np.linalg.norm(doc_vec))
                
                metadata = json.loads(row['metadata'])
                
                # Filter nach Metadata
                if metadata_filter:
                    if not all(metadata.get(k) == v for k, v in metadata_filter.items()):
                        continue
                
                results.append({
                    'id': row['id'],
                    'content': row['content'],
                    'similarity': float(similarity),
                    'metadata': metadata
                })
            except (json.JSONDecodeError, ValueError):
                continue
        
        # Sortiere nach Similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]


class LexicalSearch:
    """Lexical/Keyword Search Engine"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialisiere Lexical Search (SQLite FTS)"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        self.conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
            id, content, metadata
        )
        """)
        self.conn.commit()
    
    def index_document(self, doc_id: str, content: str, 
                      metadata: Dict[str, Any] = None):
        """Indexiere Dokument für FTS"""
        self.conn.execute("""
        INSERT OR REPLACE INTO documents_fts (id, content, metadata)
        VALUES (?, ?, ?)
        """, (doc_id, content, json.dumps(metadata or {})))
        self.conn.commit()
    
    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Full-Text Search"""
        cursor = self.conn.execute("""
        SELECT id, content, metadata, rank 
        FROM documents_fts 
        WHERE documents_fts MATCH ? 
        ORDER BY rank 
        LIMIT ?
        """, (query, top_k))
        
        results = []
        for row in cursor.fetchall():
            try:
                metadata = json.loads(row['metadata'])
                results.append({
                    'id': row['id'],
                    'content': row['content'],
                    'rank': row['rank'],
                    'metadata': metadata
                })
            except json.JSONDecodeError:
                continue
        
        return results


class SkillLevelAdaptiveRetriever:
    """Skill-Level-adaptive Retrieval Engine"""
    
    def __init__(self, graph: KnowledgeGraph, vector_store: VectorStore, 
                 lexical_search: LexicalSearch):
        self.graph = graph
        self.vector_store = vector_store
        self.lexical_search = lexical_search
        self.query_cache = {}
    
    def plan_query(self, query: str, context: RetrievalContext) -> Dict[str, Any]:
        """Erstelle Query Plan basierend auf Skill Level"""
        plan = {
            'query': query,
            'context': context,
            'strategy': self._determine_strategy(context),
            'retrieval_params': self._get_retrieval_params(context),
            'evidence_requirements': self._get_evidence_requirements(context)
        }
        
        logger.info(f"Query plan created: strategy={plan['strategy']}, "
                   f"maturity_level={context.required_maturity_level}")
        return plan
    
    def _determine_strategy(self, context: RetrievalContext) -> str:
        """Bestimme Retrieval-Strategie basierend auf Skill Level"""
        level = context.required_maturity_level
        
        if level in [MaturityLevel.AWARENESS, MaturityLevel.BASIC_EXECUTION]:
            return "comprehensive"  # Mehr Evidenz, breitere Suche
        elif level in [MaturityLevel.EFFICIENT_EXECUTION, MaturityLevel.ADAPTIVE_OPTIMIZATION]:
            return "targeted"       # Fokussierte Suche
        else:
            return "expert"         # Präzise, minimale Evidenz
    
    def _get_retrieval_params(self, context: RetrievalContext) -> Dict[str, Any]:
        """Bestimme Retrieval-Parameter basierend auf Skill Level"""
        level = context.required_maturity_level
        
        base_params = {
            'graph_expansion_depth': 1,
            'vector_top_k': 5,
            'lexical_top_k': 5,
            'min_confidence': context.min_confidence
        }
        
        if level == MaturityLevel.AWARENESS:
            base_params.update({
                'graph_expansion_depth': 2,
                'vector_top_k': 10,
                'lexical_top_k': 8,
                'include_examples': True,
                'include_tutorials': True
            })
        elif level == MaturityLevel.BASIC_EXECUTION:
            base_params.update({
                'vector_top_k': 8,
                'lexical_top_k': 6,
                'include_examples': True
            })
        elif level in [MaturityLevel.PREDICTIVE_PROACTIVE, 
                      MaturityLevel.AUTONOMOUS_SELF_TUNING]:
            base_params.update({
                'vector_top_k': 3,
                'lexical_top_k': 2,
                'focus_on_advanced': True
            })
        
        return base_params
    
    def _get_evidence_requirements(self, context: RetrievalContext) -> Dict[str, Any]:
        """Bestimme Evidenz-Anforderungen"""
        level = context.required_maturity_level
        
        # Standard requirements basierend auf Maturity Level
        requirements = {
            MaturityLevel.AWARENESS: {'min_sources': 5, 'require_tutorials': True},
            MaturityLevel.BASIC_EXECUTION: {'min_sources': 3, 'require_examples': True},
            MaturityLevel.EFFICIENT_EXECUTION: {'min_sources': 2, 'require_best_practices': True},
            MaturityLevel.ADAPTIVE_OPTIMIZATION: {'min_sources': 1, 'require_patterns': True},
            MaturityLevel.PREDICTIVE_PROACTIVE: {'min_sources': 1, 'require_advanced': True},
            MaturityLevel.AUTONOMOUS_SELF_TUNING: {'min_sources': 1, 'require_expert': True}
        }
        
        return requirements.get(level, {'min_sources': 2})
    
    def retrieve(self, query_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Führe Hybrid Retrieval durch"""
        query = query_plan['query']
        context = query_plan['context']
        params = query_plan['retrieval_params']
        
        results = {
            'graph_results': [],
            'vector_results': [],
            'lexical_results': [],
            'merged_results': [],
            'metadata': {
                'strategy': query_plan['strategy'],
                'total_sources': 0,
                'confidence_scores': []
            }
        }
        
        # 1. Graph Expansion (wenn Capability-Hint vorhanden)
        if context.capability_hint:
            graph_entities = self.graph.expand_related_entities(
                context.capability_hint, 
                params['graph_expansion_depth']
            )
            results['graph_results'] = graph_entities[:10]
        
        # 2. Vector Search (simuliert - in Realität würde Embedding generiert)
        dummy_embedding = [0.1] * 384  # Placeholder
        vector_hits = self.vector_store.search(
            dummy_embedding, 
            params['vector_top_k'],
            {'capability': context.capability_hint} if context.capability_hint else None
        )
        results['vector_results'] = vector_hits
        
        # 3. Lexical Search
        lexical_hits = self.lexical_search.search(query, params['lexical_top_k'])
        results['lexical_results'] = lexical_hits
        
        # 4. Merge und Rank
        merged = self._merge_and_rank_results(
            results['graph_results'],
            results['vector_results'], 
            results['lexical_results'],
            params
        )
        results['merged_results'] = merged
        results['metadata']['total_sources'] = len(merged)
        
        # 5. Validiere gegen Evidence Requirements
        evidence_req = query_plan['evidence_requirements']
        if len(merged) < evidence_req.get('min_sources', 1):
            logger.warning(f"Insufficient evidence: {len(merged)} < {evidence_req['min_sources']}")
            results['metadata']['insufficient_evidence'] = True
        
        return results
    
    def _merge_and_rank_results(self, graph_results: List, vector_results: List,
                               lexical_results: List, params: Dict) -> List[Dict]:
        """Merge und rank verschiedene Result-Sets"""
        scored_results = {}
        
        # Score graph results
        for i, (entity_id, predicate, confidence) in enumerate(graph_results):
            score = confidence * (1.0 - i * 0.1)  # Decay mit Position
            scored_results[entity_id] = scored_results.get(entity_id, 0) + score * 0.4
        
        # Score vector results
        for i, result in enumerate(vector_results):
            doc_id = result['id']
            score = result['similarity'] * (1.0 - i * 0.05)
            scored_results[doc_id] = scored_results.get(doc_id, 0) + score * 0.4
        
        # Score lexical results
        for i, result in enumerate(lexical_results):
            doc_id = result['id']
            score = 1.0 / (1.0 + abs(result['rank'])) * (1.0 - i * 0.05)
            scored_results[doc_id] = scored_results.get(doc_id, 0) + score * 0.2
        
        # Sortiere nach finaler Score
        final_results = []
        for doc_id, score in sorted(scored_results.items(), 
                                   key=lambda x: x[1], reverse=True):
            final_results.append({
                'id': doc_id,
                'score': score,
                'source_types': []  # TODO: Track welche Sources beigetragen haben
            })
        
        return final_results[:params.get('max_results', 10)]


class AKISRetrievalEngine:
    """Hauptklasse für AKIS Retrieval"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.graph = KnowledgeGraph(str(self.data_dir / "knowledge_graph.db"))
        self.vector_store = VectorStore(str(self.data_dir / "vector_store.db"))
        self.lexical_search = LexicalSearch(str(self.data_dir / "lexical_search.db"))
        self.retriever = SkillLevelAdaptiveRetriever(
            self.graph, self.vector_store, self.lexical_search
        )
        
        logger.info(f"AKIS Retrieval Engine initialized with data_dir: {data_dir}")
    
    def query(self, query: str, context: RetrievalContext = None) -> Dict[str, Any]:
        """Haupteingangspunkt für Knowledge Retrieval"""
        if context is None:
            context = RetrievalContext()
        
        # Erstelle Query Plan
        plan = self.retriever.plan_query(query, context)
        
        # Führe Retrieval durch
        results = self.retriever.retrieve(plan)
        
        # Erstelle Antwort-Kontext
        response = {
            'query': query,
            'context': asdict(context),
            'plan': plan,
            'results': results,
            'recommendations': self._generate_recommendations(results, context),
            'timestamp': str(datetime.datetime.now())
        }
        
        return response
    
    def _generate_recommendations(self, results: Dict, context: RetrievalContext) -> Dict[str, Any]:
        """Generiere Empfehlungen basierend auf Retrieval-Ergebnissen"""
        recommendations = {
            'confidence_level': 'medium',
            'suggested_actions': [],
            'related_queries': [],
            'skill_progression': {}
        }
        
        total_sources = results['metadata']['total_sources']
        evidence_req = context.required_maturity_level
        
        if total_sources >= 5:
            recommendations['confidence_level'] = 'high'
        elif total_sources >= 2:
            recommendations['confidence_level'] = 'medium'
        else:
            recommendations['confidence_level'] = 'low'
            recommendations['suggested_actions'].append(
                "Consider broadening search terms or lowering maturity requirements"
            )
        
        # Skill Progression Suggestions
        current_level = context.required_maturity_level
        if current_level != MaturityLevel.AUTONOMOUS_SELF_TUNING:
            next_level = MaturityLevel(current_level.value + 1)
            recommendations['skill_progression'] = {
                'current_level': current_level.name,
                'next_level': next_level.name,
                'advancement_suggestions': [
                    f"Practice {context.capability_hint} at {next_level.name} level",
                    "Review advanced patterns and optimizations"
                ]
            }
        
        return recommendations