from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.db.models import User
from app.schemas.subscription import SubscriptionOut
from app.schemas.token import TokenTransactionOut
from app.services.subscription_service import get_user_subscription, get_token_history

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/me", response_model=SubscriptionOut | None)
async def my_subscription(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_user_subscription(db, user.id)


@router.get("/tokens/history", response_model=list[TokenTransactionOut])
async def token_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_token_history(db, user.id)
