"""
Advanced Chart Engine for PME Calculator
Generates interactive charts and visualizations for PME analysis.
"""

import logging
from datetime import datetime
from typing import Any, Dict

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)


class ChartEngine:
    """Advanced chart generation engine for PME analysis."""

    def __init__(self):
        self.color_palette = {
            "fund": "#1f77b4",
            "benchmark": "#ff7f0e",
            "pme": "#2ca02c",
            "distribution": "#d62728",
            "contribution": "#9467bd",
            "nav": "#8c564b",
            "irr": "#e377c2",
            "background": "#f8f9fa",
            "grid": "#e0e0e0",
        }

        self.chart_config = {
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d"],
            "toImageButtonOptions": {
                "format": "png",
                "filename": "pme_chart",
                "height": 600,
                "width": 1000,
                "scale": 2,
            },
        }

    def create_pme_dashboard(
        self,
        fund_data: pd.DataFrame,
        benchmark_data: pd.DataFrame,
        metrics: dict[str, Any],
    ) -> dict[str, Any]:
        """Create comprehensive PME dashboard with multiple charts."""

        charts = {}

        try:
            # 1. Performance Comparison Chart
            charts["performance_comparison"] = self._create_performance_chart(
                fund_data, benchmark_data, metrics
            )

            # 2. Cash Flow Waterfall
            charts["cash_flow_waterfall"] = self._create_cashflow_waterfall(fund_data)

            # 3. PME Metrics Summary
            charts["metrics_summary"] = self._create_metrics_summary(metrics)

            # 4. Risk-Return Scatter
            charts["risk_return"] = self._create_risk_return_chart(
                fund_data, benchmark_data
            )

            # 5. Rolling Performance
            charts["rolling_performance"] = self._create_rolling_performance_chart(
                fund_data, benchmark_data
            )

            # 6. Distributions Timeline
            charts["distributions_timeline"] = self._create_distributions_timeline(
                fund_data
            )

            return {
                "success": True,
                "charts": charts,
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "chart_count": len(charts),
                    "config": self.chart_config,
                },
            }

        except Exception as e:
            logger.error(f"Dashboard creation failed: {e}")
            return {"success": False, "error": str(e), "charts": {}}

    def _create_performance_chart(
        self,
        fund_data: pd.DataFrame,
        benchmark_data: pd.DataFrame,
        metrics: dict[str, Any],
    ) -> dict[str, Any]:
        """Create performance comparison chart."""

        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Cumulative Performance",
                "Monthly Returns",
                "PME Comparison",
                "NAV vs Benchmark",
            ),
            specs=[
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": True}],
            ],
            vertical_spacing=0.1,
        )

        # Prepare data
        fund_df = fund_data.copy()
        fund_df["date"] = pd.to_datetime(fund_df["date"])
        fund_df = fund_df.sort_values("date").reset_index(drop=True)

        # Calculate cumulative returns
        fund_df["cumulative_nav"] = fund_df["nav"] / fund_df["nav"].iloc[0]

        if benchmark_data is not None and len(benchmark_data) > 0:
            bench_df = benchmark_data.copy()
            bench_df["date"] = pd.to_datetime(bench_df["date"])
            bench_df = bench_df.sort_values("date").reset_index(drop=True)
            bench_df["cumulative_price"] = bench_df["price"] / bench_df["price"].iloc[0]

        # 1. Cumulative Performance
        fig.add_trace(
            go.Scatter(
                x=fund_df["date"],
                y=fund_df["cumulative_nav"],
                name="Fund NAV",
                line={"color": self.color_palette["fund"], "width": 3},
                hovertemplate="<b>Fund NAV</b><br>Date: %{x}<br>Value: %{y:.2f}<extra></extra>",
            ),
            row=1,
            col=1,
        )

        if benchmark_data is not None and len(benchmark_data) > 0:
            fig.add_trace(
                go.Scatter(
                    x=bench_df["date"],
                    y=bench_df["cumulative_price"],
                    name="Benchmark",
                    line={
                        "color": self.color_palette["benchmark"], "width": 2, "dash": "dash"
                    },
                    hovertemplate="<b>Benchmark</b><br>Date: %{x}<br>Value: %{y:.2f}<extra></extra>",
                ),
                row=1,
                col=1,
            )

        # 2. Monthly Returns (if enough data)
        if len(fund_df) > 3:
            fund_df["returns"] = fund_df["nav"].pct_change()

            fig.add_trace(
                go.Bar(
                    x=fund_df["date"],
                    y=fund_df["returns"] * 100,
                    name="Monthly Returns (%)",
                    marker_color=self.color_palette["fund"],
                    opacity=0.7,
                    hovertemplate="<b>Monthly Return</b><br>Date: %{x}<br>Return: %{y:.1f}%<extra></extra>",
                ),
                row=1,
                col=2,
            )

        # 3. PME Metrics
        pme_metrics = ["TVPI", "DPI", "RVPI"]
        pme_values = [metrics.get(metric, 0) for metric in pme_metrics]

        fig.add_trace(
            go.Bar(
                x=pme_metrics,
                y=pme_values,
                name="PME Metrics",
                marker_color=[
                    self.color_palette["pme"],
                    self.color_palette["distribution"],
                    self.color_palette["nav"],
                ],
                text=[f"{val:.2f}x" for val in pme_values],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Value: %{y:.2f}x<extra></extra>",
            ),
            row=2,
            col=1,
        )

        # 4. NAV with Cash Flows
        fig.add_trace(
            go.Scatter(
                x=fund_df["date"],
                y=fund_df["nav"],
                name="NAV",
                line={"color": self.color_palette["nav"], "width": 2},
                yaxis="y4",
                hovertemplate="<b>NAV</b><br>Date: %{x}<br>NAV: $%{y:,.0f}<extra></extra>",
            ),
            row=2,
            col=2,
        )

        # Add cash flow markers
        cash_flows = fund_df[fund_df["cashflow"] != 0]
        if len(cash_flows) > 0:
            fig.add_trace(
                go.Scatter(
                    x=cash_flows["date"],
                    y=cash_flows["cashflow"],
                    mode="markers",
                    name="Cash Flows",
                    marker={
                        "size": abs(cash_flows["cashflow"])
                        / cash_flows["cashflow"].abs().max()
                        * 20
                        + 5,
                        "color": np.where(
                            cash_flows["cashflow"] > 0,
                            self.color_palette["distribution"],
                            self.color_palette["contribution"],
                        ),
                        "opacity": 0.8,
                    },
                    yaxis="y4",
                    hovertemplate="<b>Cash Flow</b><br>Date: %{x}<br>Amount: $%{y:,.0f}<extra></extra>",
                ),
                row=2,
                col=2,
            )

        # Update layout
        fig.update_layout(
            title="PME Performance Dashboard",
            showlegend=True,
            plot_bgcolor="white",
            height=700,
            font={"size": 12},
            hovermode="x unified",
        )

        # Update axes
        fig.update_xaxes(showgrid=True, gridcolor=self.color_palette["grid"])
        fig.update_yaxes(showgrid=True, gridcolor=self.color_palette["grid"])

        return {
            "type": "plotly",
            "data": fig.to_json(),
            "config": self.chart_config,
            "title": "Performance Dashboard",
        }

    def _create_cashflow_waterfall(self, fund_data: pd.DataFrame) -> dict[str, Any]:
        """Create cash flow waterfall chart."""

        fund_df = fund_data.copy()
        fund_df["date"] = pd.to_datetime(fund_df["date"])
        fund_df = fund_df.sort_values("date").reset_index(drop=True)

        # Calculate cumulative cash flows
        contributions = fund_df[fund_df["cashflow"] < 0]["cashflow"].sum()
        distributions = fund_df[fund_df["cashflow"] > 0]["cashflow"].sum()
        current_nav = fund_df["nav"].iloc[-1]
        total_value = distributions + current_nav

        # Waterfall data
        categories = ["Contributions", "Distributions", "Current NAV", "Total Value"]
        values = [abs(contributions), distributions, current_nav, total_value]

        fig = go.Figure(
            go.Waterfall(
                name="Cash Flow Waterfall",
                orientation="v",
                measure=["absolute", "relative", "relative", "total"],
                x=categories,
                textposition="outside",
                text=[f"${val:,.0f}" for val in values],
                y=values,
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                increasing={"marker": {"color": self.color_palette["distribution"]}},
                decreasing={"marker": {"color": self.color_palette["contribution"]}},
                totals={"marker": {"color": self.color_palette["pme"]}},
            )
        )

        fig.update_layout(
            title="Investment Cash Flow Analysis",
            showlegend=False,
            plot_bgcolor="white",
            height=500,
            yaxis_title="Amount ($)",
            font={"size": 12},
        )

        return {
            "type": "plotly",
            "data": fig.to_json(),
            "config": self.chart_config,
            "title": "Cash Flow Waterfall",
        }

    def _create_metrics_summary(self, metrics: dict[str, Any]) -> dict[str, Any]:
        """Create metrics summary visualization."""

        # Key metrics for display
        key_metrics = {
            "IRR": f"{metrics.get('Fund IRR', 0):.1%}",
            "TVPI": f"{metrics.get('TVPI', 0):.2f}x",
            "DPI": f"{metrics.get('DPI', 0):.2f}x",
            "RVPI": f"{metrics.get('RVPI', 0):.2f}x",
            "PME": f"{metrics.get('PME', 0):.2f}",
            "Alpha": f"{metrics.get('Alpha', 0):.2%}",
        }

        # Create gauge charts
        fig = make_subplots(
            rows=2,
            cols=3,
            subplot_titles=list(key_metrics.keys()),
            specs=[
                [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
            ],
        )

        positions = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3)]

        for i, (metric, value) in enumerate(key_metrics.items()):
            row, col = positions[i]

            # Set gauge parameters based on metric type
            if metric == "IRR":
                gauge_max = 50
                threshold = 15
            elif metric in ["TVPI", "DPI", "RVPI"]:
                gauge_max = 5
                threshold = 2
            elif metric == "PME":
                gauge_max = 3
                threshold = 1.2
            else:  # Alpha
                gauge_max = 20
                threshold = 5

            numeric_value = float(value.replace("%", "").replace("x", ""))

            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=numeric_value,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": metric},
                    gauge={
                        "axis": {"range": [None, gauge_max]},
                        "bar": {"color": self.color_palette["fund"]},
                        "steps": [
                            {"range": [0, threshold], "color": "lightgray"},
                            {"range": [threshold, gauge_max], "color": "gray"},
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 4},
                            "thickness": 0.75,
                            "value": threshold,
                        },
                    },
                ),
                row=row,
                col=col,
            )

        fig.update_layout(
            title="Key Performance Metrics", height=600, font={"size": 14}
        )

        return {
            "type": "plotly",
            "data": fig.to_json(),
            "config": self.chart_config,
            "title": "Metrics Summary",
        }

    def _create_risk_return_chart(
        self, fund_data: pd.DataFrame, benchmark_data: pd.DataFrame
    ) -> dict[str, Any]:
        """Create risk-return scatter plot."""

        fund_df = fund_data.copy()
        fund_df["date"] = pd.to_datetime(fund_df["date"])
        fund_df = fund_df.sort_values("date").reset_index(drop=True)

        # Calculate returns and risk metrics
        if len(fund_df) > 3:
            fund_df["returns"] = fund_df["nav"].pct_change().dropna()
            fund_return = fund_df["returns"].mean() * 12  # Annualized
            fund_volatility = fund_df["returns"].std() * np.sqrt(12)  # Annualized
        else:
            fund_return = 0
            fund_volatility = 0

        # Benchmark metrics (if available)
        bench_return = 0
        bench_volatility = 0

        if benchmark_data is not None and len(benchmark_data) > 3:
            bench_df = benchmark_data.copy()
            bench_df["date"] = pd.to_datetime(bench_df["date"])
            bench_df = bench_df.sort_values("date").reset_index(drop=True)
            bench_df["returns"] = bench_df["price"].pct_change().dropna()
            bench_return = bench_df["returns"].mean() * 12
            bench_volatility = bench_df["returns"].std() * np.sqrt(12)

        fig = go.Figure()

        # Add fund point
        fig.add_trace(
            go.Scatter(
                x=[fund_volatility * 100],
                y=[fund_return * 100],
                mode="markers",
                name="Fund",
                marker={
                    "size": 20, "color": self.color_palette["fund"], "symbol": "diamond"
                },
                hovertemplate="<b>Fund</b><br>Volatility: %{x:.1f}%<br>Return: %{y:.1f}%<extra></extra>",
            )
        )

        # Add benchmark point
        if bench_return != 0 and bench_volatility != 0:
            fig.add_trace(
                go.Scatter(
                    x=[bench_volatility * 100],
                    y=[bench_return * 100],
                    mode="markers",
                    name="Benchmark",
                    marker={
                        "size": 15, "color": self.color_palette["benchmark"], "symbol": "circle"
                    },
                    hovertemplate="<b>Benchmark</b><br>Volatility: %{x:.1f}%<br>Return: %{y:.1f}%<extra></extra>",
                )
            )

        # Add efficient frontier line (theoretical)
        x_line = np.linspace(
            0, max(fund_volatility * 100, bench_volatility * 100) * 1.2, 100
        )
        y_line = np.sqrt(x_line) * 2  # Simplified efficient frontier

        fig.add_trace(
            go.Scatter(
                x=x_line,
                y=y_line,
                mode="lines",
                name="Efficient Frontier",
                line={"color": "gray", "dash": "dot"},
                hoverinfo="skip",
            )
        )

        fig.update_layout(
            title="Risk-Return Analysis",
            xaxis_title="Volatility (%)",
            yaxis_title="Return (%)",
            plot_bgcolor="white",
            height=500,
            showlegend=True,
            font={"size": 12},
        )

        fig.update_xaxes(showgrid=True, gridcolor=self.color_palette["grid"])
        fig.update_yaxes(showgrid=True, gridcolor=self.color_palette["grid"])

        return {
            "type": "plotly",
            "data": fig.to_json(),
            "config": self.chart_config,
            "title": "Risk-Return Analysis",
        }

    def _create_rolling_performance_chart(
        self, fund_data: pd.DataFrame, benchmark_data: pd.DataFrame
    ) -> dict[str, Any]:
        """Create rolling performance chart."""

        fund_df = fund_data.copy()
        fund_df["date"] = pd.to_datetime(fund_df["date"])
        fund_df = fund_df.sort_values("date").reset_index(drop=True)

        if len(fund_df) < 4:
            return {
                "type": "plotly",
                "data": go.Figure().to_json(),
                "config": self.chart_config,
                "title": "Rolling Performance (Insufficient Data)",
            }

        # Calculate rolling metrics
        window = min(4, len(fund_df) // 2)
        fund_df["rolling_return"] = fund_df["nav"].pct_change(periods=window)
        fund_df["rolling_volatility"] = (
            fund_df["nav"].pct_change().rolling(window=window).std()
        )

        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=("Rolling Returns", "Rolling Volatility"),
            vertical_spacing=0.1,
        )

        # Rolling returns
        fig.add_trace(
            go.Scatter(
                x=fund_df["date"],
                y=fund_df["rolling_return"] * 100,
                name="Rolling Returns",
                line={"color": self.color_palette["fund"]},
                hovertemplate="<b>Rolling Return</b><br>Date: %{x}<br>Return: %{y:.1f}%<extra></extra>",
            ),
            row=1,
            col=1,
        )

        # Rolling volatility
        fig.add_trace(
            go.Scatter(
                x=fund_df["date"],
                y=fund_df["rolling_volatility"] * 100,
                name="Rolling Volatility",
                line={"color": self.color_palette["benchmark"]},
                hovertemplate="<b>Rolling Volatility</b><br>Date: %{x}<br>Volatility: %{y:.1f}%<extra></extra>",
            ),
            row=2,
            col=1,
        )

        fig.update_layout(
            title="Rolling Performance Analysis",
            height=600,
            plot_bgcolor="white",
            showlegend=False,
            font={"size": 12},
        )

        fig.update_xaxes(showgrid=True, gridcolor=self.color_palette["grid"])
        fig.update_yaxes(showgrid=True, gridcolor=self.color_palette["grid"])

        return {
            "type": "plotly",
            "data": fig.to_json(),
            "config": self.chart_config,
            "title": "Rolling Performance",
        }

    def _create_distributions_timeline(self, fund_data: pd.DataFrame) -> dict[str, Any]:
        """Create distributions timeline chart."""

        fund_df = fund_data.copy()
        fund_df["date"] = pd.to_datetime(fund_df["date"])
        fund_df = fund_df.sort_values("date").reset_index(drop=True)

        # Separate contributions and distributions
        contributions = fund_df[fund_df["cashflow"] < 0].copy()
        distributions = fund_df[fund_df["cashflow"] > 0].copy()

        fig = go.Figure()

        # Add contributions
        if len(contributions) > 0:
            fig.add_trace(
                go.Bar(
                    x=contributions["date"],
                    y=contributions["cashflow"],
                    name="Contributions",
                    marker_color=self.color_palette["contribution"],
                    hovertemplate="<b>Contribution</b><br>Date: %{x}<br>Amount: $%{y:,.0f}<extra></extra>",
                )
            )

        # Add distributions
        if len(distributions) > 0:
            fig.add_trace(
                go.Bar(
                    x=distributions["date"],
                    y=distributions["cashflow"],
                    name="Distributions",
                    marker_color=self.color_palette["distribution"],
                    hovertemplate="<b>Distribution</b><br>Date: %{x}<br>Amount: $%{y:,.0f}<extra></extra>",
                )
            )

        # Add cumulative line
        fund_df["cumulative_cf"] = fund_df["cashflow"].cumsum()
        fig.add_trace(
            go.Scatter(
                x=fund_df["date"],
                y=fund_df["cumulative_cf"],
                name="Cumulative Cash Flow",
                line={"color": self.color_palette["pme"], "width": 3},
                yaxis="y2",
                hovertemplate="<b>Cumulative CF</b><br>Date: %{x}<br>Amount: $%{y:,.0f}<extra></extra>",
            )
        )

        fig.update_layout(
            title="Cash Flow Timeline",
            xaxis_title="Date",
            yaxis_title="Cash Flow ($)",
            yaxis2={"title": "Cumulative Cash Flow ($)", "overlaying": "y", "side": "right"},
            plot_bgcolor="white",
            height=500,
            showlegend=True,
            font={"size": 12},
        )

        fig.update_xaxes(showgrid=True, gridcolor=self.color_palette["grid"])
        fig.update_yaxes(showgrid=True, gridcolor=self.color_palette["grid"])

        return {
            "type": "plotly",
            "data": fig.to_json(),
            "config": self.chart_config,
            "title": "Cash Flow Timeline",
        }

    def export_chart_data(
        self, charts: dict[str, Any], format: str = "json"
    ) -> dict[str, Any]:
        """Export chart data in various formats."""

        if format == "json":
            return {"success": True, "data": charts, "format": "json"}

        # Could add CSV, Excel export here
        return {
            "success": False,
            "error": f"Format {format} not supported",
            "supported_formats": ["json"],
        }
