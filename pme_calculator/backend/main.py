"""Main entry point for the PME Calculator FastAPI backend server."""

from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .logger import get_logger
from .routers.upload import router as upload_router
from .simple_analysis import router as simple_analysis_router

# Initialize logger
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PME Calculator API",
    description="Professional Private Market Equivalent Calculator with comprehensive validation",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_router, prefix="/api")
app.include_router(simple_analysis_router, prefix="/api")
# app.include_router(analysis_router, prefix="/api")  # Disabled due to Pydantic recursion issue

# Get the frontend build directory
frontend_dir = Path(__file__).parent.parent / "frontend" / "dist"

# Serve static files if frontend is built
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=frontend_dir / "static"), name="static")


@app.get("/")
async def serve_frontend():
    """Serve the React frontend or API info."""
    if frontend_dir.exists() and (frontend_dir / "index.html").exists():
        return FileResponse(frontend_dir / "index.html")
    else:
        return {
            "message": "PME Calculator FastAPI Backend is running",
            "frontend_status": "React frontend not built. Run npm run build in frontend directory.",
            "endpoints": {
                "api_docs": "/api/docs",
                "upload_fund": "/api/upload/fund",
                "upload_index": "/api/upload/index",
                "run_analysis": "/api/analysis/run",
                "health": "/api/health",
            },
            "features": [
                "Comprehensive file validation with Pydantic",
                "Intelligent column mapping detection",
                "Structured JSON logging",
                "Type-safe API contracts",
                "Professional error handling",
            ],
        }


@app.get("/api/health")
async def health_check():
    """Health check endpoint with system information."""
    logger.info("Health check requested")

    return {
        "status": "healthy",
        "message": "PME Calculator FastAPI Backend is running",
        "version": "1.0.0",
        "features": {
            "validation": "Pydantic schemas with comprehensive validation",
            "logging": "Structured JSON logging with context",
            "file_support": "CSV, Excel (.xlsx, .xls) with intelligent parsing",
            "api_design": "Type-safe FastAPI with auto-documentation",
        },
    }


@app.get("/api/system/info")
async def system_info():
    """System information for diagnostics."""
    import platform
    import sys
    from datetime import datetime

    from utils.time import UTC

    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "frontend_build_available": frontend_dir.exists()
        and (frontend_dir / "index.html").exists(),
        "api_endpoints": len(app.routes),
        "cors_origins": [
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:3000",
        ],
    }


# Serve React app for client-side routing
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve React SPA for client-side routing."""
    if frontend_dir.exists() and (frontend_dir / "index.html").exists():
        # Don't serve index.html for API routes
        if full_path.startswith("api/"):
            raise HTTPException(404, detail="API endpoint not found")
        return FileResponse(frontend_dir / "index.html")
    else:
        raise HTTPException(404, detail="Frontend not available")


def main():
    """Start the FastAPI development server."""
    logger.info("Starting PME Calculator FastAPI Backend Server...")
    print("=" * 60)
    print("🚀 PME CALCULATOR FASTAPI BACKEND")
    print("=" * 60)
    print("📊 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/api/docs")
    print("🩺 Health Check: http://localhost:8000/api/health")
    print("⚛️  Frontend: http://localhost:5173 (Vite dev server)")
    print("=" * 60)
    print("✅ Features Active:")
    print("   • Comprehensive file validation")
    print("   • Intelligent column mapping")
    print("   • Structured JSON logging")
    print("   • Type-safe API contracts")
    print("   • Professional error handling")
    print("=" * 60)

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")


if __name__ == "__main__":
    main()
