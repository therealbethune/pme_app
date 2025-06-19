"""Tests for analysis service."""

import random
import numpy as np
import pandas as pd
import pytest

# Set seeds for deterministic test results
random.seed(12345)
np.random.seed(12345)

from pme_app.services.analysis import (
    calculate_annualized_return,
    compute_alpha_beta,
    compute_drawdown,
    compute_volatility,
    direct_alpha,
    ks_pme,
    safe_div,
)


class TestSafeDiv:
    """Test safe division function."""

    def test_normal_division(self):
        """Test normal division cases."""
        assert safe_div(10, 2) == 5.0
        assert safe_div(7, 3) == pytest.approx(2.333, rel=1e-3)

    def test_division_by_zero(self):
        """Test division by zero returns NaN."""
        result = safe_div(10, 0)
        assert np.isnan(result)

    def test_zero_numerator(self):
        """Test zero numerator."""
        assert safe_div(0, 5) == 0.0


class TestKsPme:
    """Test Kaplan-Schoar PME calculation."""

    def test_basic_pme_calculation(self):
        """Test basic PME calculation with known values."""
        # Simple case: invest 100, get back 120, index grows 10%
        fund_cf = np.array([-100, 120])  # Contribution, then distribution
        idx_at_dates = np.array([100, 110])  # Index values at dates

        result = ks_pme(fund_cf, idx_at_dates)
        # Expected: (120 * 110/110) / (100 * 110/100) = 120/110 ≈ 1.09
        assert result == pytest.approx(1.09, rel=1e-2)

    def test_empty_arrays(self):
        """Test with empty arrays."""
        result = ks_pme(np.array([]), np.array([]))
        assert np.isnan(result)

    def test_no_contributions(self):
        """Test with no contributions (only distributions)."""
        fund_cf = np.array([100, 50])  # Only distributions
        idx_at_dates = np.array([100, 110])

        result = ks_pme(fund_cf, idx_at_dates)
        assert np.isnan(result)  # Should be NaN when no contributions


class TestDirectAlpha:
    """Test Direct Alpha calculation."""

    def test_positive_alpha(self):
        """Test case where fund outperforms index."""
        fund_irr = 0.15  # 15% fund return
        index_irr = 0.10  # 10% index return

        result = direct_alpha(fund_irr, index_irr)
        # Expected: (1.15/1.10) - 1 ≈ 0.0455
        assert result == pytest.approx(0.0455, rel=1e-2)

    def test_negative_alpha(self):
        """Test case where fund underperforms index."""
        fund_irr = 0.08  # 8% fund return
        index_irr = 0.12  # 12% index return

        result = direct_alpha(fund_irr, index_irr)
        # Expected: (1.08/1.12) - 1 ≈ -0.0357
        assert result == pytest.approx(-0.0357, rel=1e-2)

    def test_nan_inputs(self):
        """Test with NaN inputs."""
        assert np.isnan(direct_alpha(np.nan, 0.10))
        assert np.isnan(direct_alpha(0.10, np.nan))
        assert np.isnan(direct_alpha(None, 0.10))


class TestComputeVolatility:
    """Test volatility calculation."""

    def test_monthly_volatility(self):
        """Test monthly volatility calculation."""
        # Create simple return series with known volatility
        returns = pd.Series([0.01, -0.01, 0.02, -0.02, 0.01])

        result = compute_volatility(returns, freq="monthly")
        assert result > 0  # Should be positive
        assert not np.isnan(result)

    def test_empty_series(self):
        """Test with empty series."""
        returns = pd.Series([], dtype=float)
        result = compute_volatility(returns)
        assert np.isnan(result)

    def test_single_value(self):
        """Test with single value."""
        returns = pd.Series([0.05])
        result = compute_volatility(returns)
        assert np.isnan(result)


class TestComputeDrawdown:
    """Test maximum drawdown calculation."""

    def test_basic_drawdown(self):
        """Test basic drawdown calculation."""
        # Series that goes up then down
        series = pd.Series([100, 110, 120, 100, 90])

        result = compute_drawdown(series)
        # Max drawdown should be (90-120)/120 = -0.25
        assert result == pytest.approx(-0.25, rel=1e-3)

    def test_no_drawdown(self):
        """Test series with no drawdown (always increasing)."""
        series = pd.Series([100, 110, 120, 130])

        result = compute_drawdown(series)
        assert result == 0.0

    def test_single_value(self):
        """Test with single value."""
        series = pd.Series([100])
        result = compute_drawdown(series)
        assert np.isnan(result)


class TestComputeAlphaBeta:
    """Test alpha and beta calculation."""

    def test_basic_alpha_beta(self):
        """Test basic alpha/beta calculation."""
        # Create correlated return series
        index_returns = pd.Series([0.01, 0.02, -0.01, 0.03, -0.02])
        fund_returns = pd.Series(
            [0.015, 0.025, -0.005, 0.035, -0.015]
        )  # Higher returns

        alpha, beta = compute_alpha_beta(fund_returns, index_returns)

        assert not np.isnan(alpha)
        assert not np.isnan(beta)
        assert beta > 0  # Should be positive correlation

    def test_insufficient_data(self):
        """Test with insufficient data points."""
        fund_returns = pd.Series([0.01, 0.02])
        index_returns = pd.Series([0.01, 0.02])

        alpha, beta = compute_alpha_beta(fund_returns, index_returns)
        assert np.isnan(alpha)
        assert np.isnan(beta)

    def test_mismatched_lengths(self):
        """Test with different length series."""
        fund_returns = pd.Series([0.01, 0.02, 0.03])
        index_returns = pd.Series([0.01, 0.02])  # Shorter

        alpha, beta = compute_alpha_beta(fund_returns, index_returns)
        assert np.isnan(alpha)  # Should be NaN due to insufficient overlap
        assert np.isnan(beta)


class TestCalculateAnnualizedReturn:
    """Test annualized return calculation."""

    def test_positive_returns(self):
        """Test with positive returns."""
        # Monthly returns of 1%
        returns = pd.Series([0.01] * 12)

        result = calculate_annualized_return(returns, periods_per_year=12)
        # Expected: (1.01)^12 - 1 ≈ 0.1268
        assert result == pytest.approx(0.1268, rel=1e-3)

    def test_mixed_returns(self):
        """Test with mixed positive/negative returns."""
        returns = pd.Series([0.02, -0.01, 0.03, -0.02])

        result = calculate_annualized_return(returns, periods_per_year=4)
        assert not np.isnan(result)

    def test_empty_series(self):
        """Test with empty series."""
        returns = pd.Series([], dtype=float)
        result = calculate_annualized_return(returns)
        assert np.isnan(result)

    def test_extreme_negative_returns(self):
        """Test with extreme negative returns."""
        returns = pd.Series([-1.0, -0.5])  # -100% and -50% returns

        result = calculate_annualized_return(returns)
        assert np.isnan(result)  # Should handle extreme cases gracefully
