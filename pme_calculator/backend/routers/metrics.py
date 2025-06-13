"""
FastAPI router for metrics endpoints.
"""

from typing import Annotated, Optional

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, Query

router = APIRouter(prefix="/v1/metrics", tags=["metrics"])


def get_filters(
    fund: str | None = Query(None, description="Fund filter"),
    vintage: str | None = Query(None, description="Vintage year filter"),
    currency: str | None = Query(None, description="Currency filter"),
) -> str | None:
    """Extract filters from query parameters."""
    filters = {}
    if fund:
        filters["fund"] = fund
    if vintage:
        filters["vintage"] = vintage
    if currency:
        filters["currency"] = currency

    return filters if filters else None


def query_twr(filters: dict | None = None) -> pd.DataFrame:
    """
    Query TWR data with optional filters.
    Returns a DataFrame with fund and index TWR data.
    """
    # Generate sample TWR data for demonstration
    dates = pd.date_range("2020-01-01", "2023-12-31", freq="M")

    # Simulate fund TWR (more volatile, potentially higher returns)
    np.random.seed(42)
    fund_returns = np.random.normal(
        0.008, 0.04, len(dates)
    )  # 0.8% monthly avg, 4% volatility
    fund_twr = (1 + pd.Series(fund_returns, index=dates)).cumprod() - 1

    # Simulate index TWR (less volatile, steady growth)
    index_returns = np.random.normal(
        0.007, 0.02, len(dates)
    )  # 0.7% monthly avg, 2% volatility
    index_twr = (1 + pd.Series(index_returns, index=dates)).cumprod() - 1

    df = pd.DataFrame({"fund": fund_twr, "index": index_twr})

    # Apply filters if provided
    if filters:
        # In a real implementation, you would filter based on the criteria
        pass

    return df


@router.get("/twr_vs_index")
async def twr_vs_index(filters: Annotated[dict | None, Depends(get_filters)] = None):
    """
    Get TWR vs Index comparison data for charting.
    Returns Plotly-compatible data and layout.
    """
    df = query_twr(filters)

    data = [
        {
            "type": "scatter",
            "mode": "lines",
            "name": "Fund TWR",
            "x": [d.isoformat() for d in df.index],
            "y": df["fund"].tolist(),
            "line": {"color": "#00ff88", "width": 3},
        },
        {
            "type": "scatter",
            "mode": "lines",
            "name": "Index Return",
            "x": [d.isoformat() for d in df.index],
            "y": df["index"].tolist(),
            "line": {"dash": "dot", "color": "#0066cc", "width": 2},
        },
    ]

    layout = {
        "autosize": True,
        "responsive": True,
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#ffffff", "family": "Arial, sans-serif"},
        "legend": {
            "bgcolor": "rgba(0,0,0,0)",
            "bordercolor": "rgba(255,255,255,0.2)",
            "borderwidth": 1,
        },
        "margin": {"l": 50, "r": 50, "t": 50, "b": 50},
        "yaxis": {
            "tickformat": ".0%",
            "title": "Cumulative Return",
            "gridcolor": "rgba(255,255,255,0.1)",
        },
        "xaxis": {"title": "Date", "gridcolor": "rgba(255,255,255,0.1)"},
        "hovermode": "x unified",
        "title": "Time-Weighted Return Comparison",
    }

    return {"data": data, "layout": layout}
