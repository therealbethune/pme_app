"""Analysis service for PME calculations - pure business logic without dependencies."""

from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from pme_app.logger import logger


def safe_div(num: float, denom: float) -> float:
    """Safely divide two numbers, returning NaN if denominator is zero."""
    return num / denom if denom != 0 else np.nan


def ks_pme(
    fund_cf: NDArray[np.floating[Any]], idx_at_dates: NDArray[np.floating[Any]]
) -> float:
    """Calculate Kaplan-Schoar PME from fund cashflows and index values."""
    if len(fund_cf) == 0 or len(idx_at_dates) == 0:
        logger.warning(
            "ks_pme_empty_input", fund_cf_len=len(fund_cf), idx_len=len(idx_at_dates)
        )
        return np.nan

    index_end: np.floating[Any] | float = idx_at_dates[-1]
    contrib_mask: NDArray[np.bool_] = fund_cf < 0
    distrib_mask: NDArray[np.bool_] = fund_cf > 0

    contribs: NDArray[np.floating[Any]] = -fund_cf[contrib_mask]
    distribs: NDArray[np.floating[Any]] = fund_cf[distrib_mask]
    idx_contribs: NDArray[np.floating[Any]] = idx_at_dates[contrib_mask]
    idx_distribs: NDArray[np.floating[Any]] = idx_at_dates[distrib_mask]

    pv_contrib: np.floating[Any] | float = (
        np.sum(contribs * (index_end / idx_contribs)) if len(contribs) > 0 else 0.0
    )
    pv_distrib: np.floating[Any] | float = (
        np.sum(distribs * (index_end / idx_distribs)) if len(distribs) > 0 else 0.0
    )

    result: float = safe_div(float(pv_distrib), float(pv_contrib))
    logger.info(
        "ks_pme_calculated",
        pme_value=result,
        contributions=len(contribs),
        distributions=len(distribs),
    )
    return result


def direct_alpha(fund_irr: float | None, index_irr: float | None) -> float:
    """Calculate Direct Alpha from fund and index IRRs."""
    if (
        fund_irr is None
        or index_irr is None
        or np.isnan(fund_irr)
        or np.isnan(index_irr)
        or (1 + index_irr) == 0
    ):
        return np.nan
    result: float = (1 + fund_irr) / (1 + index_irr) - 1
    logger.info(
        "direct_alpha_calculated", alpha=result, fund_irr=fund_irr, index_irr=index_irr
    )
    return result


def compute_volatility(return_series: pd.Series, freq: str = "monthly") -> float:
    """Compute annualized volatility from return series."""
    return_series = pd.Series(return_series).dropna()

    if len(return_series) <= 1:
        return np.nan

    scale: float
    if freq == "monthly":
        scale = np.sqrt(12)
    elif freq == "quarterly":
        scale = np.sqrt(4)
    elif freq == "daily":
        scale = np.sqrt(252)
    else:
        scale = 1

    # TODO: np.nanstd returns Any, should be float
    volatility_result: float | Any = np.nanstd(return_series) * scale
    return float(volatility_result)


def compute_drawdown(series: pd.Series) -> float:
    """Compute maximum drawdown from a price/value series."""
    s = pd.Series(series).dropna()

    if len(s) <= 1:
        return np.nan

    cumulative: pd.Series = np.maximum.accumulate(s)
    dd: pd.Series = (s - cumulative) / cumulative
    min_dd: float | Any = dd.min()  # TODO: pd.Series.min() returns Any
    return float(min_dd)


def compute_alpha_beta(
    fund_returns: pd.Series, index_returns: pd.Series
) -> tuple[float, float]:
    """Compute alpha and beta using linear regression."""
    fund_returns = pd.Series(fund_returns).dropna()
    index_returns = pd.Series(index_returns).dropna()

    # Align series and handle unequal lengths
    if len(fund_returns) != len(index_returns):
        common_index = fund_returns.index.intersection(index_returns.index)
        if len(common_index) < 3:
            return np.nan, np.nan
        fund_returns = fund_returns.loc[common_index]
        index_returns = index_returns.loc[common_index]

    idx: pd.Series = pd.notnull(fund_returns) & pd.notnull(index_returns)
    if np.sum(idx) < 3:
        return np.nan, np.nan

    # Use aligned data for calculations
    fund_returns_aligned = fund_returns[idx]
    index_returns_aligned = index_returns[idx]

    # Add a constant for linear regression
    x_matrix = pd.DataFrame({"alpha": 1, "beta": index_returns_aligned})

    try:
        # OLS regression to find alpha and beta
        # TODO: np.linalg.lstsq returns tuple with Any elements
        params: NDArray[Any] | Any = np.linalg.lstsq(
            x_matrix, fund_returns_aligned, rcond=None
        )[0]
        alpha, beta = float(params[0]), float(params[1])
    except (np.linalg.LinAlgError, ValueError):
        alpha, beta = np.nan, np.nan

    return alpha, beta


def calculate_annualized_return(
    returns: pd.Series, periods_per_year: int = 252
) -> float:
    """Calculate annualized geometric mean return."""
    if returns.empty:
        return np.nan

    # Ensure returns are 1-based for product calculation
    returns_1based: pd.Series = 1 + returns.dropna()

    # NaNs can be produced if returns are all -1
    if (returns_1based <= 0).any():
        # Negative returns greater than 100% are problematic
        return np.nan

    # Calculate geometric mean
    # Adding small epsilon to prevent log(0)
    log_returns = np.log(returns_1based + 1e-12)
    mean_log_return: float | Any = (
        log_returns.mean()
    )  # TODO: pd.Series.mean() returns Any

    # Annualize the result
    annualized_return: float | Any = np.exp(mean_log_return * periods_per_year) - 1

    return float(annualized_return)
