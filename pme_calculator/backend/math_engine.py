"""
Math Engine - Mathematical utilities for PME calculations
Provides core mathematical functions used throughout the PME system.
"""

import numpy as np
import numpy_financial as npf
from scipy.optimize import brentq

# Try importing xirr_wrapper with relative import, fallback to creating our own
try:
    from .pme_math.metrics import xirr_wrapper
except ImportError:
    try:
        from pme_math.metrics import xirr_wrapper
    except ImportError:
        # Create a local xirr_wrapper if imports fail
        def xirr_wrapper(cashflows_dict):
            """Local fallback xirr wrapper."""
            if not cashflows_dict:
                return 0.0
            list(cashflows_dict.keys())
            amounts = list(cashflows_dict.values())
            if len(amounts) < 2:
                return 0.0
            try:
                # Simple IRR approximation
                return float(npf.irr(amounts))
            except (ValueError, FloatingPointError):
                return 0.0


class MathEngine:
    """Mathematical utilities for financial calculations."""

    @staticmethod
    def calculate_tvpi(contributions: float, distributions: float, nav: float) -> float:
        """
        Calculate Total Value to Paid-In ratio.

        Args:
            contributions: Total contributions (positive value)
            distributions: Total distributions (positive value)
            nav: Current NAV (positive value)

        Returns:
            TVPI ratio
        """
        try:
            if contributions <= 0:
                return 0.0

            total_value = distributions + nav
            return float(total_value / contributions)

        except (ZeroDivisionError, ValueError, TypeError, OverflowError):
            return 0.0

    @staticmethod
    def calculate_dpi(contributions: float, distributions: float) -> float:
        """
        Calculate Distributions to Paid-In ratio.

        Args:
            contributions: Total contributions (positive value)
            distributions: Total distributions (positive value)

        Returns:
            DPI ratio
        """
        try:
            if contributions <= 0:
                return 0.0

            return float(distributions / contributions)

        except (ZeroDivisionError, ValueError, TypeError, OverflowError):
            return 0.0

    @staticmethod
    def calculate_rvpi(contributions: float, nav: float) -> float:
        """
        Calculate Residual Value to Paid-In ratio.

        Args:
            contributions: Total contributions (positive value)
            nav: Current NAV (positive value)

        Returns:
            RVPI ratio
        """
        try:
            if contributions <= 0:
                return 0.0

            return float(nav / contributions)

        except (ZeroDivisionError, ValueError, TypeError, OverflowError):
            return 0.0

    @staticmethod
    def calculate_time_weighted_return(
        values: list[float], cash_flows: list[float]
    ) -> float:
        """
        Calculate Time-Weighted Return.

        Args:
            values: List of period-end values
            cash_flows: List of cash flows for each period

        Returns:
            TWR as decimal
        """
        try:
            if len(values) != len(cash_flows) or len(values) < 2:
                return 0.0

            period_returns = []

            for i in range(1, len(values)):
                start_value = values[i - 1]
                end_value = values[i]
                cash_flow = cash_flows[i]

                if start_value <= 0:
                    continue

                # Calculate period return: (End Value - Cash Flow) / Start Value - 1
                period_return = (end_value - cash_flow) / start_value - 1
                period_returns.append(1 + period_return)

            if not period_returns:
                return 0.0

            # Compound the period returns
            cumulative_return = np.prod(period_returns) - 1

            return float(cumulative_return)

        except (ZeroDivisionError, ValueError, TypeError, OverflowError):
            return 0.0

    @staticmethod
    def calculate_sharpe_ratio(
        returns: list[float], risk_free_rate: float = 0.0
    ) -> float:
        """
        Calculate Sharpe Ratio.

        Args:
            returns: List of period returns
            risk_free_rate: Risk-free rate

        Returns:
            Sharpe ratio
        """
        try:
            if not returns or len(returns) < 2:
                return 0.0

            excess_returns = [r - risk_free_rate for r in returns]
            mean_excess = np.mean(excess_returns)
            std_excess = np.std(excess_returns, ddof=1)

            if std_excess <= 0:
                return 0.0

            return float(mean_excess / std_excess)

        except (ZeroDivisionError, ValueError, TypeError, OverflowError):
            return 0.0

    @staticmethod
    def calculate_volatility(returns: list[float], annualize: bool = True) -> float:
        """
        Calculate volatility (standard deviation of returns).

        Args:
            returns: List of period returns
            annualize: Whether to annualize the volatility

        Returns:
            Volatility as decimal
        """
        try:
            if not returns or len(returns) < 2:
                return 0.0

            volatility = np.std(returns, ddof=1)

            if annualize:
                # Assume monthly data, annualize with sqrt(12)
                volatility *= np.sqrt(12)

            return float(volatility)

        except (ValueError, TypeError, OverflowError):
            return 0.0

    @staticmethod
    def calculate_correlation(series1: list[float], series2: list[float]) -> float:
        """
        Calculate correlation between two series.

        Args:
            series1: First data series
            series2: Second data series

        Returns:
            Correlation coefficient
        """
        try:
            if len(series1) != len(series2) or len(series1) < 2:
                return 0.0

            correlation = np.corrcoef(series1, series2)[0, 1]

            if np.isnan(correlation):
                return 0.0

            return float(correlation)

        except (ValueError, TypeError, IndexError):
            return 0.0

    @staticmethod
    def calculate_drawdown(values: list[float]) -> tuple[float, int, int]:
        """
        Calculate maximum drawdown and its duration.

        Args:
            values: List of portfolio values over time

        Returns:
            Tuple of (max_drawdown, start_index, end_index)
        """
        try:
            if not values or len(values) < 2:
                return 0.0, 0, 0

            values = np.array(values)

            # Calculate running maximum
            peak = np.maximum.accumulate(values)

            # Calculate drawdown
            drawdown = (values - peak) / peak

            # Find maximum drawdown
            max_drawdown_idx = np.argmin(drawdown)
            max_drawdown = float(drawdown[max_drawdown_idx])

            # Find the peak before the max drawdown
            peak_idx = np.argmax(peak[: max_drawdown_idx + 1])

            return abs(max_drawdown), peak_idx, max_drawdown_idx

        except Exception:
            return 0.0, 0, 0

    @staticmethod
    def calculate_irr(cash_flows: list[float]) -> float:
        """
        Calculate Internal Rate of Return.

        Args:
            cash_flows: List of cash flows (negative for outflows, positive for inflows)

        Returns:
            IRR as decimal (e.g., 0.15 for 15%) or NaN for edge cases
        """
        try:
            if not cash_flows or len(cash_flows) < 2:
                raise ValueError("Need at least 2 cash flows for IRR calculation")

            # Check if all cash flows are positive or all negative
            positive_flows = sum(1 for cf in cash_flows if cf > 0)
            negative_flows = sum(1 for cf in cash_flows if cf < 0)

            if positive_flows == 0 or negative_flows == 0:
                return np.nan  # No sign changes, no meaningful IRR

            # Use numpy financial function for IRR calculation
            try:
                irr = npf.irr(cash_flows)
                if np.isnan(irr) or np.isinf(irr):
                    return np.nan
                return float(irr)
            except:
                # Fallback to scipy optimization
                try:
                    # NPV function for IRR calculation
                    def npv(rate):
                        return sum(
                            cf / (1 + rate) ** i for i, cf in enumerate(cash_flows)
                        )

                    # Find rate where NPV = 0
                    result = brentq(npv, -0.99, 10.0)
                    return float(result)
                except:
                    return np.nan

        except Exception:
            raise  # Re-raise exceptions for empty lists or single values

    @staticmethod
    def safe_divide(
        numerator: float, denominator: float, default: float = 0.0
    ) -> float:
        """
        Safely divide two numbers, returning default value for division by zero.

        Args:
            numerator: The dividend
            denominator: The divisor
            default: Default value to return if division by zero

        Returns:
            Result of division or default/NaN for edge cases
        """
        try:
            # Handle NaN inputs
            if np.isnan(numerator):
                return np.nan

            if denominator == 0 or np.isnan(denominator) or np.isinf(denominator):
                if numerator == 0:
                    return np.nan  # 0/0 case
                return default

            result = numerator / denominator

            if np.isnan(result) or np.isinf(result):
                return default

            return float(result)

        except Exception:
            return default


# Convenience functions for backward compatibility
def calculate_tvpi(contributions: float, distributions: float, nav: float) -> float:
    """Calculate TVPI using MathEngine."""
    return MathEngine.calculate_tvpi(contributions, distributions, nav)


def calculate_dpi(contributions: float, distributions: float) -> float:
    """Calculate DPI using MathEngine."""
    return MathEngine.calculate_dpi(contributions, distributions)


def calculate_rvpi(contributions: float, nav: float) -> float:
    """Calculate RVPI using MathEngine."""
    return MathEngine.calculate_rvpi(contributions, nav)
