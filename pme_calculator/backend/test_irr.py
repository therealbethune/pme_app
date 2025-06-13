#!/usr/bin/env python3
"""
Test script to verify IRR calculation and chart data generation.
"""

from analysis_engine import PMEAnalysisEngine
import pandas as pd
import tempfile
import os


def test_analysis_engine():
    """Test the analysis engine with sample data."""

    # Create test data
    test_data = {
        "date": ["2020-01-01", "2020-06-01", "2021-01-01", "2021-06-01", "2022-01-01"],
        "cashflow": [-1000000, -500000, 200000, 300000, 800000],
        "nav": [1000000, 1400000, 1200000, 1100000, 0],
    }

    df = pd.DataFrame(test_data)
    df["date"] = pd.to_datetime(df["date"])

    # Save to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        df.to_csv(f.name, index=False)
        temp_file = f.name

    try:
        # Test analysis engine
        engine = PMEAnalysisEngine()
        result = engine.load_fund_data(temp_file)
        print("✅ Fund data loaded:", result["success"])

        # Run analysis
        analysis = engine.calculate_pme_metrics()
        print("✅ Analysis completed")
        print("📊 Fund IRR:", analysis["metrics"].get("Fund IRR", "N/A"))
        print("📊 TVPI:", analysis["metrics"].get("TVPI", "N/A"))
        print("📊 DPI:", analysis["metrics"].get("DPI", "N/A"))

        # Test chart data generation
        charts = engine._generate_chart_data()
        print("📈 Chart data keys:", list(charts.keys()) if charts else "None")

        if charts:
            for key, data in charts.items():
                if isinstance(data, list):
                    print(f"   {key}: {len(data)} items")
                else:
                    print(f"   {key}: {type(data).__name__}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        os.unlink(temp_file)


if __name__ == "__main__":
    print("🧪 Testing PME Analysis Engine...")
    success = test_analysis_engine()
    print(f"🎯 Test {'PASSED' if success else 'FAILED'}")
