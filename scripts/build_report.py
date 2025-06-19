#!/usr/bin/env python3
"""
Portfolio Analytics Report Builder

This script generates comprehensive portfolio analytics reports in PDF and Excel formats.
It processes fund data from CSV files and produces professional investment reports.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import structlog

logger = structlog.get_logger()

# Add the parent directory to the path so we can import from pme_app
sys.path.insert(0, str(Path(__file__).parent.parent))

from pme_app.reporting.pdf import render_pdf, render_simple_pdf
from pme_app.reporting.xlsx import render_simple_xlsx, render_xlsx
from pme_app.services.portfolio import calc_portfolio_metrics


def create_sample_data():
    """Create sample fund data for demonstration purposes."""
    sample_dir = Path("sample_funds")
    sample_dir.mkdir(exist_ok=True)

    # Create sample fund data
    dates = pd.date_range("2020-01-01", periods=100, freq="ME")

    # Fund A - Growth fund
    fund_a_nav = (
        100 * (1 + pd.Series([0.01, 0.02, -0.005, 0.015, 0.008] * 20)).cumprod()
    )
    fund_a = pd.DataFrame({"Date": dates, "NAV": fund_a_nav})
    fund_a.to_csv(sample_dir / "growth_fund.csv", index=False)

    # Fund B - Value fund
    fund_b_nav = (
        100 * (1 + pd.Series([0.008, 0.012, -0.003, 0.01, 0.006] * 20)).cumprod()
    )
    fund_b = pd.DataFrame({"Date": dates, "NAV": fund_b_nav})
    fund_b.to_csv(sample_dir / "value_fund.csv", index=False)

    # Fund C - Balanced fund
    fund_c_nav = (
        100 * (1 + pd.Series([0.006, 0.009, -0.002, 0.007, 0.005] * 20)).cumprod()
    )
    fund_c = pd.DataFrame({"Date": dates, "NAV": fund_c_nav})
    fund_c.to_csv(sample_dir / "balanced_fund.csv", index=False)

    logger.debug(f"✅ Created sample data in {sample_dir}")
    return sample_dir


def load_fund_data(data_dir: Path) -> dict[str, pd.DataFrame]:
    """
    Load fund data from CSV files in the specified directory.

    Args:
        data_dir: Directory containing CSV files

    Returns:
        Dictionary mapping fund names to DataFrames
    """
    fund_data = {}

    if not data_dir.exists():
        logger.debug(f"❌ Data directory {data_dir} does not exist")
        return fund_data

    csv_files = list(data_dir.glob("*.csv"))

    if not csv_files:
        logger.debug(f"❌ No CSV files found in {data_dir}")
        return fund_data

    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            fund_name = csv_file.stem  # filename without extension
            fund_data[fund_name] = df
            logger.debug(
                f"✅ Loaded {fund_name}: {len(df)} rows, {len(df.columns)} columns"
            )
        except Exception as e:
            logger.debug(f"❌ Error loading {csv_file}: {e}")

    return fund_data


def generate_reports(
    fund_data: dict[str, pd.DataFrame], output_dir: Path, simple: bool = False
):
    """
    Generate PDF and Excel reports from fund data.

    Args:
        fund_data: Dictionary of fund DataFrames
        output_dir: Directory to save reports
        simple: Whether to use simple rendering (fallback)
    """
    if not fund_data:
        logger.debug("❌ No fund data available for analysis")
        return

    # Calculate portfolio metrics
    logger.debug("📊 Calculating portfolio metrics...")
    try:
        metrics_df = calc_portfolio_metrics(fund_data)

        if metrics_df.empty:
            logger.debug("❌ Unable to calculate portfolio metrics")
            return

        logger.debug("✅ Portfolio metrics calculated successfully")

        # Display key metrics
        if not metrics_df.empty:
            metrics = metrics_df.iloc[0]
            logger.debug("\n📈 Key Portfolio Metrics:")
            logger.debug(f"  • Total NAV: ${metrics.get('Total NAV', 0):,.2f}")
            logger.debug(f"  • Funds: {int(metrics.get('Funds', 0))}")
            logger.debug(
                f"  • Annualized Return: {metrics.get('Annualized Return', 0):.2%}"
            )
            logger.debug(f"  • Volatility: {metrics.get('Volatility', 0):.2%}")
            logger.debug(f"  • Sharpe Ratio: {metrics.get('Sharpe (rf=0)', 0):.3f}")
            logger.debug(f"  • Max Drawdown: {metrics.get('Max Drawdown', 0):.2%}")

    except Exception as e:
        logger.debug(f"❌ Error calculating metrics: {e}")
        return

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

    # Generate PDF report
    pdf_path = output_dir / f"Portfolio_Report_{timestamp}.pdf"
    logger.debug(f"📄 Generating PDF report: {pdf_path}")

    try:
        if simple:
            render_simple_pdf(metrics_df, pdf_path)
        else:
            render_pdf(metrics_df, pdf_path)
        logger.debug(f"✅ PDF report saved: {pdf_path}")
    except Exception as e:
        logger.debug(f"❌ Error generating PDF: {e}")
        # Try simple fallback
        try:
            render_simple_pdf(metrics_df, pdf_path)
            logger.debug(f"✅ PDF report saved (simple format): {pdf_path}")
        except Exception as e2:
            logger.debug(f"❌ Error with simple PDF: {e2}")

    # Generate Excel report
    xlsx_path = output_dir / f"Portfolio_Report_{timestamp}.xlsx"
    logger.debug(f"📊 Generating Excel report: {xlsx_path}")

    try:
        if simple:
            render_simple_xlsx(metrics_df, xlsx_path)
        else:
            render_xlsx(metrics_df, xlsx_path)
        logger.debug(f"✅ Excel report saved: {xlsx_path}")
    except Exception as e:
        logger.debug(f"❌ Error generating Excel: {e}")
        # Try simple fallback
        try:
            render_simple_xlsx(metrics_df, xlsx_path)
            logger.debug(f"✅ Excel report saved (simple format): {xlsx_path}")
        except Exception as e2:
            logger.debug(f"❌ Error with simple Excel: {e2}")

    logger.debug("\n🎉 Reports generated successfully!")
    logger.debug(f"📁 Output directory: {output_dir.absolute()}")

    return pdf_path, xlsx_path


def main():
    """Main function to run the report builder."""
    parser = argparse.ArgumentParser(
        description="Generate portfolio analytics reports from fund data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/build_report.py                    # Use sample data
  python scripts/build_report.py --data my_funds/   # Use custom data directory
  python scripts/build_report.py --simple           # Use simple rendering
  python scripts/build_report.py --create-sample    # Create sample data only
        """,
    )

    parser.add_argument(
        "--data",
        "-d",
        type=Path,
        default=Path("sample_funds"),
        help="Directory containing fund CSV files (default: sample_funds)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("reports"),
        help="Output directory for reports (default: reports)",
    )

    parser.add_argument(
        "--simple",
        "-s",
        action="store_true",
        help="Use simple rendering (fallback for compatibility)",
    )

    parser.add_argument(
        "--create-sample", action="store_true", help="Create sample data and exit"
    )

    args = parser.parse_args()

    logger.debug("🚀 Portfolio Analytics Report Builder")
    logger.debug("=" * 50)

    # Create sample data if requested
    if args.create_sample:
        create_sample_data()
        return

    # Create sample data if data directory doesn't exist
    if not args.data.exists():
        logger.debug(
            f"📁 Data directory {args.data} not found. Creating sample data..."
        )
        sample_dir = create_sample_data()
        args.data = sample_dir

    # Load fund data
    logger.debug(f"📂 Loading fund data from: {args.data}")
    fund_data = load_fund_data(args.data)

    if not fund_data:
        logger.debug("❌ No fund data loaded. Exiting.")
        sys.exit(1)

    # Generate reports
    logger.debug(f"📊 Generating reports to: {args.output}")
    generate_reports(fund_data, args.output, simple=args.simple)


if __name__ == "__main__":
    main()
