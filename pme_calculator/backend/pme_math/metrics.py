"""
Pure mathematical functions for PME calculations.

This module contains standalone mathematical functions without any I/O or logging.
All functions are pure mathematical operations that can be tested independently.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict
import numpy_financial as npf
from scipy.optimize import brentq


def xirr_wrapper(cashflows: Dict[str, float]) -> float:
    """
    Calculate XIRR (Extended Internal Rate of Return) for irregular cash flows.

    Args:
        cashflows: Dictionary mapping dates to cash flow amounts

    Returns:
        XIRR as decimal (e.g., 0.15 for 15%)
    """
    try:
        # Convert to lists for processing
        dates = list(cashflows.keys())
        amounts = list(cashflows.values())

        # Convert dates to pandas datetime if not already
        dates = pd.to_datetime(dates)
        amounts = np.array(amounts)

        # Check for valid cash flows
        if len(amounts) < 2:
            return np.nan
        if not (np.any(amounts < 0) and np.any(amounts > 0)):
            return np.nan

        # Calculate time differences in years from first date
        dt0 = dates[0]
        times = (dates - dt0) / pd.Timedelta(days=365.25)

        def npv(rate):
            return np.sum(amounts / (1 + rate) ** times)

        # Use scipy.optimize.brentq for root finding
        return brentq(npv, -0.9999, 10)

    except (ValueError, ZeroDivisionError):
        return np.nan


def ks_pme(fund_cf: np.ndarray, idx_at_dates: np.ndarray) -> float:
    """
    Calculate Kaplan-Schoar PME ratio.

    Args:
        fund_cf: Fund cash flows array
        idx_at_dates: Index values at corresponding dates

    Returns:
        Kaplan-Schoar PME ratio
    """
    index_end = idx_at_dates[-1]
    contrib_mask = fund_cf < 0
    distrib_mask = fund_cf > 0

    contribs = -fund_cf[contrib_mask]
    distribs = fund_cf[distrib_mask]
    idx_contribs = idx_at_dates[contrib_mask]
    idx_distribs = idx_at_dates[distrib_mask]

    pv_contrib = (
        np.sum(contribs * (index_end / idx_contribs)) if len(contribs) > 0 else 0.0
    )
    pv_distrib = (
        np.sum(distribs * (index_end / idx_distribs)) if len(distribs) > 0 else 0.0
    )

    return pv_distrib / pv_contrib if pv_contrib > 0 else np.nan


def ln_pme(
    cashflows: pd.Series, index_values: pd.Series, dates: pd.Series
) -> Tuple[float, float]:
    """
    Calculate Long-Nickels PME.

    Args:
        cashflows: Fund cash flows
        index_values: Index values at corresponding dates
        dates: Dates for cash flows

    Returns:
        Tuple of (ln_irr, final_index_value)
    """
    try:
        # Replicate fund by buying/selling index units
        index_shares = 0.0
        synthetic_cashflows = []
        synthetic_dates = []

        for i, (cf, idx_val, date) in enumerate(zip(cashflows, index_values, dates)):
            if cf != 0:
                # Calculate shares bought/sold: Q_t = |CF_t| / I_t × sign(-CF_t)
                shares_transacted = abs(cf) / idx_val * np.sign(-cf)
                index_shares += shares_transacted

                # Record synthetic cash flow (opposite of fund cash flow)
                synthetic_cashflows.append(-cf)
                synthetic_dates.append(date)

        # Calculate ending index value: IndexValue_T = Σ Q_t × I_T
        final_index_value = index_shares * index_values.iloc[-1]

        # Add final index value as synthetic cash flow
        synthetic_cashflows.append(-final_index_value)
        synthetic_dates.append(dates.iloc[-1])

        # Calculate IRR of synthetic stream
        if len(synthetic_cashflows) >= 2:
            ln_irr = npf.irr(synthetic_cashflows)
            ln_irr = ln_irr if not np.isnan(ln_irr) else 0.0
        else:
            ln_irr = 0.0

        return ln_irr, final_index_value

    except Exception:
        return 0.0, 0.0


def direct_alpha(fund_irr: float, index_irr: float) -> float:
    """
    Calculate Direct Alpha.

    Args:
        fund_irr: Fund internal rate of return
        index_irr: Index/benchmark internal rate of return

    Returns:
        Direct alpha value
    """
    if (
        fund_irr is None
        or index_irr is None
        or np.isnan(fund_irr)
        or np.isnan(index_irr)
        or (1 + index_irr) == 0
    ):
        return np.nan

    return (1 + fund_irr) / (1 + index_irr) - 1


def pme_plus(
    cashflows: pd.Series,
    nav_values: pd.Series,
    index_values: pd.Series,
    dates: pd.Series,
) -> Tuple[float, float]:
    """
    Calculate PME+ metrics.

    Args:
        cashflows: Fund cash flows
        nav_values: Fund NAV values
        index_values: Index values at corresponding dates
        dates: Dates for cash flows

    Returns:
        Tuple of (lambda_value, excess_value)
    """
    try:
        final_index = index_values.iloc[-1]
        final_nav = nav_values.iloc[-1]

        # Calculate total distributions value
        distributions_value = 0.0
        contributions_value = 0.0

        for cf, idx_val in zip(cashflows, index_values):
            index_factor = final_index / idx_val

            if cf < 0:  # Contribution
                contributions_value += abs(cf) * index_factor
            elif cf > 0:  # Distribution
                distributions_value += cf * index_factor

        # Add final NAV to distributions
        distributions_value += final_nav

        # Solve for λ: λ × Σ|CF_t^-| × I_T/I_t = Σ CF_t^+ × I_T/I_t + NAV_T
        if contributions_value > 0:
            lambda_value = distributions_value / contributions_value
        else:
            lambda_value = 1.0

        # Calculate excess value: EV = 1/λ - 1
        excess_value = (1 / lambda_value - 1) if lambda_value != 0 else 0.0

        return lambda_value, excess_value

    except Exception:
        return 1.0, 0.0
