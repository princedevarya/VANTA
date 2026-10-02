import sys
from pathlib import Path

import pytest_asyncio

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import Base


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )

    @event.listens_for(
        engine.sync_engine,
        "connect",
    )
    def enable_sqlite_foreign_keys(
        dbapi_connection,
        connection_record,
    ):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session

    await engine.dispose()