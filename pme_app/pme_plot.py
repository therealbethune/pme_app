# pme_app/pme_plot.py
"""
pme_plot.py – Visualizes Net Cash Flows vs Market Index
"""

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from .utils import ensure_datetime_index


def plot_cash_flows_vs_market(
    fund_df: pd.DataFrame,
    index_price_df: pd.DataFrame,
    title: str = "Net Cash Flows vs. Index",
    index_label: str = "Index Level",
    show: bool = False,
) -> plt.Figure:
    """
    Plot net fund cash flows (contributions, distributions) against market index price/level.
    Bar widths adapt to the minimum date gap.
    """
    if fund_df is None or index_price_df is None:
        raise ValueError("Both fund_df and index_price_df are required.")

    # Ensure DatetimeIndex
    fund_df = ensure_datetime_index(fund_df.copy(), date_col="date")
    index_price_df = ensure_datetime_index(index_price_df.copy(), date_col="date")

    # Prepare contributions and distributions
    df = fund_df[["cash_flow_amount"]].copy()
    df["contributions"] = df["cash_flow_amount"].where(df["cash_flow_amount"] < 0, 0)
    df["distributions"] = df["cash_flow_amount"].where(df["cash_flow_amount"] > 0, 0)

    # Merge with index; interpolate missing index data
    merged = df.join(index_price_df[["index_level"]], how="left")
    if merged["index_level"].isna().any():
        merged["index_level"] = merged["index_level"].ffill().bfill()
        if merged["index_level"].isna().any():
            missing_indices = merged[merged["index_level"].isna()].index
            if len(missing_indices) > 0:
                first_missing = missing_indices[0]
                raise ValueError(
                    f"Index does not cover all fund dates (even after interpolation); first missing: {first_missing}"
                )

    dates = merged.index
    # --- Dynamic bar width ---
    if len(dates) > 1:
        deltas = pd.Series(dates).diff().dropna()
        min_gap = deltas.min().days if hasattr(deltas.min(), "days") else deltas.min()
        bar_width = max(
            5, min(int(min_gap * 0.7), 30)
        )  # Clamp to [5, 30] for sensible bar size
    else:
        bar_width = 10

    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax1.plot(
        merged.index, merged["index_level"], color="black", label=index_label, zorder=1
    )
    ax1.set_ylabel(index_label, color="black")
    ax1.tick_params(axis="y", labelcolor="black")
    ax1.set_title(title)

    # Format x-axis as yearly ticks
    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=45)

    # Second axis for cash flows
    ax2 = ax1.twinx()
    ax2.bar(
        merged.index,
        merged["distributions"],
        width=bar_width,
        color="deepskyblue",
        label="Distributions",
        zorder=2,
    )
    ax2.bar(
        merged.index,
        merged["contributions"],
        width=bar_width,
        color="deeppink",
        label="Contributions",
        zorder=2,
    )
    ax2.set_ylabel("Net Cash Flows", color="gray")
    ax2.tick_params(axis="y", labelcolor="gray")

    lines, labels = ax1.get_legend_handles_labels()
    bars, bar_labels = ax2.get_legend_handles_labels()
    ax2.legend(lines + bars, labels + bar_labels, loc="upper left")

    plt.tight_layout()

    if show:
        plt.show()

    return fig
