from datetime import datetime
from pathlib import Path

import pandas as pd
import xlsxwriter


def render_xlsx(df: pd.DataFrame, path: Path) -> None:
    """
    Render portfolio metrics to a professional Excel report.

    Args:
        df: DataFrame containing portfolio metrics
        path: Output path for the Excel file
    """
    # Create a workbook and add worksheets
    workbook = xlsxwriter.Workbook(str(path))

    # Define formats
    title_format = workbook.add_format(
        {
            "bold": True,
            "font_size": 16,
            "align": "center",
            "valign": "vcenter",
            "bg_color": "#4472C4",
            "font_color": "white",
        }
    )

    header_format = workbook.add_format(
        {
            "bold": True,
            "font_size": 12,
            "align": "center",
            "valign": "vcenter",
            "bg_color": "#D9E1F2",
            "border": 1,
        }
    )

    metric_format = workbook.add_format(
        {"align": "left", "valign": "vcenter", "border": 1}
    )

    number_format = workbook.add_format(
        {"align": "right", "valign": "vcenter", "border": 1, "num_format": "#,##0.00"}
    )

    percentage_format = workbook.add_format(
        {"align": "right", "valign": "vcenter", "border": 1, "num_format": "0.00%"}
    )

    currency_format = workbook.add_format(
        {"align": "right", "valign": "vcenter", "border": 1, "num_format": "$#,##0.00"}
    )

    date_format = workbook.add_format(
        {"align": "center", "font_size": 10, "italic": True}
    )

    # Summary worksheet
    summary_ws = workbook.add_worksheet("Portfolio Summary")

    # Set column widths
    summary_ws.set_column("A:A", 25)
    summary_ws.set_column("B:B", 20)
    summary_ws.set_column("C:C", 40)

    # Title and date
    summary_ws.merge_range("A1:C1", "Portfolio Analytics Report", title_format)
    report_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    summary_ws.write("A2", f"Generated on {report_date}", date_format)

    if not df.empty:
        metrics = df.iloc[0]

        # Executive Summary section
        summary_ws.write("A4", "Executive Summary", header_format)
        summary_ws.write("B4", "", header_format)
        summary_ws.write("C4", "", header_format)

        # Key metrics
        row = 5
        key_metrics = [
            ("Total Portfolio NAV", metrics.get("Total NAV", 0), currency_format),
            ("Number of Funds", int(metrics.get("Funds", 0)), number_format),
            (
                "Annualized Return",
                metrics.get("Annualized Return", 0),
                percentage_format,
            ),
            ("Volatility", metrics.get("Volatility", 0), percentage_format),
            ("Sharpe Ratio", metrics.get("Sharpe (rf=0)", 0), number_format),
            ("Maximum Drawdown", metrics.get("Max Drawdown", 0), percentage_format),
            ("Calmar Ratio", metrics.get("Calmar Ratio", 0), number_format),
        ]

        for metric_name, value, fmt in key_metrics:
            summary_ws.write(row, 0, metric_name, metric_format)
            summary_ws.write(row, 1, value, fmt)
            row += 1

        # Performance Analysis section
        row += 2
        summary_ws.write(row, 0, "Performance Analysis", header_format)
        summary_ws.write(row, 1, "", header_format)
        summary_ws.write(row, 2, "", header_format)
        row += 1

        # Risk-adjusted performance commentary
        sharpe = metrics.get("Sharpe (rf=0)", 0)
        if sharpe > 1.0:
            sharpe_comment = "Excellent risk-adjusted returns"
        elif sharpe > 0.5:
            sharpe_comment = "Good risk-adjusted returns"
        elif sharpe > 0:
            sharpe_comment = "Moderate risk-adjusted returns"
        else:
            sharpe_comment = "Poor risk-adjusted returns"

        analysis_data = [
            ("Risk Assessment", sharpe_comment),
            ("Volatility Level", f"{metrics.get('Volatility', 0):.2%} annualized"),
            ("Drawdown Risk", f"{metrics.get('Max Drawdown', 0):.2%} maximum decline"),
            ("Portfolio Size", f"{int(metrics.get('Funds', 0))} fund(s)"),
        ]

        for analysis_item, description in analysis_data:
            summary_ws.write(row, 0, analysis_item, metric_format)
            summary_ws.write(row, 1, description, metric_format)
            row += 1

    # Detailed Metrics worksheet
    details_ws = workbook.add_worksheet("Detailed Metrics")

    # Set column widths
    details_ws.set_column("A:A", 25)
    details_ws.set_column("B:B", 20)
    details_ws.set_column("C:C", 50)

    # Title
    details_ws.merge_range("A1:C1", "Detailed Portfolio Metrics", title_format)

    if not df.empty:
        # Headers
        details_ws.write("A3", "Metric", header_format)
        details_ws.write("B3", "Value", header_format)
        details_ws.write("C3", "Description", header_format)

        # Metric descriptions
        metric_descriptions = {
            "Total NAV": "Sum of all fund net asset values",
            "Annualized Return": "Geometric mean return annualized to yearly basis",
            "Volatility": "Standard deviation of returns (annualized)",
            "Sharpe (rf=0)": "Return per unit of risk (assuming zero risk-free rate)",
            "Funds": "Number of individual funds in the portfolio",
            "Max Drawdown": "Maximum peak-to-trough decline in portfolio value",
            "Calmar Ratio": "Annualized return divided by maximum drawdown magnitude",
        }

        row = 4
        for key, value in metrics.items():
            if key in metric_descriptions:
                details_ws.write(row, 0, key, metric_format)

                # Format value based on type
                if key == "Total NAV":
                    details_ws.write(row, 1, value, currency_format)
                elif key == "Funds":
                    details_ws.write(row, 1, int(value), number_format)
                elif key in ["Annualized Return", "Volatility", "Max Drawdown"]:
                    details_ws.write(row, 1, value, percentage_format)
                else:
                    details_ws.write(row, 1, value, number_format)

                details_ws.write(row, 2, metric_descriptions[key], metric_format)
                row += 1

    # Raw Data worksheet (if needed for further analysis)
    if not df.empty:
        raw_ws = workbook.add_worksheet("Raw Data")

        # Write the raw DataFrame
        for col_num, column in enumerate(df.columns):
            raw_ws.write(0, col_num, column, header_format)

        for row_num, (_index, row) in enumerate(df.iterrows(), 1):
            for col_num, value in enumerate(row):
                if isinstance(value, int | float):
                    raw_ws.write(row_num, col_num, value, number_format)
                else:
                    raw_ws.write(row_num, col_num, str(value), metric_format)

    # Charts worksheet (placeholder for future enhancement)
    charts_ws = workbook.add_worksheet("Charts")
    charts_ws.merge_range("A1:D1", "Portfolio Visualization", title_format)
    charts_ws.write(
        "A3", "Chart functionality can be added here for visual analysis", metric_format
    )

    # Close the workbook
    workbook.close()


def render_simple_xlsx(df: pd.DataFrame, path: Path) -> None:
    """
    Simple Excel renderer using pandas (fallback option).

    Args:
        df: DataFrame containing portfolio metrics
        path: Output path for the Excel file
    """
    with pd.ExcelWriter(str(path), engine="xlsxwriter") as writer:
        # Write the main data
        df.to_excel(writer, sheet_name="Portfolio Metrics", index=False)

        # Get the workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets["Portfolio Metrics"]

        # Add some basic formatting
        header_format = workbook.add_format(
            {
                "bold": True,
                "text_wrap": True,
                "valign": "top",
                "fg_color": "#D7E4BC",
                "border": 1,
            }
        )

        # Write the column headers with the defined format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Auto-adjust column widths
        for i, col in enumerate(df.columns):
            max_len = (
                max(
                    df[col].astype(str).map(len).max(),  # len of largest item
                    len(str(col)),  # len of column name/header
                )
                + 2
            )  # adding a little extra space
            worksheet.set_column(i, i, max_len)

        # Add metadata sheet
        metadata_df = pd.DataFrame(
            {
                "Report Information": ["Generated On", "Total Metrics", "Report Type"],
                "Value": [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    len(df.columns),
                    "Portfolio Analytics",
                ],
            }
        )

        metadata_df.to_excel(writer, sheet_name="Report Info", index=False)
