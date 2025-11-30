"""
Database Connection and Session Management
PostgreSQL and MongoDB connections
"""
try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    asyncpg = None

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    MOTOR_AVAILABLE = True
except ImportError:
    MOTOR_AVAILABLE = False
    AsyncIOMotorClient = None

from typing import Optional, Any
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager"""

    def __init__(self):
        self.postgres_pool: Optional[Any] = None
        self.mongo_client: Optional[Any] = None
        self.mongo_db = None

    async def connect(self):
        """Connect to all databases"""
        try:
            # PostgreSQL connection pool
            if ASYNCPG_AVAILABLE:
                self.postgres_pool = await asyncpg.create_pool(
                    host=settings.POSTGRES_SERVER,
                    port=5432,
                    user=settings.POSTGRES_USER,
                    password=settings.POSTGRES_PASSWORD,
                    database=settings.POSTGRES_DB,
                    min_size=5,
                    max_size=20
                )
                logger.info("Connected to PostgreSQL")
            else:
                logger.warning("asyncpg not available, PostgreSQL connection skipped")

            # MongoDB connection
            if MOTOR_AVAILABLE:
                self.mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
                self.mongo_db = self.mongo_client[settings.MONGODB_DB]
                logger.info("Connected to MongoDB")
            else:
                logger.warning("motor not available, MongoDB connection skipped")

        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    async def disconnect(self):
        """Disconnect from all databases"""
        if self.postgres_pool:
            await self.postgres_pool.close()
            logger.info("Disconnected from PostgreSQL")

        if self.mongo_client:
            self.mongo_client.close()
            logger.info("Disconnected from MongoDB")

    async def execute_query(self, query: str, *args):
        """Execute a PostgreSQL query"""
        async with self.postgres_pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def execute_one(self, query: str, *args):
        """Execute a PostgreSQL query and return one row"""
        async with self.postgres_pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def execute(self, query: str, *args):
        """Execute a PostgreSQL command (INSERT, UPDATE, DELETE)"""
        async with self.postgres_pool.acquire() as conn:
            return await conn.execute(query, *args)


# Global database instance
db = Database()


async def get_db():
    """Dependency for getting database instance"""
    return db
