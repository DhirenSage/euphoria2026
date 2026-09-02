"""Digital pass + PDF criterion (localhost:8080 CodeIgniter app).

Covers: 'Confirmed registration has secure QR digital pass and working PDF'. The pass and
its PDF are only reachable with an authorized session (admin) or a signed access key -
verified here via the admin session for the seeded confirmed registration
EUPHORIA-2026-000001, plus a negative case proving an anonymous request is redirected away
rather than shown the pass.
"""

from .conftest_ci import admin_login, new_client

REG_CODE = "EUPHORIA-2026-000001"


def test_admin_can_open_confirmed_pass_with_qr_and_details():
    with new_client() as client:
        admin_login(client)
        resp = client.get(f"/pass/{REG_CODE}")
        assert resp.status_code == 200, resp.text
        assert 'data-testid="pass-qr-image"' in resp.text
        assert 'data-testid="pass-qr-token"' in resp.text
        assert 'data-testid="pass-status"' in resp.text
        assert "Core Journey Acceptance" in resp.text
        assert REG_CODE in resp.text


def test_pass_pdf_download_returns_nonempty_pdf():
    with new_client() as client:
        admin_login(client)
        resp = client.get(f"/pass/{REG_CODE}/download")
        assert resp.status_code == 200, resp.text
        assert resp.headers.get("content-type", "").startswith("application/pdf")
        assert len(resp.content) > 1000
        assert resp.content[:4] == b"%PDF"


def test_anonymous_request_cannot_view_pass():
    with new_client() as client:
        resp = client.get(f"/pass/{REG_CODE}")
        assert resp.status_code in (302, 303)
        assert "/events" in resp.headers.get("location", "")
