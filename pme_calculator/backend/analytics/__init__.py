"""
Analytics package for high-performance PME calculations.
"""

from .service import VectorizedAnalytics, process_portfolio_analytics

__all__ = ["VectorizedAnalytics", "process_portfolio_analytics"]
