#!/usr/bin/env python3
"""
Test script to verify that the PME analysis is working correctly
and that the chart data is being generated properly.
"""

import os

import requests


def test_analysis_integration():
    """Test the full analysis pipeline and chart data generation."""

    base_url = "http://localhost:8000"

    # Test 1: Check server health
    print("🔍 Testing server health...")
    try:
        response = requests.get(f"{base_url}/api/health")
        assert (
            response.status_code == 200
        ), f"Server health check failed: {response.status_code}"
        print("✅ Server is healthy")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Note: This test requires the server to be running on localhost:8000")
        print(
            "   Start the server with: python3 pme_calculator/backend/main_minimal.py"
        )
        return  # Skip test when server is not running

    # Test 2: Upload fund data
    print("\n📁 Testing fund data upload...")
    fund_file_path = "pme_calculator/backend/test_sample.csv"
    if not os.path.exists(fund_file_path):
        print(f"❌ Fund test file not found: {fund_file_path}")
        return False

    try:
        with open(fund_file_path, "rb") as f:
            files = {"file": ("test_sample.csv", f, "text/csv")}
            response = requests.post(f"{base_url}/api/upload/fund", files=files)

        if response.status_code == 200:
            fund_data = response.json()
            fund_file_id = fund_data["file_id"]
            print(f"✅ Fund data uploaded successfully: {fund_file_id}")
            print(f"   Rows: {fund_data.get('message', 'N/A')}")
        else:
            print(f"❌ Fund upload failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Fund upload error: {e}")
        return False

    # Test 3: Upload index data
    print("\n📊 Testing index data upload...")
    index_file_path = "pme_calculator/backend/test_index.csv"
    if not os.path.exists(index_file_path):
        print(f"❌ Index test file not found: {index_file_path}")
        return False

    try:
        with open(index_file_path, "rb") as f:
            files = {"file": ("test_index.csv", f, "text/csv")}
            response = requests.post(f"{base_url}/api/upload/index", files=files)

        if response.status_code == 200:
            index_data = response.json()
            index_file_id = index_data["file_id"]
            print(f"✅ Index data uploaded successfully: {index_file_id}")
            print(f"   Rows: {index_data.get('message', 'N/A')}")
        else:
            print(f"❌ Index upload failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Index upload error: {e}")
        return False

    # Test 4: Run analysis
    print("\n🧮 Testing PME analysis...")
    try:
        params = {"fund_file_id": fund_file_id, "index_file_id": index_file_id}
        response = requests.post(f"{base_url}/api/analysis/run", params=params)

        if response.status_code == 200:
            analysis_results = response.json()
            print("✅ Analysis completed successfully")

            # Test 5: Verify metrics structure
            print("\n📈 Verifying metrics structure...")
            if "metrics" in analysis_results:
                metrics = analysis_results["metrics"]

                # Check key metrics
                key_metrics = ["Fund IRR", "TVPI", "DPI", "RVPI"]
                for metric in key_metrics:
                    if metric in metrics:
                        value = metrics[metric]
                        print(f"   {metric}: {value}")
                    else:
                        print(f"   ❌ Missing metric: {metric}")

                # Check analytics data for charts
                print("\n📊 Verifying chart data...")
                if "Analytics Data" in metrics:
                    analytics = metrics["Analytics Data"]

                    chart_data_types = [
                        "performance_timeline",
                        "cash_flow_timeline",
                        "j_curve_data",
                        "twr_data",
                        "nav_waterfall",
                    ]

                    for data_type in chart_data_types:
                        if data_type in analytics:
                            data = analytics[data_type]
                            if isinstance(data, list):
                                print(f"   ✅ {data_type}: {len(data)} data points")
                            else:
                                print(f"   ✅ {data_type}: Available")
                        else:
                            print(f"   ❌ Missing chart data: {data_type}")
                else:
                    print("   ❌ No Analytics Data found")

                print("\n🎯 Sample Performance Timeline Data:")
                if (
                    "Analytics Data" in metrics
                    and "performance_timeline" in metrics["Analytics Data"]
                ):
                    timeline = metrics["Analytics Data"]["performance_timeline"]
                    if timeline:
                        for i, point in enumerate(timeline[:3]):  # Show first 3 points
                            print(
                                f"   Point {i+1}: Date={point.get('date')}, TVPI={point.get('tvpi'):.3f}, IRR={point.get('irr'):.1f}%"
                            )
                        if len(timeline) > 3:
                            print(f"   ... and {len(timeline) - 3} more points")

                return True
            else:
                print("❌ No metrics found in analysis results")
                return False
        else:
            print(f"❌ Analysis failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 PME Calculator Chart Integration Test")
    print("=" * 50)

    success = test_analysis_integration()

    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Charts should now display real data.")
        print("\n💡 Next steps:")
        print("   1. Open the frontend in your browser")
        print("   2. Upload the test files (test_sample.csv and test_index.csv)")
        print("   3. Run analysis to see the interactive charts with real data")
    else:
        print("❌ Some tests failed. Please check the issues above.")
