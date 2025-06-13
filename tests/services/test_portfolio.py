import pandas as pd
import pytest

from pme_app.services.portfolio import calc_portfolio_metrics, calculate_max_drawdown


def test_portfolio_smoke():
    """Basic smoke test for portfolio metrics calculation."""
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    df = pd.DataFrame({"Date": idx, "NAV": [100, 101, 103, 104, 106]})
    result = calc_portfolio_metrics({"FundA": df})

    assert "Total NAV" in result.columns
    assert result.at[0, "Funds"] == 1
    assert result.at[0, "Total NAV"] == 106.0


def test_portfolio_multiple_funds():
    """Test portfolio metrics with multiple funds."""
    idx = pd.date_range("2024-01-01", periods=5, freq="D")

    fund_a = pd.DataFrame({"Date": idx, "NAV": [100, 101, 103, 104, 106]})
    fund_b = pd.DataFrame({"Date": idx, "NAV": [200, 202, 198, 205, 210]})

    result = calc_portfolio_metrics({"FundA": fund_a, "FundB": fund_b})

    assert result.at[0, "Funds"] == 2
    assert result.at[0, "Total NAV"] == 316.0  # 106 + 210
    assert "Annualized Return" in result.columns
    assert "Volatility" in result.columns
    assert "Sharpe (rf=0)" in result.columns


def test_portfolio_empty_input():
    """Test portfolio metrics with empty input."""
    result = calc_portfolio_metrics({})
    assert result.empty


def test_portfolio_different_column_names():
    """Test portfolio metrics with different column naming conventions."""
    idx = pd.date_range("2024-01-01", periods=3, freq="D")

    # Different date column names
    fund_a = pd.DataFrame({"date": idx, "nav": [100, 101, 102]})
    fund_b = pd.DataFrame({"timestamp": idx, "value": [200, 201, 203]})

    result = calc_portfolio_metrics({"FundA": fund_a, "FundB": fund_b})

    assert result.at[0, "Funds"] == 2
    assert result.at[0, "Total NAV"] == 305.0  # 102 + 203


def test_calculate_max_drawdown():
    """Test maximum drawdown calculation."""
    # Test with simple declining returns
    returns = pd.Series([0.1, -0.05, -0.1, 0.05])
    drawdown = calculate_max_drawdown(returns)

    assert drawdown < 0  # Drawdown should be negative

    # Test with empty series
    empty_returns = pd.Series([])
    assert calculate_max_drawdown(empty_returns) == 0.0


def test_portfolio_error_handling():
    """Test portfolio metrics error handling with malformed data."""
    # Test with DataFrame that has no valid columns
    bad_df = pd.DataFrame({"random_col": [1, 2, 3]})

    result = calc_portfolio_metrics({"BadFund": bad_df})

    # Should still return a result, possibly with synthetic data
    assert not result.empty
    assert result.at[0, "Funds"] == 1


def test_portfolio_single_data_point():
    """Test portfolio metrics with single data point."""
    df = pd.DataFrame({"Date": ["2024-01-01"], "NAV": [100]})
    result = calc_portfolio_metrics({"FundA": df})

    assert result.at[0, "Funds"] == 1
    assert result.at[0, "Total NAV"] == 100.0
    # With single point, returns should be 0
    assert result.at[0, "Annualized Return"] == 0.0
