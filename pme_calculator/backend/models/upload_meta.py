"""
Upload file metadata model.
"""

from datetime import datetime

from sqlmodel import Field, SQLModel


class UploadFileMeta(SQLModel, table=True):
    """
    Model for storing uploaded file metadata.
    """

    __tablename__ = "upload_files"

    id: int | None = Field(default=None, primary_key=True)
    filename: str
    user: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    s3_key: str | None = None  # optional future use
