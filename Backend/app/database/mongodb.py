"""
MongoDB async client lifecycle management using Motor.
The client is initialized once at app startup and closed at shutdown
via FastAPI lifespan context manager.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_client: AsyncIOMotorClient | None = None


async def connect_db() -> None:
    """Open Motor connection pool. Called in lifespan startup."""
    global _client
    _client = AsyncIOMotorClient(
        settings.mongodb_url,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
    )
    # Ping to verify connection
    await _client.admin.command("ping")
    logger.info("MongoDB connected", extra={"db": settings.mongodb_db_name})


async def close_db() -> None:
    """Close Motor connection pool. Called in lifespan shutdown."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
        logger.info("MongoDB connection closed.")


def get_database() -> AsyncIOMotorDatabase:
    """Return the application database. Raises if not connected."""
    if _client is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    return _client[settings.mongodb_db_name]
