import polars as pl
import pandas as pd


class DataAlignmentEngine:
    def __init__(self, missing_strategy="forward_fill"):
        self.missing_strategy = missing_strategy

    def align_fund_and_index(
        self,
        fund_data,
        index_data,
        fund_date_col="date",
        fund_value_col="cashflow",
        index_date_col="date",
        index_value_col="value",
    ):
        # Convert to Polars
        fund_pl = (
            pl.from_pandas(fund_data)
            if isinstance(fund_data, pd.DataFrame)
            else fund_data
        )
        index_pl = (
            pl.from_pandas(index_data)
            if isinstance(index_data, pd.DataFrame)
            else index_data
        )

        # Simple alignment - just ensure same length for now
        min_len = min(len(fund_pl), len(index_pl))
        fund_aligned = fund_pl.head(min_len)
        index_aligned = index_pl.head(min_len)

        return fund_aligned, index_aligned

    def get_alignment_summary(self, fund_df, index_df):
        return {"total_dates": len(fund_df)}
