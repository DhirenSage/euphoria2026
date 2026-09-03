"""Payment reconciliation shows real server states and supports audited manual verification."""

from tests.conftest import make_event, register_for_event


def test_manual_verify_filter_validation_and_conflict(admin_client):
    event = make_event(admin_client, fee=99.0)
    registration = register_for_event(admin_client, event)
    reg_id = registration["registration_id"]
    assert registration["payment_status"] == "created"

    # visible under the "created" filter
    created_filter = admin_client.get("/admin/payments", params={"state": "created"})
    assert created_filter.status_code == 200
    assert any(row["registration_id"] == reg_id for row in created_filter.json()["data"])

    # invalid (too short) manual verification payload -> 422
    bad_payload = {"transaction_reference": "x", "reason": "short"}
    bad_resp = admin_client.post(f"/admin/payments/{reg_id}/verify", json=bad_payload)
    assert bad_resp.status_code == 422, bad_resp.text[:300]

    # valid manual verification -> manual_verified
    good_payload = {
        "transaction_reference": "TXN-TSCHECK-0001",
        "reason": "Bank transfer confirmed by finance desk over phone.",
    }
    good_resp = admin_client.post(f"/admin/payments/{reg_id}/verify", json=good_payload)
    assert good_resp.status_code == 200, good_resp.text[:300]
    body = good_resp.json()
    assert body["payment_status"] == "manual_verified"
    assert body["status"] == "confirmed"

    verified_filter = admin_client.get("/admin/payments", params={"state": "manual_verified"})
    assert any(row["registration_id"] == reg_id for row in verified_filter.json()["data"])

    # retrying verify on an already-verified payment -> 409
    retry_resp = admin_client.post(f"/admin/payments/{reg_id}/verify", json=good_payload)
    assert retry_resp.status_code == 409, retry_resp.text[:300]


def test_scanner_role_cannot_access_admin_payments(scanner_client):
    resp = scanner_client.get("/admin/payments")
    assert resp.status_code == 403, resp.text[:300]
