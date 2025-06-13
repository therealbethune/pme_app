"""
Benchmark Library for PME Calculator
Provides built-in market indices and industry-specific benchmarks
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os

class BenchmarkLibrary:
    """Manages built-in benchmark indices and industry-specific benchmarks."""

    def __init__(self):
        self.benchmarks = self._initialize_benchmarks()

    def _initialize_benchmarks(self) -> Dict:
        """Initialize the benchmark library with available indices."""
        return {
            # Broad Market Indices
            "sp500": {
                "name": "S&P 500",
                "description": "Large-cap U.S. equity index",
                "category": "Broad Market",
                "asset_class": "Public Equity",
                "geography": "United States",
                "data_source": "synthetic",
                "risk_profile": "Medium"
            },
            "russell2000": {
                "name": "Russell 2000",
                "description": "Small-cap U.S. equity index",
                "category": "Broad Market",
                "asset_class": "Public Equity",
                "geography": "United States",
                "data_source": "synthetic",
                "risk_profile": "High"
            },
            "nasdaq": {
                "name": "NASDAQ Composite",
                "description": "Technology-heavy U.S. equity index",
                "category": "Broad Market",
                "asset_class": "Public Equity",
                "geography": "United States",
                "data_source": "synthetic",
                "risk_profile": "High"
            },
            "msci_world": {
                "name": "MSCI World",
                "description": "Global developed markets equity index",
                "category": "International",
                "asset_class": "Public Equity",
                "geography": "Global",
                "data_source": "synthetic",
                "risk_profile": "Medium"
            },
            "msci_em": {
                "name": "MSCI Emerging Markets",
                "description": "Emerging markets equity index",
                "category": "International",
                "asset_class": "Public Equity",
                "geography": "Emerging Markets",
                "data_source": "synthetic",
                "risk_profile": "High"
            },

            # Private Equity Benchmarks
            "cambridge_pe": {
                "name": "Cambridge PE Index",
                "description": "Private equity pooled return index",
                "category": "Private Equity",
                "asset_class": "Private Equity",
                "geography": "Global",
                "data_source": "synthetic",
                "risk_profile": "Very High"
            },
            "preqin_pe": {
                "name": "Preqin PE Benchmark",
                "description": "Private equity industry benchmark",
                "category": "Private Equity",
                "asset_class": "Private Equity",
                "geography": "Global",
                "data_source": "synthetic",
                "risk_profile": "Very High"
            },

            # Real Estate
            "reit_index": {
                "name": "FTSE NAREIT Index",
                "description": "U.S. real estate investment trusts",
                "category": "Real Estate",
                "asset_class": "Real Estate",
                "geography": "United States",
                "data_source": "synthetic",
                "risk_profile": "Medium-High"
            },

            # Fixed Income
            "us_10y": {
                "name": "U.S. 10-Year Treasury",
                "description": "U.S. government bond benchmark",
                "category": "Fixed Income",
                "asset_class": "Fixed Income",
                "geography": "United States",
                "data_source": "synthetic",
                "risk_profile": "Low"
            },
            "investment_grade": {
                "name": "Investment Grade Bonds",
                "description": "U.S. investment grade corporate bonds",
                "category": "Fixed Income",
                "asset_class": "Fixed Income",
                "geography": "United States",
                "data_source": "synthetic",
                "risk_profile": "Low-Medium"
            }
        }

    def get_available_benchmarks(self, category: Optional[str] = None) -> Dict:
        """Get list of available benchmarks, optionally filtered by category."""
        if category:
            return {k: v for k, v in self.benchmarks.items()
                   if v["category"] == category}
        return self.benchmarks

    def get_categories(self) -> List[str]:
        """Get list of available benchmark categories."""
        categories = set(benchmark["category"] for benchmark in self.benchmarks.values())
        return sorted(list(categories))

    def generate_benchmark_data(self, benchmark_id: str, start_date: datetime,
                              end_date: datetime, frequency: str = "M") -> pd.DataFrame:
        """Generate synthetic benchmark data for the specified period."""
        if benchmark_id not in self.benchmarks:
            raise ValueError(f"Benchmark {benchmark_id} not found in library")

        benchmark_info = self.benchmarks[benchmark_id]

        # Generate date range
        if frequency == "M":
            date_range = pd.date_range(start=start_date, end=end_date, freq="ME")
        elif frequency == "Q":
            date_range = pd.date_range(start=start_date, end=end_date, freq="QE")
        else:
            date_range = pd.date_range(start=start_date, end=end_date, freq="D")

        # Generate synthetic returns based on benchmark characteristics
        returns = self._generate_synthetic_returns(benchmark_id, len(date_range))

        # Calculate cumulative prices starting from 100
        prices = 100 * (1 + pd.Series(returns)).cumprod()

        # Create DataFrame
        df = pd.DataFrame({
            'price': prices.values,
            'return': returns
        }, index=date_range)

        return df

    def _generate_synthetic_returns(self, benchmark_id: str, num_periods: int) -> np.ndarray:
        """Generate realistic synthetic returns for a benchmark."""
        benchmark_info = self.benchmarks[benchmark_id]

        # Set parameters based on benchmark type
        if benchmark_id == "sp500":
            mean_return = 0.008  # ~10% annually
            volatility = 0.15
            trend = 0.0001
        elif benchmark_id == "russell2000":
            mean_return = 0.009  # Higher return for small caps
            volatility = 0.20
            trend = 0.0001
        elif benchmark_id == "nasdaq":
            mean_return = 0.010  # Tech premium
            volatility = 0.22
            trend = 0.0002
        elif benchmark_id == "msci_world":
            mean_return = 0.007
            volatility = 0.16
            trend = 0.0001
        elif benchmark_id == "msci_em":
            mean_return = 0.008
            volatility = 0.25
            trend = 0.0001
        elif benchmark_id in ["cambridge_pe", "preqin_pe"]:
            mean_return = 0.012  # PE premium
            volatility = 0.30
            trend = 0.0002
        elif benchmark_id == "reit_index":
            mean_return = 0.007
            volatility = 0.18
            trend = 0.0001
        elif benchmark_id == "us_10y":
            mean_return = 0.003  # Bond returns
            volatility = 0.05
            trend = -0.0001  # Declining rates trend
        elif benchmark_id == "investment_grade":
            mean_return = 0.004
            volatility = 0.07
            trend = 0.0000
        else:
            # Default parameters
            mean_return = 0.006
            volatility = 0.15
            trend = 0.0001

        # Generate returns with some autocorrelation and trends
        np.random.seed(42)  # For reproducible results

        # Base random returns
        random_returns = np.random.normal(mean_return, volatility, num_periods)

        # Add some momentum/mean reversion
        momentum_factor = 0.1
        for i in range(1, num_periods):
            random_returns[i] += momentum_factor * random_returns[i-1]

        # Add trend component
        trend_component = np.linspace(0, trend * num_periods, num_periods)
        returns = random_returns + trend_component

        # Add some market cycles (bear/bull markets)
        cycle_length = max(60, num_periods // 3)  # ~5 year cycles
        cycle_amplitude = volatility * 0.3
        cycle_component = cycle_amplitude * np.sin(2 * np.pi * np.arange(num_periods) / cycle_length)
        returns += cycle_component

        return returns

    def get_benchmark_info(self, benchmark_id: str) -> Dict:
        """Get detailed information about a specific benchmark."""
        if benchmark_id not in self.benchmarks:
            raise ValueError(f"Benchmark {benchmark_id} not found in library")
        return self.benchmarks[benchmark_id].copy()

    def search_benchmarks(self, query: str) -> Dict:
        """Search benchmarks by name or description."""
        query_lower = query.lower()
        results = {}

        for bench_id, info in self.benchmarks.items():
            if (query_lower in info["name"].lower() or
                query_lower in info["description"].lower() or
                query_lower in info["category"].lower() or
                query_lower in info["asset_class"].lower()):
                results[bench_id] = info

        return results

    def get_recommended_benchmarks(self, fund_type: str = "private_equity") -> List[str]:
        """Get recommended benchmarks for a specific fund type."""
        recommendations = {
            "private_equity": ["sp500", "russell2000", "cambridge_pe"],
            "real_estate": ["reit_index", "sp500"],
            "venture_capital": ["nasdaq", "russell2000"],
            "buyout": ["sp500", "cambridge_pe"],
            "growth_equity": ["sp500", "nasdaq"],
            "distressed": ["sp500", "investment_grade"],
            "infrastructure": ["sp500", "us_10y"],
            "natural_resources": ["sp500", "msci_world"]
        }

        return recommendations.get(fund_type, ["sp500"])

    def export_benchmark_data(self, benchmark_id: str, start_date: datetime,
                            end_date: datetime, file_path: str,
                            frequency: str = "M") -> bool:
        """Export benchmark data to CSV file."""
        try:
            df = self.generate_benchmark_data(benchmark_id, start_date, end_date, frequency)
            df.to_csv(file_path)
            return True
        except Exception as e:
            print(f"Error exporting benchmark data: {e}")
            return False

    def create_custom_benchmark(self, name: str, description: str,
                              category: str, returns_data: pd.Series) -> str:
        """Create a custom benchmark from user-provided returns data."""
        # Generate unique ID
        custom_id = f"custom_{len(self.benchmarks)}"

        # Add to benchmarks
        self.benchmarks[custom_id] = {
            "name": name,
            "description": description,
            "category": category,
            "asset_class": "Custom",
            "geography": "Custom",
            "data_source": "user_provided",
            "risk_profile": "Custom",
            "returns_data": returns_data
        }

        return custom_id

# Singleton instance
benchmark_library = BenchmarkLibrary()
