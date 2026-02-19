"""Integration tests - full booking flow with token economy."""
import pytest
from datetime import date, timedelta
from app.db.models import User, UserRole, Plan, Subscription, SubscriptionStatus, Activity, TrainingSlot
from app.auth.jwt import create_access_token

pytestmark = pytest.mark.asyncio


async def test_full_booking_flow(client, db):
    """Full flow: create user → subscribe → book → cancel → earn token → rebook with token."""

    # 1. Create user
    user = User(
        email="flow@test.com", name="Flow Tester",
        oauth_provider="github", oauth_id="flow123", role=UserRole.member,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    headers = {"Authorization": f"Bearer {create_access_token({'sub': str(user.id)})}"}

    # 2. Create plan + subscription
    plan = Plan(name="FlowPlan", trainings_per_month=12, price_eur=69.0)
    db.add(plan)
    await db.commit()
    await db.refresh(plan)

    sub = Subscription(
        user_id=user.id, plan_id=plan.id,
        status=SubscriptionStatus.active, tokens_balance=0,
        trainings_remaining=12,
        period_start=date.today(), period_end=date.today() + timedelta(days=30),
    )
    db.add(sub)
    await db.commit()
    await db.refresh(sub)

    # 3. Create activity + slot
    activity = Activity(
        name="FlowSwim", icon="🏊", description="Test",
        max_participants=15, duration_minutes=60,
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)

    from datetime import time
    slot = TrainingSlot(
        activity_id=activity.id,
        day_of_week=date.today().weekday(),
        start_time=time(9, 0), end_time=time(10, 0),
        recurring=True,
    )
    db.add(slot)
    await db.commit()
    await db.refresh(slot)

    today = date.today()

    # 4. Book a training (uses subscription)
    resp = await client.post("/bookings", json={
        "training_slot_id": slot.id,
        "date": today.isoformat(),
    }, headers=headers)
    assert resp.status_code == 200
    booking = resp.json()
    assert booking["status"] == "confirmed"
    booking_id = booking["id"]

    # Check trainings decremented
    await db.refresh(sub)
    assert sub.trainings_remaining == 11

    # 5. Cancel → earn token
    resp = await client.delete(f"/bookings/{booking_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"

    await db.refresh(sub)
    assert sub.tokens_balance == 1

    # 6. Rebook with token (trainings still at 11, use the token by setting remaining to 0 first)
    sub.trainings_remaining = 0
    await db.commit()

    resp = await client.post("/bookings", json={
        "training_slot_id": slot.id,
        "date": today.isoformat(),
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "token_used"

    await db.refresh(sub)
    assert sub.tokens_balance == 0

    # 7. Check my bookings
    resp = await client.get("/bookings/mine", headers=headers)
    assert resp.status_code == 200
    bookings = resp.json()
    assert len(bookings) == 1
    assert bookings[0]["status"] == "token_used"


async def test_subscription_endpoint(client, db, test_user, auth_headers, sample_plan, active_subscription):
    """GET /subscriptions/me returns active subscription."""
    resp = await client.get("/subscriptions/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "active"
    assert data["trainings_remaining"] == 10
    assert data["tokens_balance"] == 3


async def test_token_history_endpoint(client, db, test_user, auth_headers, sample_plan, active_subscription, sample_slot):
    """Token history tracks transactions."""
    today = date.today()
    target = today
    while target.weekday() != sample_slot.day_of_week:
        target += timedelta(days=1)

    # Book then cancel to generate token transaction
    resp = await client.post("/bookings", json={
        "training_slot_id": sample_slot.id,
        "date": target.isoformat(),
    }, headers=auth_headers)
    booking_id = resp.json()["id"]

    await client.delete(f"/bookings/{booking_id}", headers=auth_headers)

    resp = await client.get("/subscriptions/tokens/history", headers=auth_headers)
    assert resp.status_code == 200
    history = resp.json()
    assert len(history) >= 1
    assert history[0]["amount"] == 1
    assert history[0]["reason"] == "skip"


async def test_activities_endpoint(client, auth_headers, sample_activity):
    """GET /activities returns list."""
    resp = await client.get("/activities", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Swimming"


async def test_weekly_slots_endpoint(client, auth_headers, sample_slot):
    """GET /slots/week returns expanded slots."""
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    resp = await client.get(f"/slots/week?week_start={monday.isoformat()}", headers=auth_headers)
    assert resp.status_code == 200
    slots = resp.json()
    assert len(slots) >= 1
    assert slots[0]["participants_count"] == 0
    assert slots[0]["is_booked_by_user"] is False
