from pydantic import BaseModel


class PlanOut(BaseModel):
    id: int
    name: str
    trainings_per_month: int
    price_eur: float
    stripe_price_id: str | None

    model_config = {"from_attributes": True}
