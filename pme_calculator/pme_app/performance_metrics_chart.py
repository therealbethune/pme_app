import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

try:
    import numpy_financial as npf
except ImportError:
    npf = None


def running_xirr(cash_flows, navs, dates):
    xirrs = []
    for i in range(2, len(dates) + 1):
        cfs = cash_flows[:i]
        nav = navs[:i]
        dts = dates[:i]
        all_cf = np.append(cfs, nav.iloc[-1])
        all_dates = np.append(dts, dts[-1])

        # --- Sign Correction Block ---
        # IRR expects negative contributions, positive distributions
        n_neg = np.sum(all_cf < 0)
        n_pos = np.sum(all_cf > 0)
        if n_neg == 0 and n_pos > 0:
            # All positive: flip sign
            all_cf = -all_cf
        elif n_pos == 0 and n_neg > 0:
            # All negative: do nothing, already correct
            pass
        # Now, IRR is only defined if both negative and positive flows exist
        n_neg = np.sum(all_cf < 0)
        n_pos = np.sum(all_cf > 0)
        if n_neg == 0 or n_pos == 0:
            xirrs.append(np.nan)
            continue
        # --------------------------------

        try:
            # Try numpy_financial xirr first
            if npf is not None:
                rate = npf.xirr(list(zip(pd.to_datetime(all_dates), all_cf)))
                if not np.isnan(rate):
                    xirrs.append(rate)
                    continue
        except (ValueError, AttributeError):
            pass

        # Fallback to scipy.optimize.brentq
        try:
            from scipy.optimize import brentq

            def npv_fn(r):
                return np.sum(
                    [
                        cf
                        / (1 + r)
                        ** ((pd.Timestamp(dt) - pd.Timestamp(dts[0])).days / 365.25)
                        for cf, dt in zip(all_cf, all_dates)
                    ]
                )

            rate = brentq(npv_fn, -0.9999, 10)
            xirrs.append(rate)
        except ValueError:
            xirrs.append(np.nan)
    # Pad initial with nan so array length matches other series
    return [np.nan] + xirrs


def running_multiples(cash_flows, navs):
    tvpis, dpis, rvpies = [], [], []
    for i in range(1, len(cash_flows) + 1):
        partial_cf = cash_flows[:i]
        partial_nav = navs[:i]
        contrib = -partial_cf[partial_cf < 0].sum()
        distrib = partial_cf[partial_cf > 0].sum()
        nav_last = partial_nav.iloc[-1] if len(partial_nav) > 0 else 0
        tvpi = (distrib + nav_last) / contrib if contrib != 0 else np.nan
        dpi = distrib / contrib if contrib != 0 else np.nan
        rvpi = nav_last / contrib if contrib != 0 else np.nan
        tvpis.append(tvpi)
        dpis.append(dpi)
        rvpies.append(rvpi)
    return tvpis, dpis, rvpies


def plot_performance_metrics(
    fund_df: pd.DataFrame, metrics: dict = None, title: str = None
) -> Figure:
    """Plot performance metrics with enhanced interactivity and modern styling."""
    # Ensure proper data types and alignment
    fund_df = fund_df.copy()
    fund_df.index = pd.to_datetime(fund_df.index)
    fund_df = fund_df.sort_index()

    # Calculate running metrics
    running_irr = running_xirr(
        fund_df["cash_flow_amount"], fund_df["nav"], fund_df.index
    )
    running_mults = running_multiples(fund_df["cash_flow_amount"], fund_df["nav"])

    # Convert to 1D numpy arrays and ensure correct length
    x = np.array(fund_df.index)
    running_irr = np.asarray(running_irr).flatten()
    tvpi = np.asarray(running_mults[0]).flatten()
    dpi = np.asarray(running_mults[1]).flatten()
    rvpi = np.asarray(running_mults[2]).flatten()
    # Truncate or pad if needed
    n = len(x)
    running_irr = running_irr[:n]
    tvpi = tvpi[:n]
    dpi = dpi[:n]
    rvpi = rvpi[:n]

    # Set the style
    plt.style.use("seaborn-v0_8-whitegrid")

    # Create figure and axes
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot multiples on the right axis
    ax2 = ax1.twinx()

    # Plot TVPI, DPI, RVPI
    ax2.plot(x, tvpi, label="TVPI", color="blue")
    ax2.plot(x, dpi, label="DPI", color="green")
    ax2.plot(x, rvpi, label="RVPI", color="red")

    # Configure right axis
    ax2.set_ylabel("Multiple", color="black")
    ax2.tick_params(axis="y", labelcolor="black")
    ax2.grid(True, alpha=0.3)

    # Plot IRR on the left axis
    ax1.plot(x, running_irr * 100, label="IRR", color="purple", linestyle="--")

    # Configure left axis
    ax1.set_ylabel("IRR (%)", color="black")
    ax1.tick_params(axis="y", labelcolor="black")
    ax1.grid(True, alpha=0.3)

    # Add legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    # Add title
    plt.title("Performance Metrics Over Time")

    # Adjust layout
    plt.tight_layout()

    return fig


def plot_pme_metrics(metrics: dict) -> plt.Figure:
    table_keys = [
        "Fund IRR",
        "Index IRR",
        "TVPI",
        "DPI",
        "RVPI",
        "KS PME",
        "Direct Alpha",
        "Index TVPI",
        "Annualized Return",
        "Fund Volatility",
        "Index Volatility",
        "Fund Drawdown",
        "Index Drawdown",
        "Fund Best 1Y Return",
        "Fund Worst 1Y Return",
        "Index Best 1Y Return",
        "Index Worst 1Y Return",
        "Alpha",
        "Beta",
    ]
    rows = []
    for k in table_keys:
        val = metrics.get(k, None)
        rows.append([k, pretty_val(k, val)])
    if "Warnings" in metrics and metrics["Warnings"]:
        rows.append(["Warnings", "\n".join(metrics["Warnings"])])
    fig, ax = plt.subplots(figsize=(6.5, 1 + 0.3 * len(rows)))
    ax.axis("off")
    table = ax.table(
        cellText=rows,
        colLabels=["Metric", "Value"],
        cellLoc="center",
        loc="center",
        colWidths=[0.4, 0.6],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.35, 1.2)
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight="bold")
            cell.set_facecolor("#f3f3f3")
    plt.title("PME & Fund Metrics", pad=14, fontsize=15, weight="bold")
    plt.tight_layout(pad=2.0)
    return fig


def plot_benchmark_metrics(bench_results: dict) -> plt.Figure:
    keys_order = [
        "Index IRR",
        "Index TVPI",
        "Volatility",
        "Drawdown",
        "Best 1Y Return",
        "Worst 1Y Return",
        "Alpha",
        "Beta",
    ]
    all_keys = []
    for name, metrics in bench_results.items():
        all_keys.extend(metrics.keys())
    all_keys = list(dict.fromkeys(keys_order + all_keys))
    col_labels = ["Metric"] + list(bench_results.keys())
    data = []
    for key in all_keys:
        row = [key]
        for bench, metrics in bench_results.items():
            val = metrics.get(key, None)
            row.append(pretty_val(key, val))
        data.append(row)
    fig, ax = plt.subplots(figsize=(7 + len(bench_results), 2.8 + 0.3 * len(data)))
    ax.axis("off")
    table = ax.table(
        cellText=data,
        colLabels=col_labels,
        cellLoc="center",
        loc="center",
        colWidths=[0.25] + [0.17] * len(bench_results),
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.25, 1.2)
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight="bold")
            cell.set_facecolor("#f3f3f3")
        if col > 0:
            cell.set_text_props(ha="right")
    plt.title("Benchmark Metrics", pad=16, fontsize=15, weight="bold")
    plt.tight_layout(pad=2.0)
    return fig


def pretty_val(key, val):
    if val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
        return "—"

    # Handle string values directly
    if isinstance(val, str):
        return val

    # Ensure val is numeric before applying numeric formatting
    try:
        val = float(val)
    except (ValueError, TypeError):
        return str(val)

    if "IRR" in key or "Alpha" in key or "Return" in key:
        return f"{val * 100:+.2f} %"
    if key == "Beta":
        return f"{val:.2f}"
    if "Drawdown" in key:
        return f"{val * 100:.2f} %"
    elif abs(val) >= 1_000_000_000:
        return f"{val / 1_000_000_000:.2f} B"
    elif abs(val) >= 1_000_000:
        return f"{val / 1_000_000:.2f} M"
    else:
        return f"{val:.2f}"
