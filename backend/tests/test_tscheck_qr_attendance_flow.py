"""tscheck: QR validation records first entry, denies same-day duplicate, and permits
another configured day; the scanner response carries full participant validation
details.

Criteria:
- "QR validation records first entry, denies same-day duplicate and permits another
  configured day"
- "Scanner displays complete validation details" -- participant name, registration id,
  event, payment status, pass status and first-entry time for duplicates.
"""

import time

GATE = "Gate 1 · Main Entry"


def _unique_suffix() -> str:
    return str(int(time.time() * 1000))


def _create_two_day_free_event(admin_client, suffix: str) -> dict:
    slug = f"tscheck-attend-{suffix}"
    payload = {
        "category_id": "cultural",
        "name": f"tscheck Attendance Event {suffix}",
        "slug": slug,
        "short_description": "tscheck fixture event for attendance/duplicate coverage.",
        "description": "tscheck fixture event created by the automated backend test suite.",
        "event_type": "competition",
        "registration_type": "individual",
        "fee": 0,
        "capacity": 50,
        "venue": "tscheck Test Venue",
        "status": "registration_open",
        "event_date": "26-27 September 2026",
        "event_time": "09:00 AM",
        "registration_deadline": "25 September 2026",
        "eligibility": "Open to tscheck fixtures.",
        "rules": ["Carry ID"],
        "prizes": ["Certificate"],
        "coordinator_name": "tscheck Desk",
        "coordinator_contact": "tscheck Contact",
        "schedule": [{"time": "09:00 AM", "title": "Start"}],
        "event_days": [
            {"label": "Day 1", "date": "2026-09-26"},
            {"label": "Day 2", "date": "2026-09-27"},
        ],
    }
    resp = admin_client.post("/admin/events", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _register_and_get_token(admin_client, client, event: dict, suffix: str) -> dict:
    reg_resp = client.post(
        "/registrations",
        json={
            "category_id": event["category_id"],
            "event_id": event["id"],
            "name": f"tscheck Attendance Participant {suffix}",
            "email": f"tscheck-attend-{suffix}@example.com",
            "mobile": "9876543210",
            "college": "tscheck college",
            "participant_affiliation": "sageian",
        },
    )
    assert reg_resp.status_code == 201, reg_resp.text
    registration = reg_resp.json()
    assert registration["status"] == "confirmed"
    reg_id = registration["registration_id"]

    # Admin session bypasses the pass_key requirement -- fetch the real QR token.
    pass_resp = admin_client.get(f"/passes/{reg_id}")
    assert pass_resp.status_code == 200, pass_resp.text
    token = pass_resp.json()["qr_token"]
    return {"registration_id": reg_id, "token": token, "name": registration["participant_name"]}


def test_attendance_allows_first_scan_denies_duplicate_and_allows_next_day(admin_client, client, scanner_client):
    suffix = _unique_suffix()
    event = _create_two_day_free_event(admin_client, suffix)
    day1_id, day2_id = event["event_days"][0]["id"], event["event_days"][1]["id"]
    participant = _register_and_get_token(admin_client, client, event, suffix)

    # Scanner assignments are now enforced by event/day/gate (per the current
    # acceptance matrix) -- assign the demo scanner to this fixture event/both
    # days/gate before exercising the scan flow.
    assign_resp = admin_client.post(
        "/admin/staff/scanner-demo/assignments",
        json={"event_id": event["id"], "event_day_ids": [day1_id, day2_id], "gates": [GATE]},
    )
    assert assign_resp.status_code == 200, assign_resp.text

    first_scan = scanner_client.post(
        "/scanner/scan",
        json={"token": participant["token"], "event_id": event["id"], "event_day_id": day1_id, "gate": GATE},
    )
    assert first_scan.status_code == 200, first_scan.text
    first_body = first_scan.json()
    assert first_body["ok"] is True
    assert first_body["status"] == "allowed"
    assert first_body["participant"]["registration_id"] == participant["registration_id"]
    assert first_body["participant"]["participant_name"] == participant["name"]
    assert first_body["participant"]["event_name"] == event["name"]
    assert first_body["participant"]["payment_status"] in {"successful", "manual_verified"}
    assert first_body["participant"]["qr_status"] == "active"

    duplicate_scan = scanner_client.post(
        "/scanner/scan",
        json={"token": participant["token"], "event_id": event["id"], "event_day_id": day1_id, "gate": GATE},
    )
    assert duplicate_scan.status_code == 200, duplicate_scan.text
    dup_body = duplicate_scan.json()
    assert dup_body["ok"] is False
    assert dup_body["status"] == "duplicate"
    assert dup_body["first_entry_at"] is not None, "duplicate response must carry the first entry time"
    assert dup_body["participant"]["registration_id"] == participant["registration_id"]

    day2_scan = scanner_client.post(
        "/scanner/scan",
        json={"token": participant["token"], "event_id": event["id"], "event_day_id": day2_id, "gate": GATE},
    )
    assert day2_scan.status_code == 200, day2_scan.text
    day2_body = day2_scan.json()
    assert day2_body["ok"] is True, f"expected day 2 entry to be permitted, got {day2_body}"
    assert day2_body["status"] == "allowed"


def test_scan_requires_a_scanner_or_admin_session():
    import httpx
    import os

    api_url = f"{os.environ.get('BACKEND_URL', 'http://localhost:8001')}/api"
    with httpx.Client(base_url=api_url, timeout=30.0) as anon:
        resp = anon.post(
            "/scanner/scan",
            json={"token": "EUPHORIA-not-a-real-token-000000000", "event_id": "x", "event_day_id": "y", "gate": GATE},
        )
        assert resp.status_code == 401, f"expected 401 without a session, got {resp.status_code} {resp.text[:300]}"
