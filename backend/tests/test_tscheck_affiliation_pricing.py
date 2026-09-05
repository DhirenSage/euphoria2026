"""Backend coverage for CodeIgniter affiliation-specific payment calculation.

Criterion: "Server calculates affiliation-specific payment" -- submitting the
locked Dance Competition registration form with participant_affiliation=non_sageian
must create a pending registration with total_amount 250; submitting
participant_affiliation=sageian must create total_amount 100; and a
browser-posted event_id / total_amount cannot override the server-owned
event/pricing (the event stays event_id=1 and the amount is recalculated
server-side regardless of the tampered form fields).

Runs over real HTTP against the local CodeIgniter spark server (127.0.0.1:8091)
and verifies persisted rows directly against the euphoria_release MySQL
database (127.0.0.1:3307), per the briefing's seed_facts.
"""
import re
import time

import httpx
import pymysql
import pytest

BASE_URL = "http://127.0.0.1:8091"
EVENT_SLUG = "dance-competition"
EVENT_ID = 1  # seed_facts: Dance Competition is configured as SAGEian 100 / Non-SAGEian 250.


def db_conn():
    return pymysql.connect(
        host="127.0.0.1", port=3307, user="root", password="",
        database="euphoria_release", cursorclass=pymysql.cursors.DictCursor,
    )


def extract_csrf(html: str) -> str:
    m = re.search(r'name="csrf_test_name" value="([^"]+)"', html)
    assert m, "csrf token not found on registration page"
    return m.group(1)


def _unique_suffix() -> str:
    return f"{int(time.time() * 1000)}"


def submit_registration(client: httpx.Client, affiliation: str, suffix: str, extra_fields: dict | None = None) -> dict:
    page = client.get(f"/registration/{EVENT_SLUG}")
    assert page.status_code == 200, page.text[:300]
    csrf = extract_csrf(page.text)

    email = f"tscheck.affil.{affiliation}.{suffix}@example.test"
    form = {
        "csrf_test_name": csrf,
        "name": f"tscheck affiliation {suffix}",
        "mail": email,
        "mobile_no": "9876543210",
        "school_clg_name": "tscheck College",
        "participant_affiliation": affiliation,
        "category_id": "1",
        "event_id": str(EVENT_ID),
        "terms": "1",
    }
    if extra_fields:
        form.update(extra_fields)

    resp = client.post(f"/registration/{EVENT_SLUG}", data=form)
    assert resp.status_code == 303, f"unexpected status: {resp.status_code} body={resp.text[:300]}"
    location = resp.headers.get("location", "")
    assert "registration/success" in location, f"registration did not reach success redirect: {location}"

    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select registration_id, event_id, participant_affiliation, total_amount, status "
                "from registrations where email=%s", (email,),
            )
            row = cur.fetchone()
    assert row, f"no registration row persisted for {email}"
    return row


@pytest.fixture
def http_client():
    with httpx.Client(base_url=BASE_URL, timeout=30.0, follow_redirects=False) as c:
        yield c


def test_non_sageian_submission_creates_pending_registration_with_total_250(http_client):
    suffix = _unique_suffix()
    row = submit_registration(http_client, "non_sageian", suffix)
    assert row["event_id"] == EVENT_ID
    assert row["participant_affiliation"] == "non_sageian"
    assert float(row["total_amount"]) == 250.0
    assert row["status"] == "pending_payment"


def test_sageian_submission_creates_pending_registration_with_total_100(http_client):
    suffix = _unique_suffix()
    row = submit_registration(http_client, "sageian", suffix)
    assert row["event_id"] == EVENT_ID
    assert row["participant_affiliation"] == "sageian"
    assert float(row["total_amount"]) == 100.0
    assert row["status"] == "pending_payment"


def test_tampered_event_id_and_amount_cannot_override_server_pricing(http_client):
    """A browser-posted event_id / total_amount must not change the locked event or the
    server-calculated amount: the route already pins the registration to Dance
    Competition (event_id=1), so tampering the form fields is ignored server-side."""
    suffix = _unique_suffix()
    row = submit_registration(
        http_client,
        "non_sageian",
        suffix,
        extra_fields={"event_id": "999999", "category_id": "999", "total_amount": "1"},
    )
    assert row["event_id"] == EVENT_ID, "tampered event_id must not change the locked event"
    assert float(row["total_amount"]) == 250.0, "tampered total_amount must not override server pricing"
