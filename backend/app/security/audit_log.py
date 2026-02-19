"""Security audit logging."""
import logging
import json
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import SecurityLog

logger = logging.getLogger("security")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '{"timestamp":"%(asctime)s","level":"%(levelname)s","event":"%(message)s"}'
))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


async def log_security_event(
    db: AsyncSession,
    event_type: str,
    user_id: int | None = None,
    ip_address: str | None = None,
    details: str | None = None,
):
    """Log a security event to both DB and structured JSON log."""
    entry = SecurityLog(
        user_id=user_id,
        event_type=event_type,
        ip_address=ip_address,
        details=details,
    )
    db.add(entry)

    logger.info(json.dumps({
        "event_type": event_type,
        "user_id": user_id,
        "ip": ip_address,
        "details": details,
        "ts": datetime.now(timezone.utc).isoformat(),
    }))
