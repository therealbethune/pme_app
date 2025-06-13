"""
Phase 1C: API Endpoint Scaffold
Advanced data validation endpoints with progress tracking.
"""

import asyncio
import json
import os
import tempfile
import uuid
from datetime import datetime
from typing import Dict, List

import pandas as pd
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from schemas import (
    ColumnMapping,
    DatasetMetadata,
    DataValidator,
)

router = APIRouter(prefix="/api/validation", tags=["validation"])

# In-memory storage for validation jobs (in production, use Redis/database)
validation_jobs: dict[str, dict] = {}


@router.post("/upload/fund", response_model=dict[str, str])
async def upload_fund_data(
    background_tasks: BackgroundTasks, file: UploadFile = File(...)
) -> dict[str, str]:
    """Upload and validate fund cash flow data."""

    # Validate file type
    if not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="File must be CSV or Excel format")

    # Generate job ID
    job_id = f"fund_validation_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=os.path.splitext(file.filename)[1]
    ) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        temp_path = tmp_file.name

    # Initialize job status
    validation_jobs[job_id] = {
        "status": "uploaded",
        "filename": file.filename,
        "file_path": temp_path,
        "data_type": "fund",
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "result": None,
        "error": None,
    }

    # Start background validation
    background_tasks.add_task(validate_fund_file_background, job_id, temp_path)

    return {"job_id": job_id, "status": "processing"}


@router.post("/upload/index", response_model=dict[str, str])
async def upload_index_data(
    background_tasks: BackgroundTasks, file: UploadFile = File(...)
) -> dict[str, str]:
    """Upload and validate index/benchmark data."""

    if not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="File must be CSV or Excel format")

    job_id = (
        f"index_validation_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
    )

    with tempfile.NamedTemporaryFile(
        delete=False, suffix=os.path.splitext(file.filename)[1]
    ) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        temp_path = tmp_file.name

    validation_jobs[job_id] = {
        "status": "uploaded",
        "filename": file.filename,
        "file_path": temp_path,
        "data_type": "index",
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "result": None,
        "error": None,
    }

    background_tasks.add_task(validate_index_file_background, job_id, temp_path)

    return {"job_id": job_id, "status": "processing"}


@router.get("/status/{job_id}")
async def get_validation_status(job_id: str) -> dict:
    """Get validation job status and results."""

    if job_id not in validation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = validation_jobs[job_id]

    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "filename": job["filename"],
        "data_type": job["data_type"],
        "created_at": job["created_at"],
        "result": job["result"],
        "error": job["error"],
    }


@router.get("/stream/{job_id}")
async def stream_validation_progress(job_id: str):
    """Stream validation progress via Server-Sent Events."""

    if job_id not in validation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    async def event_publisher():
        while True:
            if job_id not in validation_jobs:
                break

            job = validation_jobs[job_id]

            # Send progress update
            data = {
                "job_id": job_id,
                "status": job["status"],
                "progress": job["progress"],
                "timestamp": datetime.now().isoformat(),
            }

            if job["result"]:
                data["result"] = job["result"]
            if job["error"]:
                data["error"] = job["error"]

            yield f"data: {json.dumps(data)}\n\n"

            # Stop streaming if job is complete
            if job["status"] in ["completed", "failed"]:
                break

            await asyncio.sleep(1)  # Update every second

    return StreamingResponse(
        event_publisher(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        },
    )


@router.post("/analyze/column-mapping")
async def analyze_column_mapping(
    file: UploadFile = File(...), data_type: str = "fund"
) -> dict[str, list[ColumnMapping]]:
    """Analyze file columns and suggest intelligent mappings."""

    try:
        # Read file headers
        if file.filename.lower().endswith(".csv"):
            # Read just the first row to get column names
            content = await file.read()
            lines = content.decode("utf-8").split("\n")
            if lines:
                columns = [col.strip() for col in lines[0].split(",")]
            else:
                columns = []
        else:
            # For Excel files, read just the header
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=os.path.splitext(file.filename)[1]
            ) as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                temp_path = tmp_file.name

            try:
                df_preview = pd.read_excel(temp_path, nrows=0)  # Just headers
                columns = df_preview.columns.tolist()
            finally:
                os.unlink(temp_path)

        # Generate intelligent column mappings
        mappings = DataValidator.intelligent_column_mapping(columns, data_type)

        return {
            "suggested_mappings": mappings,
            "confidence_score": (
                sum(m.confidence for m in mappings) / len(mappings) if mappings else 0
            ),
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to analyze file: {str(e)}")


@router.delete("/jobs/{job_id}")
async def cleanup_validation_job(job_id: str) -> dict[str, str]:
    """Clean up validation job and temporary files."""

    if job_id not in validation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = validation_jobs[job_id]

    # Remove temporary file
    if os.path.exists(job["file_path"]):
        os.unlink(job["file_path"])

    # Remove job from memory
    del validation_jobs[job_id]

    return {"message": "Job cleaned up successfully"}


@router.get("/jobs")
async def list_validation_jobs() -> dict[str, list[dict]]:
    """List all validation jobs with their status."""

    jobs_list = []
    for job_id, job in validation_jobs.items():
        jobs_list.append(
            {
                "job_id": job_id,
                "status": job["status"],
                "progress": job["progress"],
                "filename": job["filename"],
                "data_type": job["data_type"],
                "created_at": job["created_at"],
            }
        )

    return {"jobs": jobs_list}


# Background task functions
async def validate_fund_file_background(job_id: str, file_path: str):
    """Background task to validate fund data file."""

    try:
        # Update status
        validation_jobs[job_id]["status"] = "validating"
        validation_jobs[job_id]["progress"] = 10

        # Read file
        if file_path.lower().endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        validation_jobs[job_id]["progress"] = 30

        # Perform validation
        validation_result = DataValidator.validate_fund_data(df)

        validation_jobs[job_id]["progress"] = 80

        # Generate metadata
        metadata = DatasetMetadata(
            name=validation_jobs[job_id]["filename"],
            rows=len(df),
            columns=len(df.columns),
            date_range=(
                (df["date"].min(), df["date"].max())
                if "date" in df.columns
                else (None, None)
            ),
            data_quality_score=validation_result.overall_score,
            missing_data_percentage=df.isnull().sum().sum()
            / (len(df) * len(df.columns)),
            column_mappings=DataValidator.intelligent_column_mapping(
                df.columns.tolist(), "fund"
            ),
        )

        validation_jobs[job_id]["progress"] = 100
        validation_jobs[job_id]["status"] = "completed"
        validation_jobs[job_id]["result"] = {
            "validation_report": validation_result.dict(),
            "metadata": metadata.dict(),
            "preview_data": df.head(5).to_dict("records"),
        }

    except Exception as e:
        validation_jobs[job_id]["status"] = "failed"
        validation_jobs[job_id]["error"] = str(e)
        validation_jobs[job_id]["progress"] = 0


async def validate_index_file_background(job_id: str, file_path: str):
    """Background task to validate index data file."""

    try:
        validation_jobs[job_id]["status"] = "validating"
        validation_jobs[job_id]["progress"] = 10

        if file_path.lower().endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        validation_jobs[job_id]["progress"] = 30

        validation_result = DataValidator.validate_index_data(df)

        validation_jobs[job_id]["progress"] = 80

        metadata = DatasetMetadata(
            name=validation_jobs[job_id]["filename"],
            rows=len(df),
            columns=len(df.columns),
            date_range=(
                (df["date"].min(), df["date"].max())
                if "date" in df.columns
                else (None, None)
            ),
            data_quality_score=validation_result.overall_score,
            missing_data_percentage=df.isnull().sum().sum()
            / (len(df) * len(df.columns)),
            column_mappings=DataValidator.intelligent_column_mapping(
                df.columns.tolist(), "index"
            ),
        )

        validation_jobs[job_id]["progress"] = 100
        validation_jobs[job_id]["status"] = "completed"
        validation_jobs[job_id]["result"] = {
            "validation_report": validation_result.dict(),
            "metadata": metadata.dict(),
            "preview_data": df.head(5).to_dict("records"),
        }

    except Exception as e:
        validation_jobs[job_id]["status"] = "failed"
        validation_jobs[job_id]["error"] = str(e)
        validation_jobs[job_id]["progress"] = 0
