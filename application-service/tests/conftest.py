import os
import uuid

os.environ["DATABASE_URL"] = "postgresql+asyncpg://ccapp:change_me_strong_password@localhost:5432/test_application_db"
os.environ["JWT_SECRET_KEY"] = "test_secret_key_for_pytest_only"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["CREDIT_DECISION_SERVICE_URL"] = "http://localhost:8003"
os.environ["PORT"] = "8002"

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

TEST_DATABASE_URL = "postgresql+asyncpg://ccapp:change_me_strong_password@localhost:5432/test_application_db"


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    TestSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    yield

    await engine.dispose()
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def make_token(user_id: uuid.UUID | None = None) -> str:
    """
    Simulates a JWT that Auth Service would issue, without needing
    Auth Service to actually be running during these tests.
    """
    uid = str(user_id or uuid.uuid4())
    payload = {"user_id": uid}
    return jwt.encode(payload, "test_secret_key_for_pytest_only", algorithm="HS256")
