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
