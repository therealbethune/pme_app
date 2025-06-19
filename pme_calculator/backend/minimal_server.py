"""
Minimal FastAPI server for PME Calculator that bypasses problematic Pydantic schemas.
"""

import io
import uuid
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# Import our central timezone utility
from pme_calculator.utils.time import utc_now

app = FastAPI(title="PME Calculator - Minimal", version="1.0.0")

# CORS middleware
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

# In-memory file storage
uploaded_files: dict[str, dict[str, Any]] = {}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "PME Calculator Minimal Backend is running",
        "version": "1.0.0",
    }


@app.post("/api/upload/fund")
async def upload_fund_file(file: UploadFile = File(...)):
    """Upload fund data file."""
    try:
        # Read file content
        content = await file.read()

        # Try to parse as CSV
        try:
            df = pd.read_csv(io.StringIO(content.decode("utf-8")))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV file: {str(e)}")

        # Generate file ID
        file_id = f"fund_{len([k for k in uploaded_files if k.startswith('fund_')])}"

        # Store file info
        uploaded_files[file_id] = {
            "filename": file.filename,
            "content": content,
            "dataframe": df,
            "columns": df.columns.tolist(),
            "row_count": len(df),
            "upload_time": utc_now().isoformat(),
        }

        return {
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "message": f"Fund file uploaded successfully. {len(df)} rows detected.",
            "columns": df.columns.tolist(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload/index")
async def upload_index_file(file: UploadFile = File(...)):
    """Upload index data file."""
    try:
        # Read file content
        content = await file.read()

        # Try to parse as CSV
        try:
            df = pd.read_csv(io.StringIO(content.decode("utf-8")))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV file: {str(e)}")

        # Generate file ID
        file_id = f"index_{len([k for k in uploaded_files if k.startswith('index_')])}"

        # Store file info
        uploaded_files[file_id] = {
            "filename": file.filename,
            "content": content,
            "dataframe": df,
            "columns": df.columns.tolist(),
            "row_count": len(df),
            "upload_time": utc_now().isoformat(),
        }

        return {
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "message": f"Index file uploaded successfully. {len(df)} rows detected.",
            "columns": df.columns.tolist(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/upload/files")
async def list_uploaded_files():
    """List all uploaded files."""
    files_info = {}
    for file_id, file_data in uploaded_files.items():
        files_info[file_id] = {
            "filename": file_data["filename"],
            "columns": file_data["columns"],
            "row_count": file_data["row_count"],
            "upload_time": file_data["upload_time"],
        }

    return {"files": files_info}


@app.post("/api/simple-analysis/run")
async def run_simple_analysis():
    """Simple analysis endpoint that returns demo results."""
    try:
        # Check if we have any uploaded files
        if not uploaded_files:
            return {"success": False, "error": "No files uploaded"}

        # Find fund file
        fund_file_id = None
        for file_id in uploaded_files:
            if file_id.startswith("fund_"):
                fund_file_id = file_id
                break

        if not fund_file_id:
            return {"success": False, "error": "No fund file found"}

        # Return simple demo results
        return {
            "success": True,
            "request_id": str(uuid.uuid4()),
            "metrics": {
                "Fund IRR": 0.185,
                "TVPI": 2.34,
                "DPI": 1.67,
                "RVPI": 0.67,
                "Total Contributions": 25236151,
                "Total Distributions": 17012700,
                "Final NAV": 8500000,
            },
            "summary": {
                "fund_performance": "Strong performance with 18.5% IRR",
                "vs_benchmark": "Outperformed benchmark by 6.5%",
                "risk_profile": "Moderate risk with good diversification",
            },
            "has_benchmark": True,
            "analysis_date": utc_now().isoformat(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
