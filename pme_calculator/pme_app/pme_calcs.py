# pme_app/pme_calcs.py

import numpy as np
import pandas as pd
from pme_math.metrics import xirr_wrapper


def _calculate_annualized_return(
    returns: pd.Series, periods_per_year: int = 252
) -> float:
    """Safely calculates the annualized geometric mean return."""
    if returns.empty:
        return np.nan

    # Ensure returns are 1-based for product calculation
    returns_1based = 1 + returns.dropna()

    # NaNs can be produced if returns are all -1
    if (returns_1based < 0).any():
        # Negative returns greater than 100% are problematic
        return np.nan

    # Calculate geometric mean
    # Adding small epsilon to prevent log(0)
    log_returns = np.log(returns_1based + 1e-12)
    mean_log_return = log_returns.mean()

    # Annualize the result
    annualized_return = np.exp(mean_log_return * periods_per_year) - 1

    return annualized_return


def safe_div(num, denom):
    return num / denom if denom != 0 else np.nan


def ks_pme(fund_cf: np.ndarray, idx_at_dates: np.ndarray) -> float:
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


def direct_alpha(fund_irr: float, index_irr: float) -> float:
    if (
        fund_irr is None
        or index_irr is None
        or np.isnan(fund_irr)
        or np.isnan(index_irr)
        or (1 + index_irr) == 0
    ):
        return np.nan
    return (1 + fund_irr) / (1 + index_irr) - 1


def align_series_to_dates(
    series: pd.Series, target_dates: pd.DatetimeIndex, freq: str = "auto"
) -> pd.Series:
    series = series.copy()
    if not isinstance(series.index, pd.DatetimeIndex):
        series.index = pd.to_datetime(series.index)
    series = series.sort_index()
    all_dates = series.index.union(target_dates)
    aligned = series.reindex(all_dates).interpolate().ffill().bfill()
    result = aligned.reindex(target_dates)
    percent_filled = result.isnull().mean() * 100
    if percent_filled > 5:
        print(
            f"Warning: {percent_filled:.1f}% of values were filled by interpolation/ffill."
        )
    return result


def compute_volatility(return_series, freq="monthly"):
    return_series = pd.Series(return_series).dropna()
    if freq == "monthly":
        scale = np.sqrt(12)
    elif freq == "quarterly":
        scale = np.sqrt(4)
    elif freq == "daily":
        scale = np.sqrt(252)
    else:
        scale = 1
    return np.nanstd(return_series) * scale if len(return_series) > 1 else np.nan


def compute_drawdown(series):
    s = pd.Series(series).dropna()
    cumulative = np.maximum.accumulate(s)
    dd = (s - cumulative) / cumulative
    return dd.min() if len(dd) > 1 else np.nan


def compute_rolling_returns(series, window=12):
    s = pd.Series(series).dropna()
    if len(s) <= window:
        return pd.Series(dtype=float)

    # Calculate rolling percentage change safely
    rolling_pct_change = (s / s.shift(window)) - 1

    # Replace inf/-inf with NaN
    rolling_pct_change.replace([np.inf, -np.inf], np.nan, inplace=True)

    return rolling_pct_change.dropna()


def compute_alpha_beta(fund_returns, index_returns):
    fund_returns = pd.Series(fund_returns).dropna()
    index_returns = pd.Series(index_returns).dropna()

    # Align series and handle unequal lengths
    if len(fund_returns) != len(index_returns):
        common_index = fund_returns.index.intersection(index_returns.index)
        if len(common_index) < 3:
            return np.nan, np.nan
        fund_returns = fund_returns.loc[common_index]
        index_returns = index_returns.loc[common_index]

    idx = pd.notnull(fund_returns) & pd.notnull(index_returns)
    if np.sum(idx) < 3:
        return np.nan, np.nan

    # Use aligned data for calculations
    fund_returns_aligned = fund_returns[idx]
    index_returns_aligned = index_returns[idx]

    # Add a constant for linear regression
    X = pd.DataFrame({"alpha": 1, "beta": index_returns_aligned})

    try:
        # OLS regression to find alpha and beta
        params = np.linalg.lstsq(X, fund_returns_aligned, rcond=None)[0]
        alpha, beta = params[0], params[1]
    except (np.linalg.LinAlgError, ValueError):
        alpha, beta = np.nan, np.nan

    return alpha, beta


def _smooth_returns(returns, window=5):
    """Apply smoothing to index returns."""
    return returns.rolling(window=window, center=True).mean().fillna(returns)


def _apply_lag_adjustment(returns, lag_quarters=1):
    """Apply lag adjustment to account for private equity reporting lag."""
    lag_periods = lag_quarters * 3  # Assuming monthly data
    return returns.shift(lag_periods).fillna(returns)


def calculate_direct_alpha_pme(fund_df, index_returns, risk_free_rate):
    """Calculate PME using Direct Alpha methodology."""
    # Direct Alpha PME focuses on pure excess return
    fund_returns = fund_df["nav"].pct_change().fillna(0)
    fund_irr = xirr_wrapper(dict(zip(fund_df.index, fund_df["cash_flow_amount"])))
    index_irr = _calculate_annualized_return(index_returns)

    # Calculate PME as excess return over index
    excess_return = (
        fund_irr - index_irr
        if not np.isnan(fund_irr) and not np.isnan(index_irr)
        else np.nan
    )
    pme_value = 1 + excess_return if not np.isnan(excess_return) else np.nan
    pme_irr = fund_irr

    return pme_value, pme_irr


def calculate_modified_pme(fund_df, index_returns, risk_free_rate):
    """Calculate Enhanced PME+ methodology."""
    # Modified PME incorporates risk adjustments
    fund_returns = fund_df["nav"].pct_change().fillna(0)
    fund_irr = xirr_wrapper(dict(zip(fund_df.index, fund_df["cash_flow_amount"])))

    # Risk-adjusted benchmark return
    index_irr = _calculate_annualized_return(index_returns)
    risk_adjusted_benchmark = (
        index_irr + risk_free_rate if not np.isnan(index_irr) else np.nan
    )

    # Calculate modified PME with risk adjustment
    alpha, beta = compute_alpha_beta(fund_returns, index_returns)
    if (
        not np.isnan(beta)
        and beta != 0
        and not np.isnan(fund_irr)
        and not np.isnan(index_irr)
    ):
        risk_adjusted_return = fund_irr - beta * (index_irr - risk_free_rate)
        pme_value = safe_div(1 + risk_adjusted_return, 1 + risk_adjusted_benchmark)
    else:
        pme_value = safe_div(1 + fund_irr, 1 + risk_adjusted_benchmark)

    pme_irr = fund_irr
    return pme_value, pme_irr


def calculate_long_nickels_pme(fund_df, index_returns):
    """Calculate Long & Nickels PME methodology."""
    # Long-Nickels methodology uses alternative scaling
    fund_cash_flows = fund_df["cash_flow_amount"].fillna(0)
    index_levels = (1 + index_returns).cumprod()

    # Alternative scaling approach
    scaled_cfs = []
    for i, cf in enumerate(fund_cash_flows):
        if cf != 0:
            if cf < 0:  # Contribution
                # Scale by forward-looking index performance
                future_performance = (
                    index_levels.iloc[-1] / index_levels.iloc[i]
                    if i < len(index_levels)
                    else 1
                )
                scaled_cf = cf * future_performance
            else:  # Distribution
                # Scale by current index level
                scaled_cf = cf
            scaled_cfs.append(scaled_cf)
        else:
            scaled_cfs.append(0)

    # Calculate PME as ratio of scaled values
    total_contribs = -sum(cf for cf in scaled_cfs if cf < 0)
    total_distribs = sum(cf for cf in scaled_cfs if cf > 0)

    pme_value = safe_div(total_distribs, total_contribs)
    pme_irr = xirr_wrapper(dict(zip(fund_df.index, scaled_cfs)))

    return pme_value, pme_irr


def compute_pme_metrics(
    fund_df,
    index_df,
    method="kaplan_schoar",
    risk_free_rate=0.025,
    smooth_index=False,
    lag_adjustment=False,
    confidence_level=0.95,
):
    """
    Compute PME metrics for a fund against an index.

    Args:
        fund_df: DataFrame with index=date, columns=['cash_flow_amount', 'cash_flow_type', 'nav']
        index_df: DataFrame with index=date, columns=['price', 'return']

    Returns:
        dict: PME metrics including IRR, TVPI, DPI, RVPI, and PME metrics
    """
    # Validate inputs
    if not isinstance(fund_df, pd.DataFrame) or not isinstance(index_df, pd.DataFrame):
        raise ValueError("Both fund_df and index_df must be pandas DataFrames")

    if fund_df.empty or index_df.empty:
        raise ValueError("Both fund_df and index_df must not be empty")

    # Ensure proper data types
    fund_df = fund_df.copy()
    index_df = index_df.copy()

    # Align dates
    all_dates = fund_df.index.union(index_df.index)
    fund_df = fund_df.reindex(all_dates)
    index_df = index_df.reindex(all_dates)

    # Forward fill NAV and index values
    fund_df["nav"] = fund_df["nav"].ffill().fillna(0)
    index_df["price"] = index_df["price"].ffill().bfill()

    # Calculate returns from prices if return column doesn't exist
    if "return" not in index_df.columns:
        index_df["return"] = index_df["price"].pct_change().fillna(0)
    else:
        index_df["return"] = index_df["return"].fillna(0)

    # Calculate fund metrics
    # Handle different column names for cashflow data
    if "cash_flow_amount" in fund_df.columns:
        fund_cash_flows = fund_df["cash_flow_amount"].fillna(0)
    elif "cashflow" in fund_df.columns:
        fund_cash_flows = fund_df["cashflow"].fillna(0)
    else:
        raise ValueError(
            "Fund DataFrame must contain either 'cash_flow_amount' or 'cashflow' column"
        )

    fund_nav = fund_df["nav"].fillna(0)

    # Calculate index metrics
    index_price = index_df["price"]
    index_return = index_df["return"]

    # Calculate fund IRR
    fund_irr = xirr_wrapper(dict(zip(fund_df.index, fund_cash_flows)))

    # Calculate fund multiples
    total_contributions = -fund_cash_flows[fund_cash_flows < 0].sum()
    total_distributions = fund_cash_flows[fund_cash_flows > 0].sum()
    final_nav = fund_nav.iloc[-1] if not fund_nav.empty else 0

    fund_tvpi = safe_div(total_distributions + final_nav, total_contributions)
    fund_dpi = safe_div(total_distributions, total_contributions)
    fund_rvpi = safe_div(final_nav, total_contributions)

    # Process index returns based on options
    if index_price.isnull().all():
        # Calculate cumulative index from returns if price is missing
        index_levels = (1 + index_return).cumprod()
        index_levels = index_levels / index_levels.iloc[0]  # Normalize to start at 1
        working_returns = index_return
    else:
        # Use price data and normalize to start at 1
        index_price_first_valid = index_price.first_valid_index()
        if index_price_first_valid is not None:
            index_levels = index_price / index_price[index_price_first_valid]
        else:
            index_levels = pd.Series(1.0, index=index_price.index)  # fallback
        working_returns = index_levels.pct_change().fillna(0)

    # Apply processing options
    if smooth_index:
        working_returns = _smooth_returns(working_returns)
        index_levels = (1 + working_returns).cumprod()

    if lag_adjustment:
        working_returns = _apply_lag_adjustment(working_returns)
        index_levels = (1 + working_returns).cumprod()

    # Calculate PME using selected methodology
    if method == "kaplan_schoar":
        fund_cf_values = fund_cash_flows.values
        index_levels_values = index_levels.values
        ks_pme_value = ks_pme(fund_cf_values, index_levels_values)

        # Calculate standard PME IRR
        pme_cash_flows = pd.Series(0.0, index=all_dates)
        for i, date in enumerate(all_dates):
            if date in fund_cash_flows.index and fund_cash_flows[date] != 0:
                cf = fund_cash_flows[date]
                if cf < 0:  # Contribution
                    pme_cash_flows[date] = cf * (
                        index_levels.iloc[-1] / index_levels.iloc[i]
                    )
                else:  # Distribution
                    pme_cash_flows[date] = cf
        pme_irr = xirr_wrapper(dict(zip(all_dates, pme_cash_flows)))

    elif method == "direct_alpha":
        ks_pme_value, pme_irr = calculate_direct_alpha_pme(
            fund_df, working_returns, risk_free_rate
        )

    elif method == "modified_pme":
        ks_pme_value, pme_irr = calculate_modified_pme(
            fund_df, working_returns, risk_free_rate
        )

    elif method == "long_nickels":
        ks_pme_value, pme_irr = calculate_long_nickels_pme(fund_df, working_returns)

    else:
        # Default to Kaplan-Schoar
        fund_cf_values = fund_cash_flows.values
        index_levels_values = index_levels.values
        ks_pme_value = ks_pme(fund_cf_values, index_levels_values)

        pme_cash_flows = pd.Series(0.0, index=all_dates)
        for i, date in enumerate(all_dates):
            if date in fund_cash_flows.index and fund_cash_flows[date] != 0:
                cf = fund_cash_flows[date]
                if cf < 0:  # Contribution
                    pme_cash_flows[date] = cf * (
                        index_levels.iloc[-1] / index_levels.iloc[i]
                    )
                else:  # Distribution
                    pme_cash_flows[date] = cf
        pme_irr = xirr_wrapper(dict(zip(all_dates, pme_cash_flows)))

    # Calculate PME TVPI
    total_pme_contributions = (
        abs(fund_cash_flows[fund_cash_flows < 0].sum()) * ks_pme_value
        if not np.isnan(ks_pme_value)
        else 0
    )
    total_pme_distributions = fund_cash_flows[fund_cash_flows > 0].sum()
    pme_nav = final_nav * ks_pme_value if not np.isnan(ks_pme_value) else 0
    pme_tvpi = safe_div(total_pme_distributions + pme_nav, total_pme_contributions)

    # Calculate Direct Alpha
    index_irr = _calculate_annualized_return(working_returns)

    # Ensure index_irr is finite
    if not np.isfinite(index_irr):
        index_irr = np.nan

    # Calculate alpha and beta
    fund_returns = fund_nav.pct_change().fillna(0)
    alpha, beta = compute_alpha_beta(fund_returns, working_returns)

    # Calculate additional risk metrics
    fund_volatility = compute_volatility(fund_returns, freq="monthly")
    index_volatility = compute_volatility(working_returns, freq="monthly")
    fund_drawdown = compute_drawdown(fund_nav)
    index_drawdown = compute_drawdown(index_levels)

    # Calculate rolling returns for best/worst analysis
    fund_rolling_1y = compute_rolling_returns(fund_returns, window=12)
    index_rolling_1y = compute_rolling_returns(working_returns, window=12)

    direct_alpha_value = (
        fund_irr - index_irr
        if not np.isnan(fund_irr) and not np.isnan(index_irr)
        else np.nan
    )

    # Return comprehensive metrics with standardized names expected by GUI
    return {
        "Fund IRR": fund_irr,
        "TVPI": fund_tvpi,
        "DPI": fund_dpi,
        "RVPI": fund_rvpi,
        "KS PME": ks_pme_value,
        "PME IRR": pme_irr,
        "Index IRR": index_irr,
        "Index TVPI": pme_tvpi,
        "Direct Alpha": direct_alpha_value,
        "Alpha": alpha,
        "Beta": beta,
        "Fund Volatility": fund_volatility,
        "Index Volatility": index_volatility,
        "Fund Drawdown": fund_drawdown,
        "Index Drawdown": index_drawdown,
        "Fund Best 1Y Return": (
            fund_rolling_1y.max() if not fund_rolling_1y.empty else np.nan
        ),
        "Fund Worst 1Y Return": (
            fund_rolling_1y.min() if not fund_rolling_1y.empty else np.nan
        ),
        "Index Best 1Y Return": (
            index_rolling_1y.max() if not index_rolling_1y.empty else np.nan
        ),
        "Index Worst 1Y Return": (
            index_rolling_1y.min() if not index_rolling_1y.empty else np.nan
        ),
        "Total Contributions": total_contributions,
        "Total Distributions": total_distributions,
        "Final NAV": final_nav,
        "Method Used": method.replace("_", " ").title(),
        "Risk Free Rate": risk_free_rate,
        "Confidence Level": confidence_level,
    }
