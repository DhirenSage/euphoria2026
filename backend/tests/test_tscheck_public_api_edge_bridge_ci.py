"""Public API edge bridge for the CodeIgniter app (localhost:8080), covering the
'Admin manages database-driven categories, events...' criterion's public-facing surface:
GET /api/health, GET /api/events (seeded catalogue incl. Core Journey Acceptance), and the
404 negative case for an unknown event slug.
"""

from .conftest_ci import new_client


def test_health_ok():
    with new_client() as client:
        resp = client.get("/api/health")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["ok"] is True
        assert body["service"] == "euphoria-platform"


def test_events_lists_seeded_catalogue_including_core_journey_acceptance():
    with new_client() as client:
        resp = client.get("/api/events")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["meta"]["programme"] == "Euphoria 2026"
        names = [e["name"] for e in body["data"]]
        assert len(body["data"]) >= 8
        assert "Core Journey Acceptance" in names


def test_event_detail_matches_seeded_fee_and_slug():
    with new_client() as client:
        resp = client.get("/api/events/core-journey-acceptance")
        assert resp.status_code == 200, resp.text
        data = resp.json()["data"]
        assert data["slug"] == "core-journey-acceptance"
        assert float(data["fee"]) == 99.0


def test_event_not_found_returns_404():
    with new_client() as client:
        resp = client.get("/api/events/tscheck-not-a-real-event-slug")
        assert resp.status_code == 404, resp.text
        body = resp.json()
        assert body["error"]["code"] == "event_not_found"
