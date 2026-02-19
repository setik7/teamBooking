"""Booking service with capacity checks, quota deduction, and token handling."""
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    Booking, BookingStatus, TrainingSlot, Subscription, SubscriptionStatus,
    TokenTransaction, TokenReason, Activity,
)


async def get_active_subscription(db: AsyncSession, user_id: int) -> Subscription | None:
    result = await db.execute(
        select(Subscription)
        .where(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.active,
        )
        .order_by(Subscription.period_end.desc())
    )
    return result.scalar_one_or_none()


async def count_slot_bookings(db: AsyncSession, slot_id: int, booking_date: date) -> int:
    result = await db.execute(
        select(func.count(Booking.id)).where(
            Booking.training_slot_id == slot_id,
            Booking.date == booking_date,
            Booking.status != BookingStatus.cancelled,
        )
    )
    return result.scalar() or 0


async def create_booking(db: AsyncSession, user_id: int, slot_id: int, booking_date: date) -> Booking:
    # Check slot exists (eager load activity for capacity check)
    slot_result = await db.execute(
        select(TrainingSlot)
        .options(selectinload(TrainingSlot.activity))
        .where(TrainingSlot.id == slot_id)
    )
    slot = slot_result.scalar_one_or_none()
    if not slot:
        raise ValueError("Training slot not found")

    # Check date matches slot's day_of_week
    if booking_date.weekday() != slot.day_of_week:
        raise ValueError("Date does not match the slot's day of week")

    # Check not already booked
    existing = await db.execute(
        select(Booking).where(
            Booking.user_id == user_id,
            Booking.training_slot_id == slot_id,
            Booking.date == booking_date,
            Booking.status != BookingStatus.cancelled,
        )
    )
    if existing.scalar_one_or_none():
        raise ValueError("Already booked for this slot")

    # Check capacity
    current_count = await count_slot_bookings(db, slot_id, booking_date)
    max_cap = slot.activity.max_participants if slot.activity else 999
    if current_count >= max_cap:
        raise ValueError("Slot is full")

    # Determine payment method: subscription trainings or tokens
    subscription = await get_active_subscription(db, user_id)
    booking_status = BookingStatus.confirmed
    used_token = False

    if subscription and subscription.trainings_remaining > 0:
        subscription.trainings_remaining -= 1
    elif subscription and subscription.tokens_balance > 0:
        subscription.tokens_balance -= 1
        booking_status = BookingStatus.token_used
        used_token = True
    else:
        raise ValueError("No subscription trainings or tokens available")

    booking = Booking(
        user_id=user_id,
        training_slot_id=slot_id,
        date=booking_date,
        status=booking_status,
    )
    db.add(booking)
    await db.flush()

    if used_token:
        db.add(TokenTransaction(
            user_id=user_id,
            amount=-1,
            reason=TokenReason.book_extra,
            booking_id=booking.id,
        ))

    return booking


async def cancel_booking(db: AsyncSession, user_id: int, booking_id: int) -> Booking:
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise ValueError("Booking not found")

    # IDOR protection
    if booking.user_id != user_id:
        raise ValueError("Booking not found")

    if booking.status == BookingStatus.cancelled:
        raise ValueError("Booking already cancelled")

    was_token_used = booking.status == BookingStatus.token_used
    booking.status = BookingStatus.cancelled

    subscription = await get_active_subscription(db, user_id)

    if was_token_used:
        # Refund the token
        if subscription:
            subscription.tokens_balance += 1
        db.add(TokenTransaction(
            user_id=user_id,
            amount=1,
            reason=TokenReason.cancel_refund,
            booking_id=booking.id,
        ))
    else:
        # Earn a token for cancelling a subscribed training
        if subscription:
            subscription.tokens_balance += 1
        db.add(TokenTransaction(
            user_id=user_id,
            amount=1,
            reason=TokenReason.skip,
            booking_id=booking.id,
        ))

    return booking


async def get_user_bookings(db: AsyncSession, user_id: int) -> list[Booking]:
    result = await db.execute(
        select(Booking)
        .where(Booking.user_id == user_id, Booking.status != BookingStatus.cancelled)
        .order_by(Booking.date.desc())
    )
    return list(result.scalars().all())
