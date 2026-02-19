"""Booking security tests - IDOR, capacity bypass, double-booking."""
import pytest
from datetime import date, timedelta
from app.db.models import User, UserRole, Booking, BookingStatus, Subscription, SubscriptionStatus
from app.auth.jwt import create_access_token

pytestmark = pytest.mark.asyncio


async def test_book_training_success(client, auth_headers, sample_slot, active_subscription):
    today = date.today()
    # Find next date matching slot's day_of_week
    target = today
    while target.weekday() != sample_slot.day_of_week:
        target += timedelta(days=1)

    resp = await client.post("/bookings", json={
        "training_slot_id": sample_slot.id,
        "date": target.isoformat(),
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "confirmed"


async def test_double_booking_blocked(client, auth_headers, sample_slot, active_subscription):
    today = date.today()
    target = today
    while target.weekday() != sample_slot.day_of_week:
        target += timedelta(days=1)

    # First booking
    await client.post("/bookings", json={
        "training_slot_id": sample_slot.id,
        "date": target.isoformat(),
    }, headers=auth_headers)

    # Second booking should fail
    resp = await client.post("/bookings", json={
        "training_slot_id": sample_slot.id,
        "date": target.isoformat(),
    }, headers=auth_headers)
    assert resp.status_code == 400
    assert "Already booked" in resp.json()["detail"]


async def test_booking_without_subscription(client, auth_headers, sample_slot):
    """User without subscription cannot book."""
    today = date.today()
    target = today
    while target.weekday() != sample_slot.day_of_week:
        target += timedelta(days=1)

    resp = await client.post("/bookings", json={
        "training_slot_id": sample_slot.id,
        "date": target.isoformat(),
    }, headers=auth_headers)
    assert resp.status_code == 400
    assert "No subscription" in resp.json()["detail"]


async def test_idor_cancel_other_users_booking(
    client, db, auth_headers, sample_slot, active_subscription, test_user
):
    """User cannot cancel another user's booking."""
    today = date.today()
    target = today
    while target.weekday() != sample_slot.day_of_week:
        target += timedelta(days=1)

    # Create booking for test user
    resp = await client.post("/bookings", json={
        "training_slot_id": sample_slot.id,
        "date": target.isoformat(),
    }, headers=auth_headers)
    booking_id = resp.json()["id"]

    # Create another user
    other_user = User(
        email="other@test.com", name="Other",
        oauth_provider="github", oauth_id="other123", role=UserRole.member,
    )
    db.add(other_user)
    await db.commit()
    await db.refresh(other_user)

    other_token = create_access_token({"sub": str(other_user.id)})
    other_headers = {"Authorization": f"Bearer {other_token}"}

    # Try to cancel first user's booking
    resp = await client.delete(f"/bookings/{booking_id}", headers=other_headers)
    assert resp.status_code == 400
    assert "not found" in resp.json()["detail"].lower()


async def test_wrong_day_of_week_rejected(client, auth_headers, sample_slot, active_subscription):
    """Cannot book a slot for wrong day of week."""
    # Pick a date that doesn't match the slot's day_of_week
    target = date.today()
    while target.weekday() == sample_slot.day_of_week:
        target += timedelta(days=1)

    resp = await client.post("/bookings", json={
        "training_slot_id": sample_slot.id,
        "date": target.isoformat(),
    }, headers=auth_headers)
    assert resp.status_code == 400
    assert "day of week" in resp.json()["detail"].lower()


async def test_nonexistent_slot_rejected(client, auth_headers, active_subscription):
    resp = await client.post("/bookings", json={
        "training_slot_id": 99999,
        "date": date.today().isoformat(),
    }, headers=auth_headers)
    assert resp.status_code == 400


async def test_cancel_returns_token(client, auth_headers, sample_slot, active_subscription, db):
    today = date.today()
    target = today
    while target.weekday() != sample_slot.day_of_week:
        target += timedelta(days=1)

    resp = await client.post("/bookings", json={
        "training_slot_id": sample_slot.id,
        "date": target.isoformat(),
    }, headers=auth_headers)
    booking_id = resp.json()["id"]

    # Cancel
    resp = await client.delete(f"/bookings/{booking_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"

    # Check token was credited
    await db.refresh(active_subscription)
    assert active_subscription.tokens_balance == 4  # Was 3, now 4
