import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import get_settings
from app.auth.dependencies import get_current_user
from app.db.models import User, Plan, Payment, PaymentStatus
from app.services.subscription_service import activate_subscription, credit_tokens
from app.middleware.rate_limiter import limiter, PAYMENT_LIMIT

router = APIRouter(tags=["payments"])
settings = get_settings()

if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key


@router.post("/checkout/subscribe")
@limiter.limit(PAYMENT_LIMIT)
async def checkout_subscribe(
    request: Request,
    plan_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    result = await db.execute(select(Plan).where(Plan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {"name": f"TeamBooking - {plan.name}"},
                    "unit_amount": int(plan.price_eur * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{settings.frontend_url}/plans?success=1&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.frontend_url}/plans?cancelled=1",
            metadata={"user_id": str(user.id), "plan_id": str(plan.id), "type": "subscription"},
        )
    except Exception:
        raise HTTPException(status_code=502, detail="Payment processing error")

    db.add(Payment(
        user_id=user.id,
        stripe_session_id=session.id,
        amount=plan.price_eur,
        status=PaymentStatus.pending,
    ))

    return {"checkout_url": session.url}


@router.post("/checkout/tokens")
@limiter.limit(PAYMENT_LIMIT)
async def checkout_tokens(
    request: Request,
    amount: int = 5,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    price_per_token = 5.0
    total = amount * price_per_token

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {"name": f"TeamBooking - {amount} Tokens"},
                    "unit_amount": int(total * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{settings.frontend_url}/subscription?tokens_success=1&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.frontend_url}/subscription?cancelled=1",
            metadata={"user_id": str(user.id), "token_amount": str(amount), "type": "tokens"},
        )
    except Exception:
        raise HTTPException(status_code=502, detail="Payment processing error")

    db.add(Payment(
        user_id=user.id,
        stripe_session_id=session.id,
        amount=total,
        status=PaymentStatus.pending,
    ))

    return {"checkout_url": session.url}


@router.post("/checkout/fulfill")
async def fulfill_checkout(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """After Stripe redirects back, frontend calls this to fulfill the payment.
    Checks the Stripe session status and activates subscription/tokens."""
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    # Retrieve the session from Stripe to verify payment
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    if session.payment_status != "paid":
        raise HTTPException(status_code=400, detail="Payment not completed")

    metadata = session.metadata or {}

    # Verify the session belongs to this user
    if metadata.get("user_id") != str(user.id):
        raise HTTPException(status_code=403, detail="Session does not belong to you")

    # Check if already fulfilled
    result = await db.execute(
        select(Payment).where(Payment.stripe_session_id == session_id)
    )
    payment = result.scalar_one_or_none()
    if payment and payment.status == PaymentStatus.completed:
        return {"status": "already_fulfilled"}

    # Mark payment as completed
    if payment:
        payment.status = PaymentStatus.completed

    # Fulfill
    if metadata.get("type") == "subscription":
        plan_id = int(metadata["plan_id"])
        plan_result = await db.execute(select(Plan).where(Plan.id == plan_id))
        plan = plan_result.scalar_one()
        await activate_subscription(db, user.id, plan_id, plan.trainings_per_month)
        return {"status": "fulfilled", "type": "subscription", "plan": plan.name}

    elif metadata.get("type") == "tokens":
        token_amount = int(metadata["token_amount"])
        await credit_tokens(db, user.id, token_amount)
        return {"status": "fulfilled", "type": "tokens", "amount": token_amount}

    return {"status": "unknown_type"}


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not settings.stripe_webhook_secret:
        if settings.environment != "development":
            raise HTTPException(status_code=503, detail="Webhook not configured")
        # Dev mode only: skip signature verification
        import json
        event = json.loads(payload)
    else:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
        except (ValueError, stripe.error.SignatureVerificationError):
            raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session_data = event["data"]["object"]
        metadata = session_data.get("metadata", {})

        result = await db.execute(
            select(Payment).where(Payment.stripe_session_id == session_data["id"])
        )
        payment = result.scalar_one_or_none()
        if payment:
            payment.status = PaymentStatus.completed

        user_id = int(metadata["user_id"])

        if metadata.get("type") == "subscription":
            plan_id = int(metadata["plan_id"])
            plan_result = await db.execute(select(Plan).where(Plan.id == plan_id))
            plan = plan_result.scalar_one()
            await activate_subscription(db, user_id, plan_id, plan.trainings_per_month)

        elif metadata.get("type") == "tokens":
            token_amount = int(metadata["token_amount"])
            await credit_tokens(db, user_id, token_amount)

    return {"status": "ok"}
