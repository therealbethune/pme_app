#!/usr/bin/env python3
"""Performance profiling script for PME analysis service."""

import cProfile
import pstats
import numpy as np
import pandas as pd
import time
from pme_app.services.analysis import (
    ks_pme,
    direct_alpha,
    compute_volatility,
    compute_drawdown,
    compute_alpha_beta,
    calculate_annualized_return,
)


def generate_sample_data(size: int = 1000):
    """Generate sample data for performance testing."""
    np.random.seed(42)  # For reproducible results

    # Generate fund cashflows
    fund_cf = np.random.normal(-1000, 500, size)
    fund_cf[::10] = np.abs(fund_cf[::10])  # Some positive distributions

    # Generate index values
    idx_values = 100 * np.cumprod(1 + np.random.normal(0.001, 0.02, size))

    # Generate return series
    returns = pd.Series(np.random.normal(0.01, 0.05, size))
    index_returns = pd.Series(np.random.normal(0.008, 0.04, size))

    # Generate price series for drawdown
    prices = pd.Series(100 * np.cumprod(1 + returns))

    return fund_cf, idx_values, returns, index_returns, prices


def benchmark_analysis_functions():
    """Benchmark all analysis functions."""
    print("🚀 Starting performance benchmarking...")

    # Generate test data
    fund_cf, idx_values, returns, index_returns, prices = generate_sample_data(10000)

    # Benchmark each function
    benchmarks = {}

    # KS PME
    start_time = time.time()
    for _ in range(100):
        ks_pme(fund_cf[:100], idx_values[:100])
    benchmarks["ks_pme"] = time.time() - start_time

    # Direct Alpha
    start_time = time.time()
    for _ in range(1000):
        direct_alpha(0.15, 0.10)
    benchmarks["direct_alpha"] = time.time() - start_time

    # Volatility
    start_time = time.time()
    for _ in range(100):
        compute_volatility(returns[:1000])
    benchmarks["compute_volatility"] = time.time() - start_time

    # Drawdown
    start_time = time.time()
    for _ in range(100):
        compute_drawdown(prices[:1000])
    benchmarks["compute_drawdown"] = time.time() - start_time

    # Alpha/Beta
    start_time = time.time()
    for _ in range(50):
        compute_alpha_beta(returns[:1000], index_returns[:1000])
    benchmarks["compute_alpha_beta"] = time.time() - start_time

    # Annualized Return
    start_time = time.time()
    for _ in range(100):
        calculate_annualized_return(returns[:1000])
    benchmarks["calculate_annualized_return"] = time.time() - start_time

    return benchmarks


def run_comprehensive_analysis():
    """Run a comprehensive analysis for profiling."""
    fund_cf, idx_values, returns, index_returns, prices = generate_sample_data(5000)

    # Run multiple analysis functions
    results = {}

    # PME calculations
    for i in range(10):
        subset_size = 500 + i * 100
        results[f"pme_{i}"] = ks_pme(fund_cf[:subset_size], idx_values[:subset_size])

    # Risk metrics
    for i in range(20):
        subset_size = 200 + i * 50
        results[f"vol_{i}"] = compute_volatility(returns[:subset_size])
        results[f"dd_{i}"] = compute_drawdown(prices[:subset_size])

    # Alpha/Beta analysis
    for i in range(5):
        subset_size = 1000 + i * 200
        alpha, beta = compute_alpha_beta(
            returns[:subset_size], index_returns[:subset_size]
        )
        results[f"alpha_{i}"] = alpha
        results[f"beta_{i}"] = beta

    return results


def main():
    """Main profiling function."""
    print("📊 PME Analysis Service Performance Profiler")
    print("=" * 50)

    # Run benchmarks
    print("\n1. Running function benchmarks...")
    benchmarks = benchmark_analysis_functions()

    print("\n📈 Benchmark Results:")
    for func_name, duration in benchmarks.items():
        print(f"  {func_name:25} {duration:.4f}s")

    # Identify hotspots
    print("\n🔥 Performance Hotspots:")
    sorted_benchmarks = sorted(benchmarks.items(), key=lambda x: x[1], reverse=True)
    for func_name, duration in sorted_benchmarks[:3]:
        print(f"  {func_name:25} {duration:.4f}s (slowest)")

    # Run comprehensive profiling
    print("\n2. Running comprehensive analysis profiling...")
    profiler = cProfile.Profile()
    profiler.enable()

    results = run_comprehensive_analysis()

    profiler.disable()

    # Save profile results
    profiler.dump_stats("analysis_profile.prof")

    # Generate stats
    stats = pstats.Stats("analysis_profile.prof")
    stats.sort_stats("cumulative")

    print("\n📊 Top 10 Functions by Cumulative Time:")
    stats.print_stats(10)

    print(f"\n✅ Profiling complete! Generated {len(results)} analysis results.")
    print("📁 Profile saved to: analysis_profile.prof")
    print("🐍 View with: snakeviz analysis_profile.prof")

    # Performance recommendations
    print("\n💡 Performance Recommendations:")
    if benchmarks["compute_alpha_beta"] > 0.1:
        print(
            "  • Consider optimizing alpha/beta calculation with vectorized operations"
        )
    if benchmarks["ks_pme"] > 0.05:
        print("  • PME calculation could benefit from numpy optimization")
    if benchmarks["compute_volatility"] > 0.02:
        print("  • Volatility calculation is efficient")

    print("\n🎯 To optimize hotspots:")
    print("  1. Use numpy vectorized operations where possible")
    print("  2. Consider caching expensive calculations")
    print("  3. Profile with larger datasets to identify scaling issues")


if __name__ == "__main__":
    main()
