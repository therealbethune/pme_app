# Phase 1: DataAlignmentEngine for PME calculations

import polars as pl
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union, Literal
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

AlignmentStrategy = Literal["forward_fill", "backward_fill", "interpolate", "drop", "zero_fill"]

class DataAlignmentEngine:
    def __init__(self, missing_strategy: AlignmentStrategy = "forward_fill"):
        self.missing_strategy = missing_strategy
        
    def align_fund_and_index(self, fund_data, index_data, 
                           fund_date_col="date", fund_value_col="cashflow",
                           index_date_col="date", index_value_col="value"):
        # Convert to Polars
        if isinstance(fund_data, pd.DataFrame):
            fund_pl = pl.from_pandas(fund_data)
        else:
            fund_pl = fund_data.clone()
            
        if isinstance(index_data, pd.DataFrame):
            index_pl = pl.from_pandas(index_data)
        else:
            index_pl = index_data.clone()
        
        # Standardize columns
        fund_pl = fund_pl.select([
            pl.col(fund_date_col).str.strptime(pl.Date, format="%Y-%m-%d", strict=False).alias("date"),
            pl.col(fund_value_col).cast(pl.Float64).alias("value")
        ]).unique(subset=["date"]).sort("date")
        
        index_pl = index_pl.select([
            pl.col(index_date_col).str.strptime(pl.Date, format="%Y-%m-%d", strict=False).alias("date"),
            pl.col(index_value_col).cast(pl.Float64).alias("value")
        ]).unique(subset=["date"]).sort("date")
        
        # Create date range
        fund_dates = fund_pl.select("date").to_series().to_list()
        index_dates = index_pl.select("date").to_series().to_list()
        
        min_date = min(min(fund_dates), min(index_dates))
        max_date = max(max(fund_dates), max(index_dates))
        
        date_range = pl.date_range(min_date, max_date, interval="1d", eager=True).to_list()
        business_days = [d for d in date_range if d.weekday() < 5]
        
        # Align to common date range
        date_df = pl.DataFrame({"date": business_days})
        
        fund_aligned = date_df.join(fund_pl, on="date", how="left")
        index_aligned = date_df.join(index_pl, on="date", how="left")
        
        # Handle missing values
        if self.missing_strategy == "forward_fill":
            fund_aligned = fund_aligned.with_columns(pl.col("value").forward_fill())
            index_aligned = index_aligned.with_columns(pl.col("value").forward_fill())
        elif self.missing_strategy == "zero_fill":
            fund_aligned = fund_aligned.with_columns(pl.col("value").fill_null(0.0))
            index_aligned = index_aligned.with_columns(pl.col("value").fill_null(0.0))
        
        # Rename columns
        fund_aligned = fund_aligned.rename({"value": "fund_value"})
        index_aligned = index_aligned.rename({"value": "index_value"})
        
        return fund_aligned, index_aligned
    
    def get_alignment_summary(self, fund_df, index_df):
        return {
            "total_dates": len(fund_df),
            "date_range": {
                "start": fund_df.select(pl.col("date").min()).item(),
                "end": fund_df.select(pl.col("date").max()).item()
            }
        } 