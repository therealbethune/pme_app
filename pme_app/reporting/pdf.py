from datetime import datetime
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def render_pdf(df: pd.DataFrame, path: Path) -> None:
    """
    Render portfolio metrics to a professional PDF report.

    Args:
        df: DataFrame containing portfolio metrics
        path: Output path for the PDF file
    """
    # Create the PDF document
    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    # Container for the 'Flowable' objects
    story = []

    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    heading_style = styles["Heading1"]
    normal_style = styles["Normal"]

    # Title
    title = Paragraph("Portfolio Analytics Report", title_style)
    story.append(title)
    story.append(Spacer(1, 12))

    # Report metadata
    report_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    date_para = Paragraph(f"Generated on {report_date}", normal_style)
    story.append(date_para)
    story.append(Spacer(1, 24))

    if not df.empty:
        # Executive Summary
        summary_title = Paragraph("Executive Summary", heading_style)
        story.append(summary_title)
        story.append(Spacer(1, 12))

        # Extract key metrics
        metrics = df.iloc[0]

        # Create summary table
        summary_data = [
            ["Metric", "Value"],
            ["Total Portfolio NAV", f"${metrics.get('Total NAV', 0):,.2f}"],
            ["Number of Funds", f"{int(metrics.get('Funds', 0))}"],
            ["Annualized Return", f"{metrics.get('Annualized Return', 0):.2%}"],
            ["Volatility", f"{metrics.get('Volatility', 0):.2%}"],
            ["Sharpe Ratio", f"{metrics.get('Sharpe (rf=0)', 0):.3f}"],
            ["Maximum Drawdown", f"{metrics.get('Max Drawdown', 0):.2%}"],
            ["Calmar Ratio", f"{metrics.get('Calmar Ratio', 0):.3f}"],
        ]

        # Create table
        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                ]
            )
        )

        story.append(summary_table)
        story.append(Spacer(1, 24))

        # Performance Analysis
        analysis_title = Paragraph("Performance Analysis", heading_style)
        story.append(analysis_title)
        story.append(Spacer(1, 12))

        # Risk-adjusted performance commentary
        sharpe = metrics.get("Sharpe (rf=0)", 0)
        calmar = metrics.get("Calmar Ratio", 0)

        if sharpe > 1.0:
            sharpe_comment = "Excellent risk-adjusted returns"
        elif sharpe > 0.5:
            sharpe_comment = "Good risk-adjusted returns"
        elif sharpe > 0:
            sharpe_comment = "Moderate risk-adjusted returns"
        else:
            sharpe_comment = "Poor risk-adjusted returns"

        analysis_text = f"""
        <b>Risk-Adjusted Performance:</b> The portfolio demonstrates {sharpe_comment}
        with a Sharpe ratio of {sharpe:.3f}. The Calmar ratio of {calmar:.3f} indicates
        the return per unit of maximum drawdown risk.

        <br/><br/>
        <b>Volatility Analysis:</b> The portfolio exhibits {metrics.get('Volatility', 0):.2%}
        annualized volatility, with a maximum drawdown of {metrics.get('Max Drawdown', 0):.2%}.

        <br/><br/>
        <b>Portfolio Composition:</b> This analysis covers {int(metrics.get('Funds', 0))}
        fund(s) with a combined NAV of ${metrics.get('Total NAV', 0):,.2f}.
        """

        analysis_para = Paragraph(analysis_text, normal_style)
        story.append(analysis_para)
        story.append(Spacer(1, 24))

        # Detailed Metrics
        details_title = Paragraph("Detailed Metrics", heading_style)
        story.append(details_title)
        story.append(Spacer(1, 12))

        # All metrics table
        detailed_data = [["Metric", "Value", "Description"]]

        metric_descriptions = {
            "Total NAV": "Sum of all fund net asset values",
            "Annualized Return": "Geometric mean return annualized",
            "Volatility": "Standard deviation of returns (annualized)",
            "Sharpe (rf=0)": "Return per unit of risk (risk-free rate = 0)",
            "Funds": "Number of funds in portfolio",
            "Max Drawdown": "Maximum peak-to-trough decline",
            "Calmar Ratio": "Annualized return divided by maximum drawdown",
        }

        for key, value in metrics.items():
            if key in metric_descriptions:
                if key == "Total NAV":
                    formatted_value = f"${value:,.2f}"
                elif key == "Funds":
                    formatted_value = f"{int(value)}"
                elif key in ["Annualized Return", "Volatility", "Max Drawdown"]:
                    formatted_value = f"{value:.2%}"
                else:
                    formatted_value = f"{value:.3f}"

                detailed_data.append([key, formatted_value, metric_descriptions[key]])

        detailed_table = Table(
            detailed_data, colWidths=[2 * inch, 1.5 * inch, 2.5 * inch]
        )
        detailed_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                ]
            )
        )

        story.append(detailed_table)

    else:
        # No data available
        no_data = Paragraph("No portfolio data available for analysis.", normal_style)
        story.append(no_data)

    # Footer
    story.append(Spacer(1, 36))
    footer_text = """
    <i>This report is generated automatically based on uploaded portfolio data.
    Past performance does not guarantee future results. Please consult with a
    financial advisor for investment decisions.</i>
    """
    footer = Paragraph(footer_text, normal_style)
    story.append(footer)

    # Build PDF
    doc.build(story)


def render_simple_pdf(df: pd.DataFrame, path: Path) -> None:
    """
    Simple PDF renderer using basic canvas (fallback option).

    Args:
        df: DataFrame containing portfolio metrics
        path: Output path for the PDF file
    """
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, "Portfolio Analytics Report")

    # Date
    c.setFont("Helvetica", 10)
    report_date = datetime.now().strftime("%B %d, %Y")
    c.drawString(72, height - 100, f"Generated on {report_date}")

    # Metrics
    if not df.empty:
        y_position = height - 140
        c.setFont("Helvetica-Bold", 12)
        c.drawString(72, y_position, "Portfolio Metrics:")

        y_position -= 30
        c.setFont("Helvetica", 10)

        for key, value in df.iloc[0].items():
            if isinstance(value, int | float):
                if key == "Total NAV":
                    text = f"{key}: ${value:,.2f}"
                elif key == "Funds":
                    text = f"{key}: {int(value)}"
                elif key in ["Annualized Return", "Volatility", "Max Drawdown"]:
                    text = f"{key}: {value:.2%}"
                else:
                    text = f"{key}: {value:.3f}"
            else:
                text = f"{key}: {value}"

            c.drawString(72, y_position, text)
            y_position -= 20

            if y_position < 100:  # Start new page if needed
                c.showPage()
                y_position = height - 72
    else:
        c.drawString(72, height - 140, "No portfolio data available.")

    c.save()
