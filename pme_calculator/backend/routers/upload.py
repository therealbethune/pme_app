"""
FastAPI upload router with comprehensive file validation.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import tempfile
import uuid
from pathlib import Path
import shutil
import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession

from validation.file_check_simple import validate_file_comprehensive
from validation.schemas_simple import ValidationResult, UploadResponse, AnalysisRequest, AnalysisResponse
from logger import get_logger
from datetime import datetime

# Make database imports optional
try:
    from models.upload_meta import UploadFileMeta
    from database import get_session
    DATABASE_AVAILABLE = True
except ImportError as e:
    logger = get_logger(__name__)
    logger.warning(f"Database dependencies not available in upload router: {e}")
    DATABASE_AVAILABLE = False
    UploadFileMeta = None
    
    # Create dummy get_session function
    async def get_session():
        yield None

logger = get_logger(__name__)
router = APIRouter(prefix="/v1/uploads", tags=["upload"])

# File validation constants
MAX_MB = 20
ALLOWED = {"text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}

# In-memory storage for uploaded files (replace with Redis/DB in production)
uploaded_files: Dict[str, Dict[str, Any]] = {}


# UploadResponse now imported from schemas_simple


@router.post("/fund", response_model=UploadResponse)
async def upload_fund_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Fund cashflow file (CSV/Excel)")
):
    """
    Upload and validate fund cashflow file.
    Returns validation results and file ID for subsequent analysis.
    """
    file_id = str(uuid.uuid4())
    
    logger.info(f"Upload request started", extra={
        "file_id": file_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "file_size": file.size if hasattr(file, 'size') else "unknown"
    })
    
    # Basic file checks
    if not file.filename:
        raise HTTPException(400, detail="No filename provided")
    
    # Content type validation
    if file.content_type not in ALLOWED:
        raise HTTPException(415, detail=f"Unsupported media type. Allowed: {', '.join(ALLOWED)}")
    
    # File size validation
    if hasattr(file, 'size') and file.size > MAX_MB * 1024 ** 2:
        raise HTTPException(413, detail=f"File too large. Maximum size: {MAX_MB}MB")
    
    allowed_extensions = {'.csv', '.xlsx', '.xls'}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(400, detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}")
    
    # Create temporary file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_path = Path(tmp_file.name)
            
        # Read and save uploaded content asynchronously
        content = await file.read()
        
        # Check file size if not available from file object
        if len(content) > MAX_MB * 1024 ** 2:
            raise HTTPException(413, detail=f"File too large. Maximum size: {MAX_MB}MB")
        
        async with aiofiles.open(tmp_path, 'wb') as f:
            await f.write(content)
            
        logger.info(f"File saved to temporary location", extra={
            "file_id": file_id,
            "temp_path": str(tmp_path),
            "file_size": len(content)
        })
        
        # Validate file
        validation_result = validate_file_comprehensive(tmp_path, 'fund')
        
        if validation_result.is_valid:
            # Store file info for later analysis
            uploaded_files[file_id] = {
                'filename': file.filename,
                'temp_path': str(tmp_path),
                'file_type': 'fund',
                'validation': validation_result,
                'upload_timestamp': datetime.utcnow().isoformat()
            }
            
            # Insert UploadFileMeta row if database is available
            upload_meta = None
            if DATABASE_AVAILABLE and UploadFileMeta:
                # Skip database operations for now - running in memory mode
                pass
            
            logger.info(f"Fund file validated successfully", extra={
                "file_id": file_id,
                "upload_id": upload_meta.id if upload_meta else None,
                "row_count": validation_result.metadata.row_count if validation_result.metadata else None,
                "detected_columns": validation_result.detected_mappings
            })
            
            message = f"Fund file uploaded and validated successfully. {validation_result.metadata.row_count if validation_result.metadata else 'Unknown'} rows detected."
            
        else:
            # Clean up temp file on validation failure
            background_tasks.add_task(cleanup_temp_file, tmp_path)
            
            logger.warning(f"Fund file validation failed", extra={
                "file_id": file_id,
                "errors": validation_result.errors,
                "warnings": validation_result.warnings
            })
            
            message = f"File validation failed with {len(validation_result.errors)} errors."
        
        return UploadResponse(
            success=validation_result.is_valid,
            file_id=file_id,
            filename=file.filename,
            validation=validation_result,
            message=message
        )
        
    except Exception as e:
        logger.error(f"Upload processing failed", extra={
            "file_id": file_id,
            "error": str(e)
        })
        
        # Clean up temp file on error
        if 'tmp_path' in locals():
            background_tasks.add_task(cleanup_temp_file, tmp_path)
        
        raise HTTPException(500, detail=f"File processing failed: {str(e)}")


@router.post("/index", response_model=UploadResponse)  
async def upload_index_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Index price file (CSV/Excel)")
):
    """
    Upload and validate index price file.
    Returns validation results and file ID for subsequent analysis.
    """
    file_id = str(uuid.uuid4())
    
    logger.info(f"Index upload request started", extra={
        "file_id": file_id,
        "filename": file.filename,
        "content_type": file.content_type
    })
    
    # Basic file checks
    if not file.filename:
        raise HTTPException(400, detail="No filename provided")
    
    # Content type validation
    if file.content_type not in ALLOWED:
        raise HTTPException(415, detail=f"Unsupported media type. Allowed: {', '.join(ALLOWED)}")
    
    # File size validation
    if hasattr(file, 'size') and file.size > MAX_MB * 1024 ** 2:
        raise HTTPException(413, detail=f"File too large. Maximum size: {MAX_MB}MB")
    
    allowed_extensions = {'.csv', '.xlsx', '.xls'}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(400, detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}")
    
    # Create temporary file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_path = Path(tmp_file.name)
            
        # Read and save uploaded content asynchronously
        content = await file.read()
        
        # Check file size if not available from file object
        if len(content) > MAX_MB * 1024 ** 2:
            raise HTTPException(413, detail=f"File too large. Maximum size: {MAX_MB}MB")
        
        async with aiofiles.open(tmp_path, 'wb') as f:
            await f.write(content)
            
        logger.info(f"Index file saved to temporary location", extra={
            "file_id": file_id,
            "temp_path": str(tmp_path),
            "file_size": len(content)
        })
        
        # Validate file
        validation_result = validate_file_comprehensive(tmp_path, 'index')
        
        if validation_result.is_valid:
            # Store file info for later analysis
            uploaded_files[file_id] = {
                'filename': file.filename,
                'temp_path': str(tmp_path),
                'file_type': 'index',
                'validation': validation_result,
                'upload_timestamp': datetime.utcnow().isoformat()
            }
            
            # Insert UploadFileMeta row if database is available
            upload_meta = None
            if DATABASE_AVAILABLE and UploadFileMeta:
                # Skip database operations for now - running in memory mode
                pass
            
            logger.info(f"Index file validated successfully", extra={
                "file_id": file_id,
                "upload_id": upload_meta.id if upload_meta else None,
                "row_count": validation_result.metadata.row_count if validation_result.metadata else None,
                "detected_columns": validation_result.detected_mappings
            })
            
            message = f"Index file uploaded and validated successfully. {validation_result.metadata.row_count if validation_result.metadata else 'Unknown'} rows detected."
            
        else:
            # Clean up temp file on validation failure
            background_tasks.add_task(cleanup_temp_file, tmp_path)
            
            logger.warning(f"Index file validation failed", extra={
                "file_id": file_id,
                "errors": validation_result.errors,
                "warnings": validation_result.warnings
            })
            
            message = f"File validation failed with {len(validation_result.errors)} errors."
        
        return UploadResponse(
            success=validation_result.is_valid,
            file_id=file_id,
            filename=file.filename,
            validation=validation_result,
            message=message
        )
        
    except Exception as e:
        logger.error(f"Index upload processing failed", extra={
            "file_id": file_id,
            "error": str(e)
        })
        
        # Clean up temp file on error
        if 'tmp_path' in locals():
            background_tasks.add_task(cleanup_temp_file, tmp_path)
        
        raise HTTPException(500, detail=f"File processing failed: {str(e)}")


@router.get("")
async def get_uploads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Get paginated list of uploaded files.
    """
    try:
        # Return empty list when database is not available
        if not DATABASE_AVAILABLE or UploadFileMeta is None:
            return []
        
        # For now, return empty list - database operations disabled
        return []
        
    except Exception as e:
        logger.error(f"Failed to get uploads: {e}", exc_info=True)
        raise HTTPException(500, detail="Failed to retrieve uploads")


@router.get("/{upload_id}")
async def get_upload(
    upload_id: int
):
    """
    Get upload file metadata by ID.
    """
    try:
        # Return not found when database is not available
        if not DATABASE_AVAILABLE or UploadFileMeta is None:
            raise HTTPException(404, detail="Upload not found")
        
        # For now, return not found - database operations disabled
        raise HTTPException(404, detail="Upload not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get upload {upload_id}: {e}", exc_info=True)
        raise HTTPException(500, detail="Failed to retrieve upload")


@router.get("/files")
async def list_uploaded_files():
    """
    List all uploaded files currently in memory.
    This endpoint provides information about files available for analysis.
    """
    try:
        files_info = []
        for file_id, file_data in uploaded_files.items():
            files_info.append({
                'file_id': file_id,
                'filename': file_data['filename'],
                'file_type': file_data['file_type'],
                'upload_timestamp': file_data['upload_timestamp'],
                'is_valid': file_data['validation'].is_valid,
                'row_count': file_data['validation'].metadata.row_count if file_data['validation'].metadata else None
            })
        
        return JSONResponse({
            'success': True,
            'files': files_info,
            'total_files': len(files_info)
        })
        
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        raise HTTPException(500, detail="Failed to retrieve file list")


@router.get("/files/{file_id}")
async def get_file_info(file_id: str):
    """
    Get detailed information about a specific uploaded file.
    """
    if file_id not in uploaded_files:
        raise HTTPException(404, detail="File not found")
    
    try:
        file_data = uploaded_files[file_id]
        return JSONResponse({
            'success': True,
            'file_info': file_data
        })
        
    except Exception as e:
        logger.error(f"Failed to get file info for {file_id}: {e}")
        raise HTTPException(500, detail="Failed to retrieve file information")


@router.delete("/files/{file_id}")
async def delete_uploaded_file(file_id: str, background_tasks: BackgroundTasks):
    """
    Delete an uploaded file from memory and clean up temporary files.
    """
    if file_id not in uploaded_files:
        raise HTTPException(404, detail="File not found")
    
    try:
        file_data = uploaded_files[file_id]
        temp_path = Path(file_data['temp_path'])
        
        # Schedule cleanup of temporary file
        background_tasks.add_task(cleanup_temp_file, temp_path)
        
        # Remove from memory
        del uploaded_files[file_id]
        
        logger.info(f"File {file_id} deleted successfully")
        
        return JSONResponse({
            'success': True,
            'message': f'File {file_data["filename"]} deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to delete file {file_id}: {e}")
        raise HTTPException(500, detail="Failed to delete file")


async def cleanup_temp_file(file_path: Path):
    """
    Background task to clean up temporary files.
    """
    try:
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Temporary file cleaned up: {file_path}")
    except Exception as e:
        logger.error(f"Failed to cleanup temporary file {file_path}: {e}") 