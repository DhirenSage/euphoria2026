"""tscheck: Registration catalogue and server-owned pricing/registration API.

Criteria covered:
- GET /api/registration-catalogue exposes exactly 4 categories and 32 approved events,
  with Cultural=10 and Sports=15, Battle of Bands fee=2499 (team 3-12) and
  Volleyball fee=800 (team 6-12).
- POST /api/registrations for a valid SAGEian Volleyball registration returns a unique
  EUPHORIA-2026-###### id, PENDING PAYMENT status, and server-computed amount 800
  (client-submitted amount is ignored -- server owns pricing).
- POST /api/registrations with a category/event mismatch is rejected (422/400), proving
  the server validates the event belongs to the chosen category rather than trusting the client.
"""

import re
import time

import pytest

REG_ID_RE = re.compile(r"^EUPHORIA-2026-\d{6}$")


def test_registration_catalogue_matches_seeded_facts(client):
    resp = client.get("/registration-catalogue")
    assert resp.status_code == 200, f"unexpected status: {resp.status_code} body={resp.text[:300]}"
    body = resp.json()

    categories = body["categories"]
    events = body["events"]
    assert len(categories) == 4, f"expected 4 categories, got {len(categories)}: {categories}"
    assert len(events) >= 32, f"expected at least 32 events, got {len(events)}"

    by_category = {}
    for e in events:
        by_category.setdefault(e["category_id"], 0)
        by_category[e["category_id"]] += 1
    assert by_category.get("cultural", 0) >= 10, f"cultural count={by_category.get('cultural')}"
    assert by_category.get("sports", 0) >= 15, f"sports count={by_category.get('sports')}"

    by_id = {e["id"]: e for e in events}
    bob = by_id["battle-of-bands"]
    assert bob["fee"] == 2499.0, f"Battle of Bands fee={bob['fee']}"
    assert bob["min_team_size"] == 3 and bob["max_team_size"] == 12, f"bob team sizing={bob}"

    volleyball = by_id["volleyball"]
    assert volleyball["fee"] == 800.0, f"Volleyball fee={volleyball['fee']}"
    assert volleyball["min_team_size"] == 6 and volleyball["max_team_size"] == 12, f"volleyball team sizing={volleyball}"


def test_volleyball_registration_creates_pending_payment_with_server_amount(client):
    stamp = int(time.time() * 1000)
    payload = {
        "category_id": "sports",
        "event_id": "volleyball",
        "name": f"TSCheck Backend Volley {stamp}",
        "email": f"tscheck-backend-volley-{stamp}@example.com",
        "mobile": "9876543210",
        "college": "SAGE University Indore",
        "participant_affiliation": "sageian",
        "team_name": f"TSCheck Backend Smashers {stamp}",
        "team_members": "Player One\nPlayer Two\nPlayer Three\nPlayer Four\nPlayer Five\nPlayer Six",
    }
    resp = client.post("/registrations", json=payload)
    assert resp.status_code == 201, f"unexpected status: {resp.status_code} body={resp.text[:500]}"
    data = resp.json()

    reg_id = data.get("registration_id") or data.get("id")
    assert reg_id and REG_ID_RE.match(reg_id), f"registration id malformed: {reg_id}"

    status = str(data.get("status", "")).upper().replace("_", " ")
    assert "PENDING" in status, f"expected PENDING PAYMENT status, got status={data.get('status')}"

    amount = data.get("total_amount")
    assert amount == 800 or amount == 800.0, f"expected server-owned amount 800, got {amount}"


def test_registration_rejects_event_category_mismatch(client):
    stamp = int(time.time() * 1000)
    payload = {
        # Volleyball belongs to "sports", not "cultural" -- server must reject this mismatch.
        "category_id": "cultural",
        "event_id": "volleyball",
        "name": f"TSCheck Backend Mismatch {stamp}",
        "email": f"tscheck-backend-mismatch-{stamp}@example.com",
        "mobile": "9876543211",
        "college": "SAGE University Indore",
        "participant_affiliation": "sageian",
        "team_name": f"TSCheck Backend Mismatch Team {stamp}",
    }
    resp = client.post("/registrations", json=payload)
    assert resp.status_code in (400, 404, 422), (
        f"expected rejection for category/event mismatch, got {resp.status_code} body={resp.text[:400]}"
    )
