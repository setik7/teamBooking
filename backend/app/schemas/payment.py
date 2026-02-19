from pydantic import BaseModel
from datetime import datetime
from app.db.models import PaymentStatus


class PaymentOut(BaseModel):
    id: int
    stripe_session_id: str
    amount: float
    status: PaymentStatus
    created_at: datetime

    model_config = {"from_attributes": True}
