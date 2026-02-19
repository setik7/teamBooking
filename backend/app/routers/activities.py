from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.db.models import Activity, User
from app.schemas.activity import ActivityOut
from app.schemas.slot import WeekSlotOut
from app.services.slot_service import get_week_slots

router = APIRouter(tags=["activities"])


def _current_monday() -> date:
    """Return the Monday of the current calendar week."""
    today = date.today()
    return today - timedelta(days=today.weekday())


@router.get("/activities", response_model=list[ActivityOut])
async def list_activities(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[ActivityOut]:
    """Return all activities available for booking."""
    result = await db.execute(select(Activity).order_by(Activity.name))
    activities = result.scalars().all()
    return [ActivityOut.model_validate(a) for a in activities]


@router.get("/slots/week", response_model=list[WeekSlotOut])
async def list_week_slots(
    week_start: date | None = Query(
        default=None,
        description="Any date within the desired week (ISO-8601, YYYY-MM-DD). "
                    "Defaults to the Monday of the current week.",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[WeekSlotOut]:
    """Return expanded training slots for the Mon-Sun week that contains
    *week_start* (or the current week when *week_start* is omitted), enriched
    with live participant counts and the caller's booking state.
    """
    resolved_week_start: date = week_start if week_start is not None else _current_monday()
    return await get_week_slots(db, resolved_week_start, current_user.id)
