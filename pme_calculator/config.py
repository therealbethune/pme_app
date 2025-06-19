"""
Typed configuration management using Pydantic Settings.
Replaces scattered os.getenv() calls with type-safe configuration.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with type validation and environment variable support."""

    # Database Configuration
    DATABASE_URL: str = "postgresql://user:password@localhost/pme_db"
    REQUIRE_DATABASE: bool = False

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"

    # DuckDB Configuration
    DUCKDB_PATH: str | None = None

    # Server Configuration
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Development Settings
    DEBUG: bool = False
    RELOAD: bool = True

    # Performance Settings
    CACHE_TTL: int = 3600  # 1 hour
    MAX_WORKERS: int = 4

    # Security Settings
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",  # Allow additional environment variables
    )


class DevelopmentSettings(Settings):
    """Development-specific settings."""

    DEBUG: bool = True
    RELOAD: bool = True


class ProductionSettings(Settings):
    """Production-specific settings."""

    DEBUG: bool = False
    RELOAD: bool = False
    SECRET_KEY: str  # Must be provided in production


def get_settings() -> Settings:
    """Get settings instance based on environment."""
    import os

    env = os.getenv("ENVIRONMENT", "development").lower()

    if env == "production":
        return ProductionSettings()
    else:
        return DevelopmentSettings()


# Global settings instance
settings = get_settings()
