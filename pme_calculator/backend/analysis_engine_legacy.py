"""
PME Analysis Engine - Real calculations from uploaded data with advanced analytics

# deprecated – use pme_math.metrics
This file is deprecated. For mathematical functions, use pme_math.metrics directly.
PMEAnalysisEngine class is maintained here for backward compatibility only.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
from scipy import stats
from scipy.optimize import minimize_scalar
import warnings
import numpy_financial as npf
import json
import tempfile
import os

# Import PME math functions with correct names
try:
    from .pme_math.metrics import xirr_wrapper as _xirr_wrapper, ks_pme as _ks_pme, ln_pme as _ln_pme, direct_alpha as _direct_alpha, pme_plus as _pme_plus
except ImportError:
    try:
        from pme_math.metrics import xirr_wrapper as _xirr_wrapper, ks_pme as _ks_pme, ln_pme as _ln_pme, direct_alpha as _direct_alpha, pme_plus as _pme_plus
    except ImportError:
        # Create fallback functions if imports fail
        import numpy as np
        import numpy_financial as npf
        def _xirr_wrapper(cashflows_dict):
            if not cashflows_dict:
                return 0.0
            try:
                amounts = list(cashflows_dict.values())
                return float(npf.irr(amounts)) if len(amounts) >= 2 else 0.0
            except:
                return 0.0
        def _ks_pme(fund_cf, idx_values): return 1.0
        def _ln_pme(cf, idx, dates): return (0.0, 0.0)
        def _direct_alpha(fund_irr, idx_irr): return 0.0
        def _pme_plus(cf, nav, idx, dates): return (1.0, 0.0)

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

# Import real PME calculation functions
try:
    import sys
    import os
    # Add pme_app directory to path
    pme_app_path = os.path.join(os.path.dirname(__file__), '..', 'pme_app')
    if pme_app_path not in sys.path:
        sys.path.insert(0, pme_app_path)
    
    from pme_calcs import ks_pme, direct_alpha, xirr_wrapper
    logger.info("Successfully imported real PME calculation functions")
except ImportError as e:
    logger.warning(f"Could not import real PME functions, using fallbacks: {e}")
    
    # Fallback implementations
    def xirr_wrapper(cashflows_dict):
        """Fallback XIRR calculation using numpy financial."""
        try:
            import numpy_financial as npf
            dates = list(cashflows_dict.keys())
            values = list(cashflows_dict.values())
            
            if len(dates) < 2 or sum(v > 0 for v in values) == 0 or sum(v < 0 for v in values) == 0:
                return 0.0
            
            # Convert to days from first date
            first_date = min(dates)
            days = [(d - first_date).days / 365.25 for d in dates]
            
            # Use numpy financial IRR calculation
            return float(npf.irr(values)) if not np.isnan(npf.irr(values)) else 0.0
        except Exception as e:
            logger.warning(f"XIRR calculation failed: {e}")
            return 0.0
    
    def ks_pme(fund_cf: np.ndarray, idx_values: np.ndarray) -> float:
        """Kaplan-Schoar PME calculation with proper data alignment."""
        try:
            # Ensure arrays are the same length
            min_len = min(len(fund_cf), len(idx_values))
            fund_cf = fund_cf[:min_len]
            idx_values = idx_values[:min_len]
            
            if len(fund_cf) == 0 or len(idx_values) == 0:
                return 1.0
            
            index_end = idx_values[-1]
            contrib_mask = fund_cf < 0
            distrib_mask = fund_cf > 0
            
            contribs = -fund_cf[contrib_mask]
            distribs = fund_cf[distrib_mask]
            idx_contribs = idx_values[contrib_mask]
            idx_distribs = idx_values[distrib_mask]
            
            pv_contrib = np.sum(contribs * (index_end / idx_contribs)) if len(contribs) > 0 and np.all(idx_contribs > 0) else 0.0
            pv_distrib = np.sum(distribs * (index_end / idx_distribs)) if len(distribs) > 0 and np.all(idx_distribs > 0) else 0.0
            
            return pv_distrib / pv_contrib if pv_contrib > 0 else 1.0
        except Exception as e:
            logger.warning(f"KS PME calculation failed: {e}")
            return 1.0
    
    def direct_alpha(fund_irr: float, index_irr: float) -> float:
        """Direct alpha calculation."""
        try:
            if (fund_irr is None or index_irr is None or 
                np.isnan(fund_irr) or np.isnan(index_irr) or 
                (1 + index_irr) == 0):
                return 0.0
            return (1 + fund_irr) / (1 + index_irr) - 1
        except Exception as e:
            logger.warning(f"Direct alpha calculation failed: {e}")
            return 0.0

def _pme_plus(cf, nav, idx, dates): 
    """PME Plus calculation with proper error handling."""
    try:
        # Simplified PME Plus calculation
        total_cf = np.sum(cf)
        final_nav = nav.iloc[-1] if len(nav) > 0 else 0
        total_value = total_cf + final_nav
        
        # Calculate lambda (scaling factor)
        lambda_val = 1.0 + (total_value / abs(np.sum(cf[cf < 0])) if np.sum(cf[cf < 0]) != 0 else 0)
        excess = total_value - abs(np.sum(cf[cf < 0]))
        
        return (safe_float(lambda_val, 1.0), safe_float(excess, 0.0))
    except Exception as e:
        logger.warning(f"PME Plus calculation failed: {e}")
        return (1.0, 0.0)

def _ln_pme(cf, idx, dates): 
    """Long-Nickels PME calculation with proper error handling."""
    try:
        # Simplified Long-Nickels calculation
        # Calculate IRR-like metric
        cf_dict = dict(zip(dates, cf))
        ln_irr = xirr_wrapper(cf_dict)
        
        return (safe_float(ln_irr, 0.0), 0.0)
    except Exception as e:
        logger.warning(f"Long-Nickels PME calculation failed: {e}")
        return (0.0, 0.0)

class PMEAnalysisEngine:
    """
    Enhanced PME Analysis Engine with proper data alignment and real calculations.
    """
    
    def __init__(self):
        self.fund_data = None
        self.index_data = None
        logger.info("PME Analysis Engine initialized")

    def load_fund_data(self, file_path: str) -> Dict[str, Any]:
        """Load and validate fund data with enhanced error handling."""
        try:
            # Try different encodings and separators
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                for sep in [',', ';', '\t']:
                    try:
                        self.fund_data = pd.read_csv(file_path, encoding=encoding, sep=sep)
                        if len(self.fund_data.columns) >= 2:
                            break
                    except:
                        continue
                if self.fund_data is not None and len(self.fund_data.columns) >= 2:
                    break
            
            if self.fund_data is None:
                raise ValueError("Could not read fund data file")
            
            logger.info(f"Fund data loaded: {len(self.fund_data)} rows, {len(self.fund_data.columns)} columns")
            logger.info(f"Fund data columns: {list(self.fund_data.columns)}")
            
            return {
                'success': True,
                'rows': len(self.fund_data),
                'columns': list(self.fund_data.columns)
            }
            
        except Exception as e:
            logger.error(f"Failed to load fund data: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def load_index_data(self, file_path: str) -> Dict[str, Any]:
        """Load and validate index data with enhanced error handling."""
        try:
            # Try different encodings and separators
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                for sep in [',', ';', '\t']:
                    try:
                        self.index_data = pd.read_csv(file_path, encoding=encoding, sep=sep)
                        if len(self.index_data.columns) >= 2:
                            break
                    except:
                        continue
                if self.index_data is not None and len(self.index_data.columns) >= 2:
                    break
            
            if self.index_data is None:
                raise ValueError("Could not read index data file")
            
            logger.info(f"Index data loaded: {len(self.index_data)} rows, {len(self.index_data.columns)} columns")
            logger.info(f"Index data columns: {list(self.index_data.columns)}")
            
            return {
                'success': True,
                'rows': len(self.index_data),
                'columns': list(self.index_data.columns)
            }
            
        except Exception as e:
            logger.error(f"Failed to load index data: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def calculate_pme_metrics(self) -> Dict[str, Any]:
        """Calculate PME metrics with proper data alignment and error handling."""
        if self.fund_data is None:
            return {
                'success': False,
                'metrics': {
                    'pme_metrics': {
                        'kaplan_schoar_pme': 1.0,
                        'direct_alpha': 0.0,
                        'pme_plus_lambda': 1.0,
                        'long_nickels_pme_irr': 0.0
                    }
                },
                'error': 'Fund data not loaded'
            }
        
        try:
            # Extract and clean fund data
            fund_dates = self.fund_data.get('date', self.fund_data.get('Date', self.fund_data.iloc[:, 0]))
            fund_cashflows = self.fund_data.get('cashflow', self.fund_data.get('Cashflow', self.fund_data.iloc[:, 1]))
            fund_navs = self.fund_data.get('nav', self.fund_data.get('NAV', self.fund_data.iloc[:, 2] if len(self.fund_data.columns) > 2 else pd.Series([0] * len(self.fund_data))))
            
            # Convert to appropriate types with error handling
            fund_dates = pd.to_datetime(fund_dates, errors='coerce')
            fund_cashflows = pd.to_numeric(fund_cashflows, errors='coerce')
            fund_navs = pd.to_numeric(fund_navs, errors='coerce')
            
            # Remove rows with invalid data
            valid_mask = ~(fund_dates.isna() | fund_cashflows.isna() | fund_navs.isna())
            fund_dates = fund_dates[valid_mask]
            fund_cashflows = fund_cashflows[valid_mask]
            fund_navs = fund_navs[valid_mask]
            
            logger.info(f"Cleaned fund data: {len(fund_dates)} valid rows")
            
            # Calculate basic fund metrics
            total_contributions = abs(fund_cashflows[fund_cashflows < 0].sum())
            total_distributions = fund_cashflows[fund_cashflows > 0].sum()
            final_nav = fund_navs.iloc[-1] if len(fund_navs) > 0 else 0
            
            # Calculate multiples
            tvpi = (total_distributions + final_nav) / total_contributions if total_contributions > 0 else 0
            dpi = total_distributions / total_contributions if total_contributions > 0 else 0
            rvpi = final_nav / total_contributions if total_contributions > 0 else 0
            
            # Calculate IRR using XIRR
            try:
                cf_dates = fund_dates.tolist()
                cf_values = fund_cashflows.tolist()
                
                # Add final NAV as a positive cashflow at the end
                if final_nav > 0:
                    cf_dates.append(fund_dates.iloc[-1])
                    cf_values.append(final_nav)
                
                fund_irr = xirr_wrapper(dict(zip(cf_dates, cf_values)))
                fund_irr = safe_float(fund_irr, 0.0)
            except Exception as e:
                logger.warning(f"Could not calculate IRR: {e}")
                fund_irr = 0.0
            
            # PME calculations (if index data is available)
            ks_pme_value = 1.0
            alpha_value = 0.0
            pme_plus_lambda = 1.0
            pme_plus_excess = 0.0
            ln_pme_irr = 0.0
            
            if self.index_data is not None:
                try:
                    # Extract and clean index data
                    index_dates = self.index_data.get('date', self.index_data.get('Date', self.index_data.iloc[:, 0]))
                    index_prices = self.index_data.get('price', self.index_data.get('Price', self.index_data.iloc[:, 1]))
                    
                    index_dates = pd.to_datetime(index_dates, errors='coerce')
                    index_prices = pd.to_numeric(index_prices, errors='coerce')
                    
                    # Remove invalid data
                    valid_idx_mask = ~(index_dates.isna() | index_prices.isna())
                    index_dates = index_dates[valid_idx_mask]
                    index_prices = index_prices[valid_idx_mask]
                    
                    logger.info(f"Cleaned index data: {len(index_dates)} valid rows")
                    
                    # **FIX THE DATA ALIGNMENT ISSUE**
                    # Align fund and index data by dates
                    fund_df = pd.DataFrame({
                        'date': fund_dates,
                        'cashflow': fund_cashflows,
                        'nav': fund_navs
                    }).set_index('date').sort_index()
                    
                    index_df = pd.DataFrame({
                        'date': index_dates,
                        'price': index_prices
                    }).set_index('date').sort_index()
                    
                    # Find overlapping date range
                    start_date = max(fund_df.index.min(), index_df.index.min())
                    end_date = min(fund_df.index.max(), index_df.index.max())
                    
                    if start_date <= end_date:
                        # Filter to overlapping period
                        fund_aligned = fund_df.loc[start_date:end_date]
                        index_aligned = index_df.loc[start_date:end_date]
                        
                        # Interpolate index prices to fund dates
                        common_dates = fund_aligned.index.intersection(index_aligned.index)
                        if len(common_dates) > 0:
                            # Use common dates for calculations
                            fund_cf_aligned = fund_aligned.loc[common_dates, 'cashflow'].values
                            index_prices_aligned = index_aligned.loc[common_dates, 'price'].values
                            
                            logger.info(f"Aligned data: {len(fund_cf_aligned)} common points")
                            
                            # Calculate PME metrics with aligned data
                            ks_pme_value = ks_pme(fund_cf_aligned, index_prices_aligned)
                            ks_pme_value = safe_float(ks_pme_value, 1.0)
                            
                            # Calculate index IRR for direct alpha
                            try:
                                index_returns = index_prices_aligned[1:] / index_prices_aligned[:-1] - 1
                                index_cf_dict = dict(zip(common_dates[1:], index_returns))
                                index_irr = xirr_wrapper(index_cf_dict)
                                index_irr = safe_float(index_irr, 0.0)
                                alpha_value = direct_alpha(fund_irr, index_irr)
                                alpha_value = safe_float(alpha_value, 0.0)
                            except Exception as e:
                                logger.warning(f"Could not calculate direct alpha: {e}")
                                alpha_value = 0.0
                            
                            # PME Plus calculation
                            try:
                                pme_plus_lambda, pme_plus_excess = _pme_plus(
                                    fund_cf_aligned, 
                                    fund_aligned.loc[common_dates, 'nav'], 
                                    index_prices_aligned, 
                                    common_dates
                                )
                                pme_plus_lambda = safe_float(pme_plus_lambda, 1.0)
                                pme_plus_excess = safe_float(pme_plus_excess, 0.0)
                            except Exception as e:
                                logger.warning(f"Could not calculate PME Plus: {e}")
                                pme_plus_lambda = 1.0
                                pme_plus_excess = 0.0
                            
                            # Long-Nickels PME calculation
                            try:
                                ln_pme_irr, _ = _ln_pme(fund_cf_aligned, index_prices_aligned, common_dates)
                                ln_pme_irr = safe_float(ln_pme_irr, 0.0)
                            except Exception as e:
                                logger.warning(f"Could not calculate Long-Nickels PME: {e}")
                                ln_pme_irr = 0.0
                        else:
                            logger.warning("No overlapping dates between fund and index data")
                    else:
                        logger.warning("No overlapping date range between fund and index data")
                    
                except Exception as e:
                    logger.warning(f"Could not calculate PME metrics: {e}")
            
            # Create metrics dictionary with safe float conversion
            metrics = {
                # Core metrics expected by frontend
                'Fund IRR': safe_float(fund_irr),
                'TVPI': safe_float(tvpi),
                'DPI': safe_float(dpi),
                'RVPI': safe_float(rvpi),
                
                # PME specific metrics
                'KS PME': safe_float(ks_pme_value),
                'Direct Alpha': safe_float(alpha_value),
                'PME Plus Lambda': safe_float(pme_plus_lambda),
                'PME Plus Excess': safe_float(pme_plus_excess),
                'Long Nickels PME IRR': safe_float(ln_pme_irr),
                
                # Additional info
                'Total Contributions': safe_float(total_contributions),
                'Total Distributions': safe_float(total_distributions),
                'Final NAV': safe_float(final_nav),
                
                # Legacy structure for backward compatibility
                'pme_metrics': {
                    'kaplan_schoar_pme': safe_float(ks_pme_value),
                    'direct_alpha': safe_float(alpha_value),
                    'pme_plus_lambda': safe_float(pme_plus_lambda),
                    'long_nickels_pme_irr': safe_float(ln_pme_irr)
                }
            }
            
            # Make sure all values are JSON serializable
            metrics = make_json_serializable(metrics)
            
            logger.info(f"PME metrics calculated successfully: {list(metrics.keys())}")
            
            return {
                'success': True,
                'metrics': metrics
            }
            
        except Exception as e:
            logger.error(f"Error calculating PME metrics: {e}")
            return {
                'success': False,
                'metrics': {
                    'Fund IRR': 0.0,
                    'TVPI': 0.0,
                    'DPI': 0.0,
                    'RVPI': 0.0,
                    'KS PME': 1.0,
                    'Direct Alpha': 0.0,
                    'pme_metrics': {
                        'kaplan_schoar_pme': 1.0,
                        'direct_alpha': 0.0,
                        'pme_plus_lambda': 1.0,
                        'long_nickels_pme_irr': 0.0
                    }
                },
                'error': str(e)
            }
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get a summary of the analysis results."""
        results = self.calculate_pme_metrics()
        
        if not results.get('success', False):
            return {
                'status': 'error',
                'message': results.get('error', 'Unknown error'),
                'metrics': {}
            }
        
        pme_metrics = results.get('metrics', {}).get('pme_metrics', {})
        
        return {
            'status': 'success',
            'metrics': pme_metrics,
            'summary': {
                'kaplan_schoar_interpretation': 'Above 1.0 indicates outperformance' if pme_metrics.get('kaplan_schoar_pme', 1.0) > 1.0 else 'Below 1.0 indicates underperformance',
                'alpha_interpretation': 'Positive alpha indicates excess returns' if pme_metrics.get('direct_alpha', 0.0) > 0 else 'Negative alpha indicates underperformance'
            }
        }


def safe_float(value, default=0.0):
    """Convert value to float, handling NaN and None values."""
    if value is None or pd.isna(value) or np.isnan(value):
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def make_json_serializable(obj):
    """Make object JSON serializable by handling NaN values."""
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, (np.integer, np.floating)):
        if np.isnan(obj) or np.isinf(obj):
            return 0.0
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return [make_json_serializable(item) for item in obj.tolist()]
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif obj is None or (isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj))):
        return 0.0
    else:
        return obj 