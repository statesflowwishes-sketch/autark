"""
AKIS Ingestion Pipeline
======================

Automatisierte Ingestion von Tools, Dokumentation und Code
in die AKIS Knowledge Base mit Lernkurven-Integration.
"""

import json
import yaml
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import asdict

from ..ontology.models import (
    Tool, Capability, Document, DocumentChunk, Concept, 
    MaturityProfile, BenchmarkCase, generate_id,
    MaturityLevel, RiskLevel, ComplianceTag
)

logger = logging.getLogger(__name__)


class ToolManifestParser:
    """Parser für Tool-Manifeste"""
    
    def parse_manifest(self, manifest_path: str) -> Tool:
        """Parse Tool-Manifest YAML zu Tool-Objekt"""
        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Konvertiere Compliance Tags
        compliance_tags = []
        for tag_str in data.get('compliance_tags', []):
            try:
                compliance_tags.append(ComplianceTag(tag_str))
            except ValueError:
                logger.warning(f"Unknown compliance tag: {tag_str}")
        
        # Konvertiere Risk Level
        risk_level = RiskLevel.MEDIUM
        try:
            risk_level = RiskLevel(data.get('risk_level', 'medium'))
        except ValueError:
            logger.warning(f"Unknown risk level: {data.get('risk_level')}")
        
        # Erstelle Tool
        tool = Tool(
            tool_id=data['tool_id'],
            name=data['name'],
            version=data['version'],
            vendor=data['vendor'],
            description=data.get('description', ''),
            capabilities=[cap['id'] for cap in data.get('capabilities', [])],
            compliance_tags=compliance_tags,
            risk_level=risk_level,
            documentation_sources=data.get('documentation_sources', []),
            metadata=data
        )
        
        return tool
    
    def parse_capabilities(self, manifest_path: str) -> List[Capability]:
        """Parse Capabilities aus Tool-Manifest"""
        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        capabilities = []
        for cap_data in data.get('capabilities', []):
            
            # Parse Maturity Profile
            maturity_profile = None
            profile_id = cap_data.get('maturity_profile')
            if profile_id and profile_id in data.get('maturity_profiles', {}):
                profile_data = data['maturity_profiles'][profile_id]
                maturity_profile = self._parse_maturity_profile(profile_id, profile_data)
            
            # Parse Benchmarks
            benchmarks = []
            for bench_data in cap_data.get('benchmarks', []):
                benchmark = self._parse_benchmark(bench_data, cap_data['id'])
                benchmarks.append(benchmark)
            
            capability = Capability(
                capability_id=cap_data['id'],
                name=cap_data.get('name', cap_data['id']),
                description=cap_data.get('description', ''),
                domain=data.get('domain', 'general'),
                primary_concepts=cap_data.get('primary_concepts', []),
                maturity_profile_id=profile_id or '',
                maturity_profile=maturity_profile,
                benchmarks=benchmarks
            )
            
            capabilities.append(capability)
        
        return capabilities
    
    def _parse_maturity_profile(self, profile_id: str, profile_data: List[Dict]) -> MaturityProfile:
        """Parse Maturity Profile aus YAML"""
        from ..ontology.models import LearningCurveLevel
        
        levels = []
        for level_data in profile_data:
            level = LearningCurveLevel(
                level=MaturityLevel(level_data['level']),
                description=level_data['description'],
                expected_accuracy=level_data['expected_accuracy'],
                max_latency_ms=level_data['max_latency_ms'],
                risk_factor=level_data['risk_factor'],
                min_evidence_docs=level_data['min_evidence_docs']
            )
            levels.append(level)
        
        return MaturityProfile(
            profile_id=profile_id,
            name=f"Maturity Profile {profile_id}",
            description=f"Learning curve for {profile_id}",
            levels=levels
        )
    
    def _parse_benchmark(self, bench_data: Dict, capability_id: str) -> BenchmarkCase:
        """Parse Benchmark Case"""
        from ..ontology.models import BenchmarkMetric
        
        # Konvertiere target_metrics zu BenchmarkMetric Liste
        metrics = []
        for metric_name, target_value in bench_data.get('target_metrics', {}).items():
            metric = BenchmarkMetric(
                name=metric_name,
                target_value=target_value,
                description=f"Target {metric_name} for {capability_id}"
            )
            metrics.append(metric)
        
        return BenchmarkCase(
            case_id=bench_data['case_id'],
            capability_ref=capability_id,
            description=bench_data.get('description', ''),
            input_data={},  # Vereinfacht für jetzt
            expected_outcome=None,  # Vereinfacht für jetzt
            target_metrics=metrics
        )


class DocumentProcessor:
    """Verarbeitung von Dokumenten zu Knowledge Units"""
    
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size
    
    def process_markdown(self, file_path: str, tool_refs: List[str] = None) -> Document:
        """Verarbeite Markdown-Dokument"""
        path = Path(file_path)
        content = path.read_text(encoding='utf-8')
        
        # Erstelle Dokument
        doc_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        doc = Document(
            document_id=generate_id(),
            source_path=str(path),
            source_type='markdown',
            title=self._extract_title(content),
            content=content,
            tool_refs=tool_refs or [],
            hash=doc_hash
        )
        
        # Erstelle Chunks
        chunks = self._create_chunks(content, doc.document_id, tool_refs or [])
        doc.chunks = chunks
        
        return doc
    
    def process_code(self, file_path: str, tool_refs: List[str] = None) -> Document:
        """Verarbeite Code-Datei"""
        path = Path(file_path)
        content = path.read_text(encoding='utf-8')
        
        doc_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        doc = Document(
            document_id=generate_id(),
            source_path=str(path),
            source_type='code',
            title=path.name,
            content=content,
            tool_refs=tool_refs or [],
            hash=doc_hash,
            metadata={'language': path.suffix[1:] if path.suffix else 'unknown'}
        )
        
        # Code-spezifische Chunking
        chunks = self._create_code_chunks(content, doc.document_id, tool_refs or [])
        doc.chunks = chunks
        
        return doc
    
    def _extract_title(self, content: str) -> str:
        """Extrahiere Titel aus Markdown"""
        lines = content.split('\n')
        for line in lines[:5]:  # Schaue nur erste 5 Zeilen
            if line.startswith('# '):
                return line[2:].strip()
        return "Untitled Document"
    
    def _create_chunks(self, content: str, doc_id: str, tool_refs: List[str]) -> List[DocumentChunk]:
        """Erstelle Text-Chunks"""
        chunks = []
        words = content.split()
        
        for i in range(0, len(words), self.chunk_size):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunk_hash = hashlib.sha256(chunk_text.encode('utf-8')).hexdigest()
            
            chunk = DocumentChunk(
                chunk_id=generate_id(),
                document_id=doc_id,
                content=chunk_text,
                chunk_index=i // self.chunk_size,
                tool_refs=tool_refs,
                hash=chunk_hash
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_code_chunks(self, content: str, doc_id: str, tool_refs: List[str]) -> List[DocumentChunk]:
        """Erstelle Code-spezifische Chunks (z.B. nach Funktionen)"""
        # Vereinfachte Implementation - könnte erweitert werden für AST-basierte Chunking
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        chunk_index = 0
        
        for line in lines:
            current_chunk.append(line)
            
            # Neue Chunk bei Funktions-/Klassen-Definitionen
            if (line.strip().startswith('def ') or 
                line.strip().startswith('class ') or
                len(current_chunk) >= 50):  # Max 50 Zeilen pro Chunk
                
                chunk_text = '\n'.join(current_chunk)
                chunk_hash = hashlib.sha256(chunk_text.encode('utf-8')).hexdigest()
                
                chunk = DocumentChunk(
                    chunk_id=generate_id(),
                    document_id=doc_id,
                    content=chunk_text,
                    chunk_index=chunk_index,
                    tool_refs=tool_refs,
                    hash=chunk_hash,
                    metadata={'type': 'code_block'}
                )
                chunks.append(chunk)
                
                current_chunk = []
                chunk_index += 1
        
        # Letzter Chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            chunk_hash = hashlib.sha256(chunk_text.encode('utf-8')).hexdigest()
            
            chunk = DocumentChunk(
                chunk_id=generate_id(),
                document_id=doc_id,
                content=chunk_text,
                chunk_index=chunk_index,
                tool_refs=tool_refs,
                hash=chunk_hash,
                metadata={'type': 'code_block'}
            )
            chunks.append(chunk)
        
        return chunks


class ConceptExtractor:
    """Extraktion von Concepts aus Texten"""
    
    def __init__(self):
        # Vordefinierte Concept-Kategorien
        self.concept_patterns = {
            'technology': ['api', 'database', 'server', 'client', 'framework'],
            'programming': ['function', 'class', 'method', 'variable', 'loop'],
            'ai_video': ['generation', 'synthesis', 'rendering', 'effects', 'animation'],
            'data': ['processing', 'analytics', 'pipeline', 'transformation', 'storage']
        }
    
    def extract_concepts(self, text: str) -> List[Concept]:
        """Extrahiere Concepts aus Text"""
        concepts = []
        text_lower = text.lower()
        
        for category, terms in self.concept_patterns.items():
            for term in terms:
                if term in text_lower:
                    concept = Concept(
                        concept_id=f"{category}_{term}",
                        name=term.title(),
                        description=f"Concept: {term} in category {category}",
                        taxonomy_path=f"{category}.{term}",
                        domain_tags=[category]
                    )
                    concepts.append(concept)
        
        return concepts


class IngestionPipeline:
    """Hauptklasse für AKIS Ingestion Pipeline"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.manifest_parser = ToolManifestParser()
        self.doc_processor = DocumentProcessor()
        self.concept_extractor = ConceptExtractor()
        
        self.processed_tools = []
        self.processed_capabilities = []
        self.processed_documents = []
        self.processed_concepts = []
        
        logger.info(f"Ingestion Pipeline initialized with output_dir: {output_dir}")
    
    def ingest_tool_manifest(self, manifest_path: str) -> Dict[str, Any]:
        """Ingest Tool-Manifest und alle zugehörigen Daten"""
        logger.info(f"Ingesting tool manifest: {manifest_path}")
        
        try:
            # Parse Tool
            tool = self.manifest_parser.parse_manifest(manifest_path)
            self.processed_tools.append(tool)
            
            # Parse Capabilities
            capabilities = self.manifest_parser.parse_capabilities(manifest_path)
            self.processed_capabilities.extend(capabilities)
            
            # Process Documentation Sources
            documents = []
            for doc_source in tool.documentation_sources:
                doc_path = doc_source.get('path', '')
                if Path(doc_path).exists():
                    if doc_source.get('type') == 'markdown':
                        doc = self.doc_processor.process_markdown(doc_path, [tool.tool_id])
                    elif doc_source.get('type') == 'code':
                        doc = self.doc_processor.process_code(doc_path, [tool.tool_id])
                    else:
                        continue
                    
                    documents.append(doc)
                    
                    # Extract Concepts
                    concepts = self.concept_extractor.extract_concepts(doc.content)
                    self.processed_concepts.extend(concepts)
            
            self.processed_documents.extend(documents)
            
            result = {
                'tool': asdict(tool),
                'capabilities': [asdict(cap) for cap in capabilities],
                'documents': [asdict(doc) for doc in documents],
                'status': 'success'
            }
            
            logger.info(f"Successfully ingested tool: {tool.name} with {len(capabilities)} capabilities")
            return result
            
        except Exception as e:
            logger.error(f"Error ingesting tool manifest {manifest_path}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def ingest_directory(self, directory_path: str, recursive: bool = True) -> Dict[str, Any]:
        """Ingest alle Tool-Manifeste in einem Verzeichnis"""
        directory = Path(directory_path)
        pattern = "**/*.yml" if recursive else "*.yml"
        
        results = {
            'processed_files': [],
            'errors': [],
            'summary': {
                'total_tools': 0,
                'total_capabilities': 0,
                'total_documents': 0,
                'total_concepts': 0
            }
        }
        
        for manifest_file in directory.glob(pattern):
            try:
                result = self.ingest_tool_manifest(str(manifest_file))
                results['processed_files'].append({
                    'file': str(manifest_file),
                    'result': result
                })
                
                if result['status'] == 'success':
                    results['summary']['total_tools'] += 1
                    results['summary']['total_capabilities'] += len(result['capabilities'])
                    results['summary']['total_documents'] += len(result['documents'])
                
            except Exception as e:
                error_info = {'file': str(manifest_file), 'error': str(e)}
                results['errors'].append(error_info)
                logger.error(f"Failed to process {manifest_file}: {e}")
        
        results['summary']['total_concepts'] = len(self.processed_concepts)
        
        logger.info(f"Ingestion complete. Processed {results['summary']['total_tools']} tools")
        return results
    
    def save_processed_data(self) -> Dict[str, str]:
        """Speichere verarbeitete Daten als JSON"""
        output_files = {}
        
        # Save Tools
        tools_file = self.output_dir / "tools.json"
        with open(tools_file, 'w', encoding='utf-8') as f:
            tools_data = [asdict(tool) for tool in self.processed_tools]
            json.dump(tools_data, f, indent=2, ensure_ascii=False, default=str)
        output_files['tools'] = str(tools_file)
        
        # Save Capabilities
        capabilities_file = self.output_dir / "capabilities.json"
        with open(capabilities_file, 'w', encoding='utf-8') as f:
            caps_data = [asdict(cap) for cap in self.processed_capabilities]
            json.dump(caps_data, f, indent=2, ensure_ascii=False, default=str)
        output_files['capabilities'] = str(capabilities_file)
        
        # Save Documents
        documents_file = self.output_dir / "documents.json"
        with open(documents_file, 'w', encoding='utf-8') as f:
            docs_data = [asdict(doc) for doc in self.processed_documents]
            json.dump(docs_data, f, indent=2, ensure_ascii=False, default=str)
        output_files['documents'] = str(documents_file)
        
        # Save Concepts
        concepts_file = self.output_dir / "concepts.json"
        with open(concepts_file, 'w', encoding='utf-8') as f:
            concepts_data = [asdict(concept) for concept in self.processed_concepts]
            json.dump(concepts_data, f, indent=2, ensure_ascii=False, default=str)
        output_files['concepts'] = str(concepts_file)
        
        logger.info(f"Saved processed data to {len(output_files)} files")
        return output_files
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generiere Zusammenfassungs-Report"""
        report = {
            'ingestion_summary': {
                'tools_processed': len(self.processed_tools),
                'capabilities_processed': len(self.processed_capabilities),
                'documents_processed': len(self.processed_documents),
                'concepts_extracted': len(self.processed_concepts)
            },
            'tool_overview': [],
            'capability_maturity_distribution': {},
            'compliance_coverage': {},
            'recommendations': []
        }
        
        # Tool Overview
        for tool in self.processed_tools:
            tool_info = {
                'tool_id': tool.tool_id,
                'name': tool.name,
                'version': tool.version,
                'capabilities_count': len(tool.capabilities),
                'risk_level': tool.risk_level.value,
                'compliance_tags': [tag.value for tag in tool.compliance_tags]
            }
            report['tool_overview'].append(tool_info)
        
        # Maturity Distribution
        maturity_counts = {}
        for cap in self.processed_capabilities:
            current_level = cap.get_current_maturity_level()
            maturity_counts[current_level.name] = maturity_counts.get(current_level.name, 0) + 1
        report['capability_maturity_distribution'] = maturity_counts
        
        # Compliance Coverage
        compliance_counts = {}
        for tool in self.processed_tools:
            for tag in tool.compliance_tags:
                compliance_counts[tag.value] = compliance_counts.get(tag.value, 0) + 1
        report['compliance_coverage'] = compliance_counts
        
        # Recommendations
        if len(self.processed_tools) < 5:
            report['recommendations'].append("Consider adding more tools to increase knowledge coverage")
        
        if not any(cap.benchmarks for cap in self.processed_capabilities):
            report['recommendations'].append("Add benchmark cases to capabilities for better validation")
        
        return report


def main():
    """Beispiel-Usage der Ingestion Pipeline"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize Pipeline
    pipeline = IngestionPipeline("./akis_data")
    
    # Ingest Manifests
    results = pipeline.ingest_directory("./manifests/tools")
    
    # Save Data
    output_files = pipeline.save_processed_data()
    
    # Generate Report
    report = pipeline.generate_summary_report()
    
    print("Ingestion Pipeline Complete!")
    print(f"Processed: {results['summary']}")
    print(f"Output files: {list(output_files.keys())}")
    print(f"Report: {report['ingestion_summary']}")


if __name__ == "__main__":
    main()