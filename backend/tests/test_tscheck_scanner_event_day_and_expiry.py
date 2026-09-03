"""Backend coverage for event-day / duplicate / expired scanner behaviour on
the CodeIgniter server (127.0.0.1:8091).

Fixture registrations are seeded directly against the euphoria_release MySQL
database (127.0.0.1:3307) because the public registration and bulk-pass
import flows in this CI runtime copy fail with "Encrypter needs a starter
key" (the deployed .env used by the running `spark serve` process omits
encryption.key -- see action_items in the test report). Seeding rows
directly lets the scan business logic itself (AttendanceService::scan) still
be exercised through the real HTTP /scanner/scan endpoint.
"""
import hashlib
import re
import time

import httpx
import pymysql
import pytest

BASE_URL = "http://127.0.0.1:8091"
SCANNER_EMAIL = "scanner@euphoria.test"
SCANNER_PASSWORD = "ScannerDemo!2026"


def db_conn():
    return pymysql.connect(
        host="127.0.0.1", port=3307, user="root", password="",
        database="euphoria_release", cursorclass=pymysql.cursors.DictCursor,
    )


def extract_csrf(html: str):
    m = re.search(r'name="csrf_test_name" value="([^"]+)"', html)
    assert m, "csrf token not found on page"
    return m.group(1)


def scan(client: httpx.Client, token: str) -> dict:
    """POST /scanner/scan exactly like the browser JS: JSON body plus the
    live CSRF cookie value echoed back as the X-CSRF-TOKEN header."""
    csrf_value = client.cookies.get("csrf_cookie_name")
    r = client.post(
        "/scanner/scan",
        json={"token": token},
        headers={"X-CSRF-TOKEN": csrf_value, "X-Requested-With": "XMLHttpRequest"},
    )
    assert r.status_code == 200, r.text[:300]
    return r.json()


@pytest.fixture(scope="module")
def scanner_client():
    client = httpx.Client(base_url=BASE_URL, follow_redirects=True, timeout=30)
    r = client.get("/scanner/login")
    token = extract_csrf(r.text)
    r2 = client.post("/scanner/login", data={"csrf_test_name": token, "email": SCANNER_EMAIL, "password": SCANNER_PASSWORD})
    assert r2.status_code == 200
    yield client
    client.close()


def seed_event_with_registration(day_date: str, suffix: str) -> dict:
    now = "2026-01-01 00:00:00"
    raw_token = f"EUPHORIA-TSCHECK-{suffix}"
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select id from categories where is_active=1 limit 1")
            cat_id = cur.fetchone()["id"]
            cur.execute(
                "insert into events (category_id,name,slug,event_type,registration_type,fee,tax_amount,"
                "discount_amount,capacity,payment_required,is_featured,status,created_at,updated_at) "
                "values (%s,%s,%s,'competition','individual',0,0,0,0,0,0,'registration_open',%s,%s)",
                (cat_id, f"tscheck event {suffix}", f"tscheck-{suffix}", now, now),
            )
            event_id = cur.lastrowid
            cur.execute(
                "insert into event_days (event_id,label,event_date,is_active,created_at,updated_at) "
                "values (%s,'Fixture day',%s,1,%s,%s)", (event_id, day_date, now, now),
            )
            reg_code = f"TSCHECK-{suffix}"
            cur.execute(
                "insert into registrations (event_id,registration_id,participant_name,email,mobile,college,"
                "participant_affiliation,registration_type,total_amount,status,qr_status,pass_access_hash,"
                "created_at,updated_at) values (%s,%s,'Tscheck Scan Participant','tscheck-scan@example.test',"
                "'9876543210','tscheck Institute','non_sageian','individual',0,'confirmed','active',%s,%s,%s)",
                (event_id, reg_code, f"hash-{suffix}", now, now),
            )
            reg_id = cur.lastrowid
            cur.execute(
                "insert into payments (registration_id,txnid,amount,status,created_at,updated_at) "
                "values (%s,%s,0,'success',%s,%s)", (reg_id, f"txn-{suffix}", now, now),
            )
            cur.execute(
                "insert into qr_tokens (registration_id,token_hash,token_hint,status,created_at) "
                "values (%s,%s,%s,'active',%s)", (reg_id, token_hash, raw_token[-8:], now),
            )
        conn.commit()
    return {"event_id": event_id, "registration_id": reg_id, "raw_token": raw_token}


def test_probe_server_reachable():
    r = httpx.get(BASE_URL + "/scanner/login", timeout=10)
    assert r.status_code == 200


def test_first_scan_allowed_second_scan_duplicate_on_configured_day(scanner_client):
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select curdate() d")
            today = cur.fetchone()["d"].isoformat()
    suffix = "today-" + str(int(time.time() * 1000))
    fixture = seed_event_with_registration(today, suffix)

    r1 = scan(scanner_client, fixture["raw_token"])
    assert r1["ok"] is True and r1["status"] == "allowed", r1

    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select count(*) c from attendance where registration_id=%s", (fixture["registration_id"],))
            assert cur.fetchone()["c"] == 1

    r2 = scan(scanner_client, fixture["raw_token"])
    assert r2["ok"] is False and r2["status"] == "duplicate", r2

    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select count(*) c from attendance where registration_id=%s", (fixture["registration_id"],))
            assert cur.fetchone()["c"] == 1, "duplicate scan created a second attendance row"


def test_scan_after_final_configured_date_is_expired_and_denied(scanner_client):
    suffix = "past-" + str(int(time.time() * 1000))
    fixture = seed_event_with_registration("2020-01-01", suffix)

    body = scan(scanner_client, fixture["raw_token"])
    assert body["ok"] is False, body
    assert body["status"] == "denied", body
    assert "expired" in body["message"].lower(), body

    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select count(*) c from attendance where registration_id=%s", (fixture["registration_id"],))
            assert cur.fetchone()["c"] == 0, "an expired scan incorrectly created an attendance row"
            cur.execute("select qr_status from registrations where id=%s", (fixture["registration_id"],))
            assert cur.fetchone()["qr_status"] == "expired"


def test_pre_event_scan_of_seeded_upcoming_fixture_creates_no_attendance_row(scanner_client):
    """Cross-check of the seeded 'Upcoming QR Proof' fixture from the briefing's
    seed_facts (read-only: never mutates the seeded row)."""
    body = scan(scanner_client, "EUPHORIA-UPCOMING-TEST-TOKEN-1234567890")
    assert body["status"] == "upcoming" and body["ok"] is False, body

    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select count(*) c from attendance a join registrations r on r.id=a.registration_id "
                "where r.registration_id='UPCOMING-QR-001'"
            )
            assert cur.fetchone()["c"] == 0, "a pre-event scan created an attendance row for the upcoming fixture"
