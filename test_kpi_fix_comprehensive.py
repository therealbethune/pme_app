#!/usr/bin/env python3
"""
Comprehensive test to verify KPI and loading fixes
"""

import time

import requests
import structlog

logger = structlog.get_logger()


def test_comprehensive_fix():
    """Test the comprehensive KPI fix"""
    base_url = "http://localhost:8000"

    logger.debug("🧪 Testing Comprehensive KPI Fix...")

    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/api/health")
        logger.debug(f"✅ Health check: {response.status_code}")
    except Exception as e:
        logger.debug(f"❌ Health check failed: {e}")
        return

    # Test 2: Metrics summary endpoint (should return zeros initially)
    try:
        response = requests.get(f"{base_url}/api/metrics/summary")
        if response.status_code == 200:
            data = response.json()
            logger.debug(f"✅ Metrics summary (before analysis): {data}")

            metrics = data.get("metrics", {})
            logger.debug(f"   IRR: {metrics.get('Fund IRR', 0):.1%}")
            logger.debug(f"   TVPI: {metrics.get('TVPI', 0):.2f}x")
            logger.debug(f"   DPI: {metrics.get('DPI', 0):.2f}x")
            logger.debug(f"   RVPI: {metrics.get('RVPI', 0):.2f}x")
        else:
            logger.debug(f"❌ Metrics summary failed: {response.status_code}")
            logger.debug(f"   Response: {response.text}")
    except Exception as e:
        logger.debug(f"❌ Metrics summary error: {e}")

    # Test 3: Check uploaded files
    try:
        response = requests.get(f"{base_url}/api/upload/files")
        if response.status_code == 200:
            data = response.json()
            logger.debug(f"✅ Uploaded files: {len(data.get('files', []))} files")

            # If we have files, try to run analysis
            files = data.get("files", [])
            fund_files = [f for f in files if f.get("type") == "fund"]
            index_files = [f for f in files if f.get("type") == "index"]

            if fund_files and index_files:
                fund_id = fund_files[0]["file_id"]
                index_id = index_files[0]["file_id"]

                logger.debug(f"   Found fund: {fund_id}")
                logger.debug(f"   Found index: {index_id}")

                # Test 4: Run analysis
                try:
                    response = requests.post(
                        f"{base_url}/api/analysis/run-sync",
                        params={"fund_file_id": fund_id, "index_file_id": index_id},
                    )
                    if response.status_code == 200:
                        analysis_data = response.json()
                        logger.debug(
                            f"✅ Analysis completed: {analysis_data.get('success', False)}"
                        )

                        if "metrics" in analysis_data:
                            metrics = analysis_data["metrics"]
                            logger.debug(
                                f"   Analysis IRR: {metrics.get('Fund IRR', 0):.1%}"
                            )
                            logger.debug(
                                f"   Analysis TVPI: {metrics.get('TVPI', 0):.2f}x"
                            )

                        # Test 5: Check metrics summary after analysis
                        time.sleep(1)  # Give it a moment to store results
                        response = requests.get(f"{base_url}/api/metrics/summary")
                        if response.status_code == 200:
                            data = response.json()
                            logger.debug(f"✅ Metrics summary (after analysis): {data}")

                            metrics = data.get("metrics", {})
                            logger.debug(
                                f"   Post-analysis IRR: {metrics.get('Fund IRR', 0):.1%}"
                            )
                            logger.debug(
                                f"   Post-analysis TVPI: {metrics.get('TVPI', 0):.2f}x"
                            )
                        else:
                            logger.debug(
                                f"❌ Post-analysis metrics summary failed: {response.status_code}"
                            )
                    else:
                        logger.debug(f"❌ Analysis failed: {response.status_code}")
                        logger.debug(f"   Response: {response.text}")
                except Exception as e:
                    logger.debug(f"❌ Analysis error: {e}")
            else:
                logger.debug("   No fund/index files found for analysis test")
        else:
            logger.debug(f"❌ Upload files check failed: {response.status_code}")
    except Exception as e:
        logger.debug(f"❌ Upload files error: {e}")

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
                logger.debug(f"✅ Chart endpoint {endpoint}: OK")
            else:
                logger.debug(f"❌ Chart endpoint {endpoint}: {response.status_code}")
        except Exception as e:
            logger.debug(f"❌ Chart endpoint {endpoint} error: {e}")


if __name__ == "__main__":
    test_comprehensive_fix()
