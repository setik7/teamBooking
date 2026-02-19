"""Security tests - headers, input validation."""
import pytest

pytestmark = pytest.mark.asyncio


async def test_security_headers_present(client):
    resp = await client.get("/health")
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
    assert resp.headers.get("Strict-Transport-Security") is not None
    assert resp.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert resp.headers.get("X-Request-ID") is not None


async def test_request_id_unique(client):
    resp1 = await client.get("/health")
    resp2 = await client.get("/health")
    assert resp1.headers["X-Request-ID"] != resp2.headers["X-Request-ID"]


async def test_large_body_rejected(client, auth_headers):
    """Bodies over 1MB should be rejected."""
    large_body = "x" * (1024 * 1024 + 1)
    resp = await client.post(
        "/bookings",
        content=large_body,
        headers={**auth_headers, "Content-Type": "application/json", "Content-Length": str(len(large_body))},
    )
    assert resp.status_code in (413, 422)


async def test_health_endpoint_no_auth(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
