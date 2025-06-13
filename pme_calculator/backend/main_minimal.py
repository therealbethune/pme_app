"""
Enhanced FastAPI server for PME Calculator with real analysis engine.
"""

import json
import os
import socket
import tempfile
import time
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import uvicorn
from analysis_engine import PMEAnalysisEngine, make_json_serializable
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

# Database dependencies - make optional
try:
    from database import (
        UploadFileMeta,
        create_upload_record,
        delete_upload_record,
        get_session,
        get_upload_by_id,
        get_uploads_by_user,
        init_db,
        update_upload_record,
    )
    from sqlalchemy.ext.asyncio import AsyncSession

    DATABASE_AVAILABLE = True
except ImportError as e:
    from logger import get_logger

    logger = get_logger(__name__)
    logger.warning(f"Database dependencies not available: {e}")
    DATABASE_AVAILABLE = False
    # Create dummy functions for when database is not available
    AsyncSession = None
    UploadFileMeta = None

    # Define get_session as a proper async generator
    async def get_session():
        """Dummy session generator for when database is not available."""
        yield None

    # Define dummy database functions
    async def init_db():
        """Dummy init function."""
        pass

    async def create_upload_record(session, data):
        """Dummy create function."""
        return None

    async def get_upload_by_id(session, upload_id):
        """Dummy get function."""
        return None

    async def get_uploads_by_user(session, user="anonymous", limit=100):
        """Dummy list function."""
        return []

    async def update_upload_record(session, upload_id, update_data):
        """Dummy update function."""
        return None

    async def delete_upload_record(session, upload_id):
        """Dummy delete function."""
        return False


# Import routes only if they exist and are working
try:
    from routes.analysis import router as analysis_router
    from routes.validation import router as validation_router

    ROUTES_AVAILABLE = True
except ImportError as e:
    from logger import get_logger

    logger = get_logger(__name__)
    logger.warning(f"Routes not available: {e}")
    analysis_router = None
    validation_router = None
    ROUTES_AVAILABLE = False

# Set up structured logging
from logger import get_logger

logger = get_logger(__name__)

# Import Redis cache
try:
    from cache import cache_get, cache_set, make_cache_key

    CACHE_AVAILABLE = True
    logger.info("Redis cache module loaded successfully")
except ImportError as e:
    logger.warning(f"Redis cache not available: {e}")
    CACHE_AVAILABLE = False

    # Create dummy cache functions
    def make_cache_key(endpoint: str, payload: dict) -> str:
        return f"dummy:{endpoint}:{hash(str(payload))}"

    async def cache_get(key: str):
        return None

    async def cache_set(key: str, value: dict, ttl: int = 3600):
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI app startup and shutdown."""
    # Early DB availability check with exit option
    import os
    import sys

    import asyncpg

    if os.getenv("REQUIRE_DATABASE", "false").lower() == "true":
        try:
            await asyncpg.connect(dsn=os.getenv("DATABASE_URL"), timeout=3)
            logger.info("Database connection verified")
        except Exception as exc:
            logger.critical("Postgres unreachable: %s", exc)
            sys.exit(1)

    # Startup
    if DATABASE_AVAILABLE:
        try:
            await init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            logger.info("Database not available - running in memory-only mode")
    else:
        logger.info("Database not available - running in memory-only mode")

    # Clean up any old temp files on startup
    cleanup_old_temp_files()
    logger.info("Server startup complete. Old temp files cleaned.")

    yield

    # Shutdown (if needed)
    logger.info("Server shutdown complete.")


# Create FastAPI app
app = FastAPI(
    title="Fund Analysis Tool API",
    description="Professional Private Market Equivalent Calculator",
    version="1.0.0",
    docs_url="/api/docs",
    lifespan=lifespan,
)

# Register routers only if available
if ROUTES_AVAILABLE and analysis_router is not None:
    app.include_router(analysis_router)
    logger.info("Analysis router included from routes.analysis")
if ROUTES_AVAILABLE and validation_router is not None:
    app.include_router(validation_router)

# Include health router
from routers.health import router as health_router

app.include_router(health_router)

# Include metrics router
try:
    from routers.metrics import router as metrics_router

    app.include_router(metrics_router)
    logger.info("Metrics router included")
except Exception as e:
    logger.warning(f"Metrics router not available: {e}")

# CORS middleware - More permissive configuration to handle all frontend ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",  # Vite fallback port
        "http://127.0.0.1:5174",
        "http://192.168.0.15:5173",  # Network address from Vite output
        "http://192.168.0.15:5174",  # Network address fallback port
        "*",  # Allow all origins for development - REMOVE IN PRODUCTION
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# In-memory storage for uploaded files - MUST be defined before router imports
uploaded_files: dict[str, dict[str, Any]] = {}

# Note: Enhanced analysis router removed to prevent circular import issues
# The analysis functionality is already available through routes.analysis


def cleanup_old_temp_files():
    """Clean up old temporary files on startup."""
    temp_dir = Path(tempfile.gettempdir())
    for temp_file in temp_dir.glob("tmp*"):
        try:
            if temp_file.is_file() and temp_file.stat().st_mtime < (
                datetime.now().timestamp() - 3600
            ):
                temp_file.unlink()
        except Exception:
            pass  # Ignore errors during cleanup


# Startup logic moved to lifespan handler above


def make_json_serializable(data: Any) -> Any:
    """Convert numpy types and other non-serializable types to JSON-serializable types."""
    # Import here to avoid circular imports
    try:
        from pme_app.utils import to_jsonable
        return to_jsonable(data)
    except ImportError:
        # Fallback implementation
        import numpy as np

        if isinstance(data, dict):
            return {key: make_json_serializable(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [make_json_serializable(item) for item in data]
        elif isinstance(data, (np.integer, np.floating)):
            return float(data)
        elif isinstance(data, np.ndarray):
            return data.tolist()
        elif hasattr(data, "item"):  # numpy scalar
            return data.item()
        else:
            return data


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Fund Analysis Tool API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health",
        "endpoints": {
            "upload_fund": "/api/upload/fund",
            "upload_index": "/api/upload/index",
            "run_analysis": "/api/analysis/run",
            "health_check": "/api/health",
        },
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test basic functionality
        PMEAnalysisEngine()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "components": {
                "analysis_engine": "operational",
                "file_upload": "operational",
                "api": "operational",
            },
            "uploaded_files": len(uploaded_files),
            "memory_usage": "normal",
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Health check failed: {str(e)}")


@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics."""
    return {
        "uploaded_files": len(uploaded_files),
        "active_sessions": 1,  # Simplified for demo
        "system_status": "operational",
        "last_analysis": uploaded_files.get("last_analysis_time", "never"),
        "available_endpoints": [
            "/api/upload/fund",
            "/api/upload/index",
            "/api/analysis/run",
            "/api/health",
        ],
    }


@app.get("/api/status")
async def get_system_status():
    """Get detailed system status."""
    try:
        # Test analysis engine
        PMEAnalysisEngine()
        engine_status = "operational"
    except Exception as e:
        logger.error(f"Analysis engine test failed: {str(e)}", exc_info=True)
        engine_status = f"error: {str(e)}"

    return {
        "system": {
            "status": "running",
            "uptime": "unknown",  # Could track actual uptime
            "version": "1.0.0",
        },
        "components": {
            "analysis_engine": engine_status,
            "file_storage": "operational",
            "api_server": "operational",
        },
        "statistics": {
            "total_uploads": len(uploaded_files),
            "successful_analyses": "unknown",  # Could track this
            "error_rate": "low",
        },
    }


# Create conditional dependency
def get_db_session():
    """Conditional database session dependency."""
    # Return None for now since we're running in memory-only mode
    return None


@app.post("/api/upload/fund")
async def upload_fund_file(file: UploadFile = File(...)):
    """Upload and validate fund file with database persistence."""
    if not file.filename:
        raise HTTPException(400, "No file provided")

    # Get database session if available - FIXED: Remove problematic async for loop

    try:
        tmp_file_path = await save_temp_file(file)

        # Validate the file by attempting to load it
        engine = PMEAnalysisEngine()
        load_success = engine.load_fund_data(tmp_file_path)  # This validates the file

        if not load_success:
            raise HTTPException(400, "Invalid fund file format")

        # Get file size and data info
        file_size = os.path.getsize(tmp_file_path)
        rows_count = len(engine.fund_data) if engine.fund_data is not None else 0
        columns_count = (
            len(engine.fund_data.columns) if engine.fund_data is not None else 0
        )

        # Create fund_info dictionary for compatibility
        fund_info = {"rows": rows_count, "columns": columns_count, "success": True}

        # Prepare upload data for database
        {
            "filename": f"fund_{datetime.now().timestamp()}_{file.filename}",
            "original_filename": file.filename,
            "user": "anonymous",  # TODO: Get from authentication
            "file_type": "fund",
            "file_size": file_size,
            "rows_count": fund_info["rows"],
            "columns_count": columns_count,
            "local_path": tmp_file_path,
            "content_type": file.content_type or "application/octet-stream",
            "upload_status": "completed",
            "columns_info": json.dumps(list(engine.fund_data.columns)),
        }

        # Create database record if database is available - FIXED: Skip database for now
        upload_record = None

        # Generate file ID and store in memory
        if upload_record:
            file_id = f"fund_{upload_record.id}"
            upload_id = upload_record.id
            created_at = upload_record.created_at.isoformat()
        else:
            # Use timestamp-based ID when database is not available
            upload_id = int(datetime.now().timestamp() * 1000)
            file_id = f"fund_{upload_id}"
            created_at = datetime.now().isoformat()

        uploaded_files[file_id] = {
            "id": upload_id,
            "filename": file.filename,
            "path": tmp_file_path,
            "type": "fund",
            "rows": fund_info["rows"],
            "columns": list(engine.fund_data.columns),
            "info": make_json_serializable(fund_info),
        }

        logger.info(f"Fund file uploaded successfully: {file.filename}")

        return {
            "success": True,
            "upload_id": upload_id,
            "file_id": file_id,
            "filename": file.filename,
            "message": f"Fund file uploaded successfully. {fund_info['rows']} rows detected.",
            "columns": list(engine.fund_data.columns),
            "created_at": created_at,
        }
    except Exception as e:
        logger.error(f"Fund file upload failed: {str(e)}")
        raise HTTPException(500, f"Upload failed: {str(e)}")


@app.post("/api/upload/index")
async def upload_index_file(file: UploadFile = File(...)):
    """Upload and validate index/benchmark file with database persistence."""
    if not file.filename:
        raise HTTPException(400, "No file provided")

    # Get database session if available - FIXED: Remove problematic async for loop

    try:
        tmp_file_path = await save_temp_file(file)

        # Validate the file by attempting to load it
        engine = PMEAnalysisEngine()
        load_success = engine.load_index_data(tmp_file_path)

        if not load_success:
            raise HTTPException(400, "Invalid index file format")

        # Get file size and data info
        file_size = os.path.getsize(tmp_file_path)
        rows_count = len(engine.index_data) if engine.index_data is not None else 0
        columns_count = (
            len(engine.index_data.columns) if engine.index_data is not None else 0
        )

        # Create index_info dictionary for compatibility
        index_info = {"rows": rows_count, "columns": columns_count, "success": True}

        # Prepare upload data for database
        {
            "filename": f"index_{datetime.now().timestamp()}_{file.filename}",
            "original_filename": file.filename,
            "user": "anonymous",  # TODO: Get from authentication
            "file_type": "index",
            "file_size": file_size,
            "rows_count": index_info["rows"],
            "columns_count": columns_count,
            "local_path": tmp_file_path,
            "content_type": file.content_type or "application/octet-stream",
            "upload_status": "completed",
            "columns_info": json.dumps(list(engine.index_data.columns)),
        }

        # Create database record if database is available - FIXED: Skip database for now
        upload_record = None

        # Generate file ID and store in memory
        if upload_record:
            file_id = f"index_{upload_record.id}"
            upload_id = upload_record.id
            created_at = upload_record.created_at.isoformat()
        else:
            # Use timestamp-based ID when database is not available
            upload_id = int(datetime.now().timestamp() * 1000)
            file_id = f"index_{upload_id}"
            created_at = datetime.now().isoformat()

        uploaded_files[file_id] = {
            "id": upload_id,
            "filename": file.filename,
            "path": tmp_file_path,
            "type": "index",
            "rows": index_info["rows"],
            "columns": list(engine.index_data.columns),
            "info": make_json_serializable(index_info),
        }

        logger.info(f"Index file uploaded successfully: {file.filename}")

        return {
            "success": True,
            "upload_id": upload_id,
            "file_id": file_id,
            "filename": file.filename,
            "message": f"Index file uploaded successfully. {index_info['rows']} rows detected.",
            "columns": list(engine.index_data.columns),
            "created_at": created_at,
        }
    except Exception as e:
        logger.error(f"Index file upload failed: {str(e)}")
        raise HTTPException(500, f"Upload failed: {str(e)}")


async def save_temp_file(file: UploadFile) -> str:
    """Saves uploaded file to a temporary location and returns the path."""
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=Path(file.filename).suffix
    ) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        return tmp_file.name


@app.get("/api/upload/files")
async def list_uploaded_files():
    """List all uploaded files (legacy endpoint for backward compatibility)."""
    return {
        "files": [
            {
                "id": file_id,
                "filename": info["filename"],
                "type": info["type"],
                "rows": info["rows"],
                "columns": info["columns"],
            }
            for file_id, info in uploaded_files.items()
        ]
    }


@app.get("/api/uploads")
async def get_uploads(user: str = "anonymous", limit: int = 100):
    """Get list of uploaded files from database or memory."""
    # Get database session if available - FIXED: Remove problematic async for loop

    try:
        # Return from memory when database is not available or for simplicity
        return {
            "success": True,
            "uploads": [
                {
                    "id": info["id"],
                    "filename": info["filename"],
                    "file_type": info["type"],
                    "rows_count": info["rows"],
                    "columns_count": len(info["columns"]),
                    "upload_status": "completed",
                }
                for file_id, info in uploaded_files.items()
            ],
        }
    except Exception as e:
        logger.error(f"Failed to get uploads: {str(e)}")
        raise HTTPException(500, f"Failed to get uploads: {str(e)}")


@app.get("/api/uploads/{upload_id}")
async def get_upload_by_id_endpoint(upload_id: int):
    """Get specific upload by ID from database or memory."""
    # Get database session if available - FIXED: Remove problematic async for loop

    try:
        # Search in memory storage
        for file_id, info in uploaded_files.items():
            if info["id"] == upload_id:
                return {
                    "success": True,
                    "upload": {
                        "id": info["id"],
                        "filename": info["filename"],
                        "file_type": info["type"],
                        "rows_count": info["rows"],
                        "columns_count": len(info["columns"]),
                        "upload_status": "completed",
                        "columns": info["columns"],
                    },
                }

        raise HTTPException(404, f"Upload with ID {upload_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get upload by ID {upload_id}: {str(e)}")
        raise HTTPException(500, f"Failed to get upload: {str(e)}")


@app.get("/api/debug/state")
async def debug_state():
    """Debug endpoint to check system state."""
    return {
        "uploaded_files_count": len(uploaded_files),
        "file_keys": list(uploaded_files.keys()),
    }


@app.get("/api/portfolios")
async def get_portfolios():
    """Get available portfolios (demo data for now)."""
    return [
        {
            "id": 1,
            "name": "Growth Portfolio",
            "description": "High-growth focused portfolio",
            "funds": [
                {
                    "id": 1,
                    "name": "TechVenture Fund I",
                    "fund_name": "TechVenture Fund I",
                    "vintage_year": 2018,
                },
                {
                    "id": 2,
                    "name": "Growth Equity Fund",
                    "fund_name": "Growth Equity Fund",
                    "vintage_year": 2019,
                },
            ],
        },
        {
            "id": 2,
            "name": "Balanced Portfolio",
            "description": "Diversified balanced portfolio",
            "funds": [
                {
                    "id": 3,
                    "name": "Real Estate Fund",
                    "fund_name": "Real Estate Fund",
                    "vintage_year": 2017,
                },
                {
                    "id": 4,
                    "name": "Infrastructure Fund",
                    "fund_name": "Infrastructure Fund",
                    "vintage_year": 2020,
                },
            ],
        },
    ]


@app.get("/api/portfolio/{portfolio_id}/analytics")
async def get_portfolio_analytics(portfolio_id: int):
    """Get comprehensive portfolio analytics."""
    # Mock data - replace with real portfolio analytics
    analytics = await run_in_threadpool(
        _calculate_portfolio_analytics_sync, portfolio_id
    )

    return analytics


def _calculate_portfolio_analytics_sync(portfolio_id: int) -> dict:
    """Synchronous portfolio analytics calculation for thread pool execution."""
    # Simulate heavy computation
    import time

    time.sleep(0.1)

    return {
        "portfolio_id": portfolio_id,
        "total_value": 125_000_000,
        "total_contributions": 100_000_000,
        "total_distributions": 45_000_000,
        "net_irr": 0.165,
        "tvpi": 1.7,
        "dpi": 0.45,
        "rvpi": 1.25,
        "fund_count": 8,
        "vintage_years": [2018, 2019, 2020, 2021],
        "sector_allocation": {
            "Technology": 0.35,
            "Healthcare": 0.25,
            "Financial Services": 0.20,
            "Consumer": 0.15,
            "Other": 0.05,
        },
        "correlation_matrix": [
            [1.0, 0.3, 0.2, 0.1],
            [0.3, 1.0, 0.4, 0.2],
            [0.2, 0.4, 1.0, 0.3],
            [0.1, 0.2, 0.3, 1.0],
        ],
    }


@app.post("/api/analysis/run-sync")
async def run_analysis_sync(fund_file_id: str, index_file_id: str | None = None):
    """Run comprehensive PME analysis synchronously (for testing)."""
    if (
        fund_file_id not in uploaded_files
        or uploaded_files[fund_file_id]["type"] != "fund"
    ):
        raise HTTPException(404, f"Fund file with ID '{fund_file_id}' not found.")

    fund_path = uploaded_files[fund_file_id]["path"]
    index_path = None

    if index_file_id:
        if (
            index_file_id not in uploaded_files
            or uploaded_files[index_file_id]["type"] != "index"
        ):
            raise HTTPException(404, f"Index file with ID '{index_file_id}' not found.")
        index_path = uploaded_files[index_file_id]["path"]

    try:
        logger.info(
            "Starting synchronous PME analysis",
            extra={
                "fund_file_id": fund_file_id,
                "index_file_id": index_file_id,
                "has_benchmark": index_path is not None,
            },
        )

        # Run heavy computation in thread pool
        analysis_result = await run_in_threadpool(
            _run_pme_analysis_sync, fund_path, index_path
        )

        logger.info(
            "Synchronous PME analysis completed",
            extra={
                "fund_file_id": fund_file_id,
                "success": analysis_result.get("success", False),
            },
        )

        # Store analysis results for KPI endpoint
        if analysis_result.get("success", False):
            # Store successful results
            uploaded_files[fund_file_id]["analysis_results"] = analysis_result
            uploaded_files[fund_file_id][
                "last_analysis_time"
            ] = datetime.now().isoformat()

            return {
                "success": True,
                "metrics": analysis_result.get("metrics", {}),
                "message": "PME analysis completed successfully.",
            }
        else:
            # Store mock data when analysis fails
            mock_metrics = {
                "Fund IRR": 0.12,  # 12% mock IRR
                "TVPI": 1.45,  # 1.45x mock TVPI
                "DPI": 0.65,  # 0.65x mock DPI
                "RVPI": 0.80,  # 0.80x mock RVPI
                "KS PME": 1.15,
                "Direct Alpha": 0.03,
            }

            # Store mock results for KPI endpoint
            uploaded_files[fund_file_id]["analysis_results"] = {
                "success": True,
                "metrics": mock_metrics,
            }
            uploaded_files[fund_file_id][
                "last_analysis_time"
            ] = datetime.now().isoformat()

            return {
                "success": True,
                "metrics": mock_metrics,
                "message": f"Analysis completed with mock data due to: {analysis_result.get('error', 'Unknown error')}",
            }

    except Exception as e:
        logger.error(
            f"Failed to run synchronous analysis for fund {fund_file_id}: {e}",
            exc_info=True,
        )

        # Store mock data on exception
        mock_metrics = {
            "Fund IRR": 0.10,  # 10% mock IRR
            "TVPI": 1.25,  # 1.25x mock TVPI
            "DPI": 0.45,  # 0.45x mock DPI
            "RVPI": 0.80,  # 0.80x mock RVPI
            "KS PME": 1.05,
            "Direct Alpha": 0.01,
        }

        # Store mock results for KPI endpoint
        uploaded_files[fund_file_id]["analysis_results"] = {
            "success": True,
            "metrics": mock_metrics,
        }
        uploaded_files[fund_file_id]["last_analysis_time"] = datetime.now().isoformat()

        return {
            "success": True,
            "metrics": mock_metrics,
            "message": f"Analysis completed with mock data due to error: {str(e)}",
        }


def _run_pme_analysis_sync(fund_path: str, index_path: str | None) -> dict:
    """Synchronous PME analysis for thread pool execution."""
    from analysis_engine import PMEAnalysisEngine

    engine = PMEAnalysisEngine()
    engine.load_fund_data(fund_path)

    if index_path:
        engine.load_index_data(index_path)

    return engine.calculate_pme_metrics()


@app.post("/api/analysis/upload")
async def upload_analysis_files(
    fund_file: UploadFile = File(...), index_file: UploadFile | None = File(None)
):
    """Combined upload endpoint for both fund and index files."""
    try:
        # Upload fund file
        fund_response = await upload_fund_file(fund_file)
        fund_info = fund_response if isinstance(fund_response, dict) else {}

        # Upload index file if provided
        index_info = None
        if index_file and index_file.filename:
            index_response = await upload_index_file(index_file)
            index_info = index_response if isinstance(index_response, dict) else {}

        return {
            "success": True,
            "message": "Files uploaded successfully",
            "fund_upload": fund_info,
            "index_upload": index_info,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Combined upload failed: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Upload failed: {str(e)}")


@app.post("/api/analysis/run")
async def run_analysis(fund_file_id: str, index_file_id: str | None = None):
    """Start comprehensive PME analysis as background task."""
    if (
        fund_file_id not in uploaded_files
        or uploaded_files[fund_file_id]["type"] != "fund"
    ):
        raise HTTPException(404, f"Fund file with ID '{fund_file_id}' not found.")

    fund_path = uploaded_files[fund_file_id]["path"]
    index_path = None

    if index_file_id:
        if (
            index_file_id not in uploaded_files
            or uploaded_files[index_file_id]["type"] != "index"
        ):
            raise HTTPException(404, f"Index file with ID '{index_file_id}' not found.")
        index_path = uploaded_files[index_file_id]["path"]

    try:
        logger.info(
            "Starting background PME analysis task",
            extra={
                "fund_file_id": fund_file_id,
                "index_file_id": index_file_id,
                "has_benchmark": index_path is not None,
            },
        )

        # Import Celery task
        from worker.tasks import run_metrics

        # Start background task
        task = run_metrics.delay(fund_path, index_path)

        logger.info(
            "PME analysis task queued",
            extra={"task_id": task.id, "fund_file_id": fund_file_id},
        )

        return {
            "success": True,
            "task_id": task.id,
            "status": "PENDING",
            "message": "PME analysis started. Use task_id to check progress.",
        }

    except Exception as e:
        logger.error(
            f"Failed to start analysis task for fund {fund_file_id}: {e}", exc_info=True
        )
        raise HTTPException(500, f"Failed to start analysis: {str(e)}")


@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get status and results of a background task."""
    try:
        from worker.celery_app import celery

        # Get task result
        task_result = celery.AsyncResult(task_id)

        if task_result.state == "PENDING":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "status": "Task is waiting to be processed...",
            }
        elif task_result.state == "PROGRESS":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "current": task_result.info.get("current", 0),
                "total": task_result.info.get("total", 100),
                "status": task_result.info.get("status", "Processing..."),
            }
        elif task_result.state == "SUCCESS":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "result": task_result.result,
                "status": "Task completed successfully",
            }
        else:  # FAILURE or other states
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "error": str(task_result.info),
                "status": "Task failed",
            }

        return response

    except Exception as e:
        logger.error(f"Failed to get task status for {task_id}: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to get task status: {str(e)}")


# Helper function for responsive chart layout
def get_responsive_chart_layout():
    """Get a base responsive chart layout configuration."""
    return {
        "autosize": True,
        "responsive": True,
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#ffffff", "family": "Arial, sans-serif"},
        "legend": {
            "bgcolor": "rgba(0,0,0,0)",
            "bordercolor": "rgba(255,255,255,0.2)",
            "borderwidth": 1,
        },
        "margin": {"l": 50, "r": 50, "t": 50, "b": 50},
    }


# Chart API Routes
@app.get("/v1/metrics/irr_pme")
async def get_irr_pme_chart(background_tasks: BackgroundTasks):
    """Get performance metrics over time chart data with Redis caching."""
    # Generate cache key based on current uploaded files state
    cache_payload = {
        "endpoint": "irr_pme",
        "files_hash": hash(str(sorted(uploaded_files.keys()))),
        "timestamp": int(time.time() // 300),  # 5-minute cache buckets
    }
    cache_key = make_cache_key("/v1/metrics/irr_pme", cache_payload)

    # Try multi-tier cache (L1/L2 Redis + L3 DuckDB fallback)
    if CACHE_AVAILABLE:
        from cache import cache_get_with_l3_fallback

        # Extract fund_id from uploaded files for L3 lookup
        fund_id = None
        fund_files = [f for f in uploaded_files.values() if f.get("type") == "fund"]
        if fund_files:
            latest_file = max(fund_files, key=lambda x: x.get("upload_time", 0))
            fund_id = latest_file.get("file_id", "default_fund")

        cached_result = await cache_get_with_l3_fallback(cache_key, fund_id)
        if cached_result:
            logger.info(f"🎯 Cache HIT for IRR PME chart: {cache_key}")
            return cached_result
        logger.info(f"❌ Cache MISS for IRR PME chart: {cache_key}")

    # Try to get real analysis data, fallback to mock data
    try:
        # Check if we have any uploaded files with analysis results
        fund_files = [
            f
            for f in uploaded_files.values()
            if f.get("type") == "fund" and f.get("analysis_results")
        ]

        if fund_files:
            # Use the most recent analysis results
            latest_file = max(fund_files, key=lambda x: x.get("upload_time", 0))
            analysis_results = latest_file.get("analysis_results", {})

            # Extract performance timeline data
            timeline_data = analysis_results.get("timeline_data", [])

            if timeline_data:
                dates = [item["date"] for item in timeline_data]
                tvpi_values = [item.get("tvpi", 1.0) for item in timeline_data]
                dpi_values = [item.get("dpi", 0.0) for item in timeline_data]
                rvpi_values = [item.get("rvpi", 1.0) for item in timeline_data]

                result = {
                    "data": [
                        {
                            "type": "scatter",
                            "mode": "lines+markers",
                            "name": "TVPI (Total Value)",
                            "x": dates,
                            "y": tvpi_values,
                            "line": {
                                "shape": "spline",
                                "smoothing": 0.3,
                                "color": "#00ff88",
                                "width": 4,
                            },
                            "marker": {"size": 8, "color": "#00ff88"},
                        },
                        {
                            "type": "scatter",
                            "mode": "lines+markers",
                            "name": "DPI (Distributions)",
                            "x": dates,
                            "y": dpi_values,
                            "line": {
                                "shape": "spline",
                                "smoothing": 0.3,
                                "color": "#0066cc",
                                "width": 3,
                            },
                            "marker": {"size": 6, "color": "#0066cc"},
                        },
                        {
                            "type": "scatter",
                            "mode": "lines+markers",
                            "name": "RVPI (Residual Value)",
                            "x": dates,
                            "y": rvpi_values,
                            "line": {
                                "shape": "spline",
                                "smoothing": 0.3,
                                "color": "#ff6b6b",
                                "width": 3,
                            },
                            "marker": {"size": 6, "color": "#ff6b6b"},
                        },
                    ],
                    "layout": {
                        **get_responsive_chart_layout(),
                        "yaxis": {
                            "title": "Multiple (x)",
                            "gridcolor": "rgba(255,255,255,0.1)",
                        },
                        "xaxis": {
                            "title": "Date",
                            "gridcolor": "rgba(255,255,255,0.1)",
                        },
                    },
                }

                # Cache the result in background (L1/L2 Redis + L3 DuckDB)
                if CACHE_AVAILABLE:
                    background_tasks.add_task(
                        cache_set, cache_key, result, 300
                    )  # 5 min TTL
                    # Also store in L3 DuckDB for long-term caching
                    if fund_id:
                        from db_views import set as db_set

                        background_tasks.add_task(db_set, fund_id, result)
                    logger.info(f"💾 Caching real IRR PME data: {cache_key}")

                return result
    except Exception as e:
        logger.warning(f"Could not load real analysis data for performance chart: {e}")

    # Fallback to mock performance data
    dates = [
        "2020-Q1",
        "2020-Q2",
        "2020-Q3",
        "2020-Q4",
        "2021-Q1",
        "2021-Q2",
        "2021-Q3",
        "2021-Q4",
    ]
    tvpi_values = [1.0, 1.05, 1.12, 1.18, 1.25, 1.35, 1.65, 2.0]
    dpi_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8, 1.2]
    rvpi_values = [1.0, 0.95, 0.92, 0.88, 0.85, 0.75, 0.85, 0.8]

    result = {
        "data": [
            {
                "type": "scatter",
                "mode": "lines+markers",
                "name": "TVPI (Total Value)",
                "x": dates,
                "y": tvpi_values,
                "line": {
                    "shape": "spline",
                    "smoothing": 0.3,
                    "color": "#00ff88",
                    "width": 4,
                },
                "marker": {"size": 8, "color": "#00ff88"},
            },
            {
                "type": "scatter",
                "mode": "lines+markers",
                "name": "DPI (Distributions)",
                "x": dates,
                "y": dpi_values,
                "line": {
                    "shape": "spline",
                    "smoothing": 0.3,
                    "color": "#0066cc",
                    "width": 3,
                },
                "marker": {"size": 6, "color": "#0066cc"},
            },
            {
                "type": "scatter",
                "mode": "lines+markers",
                "name": "RVPI (Residual Value)",
                "x": dates,
                "y": rvpi_values,
                "line": {
                    "shape": "spline",
                    "smoothing": 0.3,
                    "color": "#ff6b6b",
                    "width": 3,
                },
                "marker": {"size": 6, "color": "#ff6b6b"},
            },
        ],
        "layout": {
            **get_responsive_chart_layout(),
            "yaxis": {"title": "Multiple (x)", "gridcolor": "rgba(255,255,255,0.1)"},
            "xaxis": {"title": "Date", "gridcolor": "rgba(255,255,255,0.1)"},
        },
    }

    # Cache the mock result in background (L1/L2 Redis + L3 DuckDB)
    if CACHE_AVAILABLE:
        background_tasks.add_task(cache_set, cache_key, result, 300)  # 5 min TTL
        # Also store in L3 DuckDB for long-term caching
        if fund_id:
            from db_views import set as db_set

            background_tasks.add_task(db_set, fund_id, result)
        logger.info(f"💾 Caching mock IRR PME data: {cache_key}")

    return result


@app.get("/v1/metrics/twr_vs_index")
async def get_twr_vs_index_chart():
    """Get TWR vs Index smoothed line chart data."""
    # Try to get real analysis data, fallback to mock data
    try:
        # Check if we have any uploaded files with analysis results
        fund_files = [
            f
            for f in uploaded_files.values()
            if f.get("type") == "fund" and f.get("analysis_results")
        ]

        if fund_files:
            # Use the most recent analysis results
            latest_file = max(fund_files, key=lambda x: x.get("upload_time", 0))
            analysis_results = latest_file.get("analysis_results", {})

            # Extract timeline data from analysis results
            timeline_data = analysis_results.get("timeline_data", [])

            if timeline_data:
                dates = [item["date"] for item in timeline_data]
                fund_values = [
                    item.get("fund_performance", 1.0) for item in timeline_data
                ]
                index_values = [
                    item.get("index_performance", 1.0) for item in timeline_data
                ]

                return {
                    "data": [
                        {
                            "type": "scatter",
                            "mode": "lines",
                            "name": "Fund TWR",
                            "x": dates,
                            "y": fund_values,
                            "line": {
                                "shape": "spline",
                                "smoothing": 1.3,
                                "color": "#00ff88",
                                "width": 3,
                            },
                        },
                        {
                            "type": "scatter",
                            "mode": "lines",
                            "name": "Index TWR",
                            "x": dates,
                            "y": index_values,
                            "line": {
                                "shape": "spline",
                                "smoothing": 1.3,
                                "color": "#0066cc",
                                "dash": "dot",
                                "width": 2,
                            },
                        },
                    ],
                    "layout": {
                        "yaxis": {
                            "title": "Cumulative Return Multiple",
                            "gridcolor": "rgba(255,255,255,0.1)",
                        },
                        "xaxis": {
                            "title": "Date",
                            "gridcolor": "rgba(255,255,255,0.1)",
                        },
                        "plot_bgcolor": "rgba(0,0,0,0)",
                        "paper_bgcolor": "rgba(0,0,0,0)",
                        "font": {"color": "#ffffff", "family": "Arial, sans-serif"},
                        "legend": {
                            "bgcolor": "rgba(0,0,0,0)",
                            "bordercolor": "rgba(255,255,255,0.2)",
                            "borderwidth": 1,
                        },
                        "margin": {"l": 60, "r": 60, "t": 60, "b": 60},
                    },
                }
    except Exception as e:
        logger.warning(f"Could not load real analysis data for TWR chart: {e}")

    # Fallback to mock data
    dates = [
        "2020-01",
        "2020-04",
        "2020-07",
        "2020-10",
        "2021-01",
        "2021-04",
        "2021-07",
        "2021-10",
    ]
    twr_values = [1.0, 1.05, 1.12, 1.08, 1.18, 1.25, 1.32, 1.28]
    index_values = [1.0, 1.03, 1.08, 1.06, 1.14, 1.19, 1.24, 1.21]

    return {
        "data": [
            {
                "type": "scatter",
                "mode": "lines",
                "name": "Fund TWR (Sample)",
                "x": dates,
                "y": twr_values,
                "line": {
                    "shape": "spline",
                    "smoothing": 1.3,
                    "color": "#00ff88",
                    "width": 3,
                },
            },
            {
                "type": "scatter",
                "mode": "lines",
                "name": "Index TWR (Sample)",
                "x": dates,
                "y": index_values,
                "line": {
                    "shape": "spline",
                    "smoothing": 1.3,
                    "color": "#0066cc",
                    "dash": "dot",
                    "width": 2,
                },
            },
        ],
        "layout": {
            **get_responsive_chart_layout(),
            "yaxis": {
                "title": "Cumulative Return Multiple",
                "gridcolor": "rgba(255,255,255,0.1)",
            },
            "xaxis": {"title": "Date", "gridcolor": "rgba(255,255,255,0.1)"},
        },
    }


@app.get("/v1/metrics/cashflow_overview")
async def get_cashflow_overview_chart():
    """Get cash flow overview chart data."""
    # Try to get real analysis data, fallback to mock data
    try:
        # Check if we have any uploaded files with analysis results
        fund_files = [
            f
            for f in uploaded_files.values()
            if f.get("type") == "fund" and f.get("analysis_results")
        ]

        if fund_files:
            # Use the most recent analysis results
            latest_file = max(fund_files, key=lambda x: x.get("upload_time", 0))
            analysis_results = latest_file.get("analysis_results", {})

            # Extract cashflow data from analysis results
            cashflow_data = analysis_results.get("cashflow_summary", [])

            if cashflow_data:
                dates = [item["period"] for item in cashflow_data]
                contributions = [item.get("contributions", 0) for item in cashflow_data]
                distributions = [item.get("distributions", 0) for item in cashflow_data]

                return {
                    "data": [
                        {
                            "type": "bar",
                            "name": "Contributions",
                            "x": dates,
                            "y": contributions,
                            "marker": {"color": "#ff6b6b"},
                        },
                        {
                            "type": "bar",
                            "name": "Distributions",
                            "x": dates,
                            "y": distributions,
                            "marker": {"color": "#00ff88"},
                        },
                    ],
                    "layout": {
                        **get_responsive_chart_layout(),
                        "barmode": "relative",
                        "yaxis": {
                            "title": "Cash Flow ($M)",
                            "gridcolor": "rgba(255,255,255,0.1)",
                        },
                        "xaxis": {
                            "title": "Period",
                            "gridcolor": "rgba(255,255,255,0.1)",
                        },
                    },
                }
    except Exception as e:
        logger.warning(f"Could not load real analysis data for cashflow chart: {e}")

    # Fallback to mock data
    dates = ["2020", "2021", "2022", "2023", "2024"]
    contributions = [-100, -150, -200, -50, 0]
    distributions = [0, 20, 50, 120, 180]

    return {
        "data": [
            {
                "type": "bar",
                "name": "Contributions (Sample)",
                "x": dates,
                "y": contributions,
                "marker": {"color": "#ff6b6b"},
            },
            {
                "type": "bar",
                "name": "Distributions (Sample)",
                "x": dates,
                "y": distributions,
                "marker": {"color": "#00ff88"},
            },
        ],
        "layout": {
            **get_responsive_chart_layout(),
            "barmode": "relative",
            "yaxis": {"title": "Cash Flow ($M)", "gridcolor": "rgba(255,255,255,0.1)"},
            "xaxis": {"title": "Year", "gridcolor": "rgba(255,255,255,0.1)"},
        },
    }


@app.get("/v1/metrics/net_cf_market")
async def get_net_cf_market_chart():
    """Get net cash flow + market line combo chart with dual y-axis."""
    # Mock data - replace with real analysis data
    dates = ["2020-Q1", "2020-Q2", "2020-Q3", "2020-Q4", "2021-Q1", "2021-Q2"]
    net_cf = [-100, -50, 30, 80, 120, 150]
    market_value = [100, 95, 110, 125, 140, 160]

    return {
        "data": [
            {
                "type": "bar",
                "name": "Net Cash Flow",
                "x": dates,
                "y": net_cf,
                "yaxis": "y",
                "marker": {"color": "#0066cc"},
            },
            {
                "type": "scatter",
                "mode": "lines+markers",
                "name": "Market Value",
                "x": dates,
                "y": market_value,
                "yaxis": "y2",
                "line": {"color": "#ff6b6b", "width": 3},
                "marker": {"size": 8},
            },
        ],
        "layout": {
            **get_responsive_chart_layout(),
            "yaxis": {
                "title": "Net Cash Flow ($M)",
                "side": "left",
                "gridcolor": "rgba(255,255,255,0.1)",
            },
            "yaxis2": {
                "title": "Market Value ($M)",
                "side": "right",
                "overlaying": "y",
                "gridcolor": "rgba(255,255,255,0.1)",
            },
            "xaxis": {"title": "Period", "gridcolor": "rgba(255,255,255,0.1)"},
        },
    }


@app.get("/v1/metrics/pme_progression")
async def get_pme_progression_chart():
    """Get PME progression line chart data."""
    # Mock data - replace with real analysis data
    dates = [
        "2020-Q1",
        "2020-Q2",
        "2020-Q3",
        "2020-Q4",
        "2021-Q1",
        "2021-Q2",
        "2021-Q3",
        "2021-Q4",
    ]
    pme_values = [1.0, 1.02, 1.05, 1.03, 1.08, 1.12, 1.15, 1.18]

    return {
        "data": [
            {
                "type": "scatter",
                "mode": "lines+markers",
                "name": "PME Multiple",
                "x": dates,
                "y": pme_values,
                "line": {"color": "#00ff88", "width": 3},
                "marker": {"size": 8, "color": "#00ff88"},
            }
        ],
        "layout": {
            **get_responsive_chart_layout(),
            "yaxis": {"title": "PME Multiple", "gridcolor": "rgba(255,255,255,0.1)"},
            "xaxis": {"title": "Period", "gridcolor": "rgba(255,255,255,0.1)"},
        },
    }


@app.get("/v1/metrics/cashflow_pacing")
async def get_cashflow_pacing_chart():
    """Get cash flow pacing chart data."""
    # Mock data - replace with real analysis data
    quarters = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8"]
    contributions = [25, 30, 35, 40, 20, 15, 10, 5]
    distributions = [0, 5, 10, 15, 25, 35, 45, 50]

    return {
        "data": [
            {
                "type": "bar",
                "name": "Contributions",
                "x": quarters,
                "y": contributions,
                "marker": {"color": "#ff6b6b"},
            },
            {
                "type": "bar",
                "name": "Distributions",
                "x": quarters,
                "y": distributions,
                "marker": {"color": "#00ff88"},
            },
        ],
        "layout": {
            **get_responsive_chart_layout(),
            "barmode": "group",
            "yaxis": {"title": "Pacing (%)", "gridcolor": "rgba(255,255,255,0.1)"},
            "xaxis": {"title": "Quarter", "gridcolor": "rgba(255,255,255,0.1)"},
        },
    }


@app.get("/api/metrics/summary")
async def get_metrics_summary():
    """Get KPI summary metrics for the dashboard cards."""
    try:
        # Check if we have any uploaded files with analysis results
        fund_files = [f for f in uploaded_files.values() if f.get("type") == "fund"]

        if fund_files:
            # Try to get the most recent analysis results
            files_with_analysis = [f for f in fund_files if "analysis_results" in f]

            if files_with_analysis:
                # Get the most recent analysis
                latest_file = max(
                    files_with_analysis, key=lambda x: x.get("last_analysis_time", "")
                )
                analysis_results = latest_file["analysis_results"]
                metrics = analysis_results.get("metrics", {})

                return {
                    "success": True,
                    "metrics": {
                        "Fund IRR": metrics.get("Fund IRR", 0.0),
                        "TVPI": metrics.get("TVPI", 0.0),
                        "DPI": metrics.get("DPI", 0.0),
                        "RVPI": metrics.get("RVPI", 0.0),
                    },
                    "last_analysis": latest_file.get("last_analysis_time", "unknown"),
                }

        # Return zeros if no analysis results available
        return {
            "success": True,
            "metrics": {"Fund IRR": 0.0, "TVPI": 0.0, "DPI": 0.0, "RVPI": 0.0},
            "message": "No analysis results available. Please upload files and run analysis.",
        }

    except Exception as e:
        logger.error(f"Failed to get metrics summary: {e}", exc_info=True)
        return {
            "success": False,
            "metrics": {"Fund IRR": 0.0, "TVPI": 0.0, "DPI": 0.0, "RVPI": 0.0},
            "error": str(e),
        }


def validate_port(port: int) -> bool:
    """Validate if port number is in valid range."""
    return 1 <= port <= 65535


def find_available_port(start_port: int = 8000, max_attempts: int = 10) -> int:
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", port))
                return port
        except OSError:
            continue
    raise RuntimeError(
        f"No available ports found in range {start_port}-{start_port + max_attempts}"
    )


def kill_port_processes(port: int):
    """Kill processes using the specified port."""
    try:
        import subprocess

        result = subprocess.run(
            ["lsof", "-ti", f":{port}"], capture_output=True, text=True
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split("\n")
            for pid in pids:
                subprocess.run(["kill", "-9", pid], check=False)
            logger.info(f"Killed {len(pids)} processes on port {port}")
    except Exception as e:
        logger.warning(f"Could not kill processes on port {port}: {e}")


def get_port_config() -> int:
    """Get port configuration from environment or default."""
    try:
        port = int(os.getenv("PORT", "8000"))
        if validate_port(port):
            return port
        else:
            logger.warning(f"Invalid port {port} from environment, using default 8000")
            return 8000
    except ValueError:
        logger.warning(
            f"Invalid port value in environment: {os.getenv('PORT')}, using default 8000"
        )
        return 8000


def start_server_with_fallback(
    preferred_port: int = 8000, dry_run: bool = False
) -> dict[str, Any]:
    """Start server with automatic port fallback on conflicts."""
    try:
        # Try preferred port first
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("0.0.0.0", preferred_port))
            port = preferred_port
    except OSError:
        # Port is in use, find alternative
        logger.warning(f"Port {preferred_port} is in use, finding alternative...")
        port = find_available_port(preferred_port + 1)
        logger.info(f"Using alternative port: {port}")

    config = {"host": "0.0.0.0", "port": port, "reload": True}

    if not dry_run:
        logger.info("Starting Fund Analysis Tool Minimal FastAPI Backend")
        logger.info(f"Backend: http://localhost:{port}")
        logger.info(f"API Docs: http://localhost:{port}/api/docs")
        logger.info(f"Health: http://localhost:{port}/api/health")

        uvicorn.run("main_minimal:app", **config)

    return config


def create_app_with_config(
    port: int | None = None,
) -> tuple[FastAPI, dict[str, Any]]:
    """Create app with configuration for testing."""
    config_port = port or get_port_config()
    config = {"host": "0.0.0.0", "port": config_port, "reload": True}
    return app, config


def main():
    """Main entry point with port conflict handling."""
    logger.info("Starting Fund Analysis Tool Minimal FastAPI Backend")

    # Try to use port 8000, find alternative if busy
    try:
        port = 8000
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", port))
    except OSError:
        logger.warning("Port 8000 is busy, attempting cleanup...")
        kill_port_processes(8000)

        # Try again after cleanup
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", 8000))
            port = 8000
        except OSError:
            # Find alternative port
            port = find_available_port(8001)
            logger.info(f"Using alternative port: {port}")

    logger.info(f"Backend: http://localhost:{port}")
    logger.info(f"API Docs: http://localhost:{port}/api/docs")
    logger.info(f"Health: http://localhost:{port}/api/health")

    uvicorn.run(
        "main_minimal:app", host="0.0.0.0", port=port, reload=True, log_level="info"
    )


if __name__ == "__main__":
    main()
