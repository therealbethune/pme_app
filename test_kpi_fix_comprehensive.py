#!/usr/bin/env python3
"""
Comprehensive test to verify KPI and loading fixes
"""

import time

import requests


def test_comprehensive_fix():
    """Test the comprehensive KPI fix"""
    base_url = "http://localhost:8000"

    print("🧪 Testing Comprehensive KPI Fix...")

    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"✅ Health check: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return

    # Test 2: Metrics summary endpoint (should return zeros initially)
    try:
        response = requests.get(f"{base_url}/api/metrics/summary")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Metrics summary (before analysis): {data}")

            metrics = data.get("metrics", {})
            print(f"   IRR: {metrics.get('Fund IRR', 0):.1%}")
            print(f"   TVPI: {metrics.get('TVPI', 0):.2f}x")
            print(f"   DPI: {metrics.get('DPI', 0):.2f}x")
            print(f"   RVPI: {metrics.get('RVPI', 0):.2f}x")
        else:
            print(f"❌ Metrics summary failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Metrics summary error: {e}")

    # Test 3: Check uploaded files
    try:
        response = requests.get(f"{base_url}/api/upload/files")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Uploaded files: {len(data.get('files', []))} files")

            # If we have files, try to run analysis
            files = data.get("files", [])
            fund_files = [f for f in files if f.get("type") == "fund"]
            index_files = [f for f in files if f.get("type") == "index"]

            if fund_files and index_files:
                fund_id = fund_files[0]["file_id"]
                index_id = index_files[0]["file_id"]

                print(f"   Found fund: {fund_id}")
                print(f"   Found index: {index_id}")

                # Test 4: Run analysis
                try:
                    response = requests.post(
                        f"{base_url}/api/analysis/run-sync",
                        params={"fund_file_id": fund_id, "index_file_id": index_id},
                    )
                    if response.status_code == 200:
                        analysis_data = response.json()
                        print(
                            f"✅ Analysis completed: {analysis_data.get('success', False)}"
                        )

                        if "metrics" in analysis_data:
                            metrics = analysis_data["metrics"]
                            print(f"   Analysis IRR: {metrics.get('Fund IRR', 0):.1%}")
                            print(f"   Analysis TVPI: {metrics.get('TVPI', 0):.2f}x")

                        # Test 5: Check metrics summary after analysis
                        time.sleep(1)  # Give it a moment to store results
                        response = requests.get(f"{base_url}/api/metrics/summary")
                        if response.status_code == 200:
                            data = response.json()
                            print(f"✅ Metrics summary (after analysis): {data}")

                            metrics = data.get("metrics", {})
                            print(
                                f"   Post-analysis IRR: {metrics.get('Fund IRR', 0):.1%}"
                            )
                            print(
                                f"   Post-analysis TVPI: {metrics.get('TVPI', 0):.2f}x"
                            )
                        else:
                            print(
                                f"❌ Post-analysis metrics summary failed: {response.status_code}"
                            )
                    else:
                        print(f"❌ Analysis failed: {response.status_code}")
                        print(f"   Response: {response.text}")
                except Exception as e:
                    print(f"❌ Analysis error: {e}")
            else:
                print("   No fund/index files found for analysis test")
        else:
            print(f"❌ Upload files check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Upload files error: {e}")

    # Test 6: Chart endpoints
    chart_endpoints = [
        "/v1/metrics/irr_pme",
        "/v1/metrics/twr_vs_index",
        "/v1/metrics/cashflow_overview",
    ]

    for endpoint in chart_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                print(f"✅ Chart endpoint {endpoint}: OK")
            else:
                print(f"❌ Chart endpoint {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ Chart endpoint {endpoint} error: {e}")


if __name__ == "__main__":
    test_comprehensive_fix()
