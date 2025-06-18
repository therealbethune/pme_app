import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import pandas as pd


def plot_cashflow_overview(
    fund_df: pd.DataFrame,
    currency_symbol: str = "USD",
    title: str = "Cashflow Overview",
) -> plt.Figure:
    """
    Professional PME cash flow overview: NAV, Total Value, Paid In, Distributions, Cash Flows (as step line).
    No DataFrame printouts, just the chart.
    """
    if not isinstance(currency_symbol, str):
        raise TypeError(
            "currency_symbol must be a string, not a DataFrame or other type."
        )

    # PREP DATA
    df = fund_df.copy().sort_index()
    df["contrib"] = df["cash_flow_amount"].where(df["cash_flow_amount"] < 0, 0.0)
    df["distr"] = df["cash_flow_amount"].where(df["cash_flow_amount"] > 0, 0.0)
    df["cum_paid_in"] = df["contrib"].cumsum()
    df["cum_distribs"] = df["distr"].cumsum()
    df["nav"] = df["nav"].astype(float)
    df["total_value"] = df["nav"] + df["cum_distribs"]
    df["cashflows"] = df["contrib"] + df["distr"]

    # CREATE PLOT
    fig, ax = plt.subplots(figsize=(14, 6))

    # Main lines
    (nav_line,) = ax.step(
        df.index, df["nav"], label="NAV", color="#B0B0B0", linewidth=2.5, where="post"
    )
    (tv_line,) = ax.step(
        df.index,
        df["total_value"],
        label="Total Value",
        color="#232323",
        linewidth=2.8,
        where="post",
    )
    (paidin_line,) = ax.step(
        df.index,
        df["cum_paid_in"],
        label="Total Paid In",
        color="#e43b67",
        linewidth=2.2,
        where="post",
    )
    (distr_line,) = ax.step(
        df.index,
        df["cum_distribs"],
        label="Total Distributions",
        color="#39cfff",
        linewidth=2.2,
        where="post",
    )
    (cf_line,) = ax.step(
        df.index,
        df["cashflows"],
        label="Cash Flows",
        color="#A0A0A0",
        linewidth=1.1,
        where="post",
        alpha=0.8,
    )

    # AXIS FORMATTING
    def compact_fmt(x, pos):
        abs_x = abs(x)
        if abs_x >= 1_000_000_000:
            return f"{currency_symbol} {x/1_000_000_000:.2f} B"
        elif abs_x >= 1_000_000:
            return f"{currency_symbol} {x/1_000_000:.2f} M"
        elif abs_x >= 1_000:
            return f"{currency_symbol} {x/1_000:.2f} K"
        return f"{currency_symbol} {x:,.0f}"

    ax.yaxis.set_major_formatter(plt.FuncFormatter(compact_fmt))
    ymin = min(df["cum_paid_in"].min(), df["cashflows"].min(), df["nav"].min(), 0)
    ymax = max(df["total_value"].max(), df["cum_distribs"].max(), df["nav"].max())
    ax.set_ylim(ymin * 1.10, ymax * 1.08)

    # X-axis: Jan 'YY style
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))

    # GRID, TITLE, LEGEND
    ax.grid(axis="y", linestyle="--", linewidth=0.7, alpha=0.20)
    ax.set_title(title, fontsize=17, pad=20)
    handles = [nav_line, tv_line, paidin_line, distr_line, cf_line]
    ax.legend(
        handles,
        [h.get_label() for h in handles],
        loc="lower center",
        bbox_to_anchor=(0.5, -0.23),
        ncol=5,
        frameon=False,
        fontsize=12,
    )
    fig.subplots_adjust(left=0.06, right=0.98, top=0.88, bottom=0.23)

    # INTERACTIVITY: mplcursors on all lines
    crs = mplcursors.cursor(handles, hover=True)

    @crs.connect("add")
    def on_add(sel):
        line = sel.artist
        label = line.get_label()
        xdata = line.get_xdata()
        ydata = line.get_ydata()
        idx = np.argmin(np.abs(mdates.date2num(xdata) - sel.target[0]))
        date = pd.to_datetime(xdata[idx])
        value = ydata[idx]
        sel.annotation.set_text(
            f"{label}\n{date:%b %Y}\n{currency_symbol} {value:,.0f}"
        )
        sel.annotation.get_bbox_patch().set(
            fc="white", alpha=0.97, boxstyle="round,pad=0.5", lw=1.3, ec="#393939"
        )

    return fig
