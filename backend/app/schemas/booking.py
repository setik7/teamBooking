from pydantic import BaseModel
from datetime import date, datetime
from app.db.models import BookingStatus


class BookingCreate(BaseModel):
    training_slot_id: int
    date: date


class BookingOut(BaseModel):
    id: int
    training_slot_id: int
    date: date
    status: BookingStatus
    created_at: datetime
    activity_name: str | None = None

    model_config = {"from_attributes": True}
