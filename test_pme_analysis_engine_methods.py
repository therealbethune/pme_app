#!/usr/bin/env python3
"""
Test PMEAnalysisEngine methods to ensure they work with the upload system.
"""

import sys
import os
import tempfile
import pandas as pd
from pathlib import Path
import pytest

# Add backend directory to path
backend_dir = Path(__file__).parent / "pme_calculator" / "backend"
sys.path.insert(0, str(backend_dir))

class TestPMEAnalysisEngineMethods:
    """Test class for PMEAnalysisEngine method functionality."""
    
    def test_import_pme_analysis_engine(self):
        """Test that PMEAnalysisEngine can be imported."""
        print("🔍 Testing PMEAnalysisEngine import...")
        
        try:
            from analysis_engine import PMEAnalysisEngine
            engine = PMEAnalysisEngine()
            print("✅ PMEAnalysisEngine import and instantiation: SUCCESS")
            assert engine is not None
        except Exception as e:
            print(f"❌ PMEAnalysisEngine import failed: {e}")
            assert False, f"Import failed: {e}"
    
    def test_load_fund_data_method_exists(self):
        """Test that load_fund_data method exists and works."""
        print("🔍 Testing load_fund_data method...")
        
        from analysis_engine import PMEAnalysisEngine
        engine = PMEAnalysisEngine()
        
        # Check if method exists
        assert hasattr(engine, 'load_fund_data'), "load_fund_data method missing"
        
        # Create test CSV data
        test_data = pd.DataFrame({
            'Date': ['2020-01-01', '2020-06-01', '2021-01-01'],
            'Contributions': [-100, -50, 0],
            'Distributions': [0, 10, 80],
            'NAV': [100, 140, 60]
        })
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            temp_path = f.name
        
        try:
            # Test the method
            result = engine.load_fund_data(temp_path)
            print("✅ load_fund_data method: SUCCESS")
            
            # Verify result structure
            assert isinstance(result, dict), "load_fund_data should return dict"
            assert 'rows' in result, "Result should contain 'rows' key"
            assert result['rows'] == 3, f"Expected 3 rows, got {result['rows']}"
            
            # Verify engine has fund_data attribute
            assert hasattr(engine, 'fund_data'), "Engine should have fund_data attribute"
            assert engine.fund_data is not None, "fund_data should not be None"
            assert len(engine.fund_data) == 3, "fund_data should have 3 rows"
            
        finally:
            os.unlink(temp_path)
    
    def test_load_index_data_method_exists(self):
        """Test that load_index_data method exists and works."""
        print("🔍 Testing load_index_data method...")
        
        from analysis_engine import PMEAnalysisEngine
        engine = PMEAnalysisEngine()
        
        # Check if method exists
        assert hasattr(engine, 'load_index_data'), "load_index_data method missing"
        
        # Create test index data
        test_data = pd.DataFrame({
            'Date': ['2020-01-01', '2020-06-01', '2021-01-01'],
            'Price': [100, 110, 120],
            'Return': [0.0, 0.10, 0.091]
        })
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            temp_path = f.name
        
        try:
            # Test the method
            result = engine.load_index_data(temp_path)
            print("✅ load_index_data method: SUCCESS")
            
            # Verify result structure
            assert isinstance(result, dict), "load_index_data should return dict"
            assert 'rows' in result, "Result should contain 'rows' key"
            assert result['rows'] == 3, f"Expected 3 rows, got {result['rows']}"
            
            # Verify engine has index_data attribute
            assert hasattr(engine, 'index_data'), "Engine should have index_data attribute"
            assert engine.index_data is not None, "index_data should not be None"
            assert len(engine.index_data) == 3, "index_data should have 3 rows"
            
        finally:
            os.unlink(temp_path)
    
    def test_calculate_pme_metrics_method(self):
        """Test that calculate_pme_metrics method works."""
        print("🔍 Testing calculate_pme_metrics method...")
        
        from analysis_engine import PMEAnalysisEngine
        engine = PMEAnalysisEngine()
        
        # Check if method exists
        assert hasattr(engine, 'calculate_pme_metrics'), "calculate_pme_metrics method missing"
        
        # Load test data
        fund_data = pd.DataFrame({
            'Date': ['2020-01-01', '2020-06-01', '2021-01-01'],
            'Contributions': [-100, -50, 0],
            'Distributions': [0, 10, 80],
            'NAV': [100, 140, 60]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            fund_data.to_csv(f.name, index=False)
            fund_path = f.name
        
        try:
            engine.load_fund_data(fund_path)
            result = engine.calculate_pme_metrics()
            
            print("✅ calculate_pme_metrics method: SUCCESS")
            
            # Verify result structure
            assert isinstance(result, dict), "calculate_pme_metrics should return dict"
            assert 'success' in result, "Result should contain 'success' key"
            
        finally:
            os.unlink(fund_path)
    
    def test_upload_integration(self):
        """Test the complete upload integration flow."""
        print("🔍 Testing upload integration flow...")
        
        from analysis_engine import PMEAnalysisEngine
        
        # Create test fund data
        fund_data = pd.DataFrame({
            'Date': ['2020-01-01', '2020-06-01', '2021-01-01'],
            'Contributions': [-100, -50, 0],
            'Distributions': [0, 10, 80],
            'NAV': [100, 140, 60]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            fund_data.to_csv(f.name, index=False)
            fund_path = f.name
        
        try:
            # Simulate the upload flow
            engine = PMEAnalysisEngine()
            fund_info = engine.load_fund_data(fund_path)
            
            # Verify the upload flow works
            assert fund_info['rows'] == 3
            assert len(engine.fund_data.columns) > 0
            
            print("✅ Upload integration flow: SUCCESS")
            
        finally:
            os.unlink(fund_path)

def run_pme_engine_tests():
    """Run all PME engine tests."""
    print("🚀 Starting PME Analysis Engine method tests...")
    
    test_suite = TestPMEAnalysisEngineMethods()
    
    tests = [
        test_suite.test_import_pme_analysis_engine,
        test_suite.test_load_fund_data_method_exists,
        test_suite.test_load_index_data_method_exists,
        test_suite.test_calculate_pme_metrics_method,
        test_suite.test_upload_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    success = run_pme_engine_tests()
    sys.exit(0 if success else 1) 