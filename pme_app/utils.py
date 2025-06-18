# pme_app/utils.py
"""
Utility functions for data loading and processing in the PME Calculator.
"""

from pathlib import Path

import pandas as pd


def ensure_datetime_index(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """
    Ensure that a DataFrame uses a DatetimeIndex.
    - If the DataFrame already has a DatetimeIndex, simply drop any duplicate 'date' column.
    - If not, but a 'date' column exists, convert and set it as the index.
    - Otherwise, try to convert the index itself to datetime.
    Always returns a DataFrame sorted by date.
    """
    if df is None:
        raise ValueError("DataFrame is None; cannot ensure datetime index.")

    # If already a DatetimeIndex, just drop extra 'date' column if present
    if isinstance(df.index, pd.DatetimeIndex):
        if not df.index.is_monotonic_increasing:
            df = df.sort_index()
        df = df.drop(columns=[date_col], errors="ignore")
        return df

    # If 'date' column is present, use it as index
    if date_col in df.columns:
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col).set_index(date_col)
        return df

    # Otherwise, try converting the index to datetime
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df


def load_fund_file(path: str) -> pd.DataFrame:
    """
    Loads and standardizes a fund cash flow file (Excel/CSV).
    Returns a DataFrame with a DatetimeIndex and 'cashflow' and 'nav' columns.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path, engine="openpyxl")
    elif file_path.suffix.lower() == ".csv":
        df = pd.read_csv(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

    df = ensure_datetime_index(df)

    # Comprehensive column mapping for cashflow data
    cashflow_column_names = [
        # Standard variations
        "cashflow",
        "cash_flow",
        "cf",
        "cash flow",
        # Amount variations
        "cash_flow_amount",
        "cashflow_amount",
        "cf_amount",
        "cash flow amount",
        "amount",
        "flow_amount",
        "flow",
        # Capital variations
        "capital_flow",
        "capital flow",
        "capital_amount",
        "capital amount",
        # Net variations
        "net_cashflow",
        "net_cash_flow",
        "net cashflow",
        "net cash flow",
        "net_flow",
        "net flow",
        "net_amount",
        "net amount",
        # Investment variations
        "investment_flow",
        "investment flow",
        "investment_amount",
        "investment amount",
        "contributions_distributions",
        "contrib_distrib",
        "contrib/distrib",
        # Case variations
        "Cashflow",
        "CashFlow",
        "Cash_Flow",
        "CASHFLOW",
        "CASH_FLOW",
        "Cash Flow",
        "CASH FLOW",
        "CF",
        "cf",
        "Cash_Flow_Amount",
        "CASH_FLOW_AMOUNT",
        "CashFlowAmount",
        "Amount",
        "AMOUNT",
        "Flow",
        "FLOW",
    ]

    nav_column_names = [
        # Standard variations
        "nav",
        "NAV",
        "net_asset_value",
        "Net_Asset_Value",
        "net asset value",
        "Net Asset Value",
        "NET_ASSET_VALUE",
        "NET ASSET VALUE",
        # Value variations
        "value",
        "Value",
        "VALUE",
        "fund_value",
        "Fund_Value",
        "fund value",
        "Fund Value",
        "FUND_VALUE",
        "FUND VALUE",
        # Portfolio variations
        "portfolio_value",
        "Portfolio_Value",
        "portfolio value",
        "Portfolio Value",
        "PORTFOLIO_VALUE",
        "PORTFOLIO VALUE",
        # Asset variations
        "asset_value",
        "Asset_Value",
        "asset value",
        "Asset Value",
        "ASSET_VALUE",
        "ASSET VALUE",
        "total_value",
        "Total_Value",
    ]

    # Find cashflow column with more flexible matching
    cashflow_col = None
    normalized_cashflow_names = [
        name.strip().lower().replace("_", " ").replace("-", " ")
        for name in cashflow_column_names
    ]

    for col_name in df.columns:
        normalized_col = col_name.strip().lower().replace("_", " ").replace("-", " ")
        if normalized_col in normalized_cashflow_names:
            cashflow_col = col_name
            break

    if cashflow_col is None:
        available_cols = ", ".join(df.columns.tolist())
        suggestion = (
            "Common names include: cashflow, cash_flow_amount, cf, amount, capital_flow"
        )
        raise ValueError(
            f"Could not find a cashflow column in the file.\n"
            f"Available columns: {available_cols}\n"
            f"Expected cashflow column names: {suggestion}"
        )

    # Find NAV column with more flexible matching
    nav_col = None
    normalized_nav_names = [
        name.strip().lower().replace("_", " ").replace("-", " ")
        for name in nav_column_names
    ]

    for col_name in df.columns:
        normalized_col = col_name.strip().lower().replace("_", " ").replace("-", " ")
        if normalized_col in normalized_nav_names:
            nav_col = col_name
            break

    # Create standardized DataFrame
    result_df = pd.DataFrame(index=df.index)
    result_df["cashflow"] = pd.to_numeric(df[cashflow_col], errors="coerce")

    if nav_col is not None:
        result_df["nav"] = pd.to_numeric(df[nav_col], errors="coerce")
        print(
            f"[INFO] Successfully mapped '{cashflow_col}' → 'cashflow' and '{nav_col}' → 'nav'"
        )
    else:
        print("[WARNING] No NAV column found. Setting NAV to 0.0 for all entries.")
        print(f"[INFO] Successfully mapped '{cashflow_col}' → 'cashflow'")
        result_df["nav"] = 0.0

    # Handle missing values
    result_df["cashflow"] = result_df["cashflow"].fillna(0.0)
    result_df["nav"] = result_df["nav"].fillna(0.0)

    # Validate data
    if result_df["cashflow"].isna().all():
        raise ValueError(
            f"All cashflow values are invalid/non-numeric in column '{cashflow_col}'"
        )

    return result_df[["cashflow", "nav"]]


def load_index_file(path: str) -> pd.DataFrame:
    """
    Loads and standardizes a market index file (Excel/CSV).
    Returns a DataFrame with a DatetimeIndex and 'price' column.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path, engine="openpyxl")
    elif file_path.suffix.lower() == ".csv":
        df = pd.read_csv(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

    df = ensure_datetime_index(df)

    # Comprehensive column mapping for index/price data
    price_column_names = [
        # Standard price variations
        "price",
        "close",
        "adj close",
        "adjusted close",
        "close price",
        "closing price",
        "adj_close",
        "adjusted_close",
        "close_price",
        # Index variations
        "index",
        "index_level",
        "index_value",
        "index level",
        "index value",
        "level",
        "value",
        "index_price",
        "index price",
        # Market variations
        "market_value",
        "market value",
        "market_level",
        "market level",
        "market_price",
        "market price",
        "market_index",
        "market index",
        # Specific index names
        "sp500",
        "s&p500",
        "s&p 500",
        "sp_500",
        "sp 500",
        "nasdaq",
        "nasdaq_composite",
        "nasdaq composite",
        "djia",
        "dow",
        "dow_jones",
        "dow jones",
        "russell",
        "russell_2000",
        "russell 2000",
        "ftse",
        "dax",
        "nikkei",
        "msci",
        # Generic variations
        "benchmark",
        "benchmark_value",
        "benchmark value",
        "reference",
        "reference_value",
        "reference value",
        "performance",
        "performance_index",
        "performance index",
        # Trading variations
        "last",
        "last_price",
        "last price",
        "px_last",
        "px last",
        "settlement",
        "settlement_price",
        "settlement price",
        # Case variations
        "Price",
        "PRICE",
        "Close",
        "CLOSE",
        "Value",
        "VALUE",
        "Index",
        "INDEX",
        "Level",
        "LEVEL",
        "Index_Level",
        "INDEX_LEVEL",
        "Index_Value",
        "INDEX_VALUE",
        "Market_Value",
        "MARKET_VALUE",
        "Last",
        "LAST",
        "Settlement",
        "SETTLEMENT",
    ]

    # Find price/index column with flexible matching
    price_col = None
    normalized_price_names = [
        name.strip().lower().replace("_", " ").replace("-", " ")
        for name in price_column_names
    ]

    for col_name in df.columns:
        normalized_col = col_name.strip().lower().replace("_", " ").replace("-", " ")
        if normalized_col in normalized_price_names:
            price_col = col_name
            break

    if price_col is None:
        available_cols = ", ".join(df.columns.tolist())
        suggestion = (
            "Common names include: price, close, index_level, value, level, index_value"
        )
        raise ValueError(
            f"Could not find a price/index column in the file.\n"
            f"Available columns: {available_cols}\n"
            f"Expected price/index column names: {suggestion}"
        )

    # Create standardized DataFrame
    result_df = pd.DataFrame(index=df.index)
    result_df["price"] = pd.to_numeric(df[price_col], errors="coerce")

    print(f"[INFO] Successfully mapped '{price_col}' → 'price'")

    # Handle missing values
    result_df["price"] = result_df["price"].ffill()  # Forward fill for price data

    # Validate data
    if result_df["price"].isna().all():
        raise ValueError(
            f"All price values are invalid/non-numeric in column '{price_col}'"
        )

    if (result_df["price"] <= 0).any():
        print(
            f"[WARNING] Found non-positive price values in '{price_col}'. This may cause issues in calculations."
        )

    return result_df[["price"]]
