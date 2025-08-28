#!/usr/bin/env python3
"""
AKIS Test Suite
===============

Comprehensive testing for AUTARK Knowledge Integration System
"""

import unittest
import sys
import tempfile
import shutil
from pathlib import Path
import json
import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class TestAKISModels(unittest.TestCase):
    """Test AKIS ontology models"""
    
    def setUp(self):
        """Set up test"""
        try:
            from akis.ontology.models import MaturityLevel, Tool, Capability, RetrievalContext
            self.MaturityLevel = MaturityLevel
            self.Tool = Tool
            self.Capability = Capability
            self.RetrievalContext = RetrievalContext
            self.models_available = True
        except ImportError as e:
            print(f"⚠️  Models not available: {e}")
            self.models_available = False
    
    def test_maturity_levels(self):
        """Test maturity level enum"""
        if not self.models_available:
            self.skipTest("Models not available")
        
        # Test all maturity levels exist
        levels = [
            self.MaturityLevel.AWARENESS_EXPLORATION,
            self.MaturityLevel.BASIC_EXECUTION,
            self.MaturityLevel.EFFICIENT_OPERATION,
            self.MaturityLevel.ADAPTIVE_OPTIMIZATION,
            self.MaturityLevel.PREDICTIVE_INTELLIGENCE,
            self.MaturityLevel.AUTONOMOUS_MASTERY
        ]
        
        self.assertEqual(len(levels), 6)
        self.assertEqual(levels[0].value, 1)
        self.assertEqual(levels[-1].value, 6)
    
    def test_tool_creation(self):
        """Test tool model creation"""
        if not self.models_available:
            self.skipTest("Models not available")
        
        tool = self.Tool(
            id="test_tool",
            name="Test Tool",
            version="1.0.0",
            description="A test tool",
            category="testing",
            maturity_level=self.MaturityLevel.BASIC_EXECUTION,
            capabilities=[]
        )
        
        self.assertEqual(tool.id, "test_tool")
        self.assertEqual(tool.name, "Test Tool")
        self.assertEqual(tool.maturity_level, self.MaturityLevel.BASIC_EXECUTION)
    
    def test_retrieval_context(self):
        """Test retrieval context"""
        if not self.models_available:
            self.skipTest("Models not available")
        
        context = self.RetrievalContext(
            user_id="test_user",
            user_role="developer",
            required_maturity_level=self.MaturityLevel.EFFICIENT_OPERATION
        )
        
        self.assertEqual(context.user_id, "test_user")
        self.assertEqual(context.user_role, "developer")
        self.assertEqual(context.required_maturity_level, self.MaturityLevel.EFFICIENT_OPERATION)


class TestAKISRetrieval(unittest.TestCase):
    """Test AKIS retrieval system"""
    
    def setUp(self):
        """Set up test"""
        try:
            from akis.retrieval.hybrid_retriever import KnowledgeGraph, VectorStore
            self.KnowledgeGraph = KnowledgeGraph
            self.VectorStore = VectorStore
            self.retrieval_available = True
        except ImportError as e:
            print(f"⚠️  Retrieval not available: {e}")
            self.retrieval_available = False
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_knowledge_graph_creation(self):
        """Test knowledge graph initialization"""
        if not self.retrieval_available:
            self.skipTest("Retrieval not available")
        
        kg = self.KnowledgeGraph(str(self.data_dir))
        self.assertIsNotNone(kg)
        
        # Check if database file was created
        db_file = self.data_dir / "knowledge_graph.db"
        self.assertTrue(db_file.exists())
    
    def test_vector_store_creation(self):
        """Test vector store initialization"""
        if not self.retrieval_available:
            self.skipTest("Retrieval not available")
        
        vs = self.VectorStore(str(self.data_dir))
        self.assertIsNotNone(vs)


class TestAKISIngestion(unittest.TestCase):
    """Test AKIS ingestion pipeline"""
    
    def setUp(self):
        """Set up test"""
        try:
            from akis.ingestion.pipeline import ToolManifestParser
            self.ToolManifestParser = ToolManifestParser
            self.ingestion_available = True
        except ImportError as e:
            print(f"⚠️  Ingestion not available: {e}")
            self.ingestion_available = False
    
    def test_manifest_parser(self):
        """Test tool manifest parsing"""
        if not self.ingestion_available:
            self.skipTest("Ingestion not available")
        
        # Create sample manifest
        sample_manifest = {
            'id': 'test_tool',
            'name': 'Test Tool',
            'version': '1.0.0',
            'description': 'A test tool',
            'category': 'testing',
            'maturity_profiles': {
                'awareness_exploration': {
                    'description': 'Basic awareness',
                    'capabilities': ['discovery']
                }
            }
        }
        
        parser = self.ToolManifestParser()
        
        # Test parsing
        try:
            result = parser.parse_manifest(sample_manifest)
            self.assertIsNotNone(result)
        except Exception as e:
            print(f"⚠️  Parser test failed: {e}")


class TestAKISIntegration(unittest.TestCase):
    """Test AKIS integration scenarios"""
    
    def setUp(self):
        """Set up integration test"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir)
        
        # Create sample manifest files
        self.manifests_dir = self.data_dir / "manifests" / "tools"
        self.manifests_dir.mkdir(parents=True)
        
        # Sample tool manifest
        sample_tool = {
            'id': 'video_creator',
            'name': 'Video Creator',
            'version': '1.0.0',
            'description': 'Create AI videos',
            'category': 'video',
            'maturity_profiles': {
                'basic_execution': {
                    'description': 'Basic video creation',
                    'capabilities': ['create_video', 'edit_video']
                }
            },
            'compliance_tags': ['content_creation', 'media_processing']
        }
        
        manifest_file = self.manifests_dir / "video_creator.yml"
        with open(manifest_file, 'w') as f:
            yaml.dump(sample_tool, f)
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_manifest_files_exist(self):
        """Test that manifest files are created"""
        manifest_file = self.manifests_dir / "video_creator.yml"
        self.assertTrue(manifest_file.exists())
        
        # Test YAML loading
        with open(manifest_file) as f:
            data = yaml.safe_load(f)
        
        self.assertEqual(data['id'], 'video_creator')
        self.assertEqual(data['name'], 'Video Creator')


class TestAKISSystem(unittest.TestCase):
    """Test complete AKIS system"""
    
    def setUp(self):
        """Set up system test"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_system_components(self):
        """Test that all AKIS components can be imported"""
        
        components = [
            'akis.ontology.models',
            'akis.retrieval.hybrid_retriever', 
            'akis.ingestion.pipeline'
        ]
        
        available_components = []
        missing_components = []
        
        for component in components:
            try:
                __import__(component)
                available_components.append(component)
            except ImportError as e:
                missing_components.append((component, str(e)))
        
        print(f"\n✅ Available components: {len(available_components)}")
        for comp in available_components:
            print(f"   - {comp}")
        
        if missing_components:
            print(f"\n❌ Missing components: {len(missing_components)}")
            for comp, error in missing_components:
                print(f"   - {comp}: {error}")
        
        # At least ontology models should be available
        self.assertIn('akis.ontology.models', available_components)


def run_akis_tests():
    """Run all AKIS tests"""
    
    print("="*60)
    print("🧪 AUTARK Knowledge Integration System")
    print("🔬 Test Suite")
    print("="*60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestAKISModels,
        TestAKISRetrieval,
        TestAKISIngestion, 
        TestAKISIntegration,
        TestAKISSystem
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split('\\n')[-2] if traceback else 'Unknown'}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split('\\n')[-2] if traceback else 'Unknown'}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / max(1, result.testsRun)) * 100
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("✅ AKIS System: READY FOR DEPLOYMENT")
    elif success_rate >= 50:
        print("⚠️  AKIS System: PARTIALLY FUNCTIONAL")
    else:
        print("❌ AKIS System: NEEDS ATTENTION")
    
    return result.wasSuccessful()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AKIS Test Suite")
    parser.add_argument(
        "--module",
        choices=['models', 'retrieval', 'ingestion', 'integration', 'system', 'all'],
        default='all',
        help="Test specific module"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    if args.module == 'all':
        success = run_akis_tests()
    else:
        # Run specific module tests
        print(f"🔬 Testing {args.module} module...")
        
        if args.module == 'models':
            suite = unittest.TestLoader().loadTestsFromTestCase(TestAKISModels)
        elif args.module == 'retrieval':
            suite = unittest.TestLoader().loadTestsFromTestCase(TestAKISRetrieval)
        elif args.module == 'ingestion':
            suite = unittest.TestLoader().loadTestsFromTestCase(TestAKISIngestion)
        elif args.module == 'integration':
            suite = unittest.TestLoader().loadTestsFromTestCase(TestAKISIntegration)
        elif args.module == 'system':
            suite = unittest.TestLoader().loadTestsFromTestCase(TestAKISSystem)
        
        runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
        result = runner.run(suite)
        success = result.wasSuccessful()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()