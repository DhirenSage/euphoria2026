"""tscheck: Unknown public event is rejected cleanly.

Criterion: GET /api/events/{slug} for a slug that does not exist returns 404
(not a 500 or an unrelated event), while a known published slug still resolves.
"""


def test_unknown_event_slug_returns_404(client):
    resp = client.get("/events/not-a-real-euphoria-event")
    assert resp.status_code == 404, f"expected 404, got {resp.status_code} body={resp.text[:300]}"
    body = resp.json()
    # Should be a clean not-found error payload, not a crash/trace.
    assert "error" in body or "detail" in body, f"unexpected 404 payload shape: {body}"


def test_known_free_event_slug_still_resolves(client):
    resp = client.get("/events/sample-free-pass-1788416428")
    assert resp.status_code == 200, f"expected 200 for known slug, got {resp.status_code} body={resp.text[:300]}"
    body = resp.json()
    event = body.get("data", body)
    assert event.get("slug") == "sample-free-pass-1788416428", f"unexpected event body: {body}"
