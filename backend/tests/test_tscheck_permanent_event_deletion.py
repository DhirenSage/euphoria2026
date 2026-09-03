"""Backend coverage for CodeIgniter permanent event deletion (SUPER_ADMIN only).

Runs over real HTTP against the local CodeIgniter spark server (127.0.0.1:8091)
and verifies cascade cleanup directly against the euphoria_release MySQL
database (127.0.0.1:3307), per the briefing's seed_facts.
"""
import re
import time

import httpx
import pymysql
import pytest

BASE_URL = "http://127.0.0.1:8091"
ADMIN_EMAIL = "admin@euphoria.test"
ADMIN_PASSWORD = "EuphoriaDemo!2026"
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


def login(client: httpx.Client, email: str, password: str):
    r = client.get("/admin/login")
    token = extract_csrf(r.text)
    r2 = client.post("/admin/login", data={"csrf_test_name": token, "email": email, "password": password})
    assert r2.status_code == 200
    return r2


def scanner_login(client: httpx.Client, email: str, password: str):
    r = client.get("/scanner/login")
    token = extract_csrf(r.text)
    r2 = client.post("/scanner/login", data={"csrf_test_name": token, "email": email, "password": password})
    assert r2.status_code == 200
    return r2


def csrf_from(client: httpx.Client, path: str, form_testid: str) -> tuple[str, str]:
    """Return (csrf_field_name, csrf_value) by re-fetching a page that embeds one."""
    r = client.get(path)
    m = re.search(r'name="(csrf_test_name)" value="([^"]+)"', r.text)
    assert m
    return m.group(1), m.group(2)


def create_event(client: httpx.Client, name: str) -> int:
    field, value = csrf_from(client, "/admin/events/new", "admin-event-form")
    payload = {
        field: value,
        "category_id": "1",
        "name": name,
        "slug": "",
        "event_type": "competition",
        "registration_type": "individual",
        "capacity": "0",
        "fee": "0",
        "tax_amount": "0",
        "discount_amount": "0",
        "status": "registration_open",
        "day_label[]": "Day 1",
        "day_date[]": "2031-01-01",
    }
    r = client.post("/admin/events", data=payload)
    assert r.status_code == 200, r.text[:300]
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select id from events where name=%s", (name,))
            row = cur.fetchone()
    assert row, f"event {name} was not created"
    return int(row["id"])


def seed_full_related_fixture(event_id: int) -> dict:
    """Seed one row in every table EventDeletionService is expected to cascade
    through, via direct SQL (the app's own registration flows depend on a
    server-side encryption key that is not configured in this CI runtime copy,
    so fixtures are seeded directly -- the deletion behaviour itself is still
    exercised through the real HTTP admin endpoint)."""
    now = "2026-01-01 00:00:00"
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "insert into event_days (event_id,label,event_date,is_active,created_at,updated_at) "
                "values (%s,'Fixture day','2031-02-02',1,%s,%s)", (event_id, now, now),
            )
            day_id = cur.lastrowid
            reg_code = f"tscheck-reg-{event_id}"
            cur.execute(
                "insert into registrations (event_id,registration_id,participant_name,email,mobile,college,"
                "participant_affiliation,registration_type,total_amount,status,qr_status,pass_access_hash,"
                "created_at,updated_at) values (%s,%s,'Tscheck Participant','tscheck@example.test','9876543210',"
                "'tscheck Institute','non_sageian','individual',0,'confirmed','active',%s,%s,%s)",
                (event_id, reg_code, f"hash-{event_id}", now, now),
            )
            reg_id = cur.lastrowid
            cur.execute(
                "insert into payments (registration_id,txnid,amount,status,created_at,updated_at) "
                "values (%s,%s,0,'success',%s,%s)", (reg_id, f"tscheck-txn-{event_id}", now, now),
            )
            cur.execute(
                "insert into qr_tokens (registration_id,token_hash,token_hint,status,created_at) "
                "values (%s,%s,'abcd1234','active',%s)", (reg_id, f"hash-tok-{event_id}", now),
            )
            cur.execute(
                "insert into attendance (registration_id,event_id,event_day_id,entry_time,status) "
                "values (%s,%s,%s,%s,'allowed')", (reg_id, event_id, day_id, now),
            )
            cur.execute(
                "insert into scan_attempts (registration_id,event_id,event_day_id,status,reason,attempted_at) "
                "values (%s,%s,%s,'allowed','ok',%s)", (reg_id, event_id, day_id, now),
            )
            cur.execute(
                "insert into email_jobs (registration_id,template_key,status,available_at,created_at,updated_at) "
                "values (%s,'confirmation','pending',%s,%s,%s)", (reg_id, now, now, now),
            )
            cur.execute(
                "insert into email_logs (registration_id,recipient,template_key,subject,status,created_at) "
                "values (%s,'tscheck@example.test','confirmation','Subject','sent',%s)", (reg_id, now),
            )
            cur.execute(
                "insert into registration_forms (event_id,title,created_at,updated_at) values (%s,'Form',%s,%s)",
                (event_id, now, now),
            )
            cur.execute(
                "insert into registration_fields (event_id,label,field_name,created_at,updated_at) "
                "values (%s,'Field','tscheck_field',%s,%s)", (event_id, now, now),
            )
            field_id = cur.lastrowid
            cur.execute(
                "insert into registration_field_values (registration_id,field_id,value_text,created_at) "
                "values (%s,%s,'value',%s)", (reg_id, field_id, now),
            )
            cur.execute(
                "insert into registration_members (registration_id,name,created_at) values (%s,'Member',%s)",
                (reg_id, now),
            )
            cur.execute(
                "insert into event_schedules (event_id,event_day_id,title,starts_at,created_at,updated_at) "
                "values (%s,%s,'Slot',%s,%s,%s)", (event_id, day_id, now, now, now),
            )
            cur.execute(
                "insert into event_speakers (event_id,name,created_at,updated_at) values (%s,'Speaker',%s,%s)",
                (event_id, now, now),
            )
            cur.execute(
                "insert into media_items (event_id,media_type,section,title,storage_path,created_at,updated_at) "
                "values (%s,'image','gallery','Media','tscheck-media.jpg',%s,%s)", (event_id, now, now),
            )
            cur.execute(
                "insert into event_galleries (event_id,image_path,created_at) values (%s,'tscheck-gallery.jpg',%s)",
                (event_id, now),
            )
        conn.commit()
    return {"registration_id": reg_id, "event_day_id": day_id}


def counts_for_event(event_id: int, registration_ids):
    with db_conn() as conn:
        with conn.cursor() as cur:
            out = {}
            cur.execute("select count(*) c from events where id=%s", (event_id,))
            out["events"] = cur.fetchone()["c"]
            for table in ["event_days", "media_items", "event_galleries",
                          "registration_forms", "registration_fields", "event_schedules",
                          "event_speakers"]:
                cur.execute(f"select count(*) c from {table} where event_id=%s", (event_id,))
                out[table] = cur.fetchone()["c"]
            cur.execute("select count(*) c from scan_attempts where event_id=%s", (event_id,))
            out["scan_attempts"] = cur.fetchone()["c"]
            if registration_ids:
                fmt = ",".join(["%s"] * len(registration_ids))
                for table in ["registrations", "payments", "qr_tokens", "attendance",
                              "email_jobs", "email_logs", "registration_field_values",
                              "registration_members"]:
                    col = "id" if table == "registrations" else "registration_id"
                    cur.execute(f"select count(*) c from {table} where {col} in ({fmt})", registration_ids)
                    out[table] = cur.fetchone()["c"]
            else:
                for table in ["registrations", "payments", "qr_tokens", "attendance",
                              "email_jobs", "email_logs", "registration_field_values",
                              "registration_members"]:
                    out[table] = 0
    return out


@pytest.fixture(scope="module")
def admin_client():
    client = httpx.Client(base_url=BASE_URL, follow_redirects=True, timeout=30)
    login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    yield client
    client.close()


def test_probe_server_reachable():
    r = httpx.get(BASE_URL + "/admin/login", timeout=10)
    assert r.status_code == 200


def test_permanent_delete_cascades_related_rows_and_leaves_audit(admin_client):
    suffix = str(int(time.time() * 1000))
    name = f"tscheck-permadelete-{suffix}"
    event_id = create_event(admin_client, name)

    seeded = seed_full_related_fixture(event_id)
    reg_ids = [seeded["registration_id"]]

    before = counts_for_event(event_id, reg_ids)
    assert before["events"] == 1
    for table, expected_min in [
        ("event_days", 1), ("media_items", 1), ("event_galleries", 1),
        ("registration_forms", 1), ("registration_fields", 1), ("event_schedules", 1),
        ("event_speakers", 1), ("scan_attempts", 1), ("registrations", 1), ("payments", 1),
        ("qr_tokens", 1), ("attendance", 1), ("email_jobs", 1), ("email_logs", 1),
        ("registration_field_values", 1), ("registration_members", 1),
    ]:
        assert before[table] >= expected_min, f"fixture seeding for {table} did not take effect: {before}"

    field, value = csrf_from(admin_client, "/admin/events", "")
    r = admin_client.post(f"/admin/events/{event_id}/delete", data={field: value, "confirm_name": name})
    assert r.status_code == 200

    after = counts_for_event(event_id, reg_ids)
    for table in after:
        assert after[table] == 0, f"{table} still has {after[table]} row(s) after permanent delete: {after}"

    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select count(*) c from audit_logs where action='event.permanently_deleted' and record_id=%s",
                (str(event_id),),
            )
            audit_count = cur.fetchone()["c"]
    assert audit_count >= 1, "no audit record retained for the permanent deletion"


def test_permanent_delete_rejected_with_wrong_confirmation_name(admin_client):
    suffix = str(int(time.time() * 1000))
    name = f"tscheck-wrongname-{suffix}"
    event_id = create_event(admin_client, name)

    field, value = csrf_from(admin_client, "/admin/events", "")
    r = admin_client.post(f"/admin/events/{event_id}/delete", data={field: value, "confirm_name": "not the real name"})
    assert r.status_code == 200

    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select count(*) c from events where id=%s", (event_id,))
            still_there = cur.fetchone()["c"]
    assert still_there == 1, "event was deleted despite a non-matching confirmation name"


def test_permanent_delete_forbidden_for_non_super_admin_scanner_account():
    scanner_client = httpx.Client(base_url=BASE_URL, follow_redirects=True, timeout=30)
    try:
        scanner_login(scanner_client, SCANNER_EMAIL, SCANNER_PASSWORD)
        # use the seeded upcoming-event fixture id (read-only lookup, never mutated by this test)
        with db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("select id, name from events where slug='upcoming-qr-proof'")
                seeded = cur.fetchone()
        assert seeded, "seeded 'Upcoming QR Proof' fixture missing"

        field, value = csrf_from(scanner_client, "/scanner/login", "")
        r = scanner_client.post(
            f"/admin/events/{seeded['id']}/delete",
            data={field: value, "confirm_name": seeded["name"]},
        )
        assert r.status_code in (403, 404), f"scanner account received {r.status_code} on admin delete route"

        with db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("select count(*) c from events where id=%s", (seeded["id"],))
                still_there = cur.fetchone()["c"]
        assert still_there == 1, "seeded event was deleted by a non-SUPER_ADMIN account"
    finally:
        scanner_client.close()


def test_bulk_permanent_delete_removes_only_selected_events(admin_client):
    suffix = str(int(time.time() * 1000))
    name_a = f"tscheck-bulkA-{suffix}"
    name_b = f"tscheck-bulkB-{suffix}"
    name_c = f"tscheck-bulkC-keep-{suffix}"
    id_a = create_event(admin_client, name_a)
    id_b = create_event(admin_client, name_b)
    id_c = create_event(admin_client, name_c)

    field, value = csrf_from(admin_client, "/admin/events", "")
    r = admin_client.post(
        "/admin/events/bulk-delete",
        data={field: value, "confirm_phrase": "DELETE SELECTED", "event_ids[]": [str(id_a), str(id_b)]},
    )
    assert r.status_code == 200

    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select id from events where id in (%s,%s,%s)", (id_a, id_b, id_c))
            remaining = {row["id"] for row in cur.fetchall()}
    assert remaining == {id_c}, f"expected only unselected event {id_c} to remain, got {remaining}"

    # cleanup the intentionally-kept fixture so it doesn't accumulate across reruns
    field2, value2 = csrf_from(admin_client, "/admin/events", "")
    admin_client.post(f"/admin/events/{id_c}/delete", data={field2: value2, "confirm_name": name_c})


def test_bulk_permanent_delete_rejected_with_wrong_confirmation_phrase(admin_client):
    suffix = str(int(time.time() * 1000))
    name = f"tscheck-bulkwrong-{suffix}"
    event_id = create_event(admin_client, name)

    field, value = csrf_from(admin_client, "/admin/events", "")
    r = admin_client.post(
        "/admin/events/bulk-delete",
        data={field: value, "confirm_phrase": "delete selected", "event_ids[]": [str(event_id)]},
    )
    assert r.status_code == 200

    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select count(*) c from events where id=%s", (event_id,))
            still_there = cur.fetchone()["c"]
    assert still_there == 1, "bulk deletion proceeded despite a wrong confirmation phrase"

    # cleanup with the correct phrase
    field2, value2 = csrf_from(admin_client, "/admin/events", "")
    admin_client.post(
        "/admin/events/bulk-delete",
        data={field2: value2, "confirm_phrase": "DELETE SELECTED", "event_ids[]": [str(event_id)]},
    )


def test_bulk_permanent_delete_allows_up_to_100_records(admin_client):
    """Directly seeds 100 fixture events (cheap SQL inserts) then bulk-deletes all
    100 in a single request to prove the 100-record cap is an allowance, not a
    lower artificial limit."""
    suffix = str(int(time.time() * 1000))
    now = "2026-01-01 00:00:00"
    ids = []
    with db_conn() as conn:
        with conn.cursor() as cur:
            for i in range(100):
                slug = f"tscheck-cap100-{suffix}-{i}"
                cur.execute(
                    "insert into events (category_id, name, slug, event_type, registration_type, fee, "
                    "tax_amount, discount_amount, capacity, payment_required, is_featured, status, "
                    "created_at, updated_at) values (1,%s,%s,'competition','individual',0,0,0,0,0,0,"
                    "'draft',%s,%s)",
                    (f"tscheck cap100 {suffix} {i}", slug, now, now),
                )
                ids.append(cur.lastrowid)
        conn.commit()
    assert len(ids) == 100

    field, value = csrf_from(admin_client, "/admin/events", "")
    r = admin_client.post(
        "/admin/events/bulk-delete",
        data={field: value, "confirm_phrase": "DELETE SELECTED", "event_ids[]": [str(i) for i in ids]},
    )
    assert r.status_code == 200

    with db_conn() as conn:
        with conn.cursor() as cur:
            fmt = ",".join(["%s"] * len(ids))
            cur.execute(f"select count(*) c from events where id in ({fmt})", ids)
            remaining = cur.fetchone()["c"]
    assert remaining == 0, f"{remaining} of the 100 selected fixture events survived a within-cap bulk deletion"


def test_bulk_permanent_delete_rejects_more_than_100_records(admin_client):
    suffix = str(int(time.time() * 1000))
    now = "2026-01-01 00:00:00"
    ids = []
    with db_conn() as conn:
        with conn.cursor() as cur:
            for i in range(101):
                slug = f"tscheck-cap101-{suffix}-{i}"
                cur.execute(
                    "insert into events (category_id, name, slug, event_type, registration_type, fee, "
                    "tax_amount, discount_amount, capacity, payment_required, is_featured, status, "
                    "created_at, updated_at) values (1,%s,%s,'competition','individual',0,0,0,0,0,0,"
                    "'draft',%s,%s)",
                    (f"tscheck cap101 {suffix} {i}", slug, now, now),
                )
                ids.append(cur.lastrowid)
        conn.commit()
    assert len(ids) == 101

    try:
        field, value = csrf_from(admin_client, "/admin/events", "")
        r = admin_client.post(
            "/admin/events/bulk-delete",
            data={field: value, "confirm_phrase": "DELETE SELECTED", "event_ids[]": [str(i) for i in ids]},
        )
        assert r.status_code == 200

        with db_conn() as conn:
            with conn.cursor() as cur:
                fmt = ",".join(["%s"] * len(ids))
                cur.execute(f"select count(*) c from events where id in ({fmt})", ids)
                remaining = cur.fetchone()["c"]
        assert remaining == 101, "a >100-record bulk deletion request was not fully rejected"
    finally:
        # cleanup: remove the 101 oversized fixture set directly since the app must reject it
        with db_conn() as conn:
            with conn.cursor() as cur:
                fmt = ",".join(["%s"] * len(ids))
                cur.execute(f"delete from events where id in ({fmt})", ids)
            conn.commit()
