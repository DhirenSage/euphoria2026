"""Verifies the Easebuzz payment initiation payload uses the merchant-approved
productinfo ('euphoria2026'), a correctly-ordered SHA-512 request hash, and the
production initiateLink action -- per the acceptance matrix. Does not touch the
external Easebuzz checkout (spec_deviations: no live transaction is completed).
"""

import hashlib
import os
import uuid
from pathlib import Path

import pytest

def _load_env_salt() -> str:
    """The test process doesn't source backend/.env like uvicorn does; read it directly."""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("EASEBUZZ_SALT="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("EASEBUZZ_SALT", "")


CATALOGUE_URL = "/registration-catalogue"
REGISTRATIONS_URL = "/registrations"

HASH_ORDER = ["key", "txnid", "amount", "productinfo", "firstname", "email", "udf1", "udf2", "udf3", "udf4", "udf5", "udf6", "udf7", "udf8", "udf9", "udf10"]


def _create_pending_registration(client, unique_suffix: str) -> dict:
    catalogue = client.get(CATALOGUE_URL)
    assert catalogue.status_code == 200, catalogue.text
    body = catalogue.json()
    # Battle of Bands per seed_facts: Cultural team event priced at Rs 2,499
    event = next(e for e in body["events"] if e["slug"] == "battle-of-bands")
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
        "team_name": f"tscheck-team-{unique_suffix}",
        "team_members": None,
    }
    resp = client.post(REGISTRATIONS_URL, json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["status"] == "pending_payment"
    return data


def test_payment_initiation_uses_approved_productinfo_and_prod_action(client):
    unique_suffix = uuid.uuid4().hex[:10]
    registration = _create_pending_registration(client, unique_suffix)

    resp = client.post(f"{REGISTRATIONS_URL}/{registration['registration_id']}/payment")
    assert resp.status_code == 200, resp.text
    body = resp.json()

    fields = body["fields"]
    assert fields["productinfo"] == "euphoria2026", f"unexpected productinfo: {fields['productinfo']!r}"
    # no event name, unicode middle dot, or spaces
    assert "battle" not in fields["productinfo"].lower()
    assert "\u00b7" not in fields["productinfo"]
    assert " " not in fields["productinfo"]

    assert len(fields["hash"]) == 128, f"expected 128-char SHA-512 hex hash, got {len(fields['hash'])}"
    int(fields["hash"], 16)  # valid hex

    assert body["action"] == "https://pay.easebuzz.in/payment/initiateLink"


def test_payment_initiation_hash_matches_documented_field_order(client):
    unique_suffix = uuid.uuid4().hex[:10]
    registration = _create_pending_registration(client, unique_suffix)

    resp = client.post(f"{REGISTRATIONS_URL}/{registration['registration_id']}/payment")
    assert resp.status_code == 200, resp.text
    fields = resp.json()["fields"]

    salt = _load_env_salt()
    assert salt, "EASEBUZZ_SALT must be configured for this check to be meaningful"

    recomputed = hashlib.sha512(("|".join(fields.get(k, "") for k in HASH_ORDER) + "|" + salt).encode()).hexdigest()
    assert recomputed == fields["hash"], "recomputed hash does not match server-issued hash"
