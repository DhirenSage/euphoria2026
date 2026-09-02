"""tscheck: Admin can change event pricing and status, and the public event page /
registration selector reflect the updated server-owned amount and status.

Criterion: "Admin can change event pricing and status and the public page updates" --
PUT /api/admin/events/{id} changes fee/status; GET /api/events/{slug} (the public event
detail page's data source) and GET /api/registration-catalogue (the registration
selector's data source) show the new values.
"""

import time


def _unique_suffix() -> str:
    return str(int(time.time() * 1000))


def _create_event(admin_client, suffix: str) -> dict:
    slug = f"tscheck-pricing-{suffix}"
    payload = {
        "category_id": "cultural",
        "name": f"tscheck Pricing Event {suffix}",
        "slug": slug,
        "short_description": "tscheck fixture event for pricing/status update coverage.",
        "description": "tscheck fixture event created by the automated backend test suite.",
        "event_type": "competition",
        "registration_type": "individual",
        "fee": 150,
        "capacity": 10,
        "venue": "tscheck Test Venue",
        "status": "registration_open",
        "event_date": "22 September 2026",
        "event_time": "10:00 AM",
        "registration_deadline": "21 September 2026",
        "eligibility": "Open to tscheck fixtures.",
        "rules": ["Carry ID"],
        "prizes": ["Certificate"],
        "coordinator_name": "tscheck Desk",
        "coordinator_contact": "tscheck Contact",
        "schedule": [{"time": "10:00 AM", "title": "Start"}],
        "event_days": [{"label": "Day 1", "date": "2026-09-22"}],
    }
    resp = admin_client.post("/admin/events", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_admin_updates_fee_and_status_and_public_pages_reflect_it(admin_client, client):
    suffix = _unique_suffix()
    created = _create_event(admin_client, suffix)
    event_id, slug = created["id"], created["slug"]

    # Sanity: public page shows the original fee while registration is open.
    before = client.get(f"/events/{slug}")
    assert before.status_code == 200, before.text
    assert before.json()["data"]["fee"] == 150.0

    updated_payload = {**created, "fee": 777, "status": "registration_closed"}
    updated_payload.pop("id", None)
    updated_payload["event_days"] = [{"label": day["label"], "date": day["date"]} for day in created["event_days"]]
    resp = admin_client.put(f"/admin/events/{event_id}", json=updated_payload)
    assert resp.status_code == 200, f"unexpected status: {resp.status_code} body={resp.text[:400]}"
    body = resp.json()
    assert body["fee"] == 777.0
    assert body["status"] == "registration_closed"

    # Public detail page (registration_closed events are still individually fetchable by slug).
    after = client.get(f"/events/{slug}")
    assert after.status_code == 200, after.text
    assert after.json()["data"]["fee"] == 777.0
    assert after.json()["data"]["status"] == "registration_closed"

    # Registration-open events list / catalogue must NOT include a closed event anymore.
    open_events = client.get("/events")
    assert open_events.status_code == 200, open_events.text
    assert all(row["id"] != event_id for row in open_events.json()["data"]), (
        "registration_closed event should not appear in the public open-events list"
    )
    catalogue = client.get("/registration-catalogue")
    assert catalogue.status_code == 200, catalogue.text
    assert all(row["id"] != event_id for row in catalogue.json()["events"]), (
        "registration_closed event should not appear in the registration selector"
    )

    # Re-open it and the catalogue/registration selector show the new fee again.
    reopen_payload = {**updated_payload, "fee": 777, "status": "registration_open"}
    resp = admin_client.put(f"/admin/events/{event_id}", json=reopen_payload)
    assert resp.status_code == 200, resp.text
    catalogue_after_reopen = client.get("/registration-catalogue")
    reopened = next(row for row in catalogue_after_reopen.json()["events"] if row["id"] == event_id)
    assert reopened["fee"] == 777.0
    assert reopened["status"] == "registration_open"
