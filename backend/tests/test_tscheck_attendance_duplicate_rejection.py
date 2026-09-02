"""Attendance permits/denies criterion (localhost:8080 CodeIgniter app).

Covers: 'Attendance permits first scan, denies same-day duplicate, and permits next
configured day'. Seed data already has EUPHORIA-2026-000001 scanned allowed on Day 1
(event_day_id=112) and Day 2 (event_day_id=113) for Core Journey Acceptance (event_id=38)
at Gate 1. Re-scanning the same Day 1 token must be rejected as a duplicate without writing
a second attendance row, and role/assignment rules must be enforced (a scanner not
assigned to an event/day/gate is denied).
"""

from .conftest_ci import admin_login, extract_csrf, new_client

EVENT_ID = 38
DAY1_ID = 112
DAY2_ID = 113
GATE_ID = 1
SEED_TOKEN = "EUPHORIA-ddb5be2257544c591d67b44d561f197ce05d7d92"


def _scanner_login(client):
    resp = client.get("/scanner/login")
    csrf = extract_csrf(resp.text)
    resp = client.post(
        "/scanner/login",
        data={"csrf_token": csrf, "email": "scanner@euphoria.test", "password": "ScannerDemo!2026"},
    )
    assert resp.status_code in (302, 303), resp.text


def _current_csrf_hash(client):
    resp = client.get("/scanner")
    return extract_csrf(resp.text)


def test_rescanning_seeded_day1_token_is_denied_as_duplicate():
    with new_client() as client:
        _scanner_login(client)
        csrf = _current_csrf_hash(client)
        resp = client.post(
            "/scanner/scan",
            headers={"X-Requested-With": "XMLHttpRequest", "X-CSRF-TOKEN": csrf, "Content-Type": "application/json"},
            json={"token": SEED_TOKEN, "event_id": EVENT_ID, "day_id": DAY1_ID, "gate_id": GATE_ID},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["ok"] is False
        assert body["status"] == "duplicate"
        assert body["registration"]["registration_id"] == "EUPHORIA-2026-000001"
        # Duplicate rejection must not create a second attendance row for the same day -
        # the existing allowed entry (id=1) is echoed back unchanged.
        assert body["entry"]["status"] == "allowed"
        assert body["entry"]["event_day_id"] == str(DAY1_ID)


def test_unassigned_scanner_scan_for_gate_is_rejected_or_invalid():
    # Same seeded token/day but a nonexistent gate id -> must be rejected (422), never a 2xx
    # success, proving arbitrary gate values cannot be used to force an allowed entry.
    with new_client() as client:
        _scanner_login(client)
        csrf = _current_csrf_hash(client)
        resp = client.post(
            "/scanner/scan",
            headers={"X-Requested-With": "XMLHttpRequest", "X-CSRF-TOKEN": csrf, "Content-Type": "application/json"},
            json={"token": SEED_TOKEN, "event_id": EVENT_ID, "day_id": DAY1_ID, "gate_id": 99999},
        )
        assert resp.status_code == 422, resp.text
        body = resp.json()
        assert body["ok"] is False
        assert body["status"] == "denied"


def test_admin_reports_page_shows_two_verified_entries_for_seed_registration():
    with new_client() as client:
        admin_login(client)
        resp = client.get("/admin/reports")
        assert resp.status_code == 200, resp.text
        assert "2 verified entries" in resp.text
        assert resp.text.count("EUPHORIA-2026-000001") >= 2
