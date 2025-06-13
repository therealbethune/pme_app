# pme_app/nav_waterfall.py
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd


def build_nav_change_df(fund_df: pd.DataFrame) -> pd.DataFrame:
    if fund_df is None or fund_df.empty:
        return pd.DataFrame()

    df = fund_df.copy()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").set_index("date")

    for col in ["cash_flow_amount", "nav"]:
        if col not in df.columns:
            df[col] = 0.0
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    if df[["cash_flow_amount", "nav"]].abs().sum().sum() == 0:
        # Not aborting; just returning empty for safety
        return pd.DataFrame()

    # Find initial NAV
    first_nav = df["nav"].iloc[0] if len(df) > 0 else 0
    if first_nav == 0:
        non_zero_navs = df["nav"][df["nav"] > 0]
        first_nav = (
            non_zero_navs.iloc[0]
            if not non_zero_navs.empty and len(non_zero_navs) > 0
            else 0
        )
    current_nav = first_nav

    rows = []
    for dt, row in df.iterrows():
        contrib = max(-row["cash_flow_amount"], 0.0)
        dist = max(row["cash_flow_amount"], 0.0)
        start_nav = current_nav
        nav_after_cf = start_nav + contrib - dist
        gain_loss = 0.0
        end_nav = nav_after_cf
        if not pd.isna(row["nav"]):
            gain_loss = row["nav"] - nav_after_cf
            end_nav = row["nav"]
        rows.append(
            {
                "date": dt,
                "start_nav": start_nav,
                "contribution": contrib,
                "distribution": dist,
                "gain_loss": gain_loss,
                "end_nav": end_nav,
            }
        )
        current_nav = end_nav

    result_df = pd.DataFrame(rows).set_index("date")
    result_df["cash_flow_amount"] = df["cash_flow_amount"]
    result_df["nav"] = df["nav"]
    return result_df


def compute_annual_nav_components(df: pd.DataFrame) -> pd.DataFrame:
    """
    Groups by year and ensures no missing years between first and last.
    For years with no activity, sets flows to 0 and carries forward NAV.
    """
    df = df.copy()
    df["year"] = pd.to_datetime(df.index).year
    df = df.sort_index()
    df["contribution"] = df["cash_flow_amount"].apply(lambda x: -x if x < 0 else 0)
    df["distribution"] = df["cash_flow_amount"].apply(lambda x: x if x > 0 else 0)

    # Group as before
    grouped = df.groupby("year").agg(
        {"contribution": "sum", "distribution": "sum", "nav": ["first", "last"]}
    )
    grouped.columns = ["contribution", "distribution", "start_nav", "end_nav"]
    grouped = grouped.reset_index()

    # Fill missing years and carry NAV forward
    all_years = np.arange(df["year"].min(), df["year"].max() + 1)
    grouped = grouped.set_index("year").reindex(all_years).reset_index()
    grouped["contribution"] = grouped["contribution"].fillna(0)
    grouped["distribution"] = grouped["distribution"].fillna(0)

    # Carry start_nav and end_nav forward
    last_nav = None
    for i, row in grouped.iterrows():
        if pd.isnull(row["start_nav"]):
            grouped.at[i, "start_nav"] = last_nav if last_nav is not None else 0
        if pd.isnull(row["end_nav"]):
            grouped.at[i, "end_nav"] = grouped.at[i, "start_nav"]
        last_nav = grouped.at[i, "end_nav"]

    grouped["net_value_change"] = (
        grouped["end_nav"]
        - grouped["start_nav"]
        - grouped["contribution"]
        + grouped["distribution"]
    )
    # Contributions are already positive numbers (absolute value of cash-outflows),
    # so they must be subtracted. Distributions are inflows (positive values)
    # and must be added, to isolate true investment performance.

    return grouped


def add_bar_labels(ax, bars, currency_symbol="USD"):
    for bar in bars:
        height = bar.get_height()
        if abs(height) < 1e-8:
            continue
        va = "bottom" if height > 0 else "top"
        offset = abs(height) * 0.01 + 1e6 if height > 0 else -abs(height) * 0.01 - 1e6
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + offset,
            f"{currency_symbol} {height:,.0f}",
            ha="center",
            va=va,
            fontsize=8,
        )


def plot_nav_waterfall(
    fund_df: pd.DataFrame,
    currency_symbol: str = "USD",
    title: str = "Annual NAV Waterfall",
) -> plt.Figure:

    df = build_nav_change_df(fund_df)
    if df.empty:
        # Return a minimal placeholder Figure with a user-friendly message
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(
            0.5,
            0.5,
            "No data available",
            ha="center",
            va="center",
            fontsize=16,
            color="gray",
            fontweight="bold",
            alpha=0.7,
        )
        ax.set_axis_off()
        fig.tight_layout()
        return fig

    annual = compute_annual_nav_components(df)
    years = annual["year"].astype(str)
    x = np.arange(len(years))
    bar_width = 0.22

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        x,
        annual["end_nav"],
        color="dimgray",
        label="Net Asset Value",
        marker="o",
        linewidth=2,
    )

    bars_contrib = ax.bar(
        x - bar_width,
        -annual["contribution"].astype(float).values,
        width=bar_width,
        color="crimson",
        label="Paid In",
    )
    for spine in ("left", "right"):
        ax.spines[spine].set_visible(False)
    ax.yaxis.set_label_position("right")
    bars_dist = ax.bar(
        x,
        annual["distribution"].astype(float).values,
        width=bar_width,
        color="deepskyblue",
        label="Distributed",
    )
    bars_change = ax.bar(
        x + bar_width,
        annual["net_value_change"].astype(float).values,
        width=bar_width,
        color="darkgray",
        label="Net Value Change",
    )

    ax.set_xticks(x)
    ax.set_xticklabels(years, rotation=45, ha="right")
    ax.set_title(title)
    ax.set_ylabel(f"Value ({currency_symbol})")

    def currency_fmt(x, _):
        # Always prepend '–' for negative values for clarity
        sign = "-" if x < 0 else ""
        return f"{sign}{currency_symbol}{abs(x)/1e6:,.0f}M"

    ax.yaxis.set_major_formatter(mtick.FuncFormatter(currency_fmt))
    ax.axhline(0, color="black", linewidth=1)
    ax.grid(True, axis="y", linestyle="--", alpha=0.3)
    add_bar_labels(ax, bars_contrib, currency_symbol)
    add_bar_labels(ax, bars_dist, currency_symbol)
    add_bar_labels(ax, bars_change, currency_symbol)
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.tight_layout()
    return fig
