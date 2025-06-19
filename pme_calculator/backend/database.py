"""
Database configuration and models for PME Calculator.
"""

# from datetime import datetime  # removed unused
from typing import Any

# Import our central timezone utility
from pme_calculator.utils.time import utc_now

try:
    from config import settings
except ImportError:
    from .config import settings
from logger import get_logger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, select

# Import UploadFileMeta from models package with proper fallback
UploadFileMeta = None
try:
    # Try importing from models package first
    from models import UploadFileMeta
except ImportError:
    try:
        # Try importing from models.upload_meta module
        from models.upload_meta import UploadFileMeta
    except ImportError:
        try:
            # Try importing from upload_meta directly
            from upload_meta import UploadFileMeta
        except ImportError:
            # Create a placeholder class if all imports fail
            class UploadFileMeta:
                def __init__(self, **kwargs):
                    for key, value in kwargs.items():
                        setattr(self, key, value)
                    self.id = None
                    self.filename = kwargs.get("filename", "")
                    self.user = kwargs.get("user", "anonymous")
                    self.created_at = utc_now()
                    self.s3_key = kwargs.get("s3_key")


logger = get_logger(__name__)

# Database configuration using typed settings
DATABASE_URL = settings.DATABASE_URL

# Create async engine
engine = create_async_engine(
    DATABASE_URL, echo=True, future=True  # Set to False in production
)

# Create async session factory
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session():
    """
    Dependency to get database session.
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    Initialize database tables.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise


async def get_upload_by_id(session: AsyncSession, upload_id: int) -> Any | None:
    """
    Get upload file metadata by ID.
    """
    try:
        if UploadFileMeta is None:
            return None
        result = await session.execute(
            select(UploadFileMeta).where(UploadFileMeta.id == upload_id)
        )
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error getting upload by ID {upload_id}: {e}")
        return None


async def get_uploads_by_user(
    session: AsyncSession, user: str = "anonymous", limit: int = 100
) -> list[Any]:
    """
    Get upload files for a specific user.
    """
    try:
        if UploadFileMeta is None:
            return []
        result = await session.execute(
            select(UploadFileMeta)
            .where(UploadFileMeta.user == user)
            .order_by(UploadFileMeta.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error getting uploads for user {user}: {e}")
        return []


async def create_upload_record(
    session: AsyncSession, upload_data: dict[str, Any]
) -> Any | None:
    """
    Create a new upload file record.
    """
    try:
        if UploadFileMeta is None:
            return None

        upload = UploadFileMeta(**upload_data)
        session.add(upload)
        await session.commit()
        await session.refresh(upload)
        logger.info(f"Created upload record with ID {upload.id}")
        return upload
    except Exception as e:
        logger.error(f"Error creating upload record: {e}")
        await session.rollback()
        return None


async def update_upload_record(
    session: AsyncSession, upload_id: int, update_data: dict[str, Any]
) -> Any | None:
    """
    Update an existing upload file record.
    """
    try:
        if UploadFileMeta is None:
            return None
        result = await session.execute(
            select(UploadFileMeta).where(UploadFileMeta.id == upload_id)
        )
        upload = result.scalar_one_or_none()

        if not upload:
            return None

        for key, value in update_data.items():
            setattr(upload, key, value)

        upload.updated_at = utc_now()
        await session.commit()
        await session.refresh(upload)

        logger.info(f"Updated upload record with ID {upload_id}")
        return upload
    except Exception as e:
        logger.error(f"Error updating upload record {upload_id}: {e}")
        await session.rollback()
        return None


async def delete_upload_record(session: AsyncSession, upload_id: int) -> bool:
    """
    Delete an upload file record.
    """
    try:
        if UploadFileMeta is None:
            return False
        result = await session.execute(
            select(UploadFileMeta).where(UploadFileMeta.id == upload_id)
        )
        upload = result.scalar_one_or_none()

        if not upload:
            return False

        await session.delete(upload)
        await session.commit()

        logger.info(f"Deleted upload record with ID {upload_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting upload record {upload_id}: {e}")
        await session.rollback()
        return False
