"""Scanner assignments are enforced by event, day and gate."""

from tests.conftest import make_event, register_for_event, unique_suffix, API_URL
import httpx


def _make_scanner(admin_client, suffix: str) -> dict:
    payload = {
        "name": f"tscheck-scanner-{suffix}",
        "email": f"tscheck.scanner.{suffix}@example.test",
        "password": "StrongTempPass!2026",
        "role": "scanner",
    }
    resp = admin_client.post("/admin/staff", json=payload)
    assert resp.status_code == 201, resp.text[:300]
    return resp.json()


def test_scanner_context_and_scan_restricted_to_assignment(admin_client):
    suffix = unique_suffix()
    event = make_event(admin_client, fee=0.0, days=2)
    scanner = _make_scanner(admin_client, suffix)

    assign = admin_client.post(
        f"/admin/staff/{scanner['id']}/assignments",
        json={
            "event_id": event["id"],
            "event_day_ids": [event["event_days"][0]["id"]],
            "gates": ["Gate 1 · Main Entry"],
        },
    )
    assert assign.status_code == 200, assign.text[:300]

    with httpx.Client(base_url=API_URL, timeout=30.0) as scanner_c:
        login = scanner_c.post(
            "/auth/scanner/login",
            json={"email": scanner["email"], "password": "StrongTempPass!2026"},
        )
        assert login.status_code == 200, login.text[:300]
        token = login.cookies.get("euphoria_session")
        scanner_c.cookies.set("euphoria_session", token, domain="", path="/")

        context = scanner_c.get("/scanner/context")
        assert context.status_code == 200
        ctx = context.json()
        assert [row["id"] for row in ctx["events"]] == [event["id"]]
        visible_days = ctx["events"][0]["event_days"]
        assert len(visible_days) == 1
        assert visible_days[0]["id"] == event["event_days"][0]["id"]
        assert ctx["gates"] == ["Gate 1 · Main Entry"]

        registration = register_for_event(scanner_c, event)
        token_value = registration["pass_key"]
        # fetch the raw QR token via the pass endpoint using the pass_key
        pass_resp = scanner_c.get(
            f"/passes/{registration['registration_id']}", params={"key": token_value}
        )
        assert pass_resp.status_code == 200, pass_resp.text[:300]
        qr_token = pass_resp.json()["qr_token"]

        allowed_scan = {
            "token": qr_token,
            "event_id": event["id"],
            "event_day_id": event["event_days"][0]["id"],
            "gate": "Gate 1 · Main Entry",
        }
        allow_resp = scanner_c.post("/scanner/scan", json=allowed_scan)
        assert allow_resp.status_code == 200, allow_resp.text[:300]
        assert allow_resp.json()["status"] == "allowed"

        wrong_day = {**allowed_scan, "event_day_id": event["event_days"][1]["id"]}
        registration2 = register_for_event(scanner_c, event)
        pass_resp2 = scanner_c.get(
            f"/passes/{registration2['registration_id']}", params={"key": registration2["pass_key"]}
        )
        qr_token2 = pass_resp2.json()["qr_token"]
        wrong_day["token"] = qr_token2
        denied_day = scanner_c.post("/scanner/scan", json=wrong_day)
        assert denied_day.status_code == 200
        assert denied_day.json()["status"] == "denied"

        wrong_gate = {**allowed_scan, "gate": "Gate 2 · Sports Entry", "token": qr_token2}
        denied_gate = scanner_c.post("/scanner/scan", json=wrong_gate)
        assert denied_gate.status_code == 200
        assert denied_gate.json()["status"] == "denied"
