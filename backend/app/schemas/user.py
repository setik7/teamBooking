from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.db.models import UserRole


class UserCreate(BaseModel):
    email: str
    name: str
    avatar: str | None = None
    oauth_provider: str
    oauth_id: str


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    avatar: str | None
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}
