"""
Upload file metadata model.
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class UploadFileMeta(SQLModel, table=True):
    """
    Model for storing uploaded file metadata.
    """
    __tablename__ = "upload_files"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    user: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    s3_key: Optional[str] = None  # optional future use 