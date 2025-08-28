#!/usr/bin/env python3
"""
AKIS Server
===========

Startet AUTARK Knowledge Integration System Server.
"""

import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from akis.retrieval.hybrid_retriever import AKISRetrievalEngine
    from akis.ontology.models import RetrievalContext, MaturityLevel
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure AKIS is properly initialized")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AKISServer:
    """AKIS Server für Knowledge Retrieval"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {data_dir}")
        
        # Initialize Retrieval Engine
        self.retrieval_engine = AKISRetrievalEngine(str(self.data_dir))
        self.query_history = []
        self.server_stats = {
            'start_time': datetime.now(),
            'total_queries': 0,
            'successful_queries': 0,
            'average_response_time': 0.0
        }
        
        logger.info(f"AKIS Server initialized with data_dir: {data_dir}")
    
    def process_query(self, query: str, context_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Verarbeite Knowledge Query"""
        start_time = datetime.now()
        
        try:
            # Erstelle Retrieval Context
            context = self._create_context(context_params or {})
            
            # Führe Query durch
            result = self.retrieval_engine.query(query, context)
            
            # Update Statistics
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            self.server_stats['total_queries'] += 1
            self.server_stats['successful_queries'] += 1
            self._update_average_response_time(response_time)
            
            # Add query to history
            query_record = {
                'timestamp': start_time.isoformat(),
                'query': query,
                'context': context_params,
                'response_time': response_time,
                'result_count': len(result['results']['merged_results']),
                'status': 'success'
            }
            self.query_history.append(query_record)
            
            # Enhanced result
            enhanced_result = {
                'query': query,
                'timestamp': start_time.isoformat(),
                'response_time_seconds': response_time,
                'status': 'success',
                'results': result,
                'server_info': {
                    'data_dir': str(self.data_dir),
                    'total_queries': self.server_stats['total_queries']
                }
            }
            
            logger.info(f"Query processed successfully in {response_time:.3f}s: '{query[:50]}...'")
            return enhanced_result
            
        except Exception as e:
            # Update error statistics
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            self.server_stats['total_queries'] += 1
            
            error_record = {
                'timestamp': start_time.isoformat(),
                'query': query,
                'context': context_params,
                'response_time': response_time,
                'status': 'error',
                'error': str(e)
            }
            self.query_history.append(error_record)
            
            logger.error(f"Query failed after {response_time:.3f}s: {e}")
            
            return {
                'query': query,
                'timestamp': start_time.isoformat(),
                'response_time_seconds': response_time,
                'status': 'error',
                'error': str(e),
                'server_info': {
                    'data_dir': str(self.data_dir),
                    'total_queries': self.server_stats['total_queries']
                }
            }
    
    def _create_context(self, params: Dict[str, Any]) -> RetrievalContext:
        """Erstelle RetrievalContext aus Parameters"""
        
        # Parse Maturity Level
        maturity_level = MaturityLevel.BASIC_EXECUTION
        if 'maturity_level' in params:
            try:
                if isinstance(params['maturity_level'], str):
                    maturity_level = MaturityLevel[params['maturity_level'].upper()]
                elif isinstance(params['maturity_level'], int):
                    maturity_level = MaturityLevel(params['maturity_level'])
            except (KeyError, ValueError):
                logger.warning(f"Invalid maturity level: {params['maturity_level']}")
        
        context = RetrievalContext(
            user_id=params.get('user_id', 'anonymous'),
            user_role=params.get('user_role', 'default'),
            capability_hint=params.get('capability_hint', ''),
            required_maturity_level=maturity_level,
            max_latency_ms=params.get('max_latency_ms', 5000),
            min_confidence=params.get('min_confidence', 0.7),
            max_results=params.get('max_results', 10),
            include_code=params.get('include_code', True),
            include_examples=params.get('include_examples', True)
        )
        
        return context
    
    def _update_average_response_time(self, new_response_time: float):
        """Update running average response time"""
        current_avg = self.server_stats['average_response_time']
        total_queries = self.server_stats['total_queries']
        
        if total_queries == 1:
            self.server_stats['average_response_time'] = new_response_time
        else:
            # Running average
            self.server_stats['average_response_time'] = (
                (current_avg * (total_queries - 1) + new_response_time) / total_queries
            )
    
    def get_server_status(self) -> Dict[str, Any]:
        """Hole Server Status"""
        uptime = datetime.now() - self.server_stats['start_time']
        
        status = {
            'status': 'running',
            'uptime_seconds': uptime.total_seconds(),
            'uptime_human': str(uptime),
            'statistics': self.server_stats,
            'data_directory': str(self.data_dir),
            'recent_queries': self.query_history[-10:] if self.query_history else [],
            'success_rate': (
                self.server_stats['successful_queries'] / max(1, self.server_stats['total_queries'])
            ) * 100
        }
        
        return status
    
    def run_interactive_mode(self):
        """Interaktiver Modus für Testing"""
        print("\n" + "="*60)
        print("🧠 AUTARK Knowledge Integration System")
        print("🔍 Interactive Query Mode")
        print("="*60)
        print("Commands:")
        print("  - Type your question")
        print("  - 'status' - Show server status")
        print("  - 'history' - Show query history")
        print("  - 'exit' - Exit interactive mode")
        print("="*60)
        
        while True:
            try:
                user_input = input("\n🔍 Query: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'status':
                    status = self.get_server_status()
                    print(f"\n📊 Server Status:")
                    print(f"   Uptime: {status['uptime_human']}")
                    print(f"   Total Queries: {status['statistics']['total_queries']}")
                    print(f"   Success Rate: {status['success_rate']:.1f}%")
                    print(f"   Avg Response Time: {status['statistics']['average_response_time']:.3f}s")
                    continue
                elif user_input.lower() == 'history':
                    print(f"\n📜 Recent Queries:")
                    if not self.query_history:
                        print("   No queries yet")
                    else:
                        for i, query in enumerate(self.query_history[-5:], 1):
                            status_icon = "✅" if query['status'] == 'success' else "❌"
                            print(f"   {i}. {status_icon} {query['query'][:50]}... ({query['response_time']:.3f}s)")
                    continue
                elif not user_input:
                    continue
                
                # Process query
                print("🔄 Processing...")
                result = self.process_query(user_input)
                
                if result['status'] == 'success':
                    print(f"\n✅ Query successful ({result['response_time_seconds']:.3f}s)")
                    
                    merged_results = result['results']['results']['merged_results']
                    print(f"📊 Found {len(merged_results)} relevant sources:")
                    
                    for i, source in enumerate(merged_results[:5], 1):
                        print(f"   {i}. Source ID: {source['id']} (Score: {source['score']:.3f})")
                    
                    # Show recommendations
                    recommendations = result['results']['recommendations']
                    print(f"\n💡 Confidence Level: {recommendations['confidence_level']}")
                    
                    if recommendations['suggested_actions']:
                        print("📋 Suggestions:")
                        for action in recommendations['suggested_actions']:
                            print(f"   • {action}")
                
                else:
                    print(f"\n❌ Query failed: {result['error']}")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Start AKIS Server")
    parser.add_argument(
        "--data-dir", 
        default="./data", 
        help="Data directory containing AKIS knowledge base"
    )
    parser.add_argument(
        "--mode", 
        choices=['interactive', 'server'],
        default='interactive',
        help="Run mode: interactive or server"
    )
    parser.add_argument(
        "--port", 
        type=int,
        default=8891,
        help="Server port (server mode only)"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize Server
        akis_server = AKISServer(args.data_dir)
        
        if args.mode == 'interactive':
            akis_server.run_interactive_mode()
        else:
            print(f"🚀 Starting AKIS Server on port {args.port}")
            print("Note: Full HTTP server implementation would go here")
            print("For now, use interactive mode: --mode interactive")
            
    except Exception as e:
        logger.error(f"Failed to start AKIS Server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()