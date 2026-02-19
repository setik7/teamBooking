from pydantic import BaseModel
from datetime import datetime
from app.db.models import TokenReason


class TokenTransactionOut(BaseModel):
    id: int
    amount: int
    reason: TokenReason
    booking_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
