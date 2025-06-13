#!/usr/bin/env python3
"""
Test upload integration with the fixed PMEAnalysisEngine.
"""

import sys
import os
import tempfile
import pandas as pd
from pathlib import Path
import asyncio

# Add backend directory to path
backend_dir = Path(__file__).parent / "pme_calculator" / "backend"
sys.path.insert(0, str(backend_dir))


async def test_upload_integration():
    """Test the upload integration with PMEAnalysisEngine."""
    print("🔍 Testing upload integration...")

    try:
        from analysis_engine import PMEAnalysisEngine

        # Create test fund data
        fund_data = pd.DataFrame(
            {
                "Date": ["2020-01-01", "2020-06-01", "2021-01-01"],
                "Contributions": [-100, -50, 0],
                "Distributions": [0, 10, 80],
                "NAV": [100, 140, 60],
            }
        )

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            fund_data.to_csv(f.name, index=False)
            temp_path = f.name

        try:
            # Test the upload flow exactly as main_minimal.py does it
            engine = PMEAnalysisEngine()
            fund_info = engine.load_fund_data(temp_path)  # This was failing before

            print("✅ Upload integration test: SUCCESS")
            print(f"   Loaded {fund_info['rows']} rows")
            print(f"   Columns: {fund_info['column_names']}")
            print(f"   Engine fund_data shape: {engine.fund_data.shape}")

            # Test that we can access the columns as the upload code does
            columns = list(engine.fund_data.columns)
            print(f"   Accessible columns: {columns}")

            return True

        finally:
            os.unlink(temp_path)

    except Exception as e:
        print(f"❌ Upload integration test failed: {e}")
        return False


async def test_full_upload_simulation():
    """Simulate the full upload process."""
    print("🔍 Testing full upload simulation...")

    try:
        # Mock the UploadFile
        class MockUploadFile:
            def __init__(self, content, filename):
                self.content = content
                self.filename = filename
                self.content_type = "text/csv"

            async def read(self):
                return self.content.encode()

        # Create test CSV content
        csv_content = """Date,Contributions,Distributions,NAV
2020-01-01,-100,0,100
2020-06-01,-50,10,140
2021-01-01,0,80,60"""

        mock_file = MockUploadFile(csv_content, "test_fund.csv")

        # Simulate save_temp_file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as tmp_file:
            content = await mock_file.read()
            tmp_file.write(content.decode())
            tmp_file_path = tmp_file.name

        try:
            # Simulate the upload_fund_file logic
            from analysis_engine import PMEAnalysisEngine

            engine = PMEAnalysisEngine()
            fund_info = engine.load_fund_data(tmp_file_path)

            # Simulate the response data creation
            file_size = os.path.getsize(tmp_file_path)

            upload_data = {
                "filename": f"fund_{mock_file.filename}",
                "original_filename": mock_file.filename,
                "file_size": file_size,
                "rows_count": fund_info["rows"],
                "columns_count": len(engine.fund_data.columns),
                "columns_info": list(engine.fund_data.columns),
            }

            print("✅ Full upload simulation: SUCCESS")
            print(f"   Upload data: {upload_data}")

            return True

        finally:
            os.unlink(tmp_file_path)

    except Exception as e:
        print(f"❌ Full upload simulation failed: {e}")
        return False


async def main():
    """Run all integration tests."""
    print("🚀 Starting upload integration tests...")

    tests = [test_upload_integration(), test_full_upload_simulation()]

    results = await asyncio.gather(*tests, return_exceptions=True)

    passed = sum(1 for result in results if result is True)
    failed = len(results) - passed

    print(f"\n📊 Integration Test Results: {passed} passed, {failed} failed")

    if failed > 0:
        print("❌ Some tests failed:")
        for i, result in enumerate(results):
            if result is not True:
                print(f"   Test {i+1}: {result}")

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
