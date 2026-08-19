"""
Database connection and session management.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from config import settings

# Convert postgresql:// to postgresql+asyncpg://
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine with fast connection timeout
try:
    if "asyncpg" in database_url:
        engine = create_async_engine(
            database_url,
            echo=settings.DEBUG,
            future=True,
            connect_args={"timeout": 2}
        )
    else:
        engine = create_async_engine(database_url, echo=settings.DEBUG, future=True)
except Exception:
    # SQLite in-memory/file fallback for standalone execution without Postgres
    engine = create_async_engine("sqlite+aiosqlite:///./karna_kavach.db", echo=False)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency for getting database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
