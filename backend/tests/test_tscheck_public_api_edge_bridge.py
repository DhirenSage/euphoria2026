"""tscheck: Public API edge bridge and negative case.

Criterion: GET /api/health returns 200 with ok=true and service=euphoria-platform,
GET /api/events returns programme Euphoria 2026 and database events (>=8), and
GET /api/events/not-a-real-event returns 404 with error.code=event_not_found.
"""


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200, f"unexpected status: {resp.status_code} body={resp.text[:300]}"
    body = resp.json()
    assert body.get("ok") is True, f"body={body}"
    assert body.get("service") == "euphoria-platform", f"body={body}"


def test_events_lists_programme_and_events(client):
    resp = client.get("/events")
    assert resp.status_code == 200, f"unexpected status: {resp.status_code} body={resp.text[:300]}"
    body = resp.json()
    assert body["meta"]["programme"] == "Euphoria 2026", f"meta={body.get('meta')}"
    events = body["data"]
    assert len(events) >= 8, f"expected >=8 events, got {len(events)}"
    names = {e["name"] for e in events}
    assert "Dance Competition" in names, f"names={names}"


def test_event_not_found_returns_404(client):
    resp = client.get("/events/not-a-real-event")
    assert resp.status_code == 404, f"unexpected status: {resp.status_code} body={resp.text[:300]}"
    body = resp.json()
    assert body["error"]["code"] == "event_not_found", f"body={body}"
