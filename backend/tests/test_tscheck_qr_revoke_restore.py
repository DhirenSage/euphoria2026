"""QR revoke and restore take effect immediately without changing the secure token."""

from tests.conftest import make_event, register_for_event


def test_revoke_blocks_scan_and_restore_reenables_same_token(admin_client):
    event = make_event(admin_client, fee=0.0)
    registration = register_for_event(admin_client, event)
    reg_id = registration["registration_id"]
    pass_key = registration["pass_key"]

    pass_before = admin_client.get(f"/passes/{reg_id}", params={"key": pass_key})
    assert pass_before.status_code == 200
    token = pass_before.json()["qr_token"]

    scan_payload = {
        "token": token,
        "event_id": event["id"],
        "event_day_id": event["event_days"][0]["id"],
        "gate": "Gate 1 · Main Entry",
    }
    first_scan = admin_client.post("/scanner/scan", json=scan_payload)
    assert first_scan.status_code == 200
    assert first_scan.json()["status"] == "allowed"

    revoke_resp = admin_client.post(f"/admin/registrations/{reg_id}/state", json={"action": "revoke"})
    assert revoke_resp.status_code == 200, revoke_resp.text[:300]
    assert revoke_resp.json()["qr_ready"] is False

    # revoked pass is no longer scannable -- use a second event day so we don't trip
    # the same-day duplicate rule and mask the revoke check.
    event2 = make_event(admin_client, fee=0.0)
    registration2 = register_for_event(admin_client, event2)
    reg2_id = registration2["registration_id"]
    pass2 = admin_client.get(f"/passes/{reg2_id}", params={"key": registration2["pass_key"]})
    token2 = pass2.json()["qr_token"]
    revoke2 = admin_client.post(f"/admin/registrations/{reg2_id}/state", json={"action": "revoke"})
    assert revoke2.status_code == 200

    denied_scan = admin_client.post(
        "/scanner/scan",
        json={
            "token": token2,
            "event_id": event2["id"],
            "event_day_id": event2["event_days"][0]["id"],
            "gate": "Gate 1 · Main Entry",
        },
    )
    assert denied_scan.status_code == 200
    assert denied_scan.json()["status"] == "denied"

    restore_resp = admin_client.post(f"/admin/registrations/{reg2_id}/state", json={"action": "restore"})
    assert restore_resp.status_code == 200, restore_resp.text[:300]
    restored = restore_resp.json()
    assert restored["qr_ready"] is True

    pass_after = admin_client.get(f"/passes/{reg2_id}", params={"key": registration2["pass_key"]})
    assert pass_after.status_code == 200
    assert pass_after.json()["qr_token"] == token2, "restore must not rotate the secure token"

    allowed_after_restore = admin_client.post(
        "/scanner/scan",
        json={
            "token": token2,
            "event_id": event2["id"],
            "event_day_id": event2["event_days"][0]["id"],
            "gate": "Gate 1 · Main Entry",
        },
    )
    assert allowed_after_restore.status_code == 200
    assert allowed_after_restore.json()["status"] == "allowed"
