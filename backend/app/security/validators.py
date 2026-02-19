"""Input validators for security."""
import re


def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_string(value: str, max_length: int = 255) -> str:
    """Strip dangerous characters and enforce max length."""
    # Remove null bytes
    value = value.replace('\x00', '')
    # Truncate
    return value[:max_length].strip()
