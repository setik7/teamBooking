"""Shared test fixtures."""
import asyncio
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.db.models import User, UserRole, Plan, Subscription, SubscriptionStatus, Activity, TrainingSlot
from app.auth.jwt import create_access_token
from datetime import date, time, timedelta


# Use in-memory SQLite for tests
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DB_URL, echo=False)
test_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_session() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db):
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db):
    user = User(
        email="test@example.com", name="Test User",
        oauth_provider="github", oauth_id="12345", role=UserRole.member,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db):
    user = User(
        email="admin@example.com", name="Admin User",
        oauth_provider="github", oauth_id="99999", role=UserRole.admin,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user):
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(admin_user):
    token = create_access_token({"sub": str(admin_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def sample_activity(db):
    activity = Activity(
        name="Swimming", icon="🏊", description="Pool training",
        max_participants=15, duration_minutes=60,
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


@pytest_asyncio.fixture
async def sample_slot(db, sample_activity):
    slot = TrainingSlot(
        activity_id=sample_activity.id,
        day_of_week=date.today().weekday(),
        start_time=time(9, 0),
        end_time=time(10, 0),
        recurring=True,
    )
    db.add(slot)
    await db.commit()
    await db.refresh(slot)
    return slot


@pytest_asyncio.fixture
async def sample_plan(db):
    plan = Plan(name="Standard", trainings_per_month=12, price_eur=69.0)
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


@pytest_asyncio.fixture
async def active_subscription(db, test_user, sample_plan):
    sub = Subscription(
        user_id=test_user.id, plan_id=sample_plan.id,
        status=SubscriptionStatus.active, tokens_balance=3,
        trainings_remaining=10,
        period_start=date.today(), period_end=date.today() + timedelta(days=30),
    )
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return sub
