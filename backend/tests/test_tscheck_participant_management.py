"""Participant management edits participant data and controls registration state."""

from tests.conftest import make_event, register_for_event, unique_suffix


def test_edit_participant_and_cancel_restore(admin_client):
    event = make_event(admin_client, fee=0.0)
    registration = register_for_event(admin_client, event)
    reg_id = registration["registration_id"]
    assert registration["status"] == "confirmed"

    suffix = unique_suffix()
    update_payload = {
        "participant_name": f"tscheck Updated Name {suffix}",
        "email": f"tscheck.updated.{suffix}@example.test",
        "mobile": "9123456789",
        "college": "tscheck Updated College",
    }
    update_resp = admin_client.put(f"/admin/registrations/{reg_id}", json=update_payload)
    assert update_resp.status_code == 200, update_resp.text[:300]
    updated = update_resp.json()
    assert updated["participant_name"] == update_payload["participant_name"]

    listing = admin_client.get("/admin/registrations")
    row = next(r for r in listing.json()["data"] if r["registration_id"] == reg_id)
    assert row["participant_name"] == update_payload["participant_name"]
    assert row["email"] == update_payload["email"]

    # cancel keeps the row but flips status/qr, payment state remains authoritative
    cancel_resp = admin_client.post(f"/admin/registrations/{reg_id}/state", json={"action": "cancel"})
    assert cancel_resp.status_code == 200, cancel_resp.text[:300]
    cancelled = cancel_resp.json()
    assert cancelled["status"] == "cancelled"

    # restore brings it back to confirmed because payment was already successful/free
    restore_resp = admin_client.post(
        f"/admin/registrations/{reg_id}/state", json={"action": "restore_registration"}
    )
    assert restore_resp.status_code == 200, restore_resp.text[:300]
    restored = restore_resp.json()
    assert restored["status"] == "confirmed"


def test_restore_registration_blocked_without_payment(admin_client):
    event = make_event(admin_client, fee=250.0)
    registration = register_for_event(admin_client, event)
    reg_id = registration["registration_id"]
    assert registration["status"] == "pending_payment"

    # restore path on an unpaid registration should be rejected (409)
    resp = admin_client.post(
        f"/admin/registrations/{reg_id}/state", json={"action": "restore_registration"}
    )
    assert resp.status_code == 409, resp.text[:300]
