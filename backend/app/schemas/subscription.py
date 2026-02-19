from pydantic import BaseModel
from datetime import date
from app.db.models import SubscriptionStatus
from app.schemas.plan import PlanOut


class SubscriptionOut(BaseModel):
    id: int
    plan: PlanOut
    status: SubscriptionStatus
    tokens_balance: int
    trainings_remaining: int
    period_start: date
    period_end: date

    model_config = {"from_attributes": True}
