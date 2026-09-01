"""Verifies the new server-side Easebuzz access-key exchange contract:
POST /api/registrations/{id}/payment must contact Easebuzz server-side and return only
`checkout_url` + a fresh `transaction_id` (no `action`/`fields` signed-payload contract,
which was intentionally superseded per spec_deviations). Also covers retry-safe fresh
transaction ids and rejection of payment for a nonexistent registration.
"""

import re
import uuid

import pytest

CATALOGUE_URL = "/registration-catalogue"
REGISTRATIONS_URL = "/registrations"

TXN_ID_RE = re.compile(r"^EB-[0-9a-f]+$")
CHECKOUT_URL_RE = re.compile(r"^https://pay\.easebuzz\.in/pay/[^/]+$")


def _create_pending_registration(client, unique_suffix: str) -> dict:
    catalogue = client.get(CATALOGUE_URL)
    assert catalogue.status_code == 200, catalogue.text
    body = catalogue.json()
    # Game Mania per seed_facts: Cultural individual event, low fee.
    event = next(e for e in body["events"] if e["slug"] == "game-mania")
    payload = {
        "category_id": event["category_id"],
        "event_id": event["id"],
        "name": f"tscheck-easebuzz-{unique_suffix}",
        "father_name": None,
        "email": f"tscheck-easebuzz-{unique_suffix}@example.com",
        "mobile": "9876543210",
        "age": 20,
        "college": "tscheck college",
        "city": None,
        "participant_affiliation": "sageian",
        "team_name": None,
        "team_members": None,
    }
    resp = client.post(REGISTRATIONS_URL, json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["status"] == "pending_payment"
    return data


def test_payment_initiation_returns_only_checkout_url_and_transaction_id(client):
    unique_suffix = uuid.uuid4().hex[:10]
    registration = _create_pending_registration(client, unique_suffix)

    resp = client.post(f"{REGISTRATIONS_URL}/{registration['registration_id']}/payment")
    assert resp.status_code == 200, resp.text
    body = resp.json()

    # New contract: only checkout_url + transaction_id, no signed fields/action contract exposed.
    assert set(body.keys()) == {"checkout_url", "transaction_id"}, f"unexpected response shape: {body!r}"
    assert TXN_ID_RE.match(body["transaction_id"]), f"transaction_id not EB-prefixed: {body['transaction_id']!r}"
    assert CHECKOUT_URL_RE.match(body["checkout_url"]), f"checkout_url is not a hosted Easebuzz pay link: {body['checkout_url']!r}"
    # Never the raw initiation endpoint.
    assert "initiateLink" not in body["checkout_url"]


def test_payment_initiation_is_retry_safe_with_fresh_transaction_ids(client):
    unique_suffix = uuid.uuid4().hex[:10]
    registration = _create_pending_registration(client, unique_suffix)
    registration_id = registration["registration_id"]

    first = client.post(f"{REGISTRATIONS_URL}/{registration_id}/payment")
    assert first.status_code == 200, first.text
    second = client.post(f"{REGISTRATIONS_URL}/{registration_id}/payment")
    assert second.status_code == 200, second.text

    first_body, second_body = first.json(), second.json()
    assert first_body["transaction_id"] != second_body["transaction_id"], "retry must mint a fresh EB- transaction id"
    assert TXN_ID_RE.match(second_body["transaction_id"])
    assert CHECKOUT_URL_RE.match(second_body["checkout_url"])

    # The registration must now reflect the latest attempt's checkout url/access key with no 500.
    fetched = client.get(f"{REGISTRATIONS_URL}/{registration_id}")
    assert fetched.status_code == 200, fetched.text
    assert fetched.json()["registration_id"] == registration_id


def test_payment_initiation_for_unknown_registration_is_rejected(client):
    bogus_id = f"EUPHORIA-2026-{uuid.uuid4().hex[:6]}"
    resp = client.post(f"{REGISTRATIONS_URL}/{bogus_id}/payment")
    assert resp.status_code == 404, resp.text
