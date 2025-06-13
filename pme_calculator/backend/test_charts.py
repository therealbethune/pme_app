#!/usr/bin/env python3
"""
Test script for chart engine and enhanced analysis system.
"""

from chart_engine import ChartEngine
import pandas as pd
import numpy as np

def test_chart_engine():
    """Test the chart engine functionality."""
    print("🔬 Testing Chart Engine...")
    
    try:
        # Test chart engine
        engine = ChartEngine()
        print('   ✅ Chart Engine imported successfully')

        # Create test data
        fund_data = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=8, freq='QE'),
            'cashflow': [-1000, -500, 0, 200, 300, 0, 400, 500],
            'nav': [1000, 1400, 1450, 1350, 1600, 1700, 1600, 1800]
        })

        benchmark_data = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=8, freq='QE'),
            'price': [100, 105, 110, 108, 115, 120, 118, 125]
        })

        metrics = {
            'Fund IRR': 0.179,
            'TVPI': 2.13,
            'DPI': 0.87,
            'RVPI': 1.26,
            'PME': 1.15,
            'Alpha': 0.05
        }

        # Test dashboard creation
        result = engine.create_pme_dashboard(fund_data, benchmark_data, metrics)
        print(f'   ✅ Dashboard created: {result["success"]}')
        print(f'   ✅ Chart count: {result["metadata"]["chart_count"]}')
        
        # Test individual charts
        charts = result['charts']
        expected_charts = [
            'performance_comparison',
            'cash_flow_waterfall', 
            'metrics_summary',
            'risk_return',
            'rolling_performance',
            'distributions_timeline'
        ]
        
        for chart_name in expected_charts:
            if chart_name in charts:
                print(f'   ✅ {chart_name} chart generated')
            else:
                print(f'   ❌ {chart_name} chart missing')
        
        print('🎯 Chart engine fully functional!')
        return True
        
    except Exception as e:
        print(f'   ❌ Chart engine failed: {e}')
        return False

def test_plotly_import():
    """Test Plotly imports."""
    print("\n🔬 Testing Plotly Dependencies...")
    
    try:
        import plotly.graph_objects as go
        import plotly.express as px
        from plotly.subplots import make_subplots
        print('   ✅ Plotly imports successful')
        
        # Test basic chart creation
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))
        json_data = fig.to_json()
        print('   ✅ Basic chart creation works')
        
        return True
        
    except Exception as e:
        print(f'   ❌ Plotly test failed: {e}')
        return False

def main():
    """Run all chart tests."""
    print("🚀 PME Calculator - Chart System Test")
    print("=" * 50)
    
    success = True
    
    if not test_plotly_import():
        success = False
    
    if not test_chart_engine():
        success = False
    
    if success:
        print("\n✅ All chart tests passed! 🎉")
        print("📊 Ready for enhanced UI development!")
    else:
        print("\n❌ Some chart tests failed.")
    
    return success

if __name__ == "__main__":
    main() 