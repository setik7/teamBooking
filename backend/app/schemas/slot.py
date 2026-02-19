from pydantic import BaseModel
from datetime import date, time
from app.schemas.activity import ActivityOut


class TrainingSlotOut(BaseModel):
    id: int
    activity: ActivityOut
    day_of_week: int
    start_time: time
    end_time: time
    recurring: bool

    model_config = {"from_attributes": True}


class WeekSlotOut(BaseModel):
    slot_id: int
    activity: ActivityOut
    date: date
    start_time: time
    end_time: time
    participants_count: int
    max_participants: int
    is_booked_by_user: bool
    booking_id: int | None = None
