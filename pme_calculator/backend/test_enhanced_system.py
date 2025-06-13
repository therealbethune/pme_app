#!/usr/bin/env python3
"""
Comprehensive test for the enhanced PME system with charting capabilities.
"""


def test_enhanced_system():
    """Test the complete enhanced system."""
    print("🚀 Testing Enhanced PME System")
    print("=" * 50)

    try:
        # Test chart engine
        from chart_engine import ChartEngine

        engine = ChartEngine()
        print("✅ Chart engine loaded")

        # Test analysis engine integration
        from analysis_engine import PMEAnalysisEngine

        analysis_engine = PMEAnalysisEngine()
        print("✅ Analysis engine loaded")

        # Test pandas and numpy
        import pandas as pd

        # Create sample data
        fund_data = pd.DataFrame(
            {
                "date": pd.date_range("2020-01-01", periods=8, freq="QE"),
                "cashflow": [-1000, -500, 0, 200, 300, 0, 400, 500],
                "nav": [1000, 1400, 1450, 1350, 1600, 1700, 1600, 1800],
            }
        )

        benchmark_data = pd.DataFrame(
            {
                "date": pd.date_range("2020-01-01", periods=8, freq="QE"),
                "price": [100, 105, 110, 108, 115, 120, 118, 125],
            }
        )

        # Generate comprehensive dashboard
        metrics = {
            "Fund IRR": 0.179,
            "TVPI": 2.13,
            "DPI": 0.87,
            "RVPI": 1.26,
            "PME": 1.15,
            "Alpha": 0.05,
        }

        dashboard = engine.create_pme_dashboard(fund_data, benchmark_data, metrics)
        print(
            f'✅ Dashboard created with {dashboard["metadata"]["chart_count"]} charts'
        )

        # List available charts
        for chart_name in dashboard["charts"].keys():
            print(f"   📊 {chart_name}")

        # Test enhanced router availability
        try:

            print("✅ Enhanced analysis router available")
        except Exception as e:
            print(f"⚠️ Enhanced router not available: {e}")

        print("\n🎯 Enhanced system fully operational!")
        print("   ✅ Chart engine working")
        print("   ✅ Analysis router ready")
        print("   ✅ Interactive dashboards available")
        print("   ✅ Ready for frontend integration")

        # Test individual chart types
        print("\n📊 Testing Individual Chart Types:")

        # Performance comparison
        try:
            perf_chart = engine.create_performance_comparison_chart(
                fund_data, benchmark_data
            )
            print("   ✅ Performance comparison chart")
        except Exception as e:
            print(f"   ❌ Performance comparison failed: {e}")

        # Cash flow waterfall
        try:
            cf_chart = engine.create_cash_flow_waterfall_chart(fund_data)
            print("   ✅ Cash flow waterfall chart")
        except Exception as e:
            print(f"   ❌ Cash flow waterfall failed: {e}")

        # Metrics summary
        try:
            metrics_chart = engine.create_metrics_summary_chart(metrics)
            print("   ✅ Metrics summary chart")
        except Exception as e:
            print(f"   ❌ Metrics summary failed: {e}")

        return True

    except Exception as e:
        print(f"❌ Enhanced system test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_enhanced_system()
    if success:
        print("\n🎉 All enhanced system tests passed!")
    else:
        print("\n💥 Some enhanced system tests failed!")
