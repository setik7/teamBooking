from datetime import date, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Activity, TrainingSlot, Booking, BookingStatus
from app.schemas.activity import ActivityOut
from app.schemas.slot import WeekSlotOut


def _week_monday(week_start: date) -> date:
    """Return the Monday of the week containing week_start."""
    return week_start - timedelta(days=week_start.weekday())


async def get_week_slots(
    db: AsyncSession,
    week_start: date,
    user_id: int | None,
) -> list[WeekSlotOut]:
    """Expand recurring TrainingSlots into concrete dates for the Mon-Sun week
    that begins on (or contains) week_start, then enrich each slot with
    live booking counts and the requesting user's booking state.

    Args:
        db:         Async SQLAlchemy session.
        week_start: Any date inside (or the Monday of) the target week.
        user_id:    The authenticated user's ID, or None for anonymous access.

    Returns:
        A list of WeekSlotOut, one per (TrainingSlot × calendar-date) pair,
        sorted by date then start_time.
    """
    monday: date = _week_monday(week_start)
    sunday: date = monday + timedelta(days=6)

    # --- 1. Load all recurring TrainingSlots with their Activity eagerly -------
    slot_result = await db.execute(
        select(TrainingSlot)
        .where(TrainingSlot.recurring == True)  # noqa: E712
        .options(selectinload(TrainingSlot.activity))
        .order_by(TrainingSlot.day_of_week, TrainingSlot.start_time)
    )
    training_slots: list[TrainingSlot] = list(slot_result.scalars().all())

    if not training_slots:
        return []

    # --- 2. Determine the concrete date for every slot in the week -------------
    # day_of_week: 0 = Monday … 6 = Sunday, matching Python's date.weekday()
    slot_dates: list[tuple[TrainingSlot, date]] = [
        (ts, monday + timedelta(days=ts.day_of_week))
        for ts in training_slots
    ]

    # Collect the slot IDs so we can batch-query bookings in one round-trip.
    slot_ids = [ts.id for ts, _ in slot_dates]

    # --- 3. Count active (non-cancelled) bookings per (slot_id, date) ----------
    counts_result = await db.execute(
        select(
            Booking.training_slot_id,
            Booking.date,
            func.count(Booking.id).label("cnt"),
        )
        .where(
            Booking.training_slot_id.in_(slot_ids),
            Booking.date >= monday,
            Booking.date <= sunday,
            Booking.status != BookingStatus.cancelled,
        )
        .group_by(Booking.training_slot_id, Booking.date)
    )
    counts: dict[tuple[int, date], int] = {
        (row.training_slot_id, row.date): row.cnt
        for row in counts_result
    }

    # --- 4. Load this user's own bookings for the week (if authenticated) ------
    user_bookings: dict[tuple[int, date], int] = {}  # (slot_id, date) → booking.id
    if user_id is not None:
        user_result = await db.execute(
            select(Booking.training_slot_id, Booking.date, Booking.id)
            .where(
                Booking.user_id == user_id,
                Booking.training_slot_id.in_(slot_ids),
                Booking.date >= monday,
                Booking.date <= sunday,
                Booking.status != BookingStatus.cancelled,
            )
        )
        user_bookings = {
            (row.training_slot_id, row.date): row.id
            for row in user_result
        }

    # --- 5. Build the enriched output list ------------------------------------
    results: list[WeekSlotOut] = []
    for ts, slot_date in slot_dates:
        key = (ts.id, slot_date)
        booking_id = user_bookings.get(key)

        results.append(
            WeekSlotOut(
                slot_id=ts.id,
                activity=ActivityOut.model_validate(ts.activity),
                date=slot_date,
                start_time=ts.start_time,
                end_time=ts.end_time,
                participants_count=counts.get(key, 0),
                max_participants=ts.activity.max_participants,
                is_booked_by_user=booking_id is not None,
                booking_id=booking_id,
            )
        )

    return results
