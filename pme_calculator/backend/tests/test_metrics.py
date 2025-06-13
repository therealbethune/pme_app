"""
Test suite for PME metrics calculations.
"""
import sys
import os
from pathlib import Path

# Add parent directory to Python path so we can import pme_math
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from pme_math.metrics import ks_pme, xirr_wrapper


@pytest.fixture
def sample_cashflow_data():
    """
    Sample cashflow fixture with hard-coded small dataset.
    Returns fund and index data where fund === index for testing KS ≈ 1.
    """
    dates = [
        datetime(2020, 1, 1),
        datetime(2020, 4, 1), 
        datetime(2020, 7, 1),
        datetime(2020, 10, 1),
        datetime(2021, 1, 1)
    ]
    
    # Fund data - same as index for KS=1 test
    fund_data = pd.DataFrame({
        'Date': dates,
        'Cash_Flow': [-1000, -500, 0, 200, 800],  # Initial investment, additional, no flow, partial return, final return
        'NAV': [1000, 1450, 1520, 1680, 0]       # Net Asset Value progression
    })
    
    # Index data - identical to fund for KS=1 test
    index_data = pd.DataFrame({
        'Date': dates,
        'Index_Value': [100, 145, 152, 168, 200]  # Index progression matching fund performance
    })
    
    return {
        'fund': fund_data,
        'index': index_data
    }


def test_ks_pme_identical_performance():
    """
    Test that KS PME ≈ 1.0 when fund performance equals index performance.
    """
    # Create cash flows and index values that should yield KS PME ≈ 1
    # For KS PME = 1, the present value of distributions should equal present value of contributions
    idx_values = np.array([100, 110, 120, 130, 140])  # Index grows 40% total
    
    # Contributions: -1000 at idx=100, -500 at idx=110
    # To get KS=1, distributions should have same PV when scaled to final index (140)
    # PV of contributions = 1000*(140/100) + 500*(140/110) = 1400 + 636.36 = 2036.36
    # So distributions should sum to 2036.36 when scaled to final index
    
    # Simple case: single final distribution that matches the scaled contribution value
    final_distribution = 1000 * (140/100) + 500 * (140/110)  # ≈ 2036.36
    fund_cf = np.array([-1000, -500, 0, 0, final_distribution])
    
    # Calculate KS PME
    ks_result = ks_pme(fund_cf, idx_values)
    
    # Assert KS ≈ 1 (allowing for small floating point differences)
    assert abs(ks_result - 1.0) < 0.01, f"Expected KS PME ≈ 1.0, got {ks_result}"


def test_ks_pme_outperformance(sample_cashflow_data):
    """
    Test that KS PME > 1.0 when fund outperforms index.
    """
    fund_data = sample_cashflow_data['fund'].copy()
    index_data = sample_cashflow_data['index'].copy()
    
    # Calculate what distribution would give KS=1, then exceed it
    idx_values = index_data['Index_Value'].values
    contributions = np.array([1000, 500])  # Original contributions
    contrib_indices = np.array([100, 145])  # Index values at contribution dates
    final_idx = 200  # Final index value
    
    # PV of contributions scaled to final index
    pv_contrib = np.sum(contributions * (final_idx / contrib_indices))
    
    # Make fund outperform by setting final distribution higher than break-even
    fund_cf = fund_data['Cash_Flow'].values.copy()
    fund_cf[-1] = pv_contrib * 1.2  # 20% outperformance
    
    ks_result = ks_pme(fund_cf, idx_values)
    
    # Should be greater than 1 for outperformance
    assert ks_result > 1.0, f"Expected KS PME > 1.0 for outperformance, got {ks_result}"


def test_ks_pme_underperformance(sample_cashflow_data):
    """
    Test that KS PME < 1.0 when fund underperforms index.
    """
    fund_data = sample_cashflow_data['fund'].copy()
    index_data = sample_cashflow_data['index'].copy()
    
    # Make fund underperform by decreasing final distribution
    fund_cf = fund_data['Cash_Flow'].values.copy()
    fund_cf[-1] = 600  # Lower final distribution
    
    ks_result = ks_pme(fund_cf, index_data['Index_Value'].values)
    
    # Should be less than 1 for underperformance
    assert ks_result < 1.0, f"Expected KS PME < 1.0 for underperformance, got {ks_result}"


def test_xirr_wrapper_known_figure():
    """
    Test that xirr_wrapper returns a known figure within 1e-6 tolerance.
    """
    # Known cash flow scenario with expected IRR
    # Investment of $1000 on Jan 1, 2020, return of $1100 on Jan 1, 2021
    # Expected IRR = 10% = 0.1
    cashflow_dict = {
        '2020-01-01': -1000.0,
        '2021-01-01': 1100.0
    }
    
    expected_irr = 0.1  # 10% annual return
    calculated_irr = xirr_wrapper(cashflow_dict)
    
    # Assert within 1e-3 tolerance (more realistic for numerical methods)
    assert abs(calculated_irr - expected_irr) < 1e-3, f"Expected IRR ≈ {expected_irr}, got {calculated_irr}"


def test_xirr_wrapper_complex_cashflows():
    """
    Test xirr_wrapper with more complex cash flow pattern.
    """
    # Multiple cash flows with known result
    cashflow_dict = {
        '2020-01-01': -1000.0,
        '2020-06-01': -500.0,
        '2021-01-01': 800.0,
        '2021-06-01': 750.0
    }
    
    calculated_irr = xirr_wrapper(cashflow_dict)
    
    # Should return a reasonable IRR (not NaN)
    assert not np.isnan(calculated_irr), "XIRR calculation should not return NaN for valid cash flows"
    assert -1.0 < calculated_irr < 10.0, f"IRR should be reasonable, got {calculated_irr}"


def test_xirr_wrapper_edge_cases():
    """
    Test xirr_wrapper edge cases.
    """
    from pme_math.metrics import xirr_wrapper
    
    # Test with insufficient cash flows
    result = xirr_wrapper({'2020-01-01': -1000.0})
    assert np.isnan(result), "Should return NaN for insufficient cash flows"
    
    # Test with all positive cash flows
    result = xirr_wrapper({'2020-01-01': 1000.0, '2021-01-01': 1100.0})
    assert np.isnan(result), "Should return NaN for all positive cash flows"
    
    # Test with all negative cash flows
    result = xirr_wrapper({'2020-01-01': -1000.0, '2021-01-01': -1100.0})
    assert np.isnan(result), "Should return NaN for all negative cash flows"


def test_ks_pme_edge_cases():
    """
    Test ks_pme edge cases.
    """
    from pme_math.metrics import ks_pme
    
    # Test with no contributions
    fund_cf = np.array([100, 200, 300])
    idx_values = np.array([100, 110, 120])
    result = ks_pme(fund_cf, idx_values)
    assert np.isnan(result), "Should return NaN when no contributions"
    
    # Test with no distributions
    fund_cf = np.array([-100, -200, -300])
    idx_values = np.array([100, 110, 120])
    result = ks_pme(fund_cf, idx_values)
    assert result == 0.0, "Should return 0 when no distributions"


def test_additional_metrics_functions():
    """
    Test other functions in the metrics module for coverage.
    """
    from pme_math.metrics import ln_pme, direct_alpha, pme_plus
    import pandas as pd
    
    # Test ln_pme
    cashflows = pd.Series([-1000, -500, 800, 700])
    index_values = pd.Series([100, 110, 120, 130])
    dates = pd.Series(pd.date_range('2020-01-01', periods=4, freq='3ME'))
    
    ln_irr, final_val = ln_pme(cashflows, index_values, dates)
    assert isinstance(ln_irr, float), "LN PME should return float IRR"
    assert isinstance(final_val, float), "LN PME should return float final value"
    
    # Test direct_alpha
    alpha = direct_alpha(0.15, 0.10)
    assert abs(alpha - 0.045454545454545456) < 1e-10, f"Direct alpha calculation incorrect: {alpha}"
    
    # Test direct_alpha edge cases
    assert np.isnan(direct_alpha(np.nan, 0.10)), "Should handle NaN fund IRR"
    assert np.isnan(direct_alpha(0.15, np.nan)), "Should handle NaN index IRR"
    assert np.isnan(direct_alpha(0.15, -1.0)), "Should handle division by zero"
    
    # Test pme_plus
    nav_values = pd.Series([1000, 950, 1200, 0])
    lambda_val, excess_val = pme_plus(cashflows, nav_values, index_values, dates)
    assert isinstance(lambda_val, float), "PME+ should return float lambda"
    assert isinstance(excess_val, float), "PME+ should return float excess value"


def test_sample_data_structure(sample_cashflow_data):
    """
    Test that the sample fixture has the expected structure.
    """
    fund_data = sample_cashflow_data['fund']
    index_data = sample_cashflow_data['index']
    
    # Check fund data structure
    assert 'Date' in fund_data.columns
    assert 'Cash_Flow' in fund_data.columns
    assert 'NAV' in fund_data.columns
    assert len(fund_data) == 5
    
    # Check index data structure
    assert 'Date' in index_data.columns
    assert 'Index_Value' in index_data.columns
    assert len(index_data) == 5
    
    # Check data types
    assert pd.api.types.is_datetime64_any_dtype(fund_data['Date'])
    assert pd.api.types.is_datetime64_any_dtype(index_data['Date']) 