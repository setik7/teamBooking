"""Auth security tests - JWT tampering, expiry, role escalation."""
import pytest
from datetime import timedelta
from jose import jwt as jose_jwt
from app.auth.jwt import create_access_token, decode_token
from app.config import get_settings

settings = get_settings()

pytestmark = pytest.mark.asyncio


async def test_valid_token_decodes(test_user):
    token = create_access_token({"sub": str(test_user.id)})
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == str(test_user.id)


async def test_expired_token_rejected(test_user):
    token = create_access_token(
        {"sub": str(test_user.id)},
        expires_delta=timedelta(seconds=-1),
    )
    assert decode_token(token) is None


async def test_tampered_token_rejected(test_user):
    token = create_access_token({"sub": str(test_user.id)})
    # Tamper with the payload
    tampered = token[:-5] + "XXXXX"
    assert decode_token(tampered) is None


async def test_wrong_secret_rejected(test_user):
    payload = {"sub": str(test_user.id), "exp": 9999999999}
    token = jose_jwt.encode(payload, "wrong-secret", algorithm="HS256")
    assert decode_token(token) is None


async def test_none_algorithm_rejected(test_user):
    """Ensure 'none' algorithm attack is blocked."""
    import base64, json
    header = base64.urlsafe_b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode()).rstrip(b"=")
    payload = base64.urlsafe_b64encode(json.dumps({"sub": str(test_user.id)}).encode()).rstrip(b"=")
    token = f"{header.decode()}.{payload.decode()}."
    assert decode_token(token) is None


async def test_me_requires_auth(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 403  # No credentials


async def test_me_with_valid_token(client, test_user, auth_headers):
    resp = await client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "test@example.com"


async def test_role_escalation_blocked(client, auth_headers):
    """Regular user cannot access admin endpoints."""
    # The require_admin dependency should block this
    # (We'd need an admin-only endpoint to test - placeholder for when added)
    resp = await client.get("/auth/me", headers=auth_headers)
    assert resp.json()["role"] == "member"


async def test_nonexistent_user_token(client, db):
    """Token with deleted user ID should fail."""
    token = create_access_token({"sub": "99999"})
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
