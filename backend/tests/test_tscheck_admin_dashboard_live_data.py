"""tscheck: Admin dashboard is connected to registration and attendance data.

Criterion: "Admin dashboard is connected to registration and attendance data" --
counters/recent-entry feed (GET /api/admin/dashboard) update after a fresh
registration/scan created by this test, and unauthenticated access returns 401.
"""

import time

GATE = "Gate 1 · Main Entry"


def _unique_suffix() -> str:
    return str(int(time.time() * 1000))


def test_unauthenticated_dashboard_access_is_rejected():
    import httpx
    import os

    api_url = f"{os.environ.get('BACKEND_URL', 'http://localhost:8001')}/api"
    with httpx.Client(base_url=api_url, timeout=30.0) as anon:
        resp = anon.get("/admin/dashboard")
        assert resp.status_code == 401, f"expected 401 without a session, got {resp.status_code} {resp.text[:300]}"


def test_dashboard_counters_and_recent_scans_update_after_registration_and_scan(admin_client, client, scanner_client):
    suffix = _unique_suffix()
    before = admin_client.get("/admin/dashboard")
    assert before.status_code == 200, before.text
    before_stats = before.json()["stats"]

    # Create a fresh zero-fee event + confirmed registration to move the counters.
    slug = f"tscheck-dash-{suffix}"
    event_resp = admin_client.post(
        "/admin/events",
        json={
            "category_id": "cultural",
            "name": f"tscheck Dashboard Event {suffix}",
            "slug": slug,
            "short_description": "tscheck fixture event for dashboard coverage.",
            "description": "tscheck fixture event created by the automated backend test suite.",
            "event_type": "competition",
            "registration_type": "individual",
            "fee": 0,
            "capacity": 20,
            "venue": "tscheck Test Venue",
            "status": "registration_open",
            "event_date": "28 September 2026",
            "event_time": "09:00 AM",
            "registration_deadline": "27 September 2026",
            "eligibility": "Open to tscheck fixtures.",
            "rules": ["Carry ID"],
            "prizes": ["Certificate"],
            "coordinator_name": "tscheck Desk",
            "coordinator_contact": "tscheck Contact",
            "schedule": [{"time": "09:00 AM", "title": "Start"}],
            "event_days": [{"label": "Day 1", "date": "2026-09-28"}],
        },
    )
    assert event_resp.status_code == 201, event_resp.text
    event = event_resp.json()

    reg_resp = client.post(
        "/registrations",
        json={
            "category_id": event["category_id"],
            "event_id": event["id"],
            "name": f"tscheck Dashboard Participant {suffix}",
            "email": f"tscheck-dash-{suffix}@example.com",
            "mobile": "9876543210",
            "college": "tscheck college",
            "participant_affiliation": "sageian",
        },
    )
    assert reg_resp.status_code == 201, reg_resp.text
    registration = reg_resp.json()
    assert registration["status"] == "confirmed"

    pass_resp = admin_client.get(f"/passes/{registration['registration_id']}")
    assert pass_resp.status_code == 200, pass_resp.text
    token = pass_resp.json()["qr_token"]

    # Scanning is now fully automatic (no event/day/gate/assignment selection) --
    # the scanner just posts the raw token and the server auto-detects the event/day.
    scan_resp = scanner_client.post("/scanner/scan", json={"token": token})
    assert scan_resp.status_code == 200, scan_resp.text
    assert scan_resp.json()["ok"] is True

    after = admin_client.get("/admin/dashboard")
    assert after.status_code == 200, after.text
    after_body = after.json()
    after_stats = after_body["stats"]

    assert after_stats["events"] == before_stats["events"] + 1
    assert after_stats["registrations"] == before_stats["registrations"] + 1
    assert after_stats["confirmed"] == before_stats["confirmed"] + 1
    assert after_stats["entries"] == before_stats["entries"] + 1

    matches = [row for row in after_body["events"] if row["id"] == event["id"]]
    assert len(matches) == 1, "newly created event must appear in the dashboard's event list"

    recent_ids = [scan.get("registration_id") for scan in after_body["recent_scans"]]
    assert registration["registration_id"] in recent_ids, "the fresh scan must appear in the recent entry feed"
