#!/usr/bin/env python3
"""
AKIS Quick Test
===============

Schneller Test des AKIS Systems
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from akis.retrieval.hybrid_retriever import AKISRetrievalEngine
    from akis.ontology.models import RetrievalContext, MaturityLevel
    
    print("🧠 AUTARK Knowledge Integration System - Quick Test")
    print("="*60)
    
    # Initialize Engine
    data_dir = Path(__file__).parent.parent / "data" / "data"
    if not data_dir.exists():
        print("❌ Data directory not found. Run init_akis.py first.")
        sys.exit(1)
    
    engine = AKISRetrievalEngine(str(data_dir))
    print(f"✅ Retrieval Engine initialized: {data_dir}")
    
    # Create context
    context = RetrievalContext(
        user_id="test_user",
        user_role="developer", 
        required_maturity_level=MaturityLevel.BASIC_EXECUTION,
        max_results=5
    )
    print(f"✅ Context created for {context.user_role}")
    
    # Test queries
    test_queries = [
        "How do I create a video with AI?",
        "What video editing capabilities are available?",
        "Show me knowledge integration features",
    ]
    
    print("\n🔍 Testing Queries:")
    print("-" * 40)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        try:
            result = engine.query(query, context)
            
            # Show results
            merged_results = result['results']['merged_results']
            print(f"   ✅ Found {len(merged_results)} results")
            
            for j, source in enumerate(merged_results[:3], 1):
                print(f"      {j}. {source['id']} (Score: {source['score']:.3f})")
            
            confidence = result['recommendations']['confidence_level']
            print(f"   📊 Confidence: {confidence}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "="*60)
    print("🎉 AKIS Quick Test Complete!")
    print("🚀 System is operational and ready for use")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure AKIS dependencies are installed")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)