"""Super Admin can create/manage role-based staff accounts without exposing passwords."""

from tests.conftest import unique_suffix


ROLES = ["scanner", "event_admin", "finance", "report_viewer", "admin"]


def test_create_each_role_without_exposing_password(admin_client):
    created_ids = []
    for role in ROLES:
        suffix = unique_suffix()
        payload = {
            "name": f"tscheck-staff-{role}-{suffix}",
            "email": f"tscheck.staff.{role}.{suffix}@example.test",
            "password": "StrongTempPass!2026",
            "role": role,
        }
        resp = admin_client.post("/admin/staff", json=payload)
        assert resp.status_code == 201, f"create {role} failed: {resp.status_code} {resp.text[:300]}"
        body = resp.json()
        assert body["role"] == role
        assert "password_hash" not in body
        assert "password" not in body
        created_ids.append((body["id"], role))

    listing = admin_client.get("/admin/staff")
    assert listing.status_code == 200
    rows = listing.json()["data"]
    row_by_id = {row["id"]: row for row in rows}
    for staff_id, role in created_ids:
        assert staff_id in row_by_id
        row = row_by_id[staff_id]
        assert row["role"] == role
        assert "password_hash" not in row
        assert "password" not in row


def test_activate_deactivate_staff_persists(admin_client):
    suffix = unique_suffix()
    payload = {
        "name": f"tscheck-staff-toggle-{suffix}",
        "email": f"tscheck.staff.toggle.{suffix}@example.test",
        "password": "StrongTempPass!2026",
        "role": "scanner",
    }
    created = admin_client.post("/admin/staff", json=payload).json()
    assert created["is_active"] is True

    deactivate = admin_client.put(
        f"/admin/staff/{created['id']}",
        json={"name": created["name"], "role": "scanner", "is_active": False, "password": None},
    )
    assert deactivate.status_code == 200, deactivate.text[:300]
    assert deactivate.json()["is_active"] is False

    reactivate = admin_client.put(
        f"/admin/staff/{created['id']}",
        json={"name": created["name"], "role": "scanner", "is_active": True, "password": None},
    )
    assert reactivate.status_code == 200
    assert reactivate.json()["is_active"] is True


def test_non_admin_cannot_manage_staff(scanner_client):
    resp = scanner_client.get("/admin/staff")
    assert resp.status_code == 403, resp.text[:300]
