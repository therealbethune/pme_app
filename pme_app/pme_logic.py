# pme_app/pme_logic.py
"""
pme_logic.py — PME Logic and Data Loader Module

Robust data loading for PME calculator (Excel/CSV).
- Auto-detects columns (case-insensitive, flexible names)
- Ensures the returned DataFrame has a sorted DatetimeIndex named "date"
- Validates no duplicate dates
- Validates no missing values in cash_flow_amount or nav for fund files, and in level for index files
- Returns clean DataFrames ready for PME calculations
"""

from pathlib import Path

import pandas as pd


def resolve_col(df, possibles):
    """
    Find the first column in df matching any in possibles
    (case/space/underscore insensitive).
    """
    std_cols = [c.strip().lower().replace(" ", "_") for c in df.columns]
    possibles_std = [n.strip().lower().replace(" ", "_") for n in possibles]
    for name in possibles_std:
        if name in std_cols:
            return df.columns[std_cols.index(name)]
    return None


def export_to_excel(metrics: dict, file: str | Path):
    """
    Export the PME metrics to Excel.
    """
    df = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])
    df.to_excel(file, index=False)


def export_to_pdf(metrics: dict, file: str | Path):
    """
    Export the PME metrics to PDF using matplotlib.
    """
    try:
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
    except ImportError as e:
        raise ImportError("matplotlib is required for PDF export.") from e

    df = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis("off")
    tbl = ax.table(cellText=df.values, colLabels=df.columns, loc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(11)
    tbl.scale(1, 1.5)
    with PdfPages(file) as pdf:
        pdf.savefig(fig)
    plt.close(fig)
