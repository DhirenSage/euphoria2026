"""Shared helpers for the CodeIgniter/MySQL Euphoria app under test at localhost:8080.

This is a *plain helper module*, not conftest.py, because the target application for this
briefing is the PHP/CodeIgniter monolith served on port 8080 (per spec_deviations) rather
than the FastAPI backend on 8001 that backend/tests/conftest.py is wired for. Importing this
module gives isolated httpx clients/session helpers without touching the existing fixtures.
"""

import os
import re

import httpx

CI_BASE_URL = os.environ.get("CI_BASE_URL", "http://localhost:8080")

ADMIN_EMAIL = "admin@euphoria.test"
ADMIN_PASSWORD = "EuphoriaDemo!2026"
SCANNER_EMAIL = "scanner@euphoria.test"
SCANNER_PASSWORD = "ScannerDemo!2026"


def extract_csrf(html: str) -> str:
    match = re.search(r'csrf_token"\s+value="([^"]+)"', html)
    assert match, "csrf_token input not found in HTML"
    return match.group(1)


def new_client() -> httpx.Client:
    return httpx.Client(base_url=CI_BASE_URL, timeout=30.0, follow_redirects=False)


def admin_login(client: httpx.Client) -> None:
    resp = client.get("/admin/login")
    csrf = extract_csrf(resp.text)
    resp = client.post(
        "/admin/login",
        data={"csrf_token": csrf, "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert resp.status_code in (302, 303), f"admin login failed: {resp.status_code}"


def current_csrf(client: httpx.Client, path: str = "/admin") -> str:
    resp = client.get(path)
    return extract_csrf(resp.text)


def register_participant(client: httpx.Client, *, name: str, email: str, portfolio_url: str) -> str:
    """Submits the public registration form for Core Journey Acceptance (event_id=38,
    category_id=1) and returns the created registration code (e.g. EUPHORIA-2026-000123)."""
    resp = client.get("/registration/core-journey-acceptance")
    csrf = extract_csrf(resp.text)
    resp = client.post(
        "/registration/core-journey-acceptance",
        data={
            "csrf_token": csrf,
            "name": name,
            "fathername": "Tscheck Guardian",
            "mail": email,
            "mobile_no": "9876543210",
            "age": "21",
            "school_clg_name": "SAGE University Indore",
            "city": "Indore",
            "participant_affiliation": "sageian",
            "category_id": "1",
            "event_id": "38",
            "team_name": "",
            "portfolio_url": portfolio_url,
            "terms": "1",
        },
    )
    assert resp.status_code in (302, 303), f"registration submit failed: {resp.status_code} {resp.text[:300]}"
    location = resp.headers.get("location", "")
    match = re.search(r"registration/success/(EUPHORIA-\d{4}-\d+)", location)
    assert match, f"could not find registration code in redirect location: {location}"
    return match.group(1)
