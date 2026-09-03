"""Pass resend uses real SMTP and rotates secure access; unauthorized roles cannot use it."""

from tests.conftest import make_event, register_for_event


def test_resend_pass_succeeds_via_real_smtp_and_rotates_key(admin_client, client):
    event = make_event(admin_client, fee=0.0)
    registration = register_for_event(admin_client, event)
    reg_id = registration["registration_id"]
    old_key = registration["pass_key"]

    resend_resp = admin_client.post(f"/admin/registrations/{reg_id}/resend-pass")
    assert resend_resp.status_code == 200, resend_resp.text[:300]
    body = resend_resp.json()
    assert body["ok"] is True

    # the old pass key must have been rotated (no longer valid); use an
    # unauthenticated client so the admin session doesn't bypass the key check.
    old_key_lookup = client.get(f"/passes/{reg_id}", params={"key": old_key})
    assert old_key_lookup.status_code == 403, old_key_lookup.text[:300]


def test_resend_pass_rejected_for_unconfirmed_registration(admin_client):
    event = make_event(admin_client, fee=150.0)
    registration = register_for_event(admin_client, event)
    reg_id = registration["registration_id"]
    resp = admin_client.post(f"/admin/registrations/{reg_id}/resend-pass")
    assert resp.status_code == 409, resp.text[:300]


def test_resend_pass_denied_for_scanner_role(admin_client, scanner_client):
    event = make_event(admin_client, fee=0.0)
    registration = register_for_event(admin_client, event)
    reg_id = registration["registration_id"]
    resp = scanner_client.post(f"/admin/registrations/{reg_id}/resend-pass")
    assert resp.status_code == 403, resp.text[:300]
