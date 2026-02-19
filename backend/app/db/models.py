import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date, Time,
    ForeignKey, UniqueConstraint, Enum as SAEnum, Text,
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    member = "member"
    admin = "admin"


class BookingStatus(str, enum.Enum):
    confirmed = "confirmed"
    cancelled = "cancelled"
    token_used = "token_used"


class SubscriptionStatus(str, enum.Enum):
    active = "active"
    cancelled = "cancelled"
    expired = "expired"
    pending = "pending"


class TokenReason(str, enum.Enum):
    skip = "skip"
    book_extra = "book_extra"
    purchase = "purchase"
    cancel_refund = "cancel_refund"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


# ── Models ───────────────────────────────────────────────────────────


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    avatar = Column(String(512), nullable=True)
    oauth_provider = Column(String(50), nullable=False)
    oauth_id = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.member, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    subscriptions = relationship("Subscription", back_populates="user")
    bookings = relationship("Booking", back_populates="user")
    token_transactions = relationship("TokenTransaction", back_populates="user")
    payments = relationship("Payment", back_populates="user")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    trainings_per_month = Column(Integer, nullable=False)
    price_eur = Column(Float, nullable=False)
    stripe_price_id = Column(String(255), nullable=True)

    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    status = Column(SAEnum(SubscriptionStatus), default=SubscriptionStatus.pending, nullable=False)
    tokens_balance = Column(Integer, default=0, nullable=False)
    trainings_remaining = Column(Integer, nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    icon = Column(String(10), nullable=True)
    description = Column(Text, nullable=True)
    max_participants = Column(Integer, nullable=False, default=20)
    duration_minutes = Column(Integer, nullable=False, default=60)

    training_slots = relationship("TrainingSlot", back_populates="activity")


class TrainingSlot(Base):
    __tablename__ = "training_slots"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday .. 6=Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    recurring = Column(Boolean, default=True, nullable=False)

    activity = relationship("Activity", back_populates="training_slots")
    bookings = relationship("Booking", back_populates="training_slot")


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        UniqueConstraint("user_id", "training_slot_id", "date", name="uq_user_slot_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    training_slot_id = Column(Integer, ForeignKey("training_slots.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(SAEnum(BookingStatus), default=BookingStatus.confirmed, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="bookings")
    training_slot = relationship("TrainingSlot", back_populates="bookings")
    token_transactions = relationship("TokenTransaction", back_populates="booking")


class TokenTransaction(Base):
    __tablename__ = "token_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)  # positive = credit, negative = debit
    reason = Column(SAEnum(TokenReason), nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="token_transactions")
    booking = relationship("Booking", back_populates="token_transactions")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_session_id = Column(String(255), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(SAEnum(PaymentStatus), default=PaymentStatus.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="payments")


class SecurityLog(Base):
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(100), nullable=False)
    ip_address = Column(String(45), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
