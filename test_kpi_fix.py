#!/usr/bin/env python3
"""
Quick test to verify KPI and loading fixes
"""

import requests
import json
import time

def test_kpi_endpoints():
    """Test the KPI endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing KPI Fix...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"✅ Health check: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test metrics summary endpoint
    try:
        response = requests.get(f"{base_url}/api/metrics/summary")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Metrics summary: {data}")
            
            # Check if we have the expected structure
            if 'metrics' in data:
                metrics = data['metrics']
                print(f"   IRR: {metrics.get('Fund IRR', 0):.1%}")
                print(f"   TVPI: {metrics.get('TVPI', 0):.2f}x")
                print(f"   DPI: {metrics.get('DPI', 0):.2f}x")
                print(f"   RVPI: {metrics.get('RVPI', 0):.2f}x")
        else:
            print(f"❌ Metrics summary failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Metrics summary error: {e}")
    
    # Test chart endpoints
    chart_endpoints = [
        "/v1/metrics/irr_pme",
        "/v1/metrics/twr_vs_index",
        "/v1/metrics/cashflow_overview"
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
    test_kpi_endpoints() 