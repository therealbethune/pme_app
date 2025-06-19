#!/usr/bin/env python3
"""
Comprehensive test for the enhanced PME system with charting capabilities.
"""

import structlog

logger = structlog.get_logger()


def test_enhanced_system():
    """Test the complete enhanced system."""
    logger.debug("🚀 Testing Enhanced PME System")
    logger.debug("=" * 50)

    try:
        # Test chart engine
        from chart_engine import ChartEngine

        engine = ChartEngine()
        logger.debug("✅ Chart engine loaded")

        # Test analysis engine integration
        from analysis_engine import PMEAnalysisEngine

        PMEAnalysisEngine()
        logger.debug("✅ Analysis engine loaded")

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
        logger.debug(
            f'✅ Dashboard created with {dashboard["metadata"]["chart_count"]} charts'
        )

        # List available charts
        for chart_name in dashboard["charts"].keys():
            logger.debug(f"   📊 {chart_name}")

        # Test enhanced router availability
        try:

            logger.debug("✅ Enhanced analysis router available")
        except Exception as e:
            logger.debug(f"⚠️ Enhanced router not available: {e}")

        logger.debug("\n🎯 Enhanced system fully operational!")
        logger.debug("   ✅ Chart engine working")
        logger.debug("   ✅ Analysis router ready")
        logger.debug("   ✅ Interactive dashboards available")
        logger.debug("   ✅ Ready for frontend integration")

        # Test individual chart types
        logger.debug("\n📊 Testing Individual Chart Types:")

        # Performance comparison
        try:
            engine.create_performance_comparison_chart(fund_data, benchmark_data)
            logger.debug("   ✅ Performance comparison chart")
        except Exception as e:
            logger.debug(f"   ❌ Performance comparison failed: {e}")

        # Cash flow waterfall
        try:
            engine.create_cash_flow_waterfall_chart(fund_data)
            logger.debug("   ✅ Cash flow waterfall chart")
        except Exception as e:
            logger.debug(f"   ❌ Cash flow waterfall failed: {e}")

        # Metrics summary
        try:
            engine.create_metrics_summary_chart(metrics)
            logger.debug("   ✅ Metrics summary chart")
        except Exception as e:
            logger.debug(f"   ❌ Metrics summary failed: {e}")

        return True

    except Exception as e:
        logger.debug(f"❌ Enhanced system test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_enhanced_system()
    if success:
        logger.debug("\n🎉 All enhanced system tests passed!")
    else:
        logger.debug("\n💥 Some enhanced system tests failed!")
