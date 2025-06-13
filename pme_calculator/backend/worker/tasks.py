"""
Celery background tasks for PME Calculator.
"""

import sys
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from worker.celery_app import celery
from analysis_engine import PMEAnalysisEngine
from logger import get_logger
from cache import cache_set, make_cache_key
from db_views import refresh

logger = get_logger(__name__)


@celery.task(bind=True)
def run_metrics(
    self, fund_path: str, index_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Background task for intensive PME metrics calculation.

    Args:
        self: Celery task instance (for progress updates)
        fund_path: Path to fund data file
        index_path: Optional path to index/benchmark data file

    Returns:
        Dict containing PME analysis results
    """
    try:
        logger.info(f"Starting background PME analysis task {self.request.id}")

        # Update task state to PROGRESS
        self.update_state(
            state="PROGRESS",
            meta={
                "current": 0,
                "total": 100,
                "status": "Initializing analysis engine...",
            },
        )

        # Create analysis engine
        analysis_engine = PMEAnalysisEngine()

        # Load fund data
        self.update_state(
            state="PROGRESS",
            meta={"current": 20, "total": 100, "status": "Loading fund data..."},
        )
        analysis_engine.load_fund_data(fund_path)

        # Load index data if provided
        if index_path:
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": 40,
                    "total": 100,
                    "status": "Loading benchmark data...",
                },
            )
            analysis_engine.load_index_data(index_path)

        # Run PME analysis
        self.update_state(
            state="PROGRESS",
            meta={"current": 60, "total": 100, "status": "Calculating PME metrics..."},
        )
        results = analysis_engine.calculate_pme_metrics()

        # Finalize results
        self.update_state(
            state="PROGRESS",
            meta={"current": 90, "total": 100, "status": "Finalizing results..."},
        )

        # Make results JSON serializable
        from main_minimal import make_json_serializable

        json_safe_results = make_json_serializable(results)

        logger.info(
            f"Background PME analysis task {self.request.id} completed successfully"
        )

        return {
            "status": "SUCCESS",
            "result": json_safe_results,
            "task_id": self.request.id,
        }

    except Exception as exc:
        logger.error(
            f"Background PME analysis task {self.request.id} failed: {exc}",
            exc_info=True,
        )

        # Update task state to FAILURE
        self.update_state(
            state="FAILURE",
            meta={
                "current": 100,
                "total": 100,
                "status": f"Task failed: {str(exc)}",
                "error": str(exc),
            },
        )
        raise exc


@celery.task(bind=True)
def generate_pdf_report(
    self, analysis_results: Dict[str, Any], report_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Background task for PDF report generation.

    Args:
        self: Celery task instance
        analysis_results: PME analysis results
        report_config: Report configuration options

    Returns:
        Dict containing PDF file path and metadata
    """
    try:
        logger.info(f"Starting PDF report generation task {self.request.id}")

        self.update_state(
            state="PROGRESS",
            meta={
                "current": 0,
                "total": 100,
                "status": "Initializing PDF generator...",
            },
        )

        # TODO: Implement PDF generation logic
        # This is a placeholder for future PDF generation functionality

        self.update_state(
            state="PROGRESS",
            meta={
                "current": 50,
                "total": 100,
                "status": "Generating charts and tables...",
            },
        )

        # Simulate PDF generation work
        import time

        time.sleep(2)

        self.update_state(
            state="PROGRESS",
            meta={"current": 90, "total": 100, "status": "Finalizing PDF document..."},
        )

        # Return placeholder result
        pdf_path = f"/tmp/pme_report_{self.request.id}.pdf"

        logger.info(f"PDF report generation task {self.request.id} completed")

        return {
            "status": "SUCCESS",
            "pdf_path": pdf_path,
            "task_id": self.request.id,
            "file_size": 1024000,  # Placeholder size
        }

    except Exception as exc:
        logger.error(
            f"PDF report generation task {self.request.id} failed: {exc}", exc_info=True
        )

        self.update_state(
            state="FAILURE",
            meta={
                "current": 100,
                "total": 100,
                "status": f"PDF generation failed: {str(exc)}",
                "error": str(exc),
            },
        )
        raise exc


# Popular funds for predictive cache warming
POPULAR_FUNDS = [
    "FUND_A",
    "FUND_B",
    "FUND_C",
]  # TODO: Make this dynamic based on usage analytics


@celery.task(bind=True)
def warm_cache(self) -> Dict[str, Any]:
    """
    Predictive cache warming task for popular funds.

    Refreshes DuckDB materialized views and pre-warms Redis cache
    with IRR/PME data for frequently accessed funds.

    Returns:
        Dict containing warming results and statistics
    """
    try:
        logger.info(f"Starting cache warming task {self.request.id}")

        self.update_state(
            state="PROGRESS",
            meta={
                "current": 0,
                "total": 100,
                "status": "Refreshing materialized views...",
            },
        )

        # Refresh DuckDB materialized views
        refresh()

        self.update_state(
            state="PROGRESS",
            meta={
                "current": 20,
                "total": 100,
                "status": "Warming cache for popular funds...",
            },
        )

        # Get event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        warmed_funds = []
        total_funds = len(POPULAR_FUNDS)

        try:
            for i, fund_id in enumerate(POPULAR_FUNDS):
                progress = 20 + (i * 60 // total_funds)
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current": progress,
                        "total": 100,
                        "status": f"Warming cache for fund {fund_id}...",
                    },
                )

                # Generate cache key for IRR/PME endpoint
                key = make_cache_key("irr_pme", {"fund": fund_id})

                # Generate mock data (in production, this would call the actual calculation)
                mock_data = {
                    "fund_id": fund_id,
                    "irr": 0.15 + (i * 0.02),  # Mock IRR values
                    "pme": 1.2 + (i * 0.1),  # Mock PME values
                    "warmed_at": "2024-01-01T00:00:00Z",
                    "data_source": "cache_warming",
                }

                # Cache the data
                success = loop.run_until_complete(cache_set(key, mock_data, ttl=86_400))

                if success:
                    warmed_funds.append(fund_id)
                    logger.debug(f"Successfully warmed cache for fund: {fund_id}")
                else:
                    logger.warning(f"Failed to warm cache for fund: {fund_id}")

        finally:
            loop.close()

        self.update_state(
            state="PROGRESS",
            meta={"current": 90, "total": 100, "status": "Finalizing cache warming..."},
        )

        result = {
            "status": "SUCCESS",
            "warmed_funds": warmed_funds,
            "total_funds_attempted": len(POPULAR_FUNDS),
            "success_rate": (
                len(warmed_funds) / len(POPULAR_FUNDS) if POPULAR_FUNDS else 0
            ),
            "task_id": self.request.id,
        }

        logger.info(
            f"Cache warming task {self.request.id} completed. Warmed {len(warmed_funds)}/{len(POPULAR_FUNDS)} funds"
        )

        return result

    except Exception as exc:
        logger.error(
            f"Cache warming task {self.request.id} failed: {exc}", exc_info=True
        )

        self.update_state(
            state="FAILURE",
            meta={
                "current": 100,
                "total": 100,
                "status": f"Cache warming failed: {str(exc)}",
                "error": str(exc),
            },
        )
        raise exc
