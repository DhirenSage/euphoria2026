"""Signed server-side payment callback confirmation (localhost:8080 CodeIgniter app).

Covers: 'Paid registration is confirmed only by the signed server-side callback path'.
A fresh fixture registration starts pending_payment; it is confirmed only via the
authenticated admin-session-gated development callback fixture (POST
/admin/dev/easebuzz/callback-test), which internally signs the payload server-side before
handing it to PaymentConfirmationService. We also assert the endpoint is unreachable
without an authenticated admin session (404, since the filter + ENVIRONMENT/env flag guard
sit in front of it) and that an unknown registration code is rejected (404).
"""

import re
import uuid

from .conftest_ci import admin_login, current_csrf, extract_csrf, new_client, register_participant


def test_paid_registration_starts_pending_and_is_confirmed_only_by_signed_callback():
    unique = uuid.uuid4().hex[:10]
    with new_client() as reg_client:
        code = register_participant(
            reg_client,
            name=f"Tscheck Callback {unique}",
            email=f"tscheck.callback.{unique}@example.com",
            portfolio_url=f"https://example.com/tscheck-{unique}",
        )

        # Fresh registration is pending_payment before any callback.
        resp = reg_client.get(f"/registration/success/{code}")
        assert resp.status_code == 200
        assert 'data-testid="confirmation-status">PENDING PAYMENT' in resp.text

    with new_client() as admin_client:
        admin_login(admin_client)
        csrf = current_csrf(admin_client, "/admin")
        callback_resp = admin_client.post(
            "/admin/dev/easebuzz/callback-test",
            headers={"X-Requested-With": "XMLHttpRequest"},
            data={"csrf_token": csrf, "registration_id": code},
        )
        assert callback_resp.status_code == 200, callback_resp.text
        body = callback_resp.json()
        assert body["ok"] is True
        assert body["status"] == "success"
        assert body["registration_id"] == code

    with new_client() as verify_client:
        resp = verify_client.get(f"/registration/success/{code}")
        assert resp.status_code == 200
        assert 'data-testid="confirmation-status">CONFIRMED' in resp.text


def test_dev_callback_fixture_requires_admin_session():
    # No admin login performed - the route sits behind the admin auth filter, so an
    # unauthenticated POST must not be able to confirm a payment.
    with new_client() as client:
        resp = client.post(
            "/admin/dev/easebuzz/callback-test",
            data={"csrf_token": "irrelevant", "registration_id": "EUPHORIA-2026-000001"},
        )
        assert resp.status_code in (302, 303, 403, 404), resp.text
        assert resp.status_code != 200


def test_dev_callback_rejects_unknown_registration():
    with new_client() as admin_client:
        admin_login(admin_client)
        csrf = current_csrf(admin_client, "/admin")
        resp = admin_client.post(
            "/admin/dev/easebuzz/callback-test",
            headers={"X-Requested-With": "XMLHttpRequest"},
            data={"csrf_token": csrf, "registration_id": f"EUPHORIA-2026-{uuid.uuid4().hex[:8]}"},
        )
        assert resp.status_code == 404, resp.text
        body = resp.json()
        assert body["ok"] is False


def test_seed_registration_000001_is_confirmed_with_verified_revenue():
    with new_client() as client:
        resp = client.get("/registration/success/EUPHORIA-2026-000001")
        assert resp.status_code == 200
        assert 'data-testid="confirmation-status">CONFIRMED' in resp.text
        assert re.search(r'data-testid="confirmation-server-amount">\s*.?99', resp.text)
