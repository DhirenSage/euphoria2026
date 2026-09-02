"""tscheck: Admin can create an event with their own name, slug, status, capacity,
dates and event days; it persists in Mongo and appears in the admin event table.

Criterion: "Admin can create an event with their own name, slug, status, capacity,
dates and event days" -- POST /api/admin/events persists a unique event and it shows
up in GET /api/admin/events (the admin event table's data source).
"""

import time

import pytest


def _unique_suffix() -> str:
    return str(int(time.time() * 1000))


def test_admin_creates_event_and_it_appears_in_admin_table(admin_client):
    suffix = _unique_suffix()
    slug = f"tscheck-event-{suffix}"
    payload = {
        "category_id": "cultural",
        "name": f"tscheck Event {suffix}",
        "slug": slug,
        "short_description": "tscheck fixture event for admin creation coverage.",
        "description": "tscheck fixture event created by the automated backend test suite.",
        "event_type": "competition",
        "registration_type": "individual",
        "fee": 321,
        "capacity": 42,
        "venue": "tscheck Test Venue",
        "status": "registration_open",
        "min_team_size": None,
        "max_team_size": None,
        "banner_url": "",
        "event_date": "20 September 2026",
        "event_time": "11:00 AM",
        "registration_deadline": "19 September 2026",
        "eligibility": "Open to tscheck fixtures.",
        "rules": ["Carry ID"],
        "prizes": ["Certificate"],
        "coordinator_name": "tscheck Desk",
        "coordinator_contact": "tscheck Contact",
        "schedule": [{"time": "11:00 AM", "title": "Start"}],
        "event_days": [
            {"label": "Day 1", "date": "2026-09-20"},
            {"label": "Day 2", "date": "2026-09-21"},
        ],
    }
    resp = admin_client.post("/admin/events", json=payload)
    assert resp.status_code == 201, f"unexpected status: {resp.status_code} body={resp.text[:400]}"
    created = resp.json()
    assert created["slug"] == slug
    assert created["name"] == payload["name"]
    assert created["status"] == "registration_open"
    assert created["capacity"] == 42
    assert len(created["event_days"]) == 2
    event_id = created["id"]

    listing = admin_client.get("/admin/events")
    assert listing.status_code == 200, listing.text
    rows = listing.json()["data"]
    matches = [row for row in rows if row["id"] == event_id]
    assert len(matches) == 1, f"created event {event_id} not found in admin event table"
    assert matches[0]["slug"] == slug
    assert matches[0]["fee"] == 321.0


def test_admin_event_creation_requires_admin_session():
    import httpx
    import os

    api_url = f"{os.environ.get('BACKEND_URL', 'http://localhost:8001')}/api"
    with httpx.Client(base_url=api_url, timeout=30.0) as anon:
        resp = anon.post(
            "/admin/events",
            json={
                "category_id": "cultural",
                "name": "tscheck unauth event",
                "slug": f"tscheck-unauth-{_unique_suffix()}",
                "short_description": "should be rejected",
                "description": "should be rejected",
                "fee": 0,
                "capacity": 1,
                "venue": "tscheck venue",
                "status": "draft",
                "event_date": "1 January 2026",
                "event_time": "1:00 AM",
                "registration_deadline": "1 January 2026",
                "event_days": [{"label": "Day 1", "date": "2026-01-01"}],
            },
        )
        assert resp.status_code == 401, f"expected 401 without a session, got {resp.status_code} {resp.text[:300]}"
