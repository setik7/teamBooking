from pydantic import BaseModel


class ActivityOut(BaseModel):
    id: int
    name: str
    icon: str | None
    description: str | None
    max_participants: int
    duration_minutes: int

    model_config = {"from_attributes": True}
