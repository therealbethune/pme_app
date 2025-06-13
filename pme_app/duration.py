# pme_app/duration.py
import pandas as pd
import numpy as np


def compute_realized_cash_flow_duration(dates, cashflows, navs, discount_rate):
    """
    Computes period-by-period realized cash flow duration.
    Returns: pd.Series (indexed by dates), duration in years for each period.
    """
    dates = pd.to_datetime(dates)
    cashflows = np.array(cashflows)
    navs = np.array(navs)
    duration_series = []
    t0 = dates.min()
    for i, t in enumerate(dates):
        cf_to_t = cashflows[: i + 1]
        navs[: i + 1]
        (t - t0).days / 365.25
        # Example calculation: duration = sum(time-weighted PV of CFs) / sum(PV of CFs)
        if np.abs(cf_to_t).sum() == 0:
            duration = np.nan
        else:
            pv_times = []
            pv = []
            for j in range(i + 1):
                years = (dates[j] - t0).days / 365.25
                d = (1 + discount_rate) ** years
                pv.append(cf_to_t[j] / d)
                pv_times.append(cf_to_t[j] * years / d)
            duration = np.sum(pv_times) / (np.sum(pv) if np.sum(pv) else 1)
        duration_series.append(duration)
    return pd.Series(duration_series, index=dates)


import matplotlib.pyplot as plt
import mplcursors


def plot_duration_line(duration_series):
    fig, ax = plt.subplots(figsize=(10, 4))
    (line,) = ax.plot(
        duration_series.index, duration_series.values, marker="o", color="#1976d2", lw=2
    )
    ax.set_title("Realized Cash-Flow Duration Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Duration (years)")
    ax.grid(True, linestyle="--", alpha=0.3)

    # Mplcursors callback
    def on_add(sel):
        idx = int(sel.index)
        date = duration_series.index[idx]
        val = duration_series.iloc[idx]
        sel.annotation.set_text(
            f"Date: {pd.to_datetime(date).strftime('%b %Y')}\nDuration: {val:.2f} yrs"
        )
        sel.annotation.get_bbox_patch().set(fc="white", alpha=0.95, boxstyle="round")

    mplcursors.cursor(line, hover=True).connect("add", on_add)
    return fig
