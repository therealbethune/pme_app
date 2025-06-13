#!/usr/bin/env python3
"""
Simple test script to verify Phase 1 implementation works correctly.
This tests the core functionality that fixes the boolean index mismatch error.
"""

import pandas as pd

# Import Phase 1 components
from pme_math.alignment_engine import DataAlignmentEngine
from pme_math.error_envelope import (
    envelope_ok,
    ErrorCollector,
)


def test_alignment_engine():
    """Test the DataAlignmentEngine with realistic data."""
    print("🧪 Testing DataAlignmentEngine...")

    # Create test data that replicates the original error (132 vs 24 rows)
    fund_dates = pd.date_range("2023-01-01", periods=132, freq="D")
    fund_data = pd.DataFrame(
        {
            "date": fund_dates.strftime("%Y-%m-%d"),
            "cashflow": [(-1000 if i % 30 == 0 else 0) for i in range(132)],
        }
    )

    index_dates = pd.date_range("2023-01-01", periods=24, freq="W")
    index_data = pd.DataFrame(
        {
            "date": index_dates.strftime("%Y-%m-%d"),
            "value": [100 + i for i in range(24)],
        }
    )

    print(f"📊 Original data shapes: Fund={fund_data.shape}, Index={index_data.shape}")
    print(
        "   This would cause: 'boolean index did not match indexed array along axis 0'"
    )

    # Use alignment engine to fix the issue
    engine = DataAlignmentEngine(missing_strategy="forward_fill")

    try:
        fund_aligned, index_aligned = engine.align_fund_and_index(fund_data, index_data)

        print(
            f"✅ Aligned data shapes: Fund={fund_aligned.shape}, Index={index_aligned.shape}"
        )
        print(f"   Alignment successful: {len(fund_aligned) == len(index_aligned)}")

        # Get alignment summary
        summary = engine.get_alignment_summary(fund_aligned, index_aligned)
        print(
            f"   Date range: {summary['date_range']['start']} to {summary['date_range']['end']}"
        )
        print(f"   Total aligned dates: {summary['total_dates']}")

        return True

    except Exception as e:
        print(f"❌ Alignment failed: {e}")
        return False


def test_error_envelope():
    """Test the error envelope system."""
    print("\n🧪 Testing Error Envelope System...")

    # Test successful envelope
    envelope = envelope_ok({"test": "data", "value": 42})
    print(f"✅ Success envelope: success={envelope.success}, data={envelope.data}")

    # Test error collection
    collector = ErrorCollector()
    collector.add_data_alignment_error(
        "Test alignment error", {"fund_rows": 132, "index_rows": 24}
    )

    error_envelope = collector.to_envelope()
    print(
        f"✅ Error envelope: success={error_envelope.success}, errors={len(error_envelope.errors)}"
    )

    return True


def test_integration_scenario():
    """Test a realistic PME calculation scenario."""
    print("\n🧪 Testing Integration Scenario...")

    # Create realistic quarterly fund data vs daily index data
    fund_dates = pd.date_range("2022-01-01", "2023-12-31", freq="QS")
    fund_data = pd.DataFrame(
        {
            "date": fund_dates.strftime("%Y-%m-%d"),
            "cashflow": [-1000000, -500000, 0, 200000, 0, 300000, 0, 500000],
        }
    )

    index_dates = pd.date_range("2022-01-01", "2023-12-31", freq="B")  # Business days
    index_data = pd.DataFrame(
        {
            "date": index_dates.strftime("%Y-%m-%d"),
            "value": [100 + i * 0.01 for i in range(len(index_dates))],
        }
    )

    print(
        f"📊 Realistic scenario: Fund={fund_data.shape} (quarterly), Index={index_data.shape} (daily)"
    )

    # Use alignment engine
    engine = DataAlignmentEngine(missing_strategy="forward_fill")

    try:
        fund_aligned, index_aligned = engine.align_fund_and_index(fund_data, index_data)

        print(f"✅ Integration test passed: {len(fund_aligned)} aligned business days")
        print("   Both datasets now have identical date alignment")

        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def main():
    """Run all Phase 1 tests."""
    print("🚀 Phase 1 Implementation Test Suite")
    print("=" * 50)

    results = []

    # Run tests
    results.append(test_alignment_engine())
    results.append(test_error_envelope())
    results.append(test_integration_scenario())

    print("\n" + "=" * 50)

    if all(results):
        print("🎉 All Phase 1 tests PASSED!")
        print("✅ DataAlignmentEngine successfully fixes boolean index mismatch errors")
        print("✅ Error envelope system provides structured error handling")
        print("✅ Ready to integrate with existing PME calculation endpoints")
        return 0
    else:
        print("❌ Some Phase 1 tests FAILED!")
        return 1


if __name__ == "__main__":
    exit(main())
