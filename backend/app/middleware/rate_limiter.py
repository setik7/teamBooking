"""Rate limiting middleware using slowapi."""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Rate limit constants for use in route decorators
AUTH_LIMIT = "10/minute"
CALENDAR_LIMIT = "60/minute"
BOOKING_LIMIT = "20/minute"
PAYMENT_LIMIT = "5/minute"
