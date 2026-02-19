"""Subscription management with auto-renewal logic."""
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    Subscription, SubscriptionStatus, TokenTransaction, TokenReason,
)


async def get_user_subscription(db: AsyncSession, user_id: int) -> Subscription | None:
    result = await db.execute(
        select(Subscription)
        .options(selectinload(Subscription.plan))
        .where(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.active,
        )
        .order_by(Subscription.period_end.desc())
    )
    sub = result.scalar_one_or_none()

    if sub and sub.period_end < date.today():
        # Auto-renew: reset trainings, keep tokens, extend period
        sub.trainings_remaining = sub.plan.trainings_per_month
        sub.period_start = date.today()
        sub.period_end = date.today() + timedelta(days=30)
        await db.flush()

    return sub


async def get_token_history(db: AsyncSession, user_id: int) -> list[TokenTransaction]:
    result = await db.execute(
        select(TokenTransaction)
        .where(TokenTransaction.user_id == user_id)
        .order_by(TokenTransaction.created_at.desc())
        .limit(50)
    )
    return list(result.scalars().all())


async def activate_subscription(
    db: AsyncSession, user_id: int, plan_id: int, trainings_per_month: int
) -> Subscription:
    # Deactivate any existing active subscription
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.active,
        )
    )
    for old_sub in result.scalars():
        old_sub.status = SubscriptionStatus.expired

    sub = Subscription(
        user_id=user_id,
        plan_id=plan_id,
        status=SubscriptionStatus.active,
        tokens_balance=0,
        trainings_remaining=trainings_per_month,
        period_start=date.today(),
        period_end=date.today() + timedelta(days=30),
    )
    db.add(sub)
    await db.flush()
    return sub


async def credit_tokens(db: AsyncSession, user_id: int, amount: int) -> None:
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.active,
        )
    )
    sub = result.scalar_one_or_none()
    if sub:
        sub.tokens_balance += amount

    db.add(TokenTransaction(
        user_id=user_id,
        amount=amount,
        reason=TokenReason.purchase,
    ))
