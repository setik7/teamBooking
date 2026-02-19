from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.db.models import User
from app.schemas.booking import BookingCreate, BookingOut
from app.services.booking_service import create_booking, cancel_booking, get_user_bookings

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingOut)
async def book_training(
    data: BookingCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        booking = await create_booking(db, user.id, data.training_slot_id, data.date)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{booking_id}", response_model=BookingOut)
async def cancel_training(
    booking_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        booking = await cancel_booking(db, user.id, booking_id)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/mine", response_model=list[BookingOut])
async def my_bookings(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_user_bookings(db, user.id)
