from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.database import create_tables
from app.routers import auth, activities, bookings, subscriptions, payments
from app.middleware.rate_limiter import limiter
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.input_sanitizer import InputSanitizerMiddleware
from app.middleware.request_id import RequestIdMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    # Auto-seed on first run
    try:
        from seed_data import seed
        await seed()
    except Exception:
        pass
    yield


app = FastAPI(title="TeamBooking", version="1.0.0", lifespan=lifespan)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware (order matters - outermost first)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(InputSanitizerMiddleware)
app.add_middleware(SessionMiddleware, secret_key=settings.jwt_secret)

cors_origins = [settings.frontend_url]
if "localhost" not in settings.frontend_url:
    cors_origins.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(activities.router)
app.include_router(bookings.router)
app.include_router(subscriptions.router)
app.include_router(payments.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
