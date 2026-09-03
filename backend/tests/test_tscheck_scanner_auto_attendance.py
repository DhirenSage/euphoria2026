"""Backend coverage for criteria:
- QR automatically records the correct event-day attendance (no event/day/gate input).
- Same QR on the same event day is concurrency-safe (second scan -> duplicate, no 2nd row).
"""
from datetime import datetime, timezone

import httpx

from .conftest import API_URL, make_event, register_for_event, unique_suffix


def _today_iso() -> str:
    # Server treats "today" as Asia/Kolkata date; tests run against the same box/tz env
    # SCANNER_ALLOW_OFFDATE=true in this preview also lets an off-date pass select the
    # next unused configured day, so using today's date keeps this deterministic either way.
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")


def test_scan_allows_entry_and_returns_full_details_without_event_day_gate_input(admin_client, scanner_client):
    event = make_event(admin_client, fee=0.0, days=1, event_days=[{"label": "Day 1", "date": _today_iso()}])
    reg = register_for_event(httpx.Client(base_url=API_URL, timeout=30.0), event)
    pass_key = reg["pass_key"]
    registration_id = reg["registration_id"]

    pass_resp = admin_client.get(f"/passes/{registration_id}", params={"key": pass_key})
    assert pass_resp.status_code == 200, pass_resp.text[:300]
    token = pass_resp.json()["qr_token"]

    scan_resp = scanner_client.post("/scanner/scan", json={"token": token})
    assert scan_resp.status_code == 200, scan_resp.text[:300]
    body = scan_resp.json()
    assert body["ok"] is True
    assert body["status"] == "allowed"
    participant = body["participant"]
    assert participant["registration_id"] == registration_id
    assert participant["event_name"] == event["name"]
    assert participant["college"] == "tscheck College"
    assert participant["event_day_label"] is not None
    # No gate/event/day was supplied in the request payload -- only the raw token.


def test_second_scan_of_same_qr_is_duplicate_and_does_not_double_record(admin_client, scanner_client):
    event = make_event(admin_client, fee=0.0, days=1, event_days=[{"label": "Day 1", "date": _today_iso()}])
    reg = register_for_event(httpx.Client(base_url=API_URL, timeout=30.0), event, email=f"tscheck.dup.{unique_suffix()}@example.test")
    pass_key = reg["pass_key"]
    registration_id = reg["registration_id"]

    token = admin_client.get(f"/passes/{registration_id}", params={"key": pass_key}).json()["qr_token"]

    first = scanner_client.post("/scanner/scan", json={"token": token})
    assert first.status_code == 200 and first.json()["status"] == "allowed", first.text[:300]

    second = scanner_client.post("/scanner/scan", json={"token": token})
    assert second.status_code == 200, second.text[:300]
    second_body = second.json()
    assert second_body["ok"] is False
    assert second_body["status"] == "duplicate"
    assert second_body["participant"]["registration_id"] == registration_id

    third = scanner_client.post("/scanner/scan", json={"token": token})
    assert third.json()["status"] == "duplicate"
