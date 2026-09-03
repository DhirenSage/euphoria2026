"""Pre-scaffolded pytest fixtures for the FastAPI backend.

Tests hit the live uvicorn process managed by supervisor (not an in-process ASGI app), so
the app under test is the same one the frontend and Playwright see. Do NOT re-create this
file — add app-specific fixtures below the marker at the bottom.
"""

import os

import httpx
import pytest
import pytest_asyncio

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8001")
API_URL = f"{BACKEND_URL}/api"


def api_url(path: str = "") -> str:
    """Absolute URL for an /api route: api_url("/status") -> http://localhost:8001/api/status."""
    return f"{API_URL}{path}"


@pytest.fixture(scope="session")
def backend_url() -> str:
    return BACKEND_URL


@pytest.fixture
def client():
    """Sync httpx client rooted at /api — the default for endpoint tests.

    Example:
        def test_status(client):
            assert client.get("/status").status_code == 200
    """
    with httpx.Client(base_url=API_URL, timeout=30.0) as c:
        yield c


@pytest_asyncio.fixture
async def aclient():
    """Async variant, for tests that also await motor/backend helpers directly."""
    async with httpx.AsyncClient(base_url=API_URL, timeout=30.0) as c:
        yield c


# --- app-specific fixtures below this line ---

ADMIN_EMAIL = "admin@euphoria.test"
ADMIN_PASSWORD = "EuphoriaDemo!2026"
SCANNER_EMAIL = "scanner@euphoria.test"
SCANNER_PASSWORD = "ScannerDemo!2026"


def _login_client(email: str, password: str, portal: str) -> httpx.Client:
    c = httpx.Client(base_url=API_URL, timeout=30.0)
    resp = c.post(f"/auth/{portal}/login", json={"email": email, "password": password})
    assert resp.status_code == 200, f"{portal} login failed: {resp.status_code} {resp.text[:300]}"
    # httpx's cookiejar treats the single-label host "localhost" oddly (stores it as
    # "localhost.local"), so cookies set from the login response are not reliably resent
    # by the jar on subsequent requests against the same "localhost" base_url. Re-set the
    # session cookie explicitly (domain="" matches any host) so it is always attached.
    token = resp.cookies.get("euphoria_session")
    assert token, "login response did not set a session cookie"
    c.cookies.set("euphoria_session", token, domain="", path="/")
    return c


@pytest.fixture
def admin_client():
    """httpx.Client with a live admin session cookie (cookies persist across requests)."""
    c = _login_client(ADMIN_EMAIL, ADMIN_PASSWORD, "admin")
    yield c
    c.close()


@pytest.fixture
def scanner_client():
    """httpx.Client with a live scanner session cookie."""
    c = _login_client(SCANNER_EMAIL, SCANNER_PASSWORD, "scanner")
    yield c
    c.close()


def unique_suffix() -> str:
    import secrets as _secrets
    return _secrets.token_hex(6)


def make_event(admin_client: httpx.Client, fee: float = 0.0, days: int = 1, **overrides) -> dict:
    """Create a tscheck- fixture event via the real admin API and return the created event dict."""
    suffix = unique_suffix()
    event_days = [{"label": f"Day {i + 1}", "date": f"2026-09-{15 + i:02d}"} for i in range(days)]
    payload = {
        "category_id": "cultural",
        "name": f"tscheck-event-{suffix}",
        "slug": f"tscheck-event-{suffix}",
        "short_description": "Automated fixture event.",
        "description": "Automated fixture event for backend test isolation.",
        "event_type": "competition",
        "registration_type": "individual",
        "fee": fee,
        "capacity": 100,
        "venue": "Test Venue",
        "status": "registration_open",
        "event_date": "15 September 2026",
        "event_time": "10:00 AM - 6:00 PM",
        "registration_deadline": "14 September 2026 . 11:59 PM",
        "event_days": event_days,
    }
    payload.update(overrides)
    resp = admin_client.post("/admin/events", json=payload)
    assert resp.status_code == 201, f"event creation failed: {resp.status_code} {resp.text[:300]}"
    return resp.json()


def register_for_event(client: httpx.Client, event: dict, **overrides) -> dict:
    """Create a tscheck- fixture registration for the given event via the public API."""
    suffix = unique_suffix()
    payload = {
        "category_id": event["category_id"],
        "event_id": event["id"],
        "name": f"tscheck participant {suffix}",
        "email": f"tscheck.{suffix}@example.test",
        "mobile": "9876543210",
        "college": "tscheck College",
        "participant_affiliation": "non_sageian",
    }
    payload.update(overrides)
    resp = client.post("/registrations", json=payload)
    assert resp.status_code == 201, f"registration creation failed: {resp.status_code} {resp.text[:300]}"
    return resp.json()
