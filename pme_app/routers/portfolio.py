import io

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from pme_app.services.portfolio import calc_portfolio_metrics

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.post("/metrics")
async def portfolio_metrics(files: list[UploadFile] = File(...)):
    """
    Calculate portfolio metrics from multiple uploaded CSV files.
    Each file should contain fund data with Date and NAV columns.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    data = {}

    for f in files:
        try:
            # Read file content
            content = await f.read()

            # Reset file pointer for pandas
            f.file.seek(0)

            # Try to read as CSV
            try:
                df = pd.read_csv(io.StringIO(content.decode("utf-8")))
            except UnicodeDecodeError:
                # Try with different encoding
                df = pd.read_csv(io.StringIO(content.decode("latin-1")))

            if df.empty:
                continue

            # Store with filename as key
            filename = f.filename or f"fund_{len(data)}"
            data[filename] = df

        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Error processing file {f.filename}: {str(e)}"
            ) from None

    if not data:
        raise HTTPException(
            status_code=400, detail="No valid data found in uploaded files"
        )

    try:
        # Calculate portfolio metrics
        metrics_df = calc_portfolio_metrics(data)

        if metrics_df.empty:
            raise HTTPException(
                status_code=400, detail="Unable to calculate metrics from provided data"
            )

        # Convert to dict and return
        result = metrics_df.to_dict(orient="records")[0]

        # Add metadata
        result["files_processed"] = len(data)
        result["file_names"] = list(data.keys())

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error calculating portfolio metrics: {str(e)}"
        ) from None


@router.get("/health")
async def portfolio_health():
    """Health check for portfolio service."""
    return {"status": "healthy", "service": "portfolio"}


@router.post("/preview")
async def preview_portfolio_data(files: list[UploadFile] = File(...)):
    """
    Preview the structure of uploaded portfolio files without calculating metrics.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    preview_data = {}

    for f in files:
        try:
            content = await f.read()
            f.file.seek(0)

            try:
                df = pd.read_csv(io.StringIO(content.decode("utf-8")))
            except UnicodeDecodeError:
                df = pd.read_csv(io.StringIO(content.decode("latin-1")))

            filename = f.filename or f"fund_{len(preview_data)}"

            preview_data[filename] = {
                "rows": len(df),
                "columns": list(df.columns),
                "sample_data": (
                    df.head(3).to_dict(orient="records") if not df.empty else []
                ),
                "data_types": df.dtypes.astype(str).to_dict(),
            }

        except Exception as e:
            preview_data[f.filename or "unknown"] = {"error": str(e)}

    return {"files_processed": len(preview_data), "preview": preview_data}
