"""Complete branded PDF download endpoint: valid secure key succeeds, invalid key is rejected."""

from tests.conftest import make_event, register_for_event


def test_pass_pdf_download_returns_complete_branded_pdf(admin_client, client):
    event = make_event(admin_client, fee=0.0)
    registration = register_for_event(admin_client, event)
    reg_id = registration["registration_id"]
    pass_key = registration["pass_key"]
    assert pass_key, "confirmed free registration must return a pass_key"

    resp = client.get(f"/passes/{reg_id}/pdf", params={"key": pass_key})
    assert resp.status_code == 200, resp.text[:300]
    assert resp.headers.get("content-type", "").startswith("application/pdf")
    body = resp.content
    assert body[:5] == b"%PDF-", f"unexpected magic bytes: {body[:5]!r}"
    assert len(body) > 50 * 1024, f"PDF unexpectedly small: {len(body)} bytes"
    disposition = resp.headers.get("content-disposition", "")
    assert "complete-event-pass.pdf" in disposition


def test_pass_pdf_download_rejects_invalid_key(client):
    # unauthenticated client + a registration id that requires a key -- garbage key -> 403
    resp = client.get("/passes/EUPHORIA-2026-000126/pdf", params={"key": "not-the-real-key"})
    assert resp.status_code == 403, resp.text[:300]


def test_pass_json_view_also_rejects_invalid_key(client):
    resp = client.get("/passes/EUPHORIA-2026-000126", params={"key": "not-the-real-key"})
    assert resp.status_code == 403, resp.text[:300]
