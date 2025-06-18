#!/usr/bin/env python3
"""Performance profiling script for PME calculations."""

import cProfile
import pstats
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add project paths
sys.path.append(".")
sys.path.append("pme_calculator")


def create_test_data(n_periods=20):
    """Create realistic test data for profiling."""
    np.random.seed(42)
    dates = pd.date_range("2020-01-01", periods=n_periods, freq="Q")

    # Simulate realistic PE fund data
    fund_data = pd.DataFrame(
        {
            "Date": dates,
            "Cash_Flow": np.random.normal(
                -500000, 1000000, n_periods
            ),  # Negative = investments
            "NAV": np.cumsum(np.random.uniform(100000, 500000, n_periods)),
        }
    )

    # Simulate index data
    index_data = pd.DataFrame(
        {
            "Date": dates,
            "Cash_Flow": np.zeros(n_periods),  # Index has no cash flows
            "NAV": np.cumprod(1 + np.random.normal(0.02, 0.05, n_periods)) * 1000000,
        }
    )

    return fund_data, index_data


def profile_pme_calculations():
    """Profile PME calculation performance."""
    print("Creating test data...")
    fund_data, index_data = create_test_data(50)  # 50 quarters = ~12 years

    print("Starting performance profiling...")

    def run_pme_analysis():
        try:
            # Import here to avoid import issues in profiling
            from pme_calculator.backend.pme_engine import PMEEngine

            engine = PMEEngine()
            result = engine.calculate_pme_metrics(fund_data, index_data)
            print(f"PME calculation completed: {len(result) if result else 0} metrics")
            return result

        except ImportError as e:
            print(f"Import error: {e}")
            # Fallback to basic math operations
            return perform_basic_pme_calc(fund_data, index_data)
        except Exception as e:
            print(f"PME calculation error: {e}")
            return None

    # Run profiling
    profiler = cProfile.Profile()
    profiler.enable()

    result = run_pme_analysis()

    profiler.disable()

    # Save and analyze results
    profiler.dump_stats("pme_performance.prof")

    # Print top bottlenecks
    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")

    print("\n=== TOP 20 PERFORMANCE BOTTLENECKS ===")
    stats.print_stats(20)

    print("\n=== FUNCTION CALL ANALYSIS ===")
    stats.sort_stats("calls")
    stats.print_stats(10)

    return result


def perform_basic_pme_calc(fund_data, index_data):
    """Basic PME calculation for profiling fallback."""
    print("Running basic PME calculation...")

    # Simple PME calculation
    fund_cf = fund_data["Cash_Flow"].sum()
    fund_nav = fund_data["NAV"].iloc[-1]
    index_nav = index_data["NAV"].iloc[-1]

    # Basic multiple calculation
    total_value = fund_nav + fund_cf
    multiple = total_value / abs(fund_cf) if fund_cf != 0 else 0

    return {
        "multiple": multiple,
        "total_value": total_value,
        "fund_nav": fund_nav,
        "index_nav": index_nav,
    }


if __name__ == "__main__":
    print("=== PME PERFORMANCE PROFILING ===")
    result = profile_pme_calculations()
    print(f"\nProfiling complete. Results: {result}")
    print("Profile saved to: pme_performance.prof")
