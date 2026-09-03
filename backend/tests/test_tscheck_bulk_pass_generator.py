"""Backend coverage for criterion: Admin bulk pass generator accepts CSV and XLSX,
creates confirmed complimentary registrations with unique IDs/active QR/zero-value
payment and scheduled email, and reports row errors for invalid/duplicate rows.
"""
import io

from .conftest import make_event, unique_suffix


def _csv_bytes(rows: list[str]) -> bytes:
    header = "participant_name,mobile,institute_name,email,event_name\n"
    return (header + "\n".join(rows)).encode()


def test_csv_upload_creates_confirmed_complimentary_pass_and_flags_bad_rows(admin_client):
    event = make_event(admin_client, fee=0.0, days=1)
    suffix = unique_suffix()
    good_email = f"tscheck.bulk.{suffix}@example.test"
    valid_row = f"tscheck bulk participant {suffix},9876543210,tscheck Institute,{good_email},{event['name']}"
    bad_mobile_row = f"tscheck bulk bad {suffix},12345,tscheck Institute,tscheck.bad.{suffix}@example.test,{event['name']}"
    csv_content = _csv_bytes([valid_row, bad_mobile_row])

    files = {"file": (f"tscheck-bulk-{suffix}.csv", io.BytesIO(csv_content), "text/csv")}
    resp = admin_client.post("/admin/bulk-passes/import", files=files)
    assert resp.status_code == 200, resp.text[:300]
    body = resp.json()

    assert body["total_rows"] == 2
    assert body["created"] == 1
    assert body["emails_scheduled"] == 1
    assert len(body["errors"]) == 1
    assert body["errors"][0]["row"] == 3  # header + row 1 = data row 2, bad row is row 3
    registration_id = body["registration_ids"][0]
    assert registration_id.startswith("EUPHORIA-2026-")

    # Verify the created registration is confirmed, zero-value, complimentary, active QR.
    roster = admin_client.get("/admin/registrations").json()["data"]
    created = next(row for row in roster if row["registration_id"] == registration_id)
    assert created["status"] == "confirmed"
    assert created["total_amount"] == 0.0
    assert created["payment_status"] in {"successful", "manual_verified"}
    assert created["qr_status"] == "active"


def test_duplicate_email_for_same_event_is_skipped_with_row_error(admin_client):
    event = make_event(admin_client, fee=0.0, days=1)
    suffix = unique_suffix()
    email = f"tscheck.bulkdup.{suffix}@example.test"
    row = f"tscheck bulk dup {suffix},9876543210,tscheck Institute,{email},{event['name']}"
    csv_content = _csv_bytes([row])

    first = admin_client.post(
        "/admin/bulk-passes/import",
        files={"file": (f"tscheck-bulkdup-a-{suffix}.csv", io.BytesIO(csv_content), "text/csv")},
    )
    assert first.status_code == 200 and first.json()["created"] == 1, first.text[:300]

    second = admin_client.post(
        "/admin/bulk-passes/import",
        files={"file": (f"tscheck-bulkdup-b-{suffix}.csv", io.BytesIO(csv_content), "text/csv")},
    )
    assert second.status_code == 200, second.text[:300]
    second_body = second.json()
    assert second_body["created"] == 0
    assert second_body["skipped"] == 1
    assert len(second_body["errors"]) == 1
    assert "already" in second_body["errors"][0]["message"].lower()
