import io
import logging
from datetime import datetime
from typing import Dict

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from jinja2 import Template
from weasyprint import CSS, HTML

matplotlib.use("Agg")  # Use non-interactive backend
import seaborn as sns
from models import Portfolio, PortfolioFund
from portfolio_service import PortfolioService
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ReportingService:
    """Service for generating PDF and Excel reports."""

    def __init__(self, db: Session):
        self.db = db
        self.portfolio_service = PortfolioService(db)

    async def generate_pdf(self, portfolio_id: int) -> bytes:
        """Generate branded PDF report for portfolio."""
        try:
            # Get portfolio data
            portfolio = (
                self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            )
            if not portfolio:
                raise ValueError(f"Portfolio {portfolio_id} not found")

            # Get portfolio analytics
            analytics = await self.portfolio_service.calc_portfolio_kpis(portfolio_id)

            # Generate charts
            charts = await self._generate_charts(portfolio_id, analytics)

            # Render HTML template
            html_content = self._render_pdf_template(portfolio, analytics, charts)

            # Generate PDF
            pdf_bytes = HTML(string=html_content).write_pdf(
                stylesheets=[CSS(string=self._get_pdf_styles())]
            )

            logger.info(f"Generated PDF report for portfolio {portfolio_id}")
            return pdf_bytes

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise

    async def generate_excel(self, portfolio_id: int) -> bytes:
        """Generate Excel workbook with multiple sheets."""
        try:
            portfolio = (
                self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            )
            if not portfolio:
                raise ValueError(f"Portfolio {portfolio_id} not found")

            # Create Excel writer
            buffer = io.BytesIO()

            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:

                # Summary sheet
                await self._write_summary_sheet(writer, portfolio_id)

                # Individual fund sheets
                portfolio_funds = (
                    self.db.query(PortfolioFund)
                    .filter(PortfolioFund.portfolio_id == portfolio_id)
                    .all()
                )

                for pf in portfolio_funds:
                    await self._write_fund_sheet(writer, pf.fund_id, pf.fund.name)

                # Analytics sheet
                await self._write_analytics_sheet(writer, portfolio_id)

            buffer.seek(0)
            excel_bytes = buffer.getvalue()

            logger.info(f"Generated Excel report for portfolio {portfolio_id}")
            return excel_bytes

        except Exception as e:
            logger.error(f"Error generating Excel: {str(e)}")
            raise

    def _render_pdf_template(
        self, portfolio: Portfolio, analytics: dict, charts: dict
    ) -> str:
        """Render HTML template for PDF generation."""

        template_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>PME Portfolio Report - {{ portfolio.name }}</title>
        </head>
        <body>
            <div class="header">
                <h1>PME Portfolio Report</h1>
                <h2>{{ portfolio.name }}</h2>
                <p>Generated on {{ report_date }}</p>
            </div>

            <div class="section">
                <h3>Portfolio Overview</h3>
                <table class="kpi-table">
                    <tr><td>Number of Funds</td><td>{{ analytics.num_funds }}</td></tr>
                    <tr><td>Portfolio TVPI</td><td>{{ "%.2f"|format(analytics.kpis.get('Portfolio TVPI', 0)) }}</td></tr>
                    <tr><td>Portfolio IRR</td><td>{{ "%.1f%"|format(analytics.kpis.get('Portfolio Fund IRR', 0) * 100) }}</td></tr>
                    <tr><td>Total Contributions</td><td>${{ "${:,.0f}"|format(analytics.kpis.get('Portfolio Total Contributions', 0)) }}</td></tr>
                    <tr><td>Total Distributions</td><td>${{ "${:,.0f}"|format(analytics.kpis.get('Portfolio Total Distributions', 0)) }}</td></tr>
                    <tr><td>Remaining NAV</td><td>${{ "${:,.0f}"|format(analytics.kpis.get('Portfolio Final NAV', 0)) }}</td></tr>
                </table>
            </div>

            <div class="section">
                <h3>Risk Metrics</h3>
                <table class="kpi-table">
                    {% for key, value in analytics.risk_metrics.items() %}
                    <tr><td>{{ key.replace('portfolio_', '').replace('_', ' ').title() }}</td><td>{{ "%.2f"|format(value) }}</td></tr>
                    {% endfor %}
                </table>
            </div>

            <div class="section">
                <h3>Current vs Optimal Weights</h3>
                {% if analytics.optimal_weights.optimization_success %}
                <table class="weights-table">
                    <thead>
                        <tr><th>Fund</th><th>Current Weight</th><th>Optimal Weight</th></tr>
                    </thead>
                    <tbody>
                        {% for i in range(analytics.current_weights|length) %}
                        <tr>
                            <td>Fund {{ i + 1 }}</td>
                            <td>{{ "%.1f%"|format(analytics.current_weights[i] * 100) }}</td>
                            <td>{{ "%.1f%"|format(analytics.optimal_weights.optimal_weights[i] * 100) }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% endif %}
            </div>

            {% if charts.correlation_heatmap %}
            <div class="section">
                <h3>Fund Correlation Matrix</h3>
                <img src="data:image/png;base64,{{ charts.correlation_heatmap }}" alt="Correlation Heatmap">
            </div>
            {% endif %}

            <div class="footer">
                <p>Report generated by Fund Analysis Tool</p>
                <p>Glasfunds Analytics Platform</p>
            </div>
        </body>
        </html>
        """

        template = Template(template_html)
        return template.render(
            portfolio=portfolio,
            analytics=analytics,
            charts=charts,
            report_date=datetime.now().strftime("%B %d, %Y"),
        )

    def _get_pdf_styles(self) -> str:
        """Get CSS styles for PDF generation."""
        return """
        @page {
            margin: 1in;
            @top-center {
                content: "PME Portfolio Report";
                font-family: 'Inter', sans-serif;
                font-size: 10pt;
                color: #003d6d;
            }
        }

        body {
            font-family: 'Inter', sans-serif;
            font-size: 12pt;
            line-height: 1.4;
            color: #333;
        }

        .header {
            text-align: center;
            margin-bottom: 2em;
            border-bottom: 2px solid #003d6d;
            padding-bottom: 1em;
        }

        .header h1 {
            color: #003d6d;
            font-size: 24pt;
            margin: 0;
        }

        .header h2 {
            color: #00d2c3;
            font-size: 18pt;
            margin: 0.5em 0;
        }

        .section {
            margin-bottom: 2em;
            page-break-inside: avoid;
        }

        .section h3 {
            color: #003d6d;
            font-size: 16pt;
            border-bottom: 1px solid #00d2c3;
            padding-bottom: 0.2em;
        }

        .kpi-table, .weights-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1em 0;
        }

        .kpi-table td, .weights-table td, .weights-table th {
            border: 1px solid #ddd;
            padding: 0.5em;
            text-align: left;
        }

        .weights-table th {
            background-color: #f8f9fa;
            font-weight: bold;
        }

        .kpi-table td:first-child {
            font-weight: bold;
            background-color: #f8f9fa;
        }

        .footer {
            margin-top: 3em;
            text-align: center;
            font-size: 10pt;
            color: #666;
            border-top: 1px solid #ddd;
            padding-top: 1em;
        }

        img {
            max-width: 100%;
            height: auto;
        }
        """

    async def _generate_charts(self, portfolio_id: int, analytics: dict) -> dict:
        """Generate charts for PDF report."""
        charts = {}

        try:
            # Correlation heatmap
            if analytics.get("correlation_matrix"):
                correlation_matrix = analytics["correlation_matrix"]

                plt.figure(figsize=(8, 6))
                sns.heatmap(
                    correlation_matrix,
                    annot=True,
                    cmap="RdYlBu_r",
                    center=0,
                    square=True,
                    fmt=".2f",
                )
                plt.title("Fund Correlation Matrix")

                # Save to base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format="png", dpi=300, bbox_inches="tight")
                buffer.seek(0)

                import base64

                charts["correlation_heatmap"] = base64.b64encode(
                    buffer.getvalue()
                ).decode()
                plt.close()

        except Exception as e:
            logger.error(f"Error generating charts: {str(e)}")

        return charts

    async def _write_summary_sheet(self, writer: pd.ExcelWriter, portfolio_id: int):
        """Write portfolio summary sheet to Excel."""
        try:
            analytics = await self.portfolio_service.calc_portfolio_kpis(portfolio_id)

            # Create summary DataFrame
            summary_data = []

            # Portfolio KPIs
            kpis = analytics.get("kpis", {})
            for key, value in kpis.items():
                summary_data.append(["Portfolio KPIs", key, value])

            # Risk metrics
            risk_metrics = analytics.get("risk_metrics", {})
            for key, value in risk_metrics.items():
                summary_data.append(
                    [
                        "Risk Metrics",
                        key.replace("portfolio_", "").replace("_", " ").title(),
                        value,
                    ]
                )

            # Create DataFrame
            df = pd.DataFrame(summary_data, columns=["Category", "Metric", "Value"])
            df.to_excel(writer, sheet_name="Portfolio Summary", index=False)

        except Exception as e:
            logger.error(f"Error writing summary sheet: {str(e)}")

    async def _write_fund_sheet(
        self, writer: pd.ExcelWriter, fund_id: int, fund_name: str
    ):
        """Write individual fund sheet to Excel."""
        try:
            fund_data = await self.portfolio_service._get_fund_data(fund_id)
            if not fund_data:
                return

            # Cash flows sheet
            cf_data = []
            for cf in fund_data["cash_flows"]:
                cf_data.append(
                    {
                        "Date": cf["date"],
                        "Amount": cf["amount"],
                        "Type": "Contribution" if cf["amount"] > 0 else "Distribution",
                    }
                )

            if cf_data:
                cf_df = pd.DataFrame(cf_data)
                sheet_name = f"{fund_name[:25]}_CashFlows"  # Excel sheet name limit
                cf_df.to_excel(writer, sheet_name=sheet_name, index=False)

        except Exception as e:
            logger.error(f"Error writing fund sheet for {fund_name}: {str(e)}")

    async def _write_analytics_sheet(self, writer: pd.ExcelWriter, portfolio_id: int):
        """Write analytics sheet with correlation matrix and weights."""
        try:
            analytics = await self.portfolio_service.calc_portfolio_kpis(portfolio_id)

            # Correlation matrix
            if analytics.get("correlation_matrix"):
                corr_df = pd.DataFrame(
                    analytics["correlation_matrix"],
                    columns=[
                        f"Fund_{i+1}"
                        for i in range(len(analytics["correlation_matrix"]))
                    ],
                    index=[
                        f"Fund_{i+1}"
                        for i in range(len(analytics["correlation_matrix"]))
                    ],
                )
                corr_df.to_excel(writer, sheet_name="Correlations")

            # Weights comparison
            if analytics.get("optimal_weights", {}).get("optimization_success"):
                weights_data = []
                current_weights = analytics["current_weights"]
                optimal_weights = analytics["optimal_weights"]["optimal_weights"]

                for i, (current, optimal) in enumerate(
                    zip(current_weights, optimal_weights, strict=False)
                ):
                    weights_data.append(
                        {
                            "Fund": f"Fund_{i+1}",
                            "Current_Weight": current,
                            "Optimal_Weight": optimal,
                            "Difference": optimal - current,
                        }
                    )

                weights_df = pd.DataFrame(weights_data)
                weights_df.to_excel(writer, sheet_name="Weight_Analysis", index=False)

        except Exception as e:
            logger.error(f"Error writing analytics sheet: {str(e)}")


# Scheduled reporting function (for Celery)
async def generate_monthly_performance_pack(portfolio_id: int) -> dict:
    """Generate monthly performance pack (for Celery scheduling)."""
    try:

        # This would be called by Celery beat scheduler
        # Implementation would depend on your Celery setup

        logger.info(f"Generating monthly performance pack for portfolio {portfolio_id}")

        # Generate both PDF and Excel
        reporting_service = ReportingService(db=None)  # Would need proper DB session

        pdf_bytes = await reporting_service.generate_pdf(portfolio_id)
        excel_bytes = await reporting_service.generate_excel(portfolio_id)

        # Save to file system or cloud storage
        # Send via email
        # Log completion

        return {
            "portfolio_id": portfolio_id,
            "pdf_size": len(pdf_bytes),
            "excel_size": len(excel_bytes),
            "generated_at": datetime.utcnow().isoformat(),
            "status": "success",
        }

    except Exception as e:
        logger.error(f"Error in monthly performance pack: {str(e)}")
        return {"status": "error", "error": str(e)}
