"""Idempotent seed script for plans, activities, and training slots."""
import asyncio
import datetime
from sqlalchemy import select
from app.database import async_session, create_tables
from app.db.models import Plan, Activity, TrainingSlot


PLANS = [
    {"name": "Starter", "trainings_per_month": 8, "price_eur": 49.0},
    {"name": "Standard", "trainings_per_month": 12, "price_eur": 69.0},
    {"name": "Unlimited", "trainings_per_month": 999, "price_eur": 99.0},
]

ACTIVITIES = [
    {"name": "Swimming", "icon": "🏊", "description": "Pool training session", "max_participants": 15, "duration_minutes": 60},
    {"name": "Running", "icon": "🏃", "description": "Group running session", "max_participants": 25, "duration_minutes": 45},
    {"name": "Gym", "icon": "🏋️", "description": "Gym workout with trainer", "max_participants": 20, "duration_minutes": 60},
    {"name": "Cycling", "icon": "🚴", "description": "Indoor cycling class", "max_participants": 18, "duration_minutes": 50},
    {"name": "Yoga", "icon": "🧘", "description": "Yoga and stretching", "max_participants": 20, "duration_minutes": 60},
    {"name": "HIIT", "icon": "💪", "description": "High-intensity interval training", "max_participants": 16, "duration_minutes": 30},
]

# (activity_name, day_of_week, start_time, end_time)
SLOTS = [
    # Monday
    ("Swimming", 0, "06:30", "07:30"),
    ("Gym", 0, "07:00", "08:00"),
    ("HIIT", 0, "12:00", "12:30"),
    ("Yoga", 0, "18:00", "19:00"),
    # Tuesday
    ("Running", 1, "06:00", "06:45"),
    ("Cycling", 1, "12:00", "12:50"),
    ("Swimming", 1, "17:30", "18:30"),
    ("Gym", 1, "18:00", "19:00"),
    # Wednesday
    ("HIIT", 2, "07:00", "07:30"),
    ("Yoga", 2, "12:00", "13:00"),
    ("Cycling", 2, "17:00", "17:50"),
    # Thursday
    ("Swimming", 3, "06:30", "07:30"),
    ("Running", 3, "12:00", "12:45"),
    ("Gym", 3, "17:00", "18:00"),
    ("HIIT", 3, "18:00", "18:30"),
    # Friday
    ("Cycling", 4, "07:00", "07:50"),
    ("Yoga", 4, "12:00", "13:00"),
    ("Swimming", 4, "17:30", "18:30"),
    # Saturday
    ("Running", 5, "08:00", "08:45"),
    ("Gym", 5, "09:00", "10:00"),
    ("HIIT", 5, "10:00", "10:30"),
    # Sunday
    ("Yoga", 6, "09:00", "10:00"),
    ("Swimming", 6, "10:00", "11:00"),
]


def parse_time(t: str) -> datetime.time:
    h, m = t.split(":")
    return datetime.time(int(h), int(m))


async def seed():
    await create_tables()

    async with async_session() as session:
        # Seed plans
        for p in PLANS:
            existing = await session.execute(select(Plan).where(Plan.name == p["name"]))
            if not existing.scalar_one_or_none():
                session.add(Plan(**p))
        await session.commit()

        # Seed activities
        for a in ACTIVITIES:
            existing = await session.execute(select(Activity).where(Activity.name == a["name"]))
            if not existing.scalar_one_or_none():
                session.add(Activity(**a))
        await session.commit()

        # Seed training slots
        activities = {}
        result = await session.execute(select(Activity))
        for act in result.scalars():
            activities[act.name] = act.id

        existing_slots = await session.execute(select(TrainingSlot))
        existing_count = len(existing_slots.all())

        if existing_count == 0:
            for act_name, dow, start, end in SLOTS:
                session.add(TrainingSlot(
                    activity_id=activities[act_name],
                    day_of_week=dow,
                    start_time=parse_time(start),
                    end_time=parse_time(end),
                    recurring=True,
                ))
            await session.commit()

    print(f"Seeded {len(PLANS)} plans, {len(ACTIVITIES)} activities, {len(SLOTS)} slots.")


if __name__ == "__main__":
    asyncio.run(seed())
