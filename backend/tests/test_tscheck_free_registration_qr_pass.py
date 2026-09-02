"""tscheck: A free event registration generates a confirmed, secure QR pass.

Criterion: "A free event registration generates a confirmed secure QR pass" --
POST /api/registrations for a zero-fee event returns a unique EUPHORIA-2026-###### id
with status CONFIRMED; GET /api/passes/{id}?key=... (View QR pass) returns a real PNG
QR data URL plus an unpredictable EUPHORIA-prefixed token.
"""

import re
import time

REG_ID_RE = re.compile(r"^EUPHORIA-2026-\d{6}$")


def _unique_suffix() -> str:
    return str(int(time.time() * 1000))


def _create_free_event(admin_client, suffix: str) -> dict:
    slug = f"tscheck-free-{suffix}"
    payload = {
        "category_id": "cultural",
        "name": f"tscheck Free Event {suffix}",
        "slug": slug,
        "short_description": "tscheck fixture zero-fee event for QR pass coverage.",
        "description": "tscheck fixture zero-fee event created by the automated backend test suite.",
        "event_type": "competition",
        "registration_type": "individual",
        "fee": 0,
        "capacity": 50,
        "venue": "tscheck Test Venue",
        "status": "registration_open",
        "event_date": "25 September 2026",
        "event_time": "09:00 AM",
        "registration_deadline": "24 September 2026",
        "eligibility": "Open to tscheck fixtures.",
        "rules": ["Carry ID"],
        "prizes": ["Certificate"],
        "coordinator_name": "tscheck Desk",
        "coordinator_contact": "tscheck Contact",
        "schedule": [{"time": "09:00 AM", "title": "Start"}],
        "event_days": [{"label": "Day 1", "date": "2026-09-25"}],
    }
    resp = admin_client.post("/admin/events", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_free_event_registration_is_confirmed_with_secure_qr_pass(admin_client, client):
    suffix = _unique_suffix()
    event = _create_free_event(admin_client, suffix)

    reg_resp = client.post(
        "/registrations",
        json={
            "category_id": event["category_id"],
            "event_id": event["id"],
            "name": f"tscheck Free Participant {suffix}",
            "email": f"tscheck-free-{suffix}@example.com",
            "mobile": "9876543210",
            "college": "tscheck college",
            "participant_affiliation": "sageian",
        },
    )
    assert reg_resp.status_code == 201, f"unexpected status: {reg_resp.status_code} body={reg_resp.text[:400]}"
    registration = reg_resp.json()

    reg_id = registration["registration_id"]
    assert REG_ID_RE.match(reg_id), f"registration id malformed: {reg_id}"
    assert registration["status"] == "confirmed", f"expected CONFIRMED status, got {registration['status']}"
    assert registration["total_amount"] == 0.0
    pass_key = registration["pass_key"]
    assert pass_key, "confirmed free registration must return a pass_key to view the QR pass"

    pass_resp = client.get(f"/passes/{reg_id}", params={"key": pass_key})
    assert pass_resp.status_code == 200, f"unexpected status: {pass_resp.status_code} body={pass_resp.text[:400]}"
    pass_body = pass_resp.json()
    assert pass_body["registration_id"] == reg_id
    assert pass_body["qr_status"] == "active"
    assert pass_body["qr_data_url"].startswith("data:image/png;base64,"), "expected a real PNG QR data URL"
    assert len(pass_body["qr_data_url"]) > 500, "PNG QR data URL looks too small to be a real image"
    assert pass_body["qr_token"].startswith("EUPHORIA-"), f"unexpected qr token shape: {pass_body['qr_token']!r}"
    assert len(pass_body["qr_token"]) > 30, "qr token does not look unpredictable/secure"


def test_pass_view_requires_a_valid_pass_key(admin_client, client):
    suffix = _unique_suffix()
    event = _create_free_event(admin_client, suffix + "-b")
    reg_resp = client.post(
        "/registrations",
        json={
            "category_id": event["category_id"],
            "event_id": event["id"],
            "name": f"tscheck Free Participant B {suffix}",
            "email": f"tscheck-free-b-{suffix}@example.com",
            "mobile": "9876543211",
            "college": "tscheck college",
            "participant_affiliation": "sageian",
        },
    )
    assert reg_resp.status_code == 201, reg_resp.text
    reg_id = reg_resp.json()["registration_id"]

    denied = client.get(f"/passes/{reg_id}", params={"key": "wrong-key-entirely"})
    assert denied.status_code == 403, f"expected 403 with an invalid pass key, got {denied.status_code}"
