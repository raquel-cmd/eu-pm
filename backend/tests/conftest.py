"""Test configuration and fixtures."""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.database import Base

# Import all models so metadata knows about them
from app.models import *  # noqa: F401, F403

# Use a separate test database - replace only the database name at end of URL
TEST_DB_URL = settings.database_url.rsplit("/", 1)[0] + "/eupm_test"


@pytest_asyncio.fixture
async def db():
    """Provide a database session that rolls back after each test.

    Creates a fresh engine per test to avoid event loop conflicts.
    NullPool ensures no connections persist across tests.
    """
    engine = create_async_engine(TEST_DB_URL, echo=False, poolclass=NullPool)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        async with session.begin():
            yield session
            await session.rollback()

    await engine.dispose()
