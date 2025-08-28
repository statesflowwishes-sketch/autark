#!/usr/bin/env python3
"""
AKIS Initialization Script
=========================

Initialisiert das AUTARK Knowledge Integration System.
"""

import json
import logging
import argparse
from pathlib import Path
import sys
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from akis.ingestion.pipeline import IngestionPipeline
from akis.retrieval.hybrid_retriever import AKISRetrievalEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_akis(base_dir: str, manifests_dir: str) -> Dict[str, Any]:
    """Initialize AKIS from manifests"""
    
    print("🚀 Initializing AUTARK Knowledge Integration System...")
    print("=" * 60)
    
    base_path = Path(base_dir)
    manifests_path = Path(manifests_dir)
    
    if not manifests_path.exists():
        raise FileNotFoundError(f"Manifests directory not found: {manifests_path}")
    
    # Create data directory
    data_dir = base_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize Ingestion Pipeline
    print("📥 Starting Ingestion Pipeline...")
    pipeline = IngestionPipeline(str(data_dir))
    
    # Ingest all manifests
    print(f"📁 Processing manifests from: {manifests_path}")
    results = pipeline.ingest_directory(str(manifests_path))
    
    # Save processed data
    print("💾 Saving processed data...")
    output_files = pipeline.save_processed_data()
    
    # Generate summary report
    print("📊 Generating summary report...")
    report = pipeline.generate_summary_report()
    
    # Save report
    report_file = data_dir / "ingestion_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    # Initialize Retrieval Engine
    print("🔍 Initializing Retrieval Engine...")
    retrieval_engine = AKISRetrievalEngine(str(data_dir))
    
    # Create summary
    summary = {
        'status': 'success',
        'data_directory': str(data_dir),
        'ingestion_results': results,
        'output_files': output_files,
        'report': report,
        'report_file': str(report_file)
    }
    
    print("\n" + "=" * 60)
    print("✅ AKIS Initialization Complete!")
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   Tools: {report['ingestion_summary']['tools_processed']}")
    print(f"   Capabilities: {report['ingestion_summary']['capabilities_processed']}")
    print(f"   Documents: {report['ingestion_summary']['documents_processed']}")
    print(f"   Concepts: {report['ingestion_summary']['concepts_extracted']}")
    print(f"📁 Data Directory: {data_dir}")
    print(f"📋 Report: {report_file}")
    
    # Show recommendations
    if report['recommendations']:
        print("\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"   • {rec}")
    
    return summary


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Initialize AKIS")
    parser.add_argument(
        "--base-dir", 
        default=".", 
        help="Base directory for AKIS data"
    )
    parser.add_argument(
        "--manifests-dir", 
        default="./manifests/tools", 
        help="Directory containing tool manifests"
    )
    parser.add_argument(
        "--output", 
        help="Output file for initialization summary"
    )
    
    args = parser.parse_args()
    
    try:
        summary = init_akis(args.base_dir, args.manifests_dir)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
            print(f"📄 Summary written to: {args.output}")
            
    except Exception as e:
        logger.error(f"AKIS initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()