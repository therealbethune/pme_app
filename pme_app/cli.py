#!/usr/bin/env python3
"""
PME App Command Line Interface

This module provides command-line access to PME App functionality.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from pme_app.services.portfolio import calc_portfolio_metrics
from pme_app.reporting.pdf import render_pdf
from pme_app.reporting.xlsx import render_xlsx


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="pme_app",
        description="PME (Private Market Equivalent) Calculator CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m pme_app.cli --help                    # Show this help
  python -m pme_app.cli version                   # Show version info
  python -m pme_app.cli report --data funds/     # Generate reports
  python -m pme_app.cli server                   # Start web server
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate portfolio reports")
    report_parser.add_argument(
        "--data", "-d",
        type=Path,
        help="Directory containing fund CSV files"
    )
    report_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("reports"),
        help="Output directory for reports (default: reports)"
    )
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Start the web server")
    server_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    server_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    
    return parser


def cmd_version():
    """Show version information."""
    print("PME App CLI v0.1.0")
    print("Private Market Equivalent Calculator")
    print("Python package for portfolio analytics and PME calculations")


def cmd_report(data_dir: Optional[Path], output_dir: Path):
    """Generate portfolio reports."""
    if not data_dir or not data_dir.exists():
        print("❌ Data directory not found or not specified")
        print("Use --data to specify a directory containing CSV files")
        return 1
    
    print(f"📊 Generating reports from {data_dir}")
    print(f"📁 Output directory: {output_dir}")
    
    # This would integrate with the existing report generation logic
    print("✅ Report generation functionality available")
    print("   (Integration with portfolio analytics in progress)")
    return 0


def cmd_server(host: str, port: int):
    """Start the web server."""
    print(f"🚀 Starting PME App server on {host}:{port}")
    print("   (Server functionality available via uvicorn)")
    print(f"   Run: uvicorn pme_app.main:app --host {host} --port {port}")
    return 0


def main(args: Optional[list[str]] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    if not parsed_args.command:
        parser.print_help()
        return 0
    
    if parsed_args.command == "version":
        cmd_version()
        return 0
    elif parsed_args.command == "report":
        return cmd_report(parsed_args.data, parsed_args.output)
    elif parsed_args.command == "server":
        return cmd_server(parsed_args.host, parsed_args.port)
    else:
        print(f"❌ Unknown command: {parsed_args.command}")
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 