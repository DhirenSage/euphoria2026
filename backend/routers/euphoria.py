import hashlib
import os
import secrets
import base64
import asyncio
import smtplib
import html
from io import BytesIO
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from urllib.parse import parse_qs

import bcrypt
from cryptography.fernet import Fernet
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
import httpx
import qrcode
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument

from lib.catalogue import CATEGORIES, ensure_catalogue
from lib.dates import today_iso
from lib.db import db
from models.euphoria import (
    AdminDashboardResponse,
    AdminEventWrite,
    AdminPaymentsResponse,
    AdminRegistrationsResponse,
    AdminStaffResponse,
    EuphoriaEvent,
    EuphoriaEventResponse,
    EuphoriaEventsResponse,
    EuphoriaHealth,
    LoginRequest,
    ManualVerificationRequest,
    PaymentInitiationResponse,
    PassResponse,
    ParticipantUpdate,
    QrStateRequest,
    RegistrationCatalogueResponse,
    RegistrationCreate,
    RegistrationResponse,
    ScanRequest,
    ScannerContextResponse,
    ScannerAssignmentInput,
    ScanResponse,
    SessionUser,
    StaffCreate,
    StaffRow,
    StaffUpdate,
)

router = APIRouter()


def clean(document: dict) -> dict:
    document.pop("_id", None)
    return document


SESSION_COOKIE = "euphoria_session"
SESSION_HOURS = 8
GATES = ["Gate 1 · Main Entry", "Gate 2 · Sports Entry", "Gate 3 · Auditorium"]
ADMIN_PORTAL_ROLES = {"admin", "event_admin", "finance", "report_viewer"}
EVENT_MANAGER_ROLES = {"admin", "event_admin"}
FINANCE_ROLES = {"admin", "finance"}


def cipher() -> Fernet:
    secret = os.environ.get("PASS_SIGNING_SECRET", "")
    if not secret:
        raise HTTPException(status_code=503, detail="Pass signing is not configured.")
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest()))


def registration_view(row: dict, pass_key: str | None = None) -> dict:
    return {
        "registration_id": row["registration_id"],
        "participant_name": row["participant_name"],
        "event_id": row["event_id"],
        "event_name": row["event_name"],
        "category_name": row["category_name"],
        "registration_type": row["registration_type"],
        "total_amount": float(row["total_amount"]),
        "status": row["status"],
        "created_at": row["created_at"],
        "payment_status": row.get("payment", {}).get("status", "created"),
        "qr_ready": row.get("status") == "confirmed" and row.get("qr_status") == "active",
        "pass_key": pass_key,
    }


async def session_user(request: Request) -> dict | None:
    raw = request.cookies.get(SESSION_COOKIE, "")
    if not raw:
        return None
    session = await db.euphoria_sessions.find_one({
        "token_hash": hashlib.sha256(raw.encode()).hexdigest(),
        "expires_at": {"$gt": datetime.now(timezone.utc)},
    })
    if not session:
        return None
    user = await db.euphoria_users.find_one({"id": session["user_id"], "is_active": True}, {"_id": 0, "password_hash": 0})
    return user


async def require_user(request: Request, roles: set[str]) -> dict:
    user = await session_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Sign in to continue.")
    if user["role"] not in roles:
        raise HTTPException(status_code=403, detail="This account cannot access this portal.")
    return user


async def audit(user: dict | None, action: str, module: str, record_id: str | None, details: dict | None = None):
    await db.euphoria_audit_logs.insert_one({
        "user_id": user.get("id") if user else None,
        "user_name": user.get("name") if user else "system",
        "action": action,
        "module": module,
        "record_id": record_id,
        "details": details or {},
        "created_at": datetime.now(timezone.utc),
    })


async def login(payload: LoginRequest, response: Response, allowed_roles: set[str]) -> SessionUser:
    email = payload.email.strip().lower()
    user = await db.euphoria_users.find_one({"email": email, "is_active": True})
    if not user or user.get("role") not in allowed_roles or not bcrypt.checkpw(payload.password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Email or password is incorrect for this portal.")
    raw = secrets.token_urlsafe(48)
    expires = datetime.now(timezone.utc) + timedelta(hours=SESSION_HOURS)
    await db.euphoria_sessions.insert_one({
        "token_hash": hashlib.sha256(raw.encode()).hexdigest(),
        "user_id": user["id"],
        "expires_at": expires,
        "created_at": datetime.now(timezone.utc),
    })
    response.set_cookie(
        SESSION_COOKIE,
        raw,
        max_age=SESSION_HOURS * 3600,
        httponly=True,
        secure=os.environ.get("APP_URL", "").startswith("https://"),
        samesite="lax",
        path="/",
    )
    await audit(user, "auth.login", "auth", user["id"])
    return SessionUser(id=user["id"], name=user["name"], email=user["email"], role=user["role"])


@router.post("/auth/admin/login", response_model=SessionUser)
async def admin_login(payload: LoginRequest, response: Response):
    return await login(payload, response, ADMIN_PORTAL_ROLES)


@router.post("/auth/scanner/login", response_model=SessionUser)
async def scanner_login(payload: LoginRequest, response: Response):
    return await login(payload, response, {"scanner"})


@router.get("/auth/me", response_model=SessionUser)
async def auth_me(request: Request):
    user = await require_user(request, ADMIN_PORTAL_ROLES | {"scanner"})
    return user


@router.post("/auth/logout", status_code=204)
async def auth_logout(request: Request, response: Response):
    raw = request.cookies.get(SESSION_COOKIE, "")
    if raw:
        await db.euphoria_sessions.delete_one({"token_hash": hashlib.sha256(raw.encode()).hexdigest()})
    response.delete_cookie(SESSION_COOKIE, path="/")


def event_document(payload: AdminEventWrite, event_id: str) -> dict:
    category = next((item for item in CATEGORIES if item["id"] == payload.category_id), None)
    if not category:
        raise HTTPException(status_code=422, detail="Select a valid category.")
    if payload.registration_type == "team":
        if not payload.min_team_size or not payload.max_team_size or payload.min_team_size > payload.max_team_size:
            raise HTTPException(status_code=422, detail="Team minimum and maximum sizes are required and must be valid.")
    return {
        **payload.model_dump(exclude={"event_days"}),
        "id": event_id,
        "category_name": category["name"],
        "event_days": [
            {"id": f"{event_id}-day-{index + 1}", "label": day.label, "date": day.date}
            for index, day in enumerate(payload.event_days)
        ],
        "updated_at": datetime.now(timezone.utc),
    }


@router.get("/admin/dashboard", response_model=AdminDashboardResponse)
async def admin_dashboard(request: Request):
    await require_user(request, ADMIN_PORTAL_ROLES)
    all_events = await db.euphoria_events.find({}, {"_id": 0}).sort("name", 1).to_list(1000)
    registrations = await db.euphoria_registrations.find({}, {"_id": 0}).to_list(10000)
    entries = await db.euphoria_attendance.count_documents({"status": "allowed"})
    duplicates = await db.euphoria_scan_attempts.count_documents({"status": "duplicate"})
    revenue = sum(float(row.get("total_amount", 0)) for row in registrations if row.get("payment", {}).get("status") in {"successful", "manual_verified"})
    recent_scans = await db.euphoria_scan_attempts.find({}, {"_id": 0}).sort("created_at", -1).to_list(10)
    return {
        "stats": {
            "events": len(all_events),
            "registrations": len(registrations),
            "confirmed": sum(1 for row in registrations if row.get("status") == "confirmed"),
            "revenue": revenue,
            "entries": entries,
            "duplicate_attempts": duplicates,
        },
        "events": all_events,
        "recent_scans": recent_scans,
    }


@router.get("/admin/events", response_model=EuphoriaEventsResponse)
async def admin_events(request: Request):
    await require_user(request, ADMIN_PORTAL_ROLES)
    rows = await db.euphoria_events.find({}, {"_id": 0}).sort("name", 1).to_list(1000)
    return {"data": rows, "meta": {"programme": "Euphoria 2026"}}


@router.post("/admin/events", response_model=EuphoriaEvent, status_code=201)
async def create_admin_event(payload: AdminEventWrite, request: Request):
    user = await require_user(request, EVENT_MANAGER_ROLES)
    if await db.euphoria_events.find_one({"slug": payload.slug}):
        raise HTTPException(status_code=409, detail="An event with this slug already exists.")
    event_id = f"evt-{secrets.token_hex(8)}"
    row = event_document(payload, event_id)
    row["created_at"] = datetime.now(timezone.utc)
    await db.euphoria_events.insert_one(row)
    await audit(user, "event.created", "events", event_id, {"fee": payload.fee, "status": payload.status})
    return clean(row)


@router.put("/admin/events/{event_id}", response_model=EuphoriaEvent)
async def update_admin_event(event_id: str, payload: AdminEventWrite, request: Request):
    user = await require_user(request, EVENT_MANAGER_ROLES)
    existing = await db.euphoria_events.find_one({"id": event_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Event not found.")
    duplicate = await db.euphoria_events.find_one({"slug": payload.slug, "id": {"$ne": event_id}})
    if duplicate:
        raise HTTPException(status_code=409, detail="An event with this slug already exists.")
    row = event_document(payload, event_id)
    await db.euphoria_events.update_one({"id": event_id}, {"$set": row})
    await audit(user, "event.updated", "events", event_id, {"old_fee": existing.get("fee"), "fee": payload.fee, "status": payload.status})
    return row


@router.delete("/admin/events/{event_id}", status_code=204)
async def delete_admin_event(event_id: str, request: Request):
    user = await require_user(request, EVENT_MANAGER_ROLES)
    if await db.euphoria_registrations.count_documents({"event_id": event_id}):
        await db.euphoria_events.update_one({"id": event_id}, {"$set": {"status": "cancelled", "updated_at": datetime.now(timezone.utc)}})
        await audit(user, "event.cancelled", "events", event_id)
    else:
        result = await db.euphoria_events.delete_one({"id": event_id})
        if not result.deleted_count:
            raise HTTPException(status_code=404, detail="Event not found.")
        await audit(user, "event.deleted", "events", event_id)


@router.get("/admin/registrations", response_model=AdminRegistrationsResponse)
async def admin_registrations(request: Request):
    await require_user(request, ADMIN_PORTAL_ROLES)
    rows = await db.euphoria_registrations.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    output = []
    for row in rows:
        attendance = await db.euphoria_attendance.find({"registration_id": row["registration_id"]}, {"_id": 0, "scanner_id": 0, "scanner_name": 0, "status": 0}).sort("entry_at", 1).to_list(20)
        output.append({
            "registration_id": row["registration_id"], "participant_name": row["participant_name"],
            "email": row["email"], "mobile": row["mobile"], "college": row["college"],
            "event_id": row["event_id"], "event_name": row["event_name"], "category_name": row["category_name"],
            "registration_type": row["registration_type"], "total_amount": float(row["total_amount"]),
            "status": row["status"], "payment_status": row.get("payment", {}).get("status", "created"),
            "qr_status": row.get("qr_status", "pending"), "created_at": row["created_at"], "attendance": attendance,
        })
    return {"data": output}


@router.post("/admin/registrations/{registration_id}/confirm", response_model=RegistrationResponse)
async def admin_confirm_registration(registration_id: str, request: Request):
    user = await require_user(request, FINANCE_ROLES)
    existing = await db.euphoria_registrations.find_one({"registration_id": registration_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Registration not found.")
    if float(existing.get("total_amount", 0)) > 0:
        raise HTTPException(status_code=409, detail="Use Payment Reconciliation with a transaction reference and reason.")
    row = await db.euphoria_registrations.find_one_and_update(
        {"registration_id": registration_id},
        {"$set": {"status": "confirmed", "payment.status": "manual_verified", "qr_status": "active", "updated_at": datetime.now(timezone.utc)}},
        return_document=ReturnDocument.AFTER,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Registration not found.")
    await audit(user, "registration.manual_confirmed", "registrations", registration_id)
    return registration_view(row)


def mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    return f"{local[:2]}***@{domain}" if domain else "***"


@router.get("/admin/payments", response_model=AdminPaymentsResponse)
async def admin_payments(request: Request, state: str = ""):
    await require_user(request, FINANCE_ROLES)
    rows = await db.euphoria_registrations.find({}, {"_id": 0}).sort("updated_at", -1).to_list(2000)
    data = []
    for row in rows:
        payment = row.get("payment", {})
        payment_state = payment.get("status", "created")
        if state and payment_state != state:
            continue
        data.append({
            "payment_ref": row["registration_id"], "registration_id": row["registration_id"],
            "participant_name": row["participant_name"], "masked_email": mask_email(row["email"]),
            "event_name": row["event_name"], "amount": float(row["total_amount"]), "state": payment_state,
            "txnid": payment.get("txnid", ""), "gateway_payment_id": payment.get("easepayid"),
            "attempts": payment.get("attempts", []), "updated_at": row.get("updated_at", row["created_at"]),
        })
    return {"data": data}


@router.post("/admin/payments/{registration_id}/verify", response_model=RegistrationResponse)
async def manual_verify_payment(registration_id: str, payload: ManualVerificationRequest, request: Request):
    user = await require_user(request, FINANCE_ROLES)
    row = await db.euphoria_registrations.find_one_and_update(
        {"registration_id": registration_id, "payment.status": {"$nin": ["successful", "manual_verified"]}},
        {"$set": {
            "status": "confirmed", "payment.status": "manual_verified",
            "payment.manual_reference": payload.transaction_reference, "payment.manual_reason": payload.reason,
            "payment.verified_by": user["id"], "payment.verified_at": datetime.now(timezone.utc),
            "qr_status": "active", "updated_at": datetime.now(timezone.utc),
        }},
        return_document=ReturnDocument.AFTER,
    )
    if not row:
        existing = await db.euphoria_registrations.find_one({"registration_id": registration_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Payment not found.")
        raise HTTPException(status_code=409, detail="This payment is already verified.")
    await audit(user, "payment.manual_verified", "payments", registration_id, {"reason": payload.reason, "reference": payload.transaction_reference})
    return registration_view(row)


@router.post("/admin/payments/{registration_id}/retry", response_model=PaymentInitiationResponse)
async def admin_retry_payment(registration_id: str, request: Request):
    user = await require_user(request, FINANCE_ROLES)
    row = await db.euphoria_registrations.find_one({"registration_id": registration_id})
    if not row:
        raise HTTPException(status_code=404, detail="Payment not found.")
    return await initiate_gateway_checkout(row, user)


@router.put("/admin/registrations/{registration_id}", response_model=RegistrationResponse)
async def update_participant(registration_id: str, payload: ParticipantUpdate, request: Request):
    user = await require_user(request, EVENT_MANAGER_ROLES)
    row = await db.euphoria_registrations.find_one_and_update(
        {"registration_id": registration_id},
        {"$set": {
            "participant_name": payload.participant_name.strip(), "email": payload.email.lower(),
            "mobile": payload.mobile, "college": payload.college.strip(), "updated_at": datetime.now(timezone.utc),
        }},
        return_document=ReturnDocument.AFTER,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Registration not found.")
    await audit(user, "participant.updated", "registrations", registration_id)
    return registration_view(row)


@router.post("/admin/registrations/{registration_id}/state", response_model=RegistrationResponse)
async def registration_state(registration_id: str, payload: QrStateRequest, request: Request):
    user = await require_user(request, EVENT_MANAGER_ROLES | FINANCE_ROLES)
    existing = await db.euphoria_registrations.find_one({"registration_id": registration_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Registration not found.")
    update: dict = {"updated_at": datetime.now(timezone.utc)}
    if payload.action == "cancel":
        update.update({"status": "cancelled", "qr_status": "revoked"})
    elif payload.action == "revoke":
        update["qr_status"] = "revoked"
    elif payload.action == "restore":
        if existing.get("status") != "confirmed":
            raise HTTPException(status_code=409, detail="Restore the registration before restoring its QR.")
        update["qr_status"] = "active"
    else:
        paid = existing.get("payment", {}).get("status") in {"successful", "manual_verified"} or float(existing.get("total_amount", 0)) == 0
        if not paid:
            raise HTTPException(status_code=409, detail="Payment verification is required before restoration.")
        update.update({"status": "confirmed", "qr_status": "active"})
    row = await db.euphoria_registrations.find_one_and_update({"_id": existing["_id"]}, {"$set": update}, return_document=ReturnDocument.AFTER)
    await audit(user, f"registration.{payload.action}", "registrations", registration_id)
    return registration_view(row)


def qr_png(token: str) -> bytes:
    image = qrcode.make(token)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def send_pass_email_sync(recipient: str, participant: str, event_name: str, registration_id: str, pass_url: str, image: bytes):
    message = EmailMessage()
    message["Subject"] = "Euphoria 2026 – Your Event Pass"
    message["From"] = f"{os.environ.get('SMTP_FROM_NAME', 'SAGE EUPHORIA')} <{os.environ.get('SMTP_FROM_EMAIL', '')}>"
    message["To"] = recipient
    message.set_content(f"Hello {participant},\n\nYour pass for {event_name} is ready.\nRegistration ID: {registration_id}\nSecure pass: {pass_url}\n\nKeep the attached QR ready at the gate.")
    message.add_alternative(f"<h2>Your EUPHORIA pass is ready</h2><p>Hello {html.escape(participant)},</p><p><strong>{html.escape(event_name)}</strong><br>Registration ID: {html.escape(registration_id)}</p><p><a href=\"{html.escape(pass_url, quote=True)}\">Open secure digital pass</a></p><p>Keep the attached QR ready at the gate.</p>", subtype="html")
    message.add_attachment(image, maintype="image", subtype="png", filename=f"{registration_id}-qr.png")
    with smtplib.SMTP(os.environ.get("SMTP_HOST", ""), int(os.environ.get("SMTP_PORT", "587")), timeout=20) as smtp:
        smtp.starttls()
        smtp.login(os.environ.get("SMTP_USER", ""), os.environ.get("SMTP_PASSWORD", ""))
        smtp.send_message(message)


@router.post("/admin/registrations/{registration_id}/resend-pass")
async def resend_pass(registration_id: str, request: Request):
    user = await require_user(request, EVENT_MANAGER_ROLES | FINANCE_ROLES)
    registration = await db.euphoria_registrations.find_one({"registration_id": registration_id})
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found.")
    if registration.get("status") != "confirmed" or registration.get("qr_status") != "active":
        raise HTTPException(status_code=409, detail="Only an active confirmed pass can be sent.")
    pass_key = secrets.token_urlsafe(32)
    await db.euphoria_registrations.update_one({"_id": registration["_id"]}, {"$set": {"pass_key_hash": hashlib.sha256(pass_key.encode()).hexdigest(), "pass_sent_at": datetime.now(timezone.utc)}})
    token = cipher().decrypt(registration["qr_token_ciphertext"].encode()).decode()
    pass_url = f"{os.environ.get('APP_URL', '').rstrip('/')}/pass/{registration_id}?key={pass_key}"
    try:
        await asyncio.to_thread(send_pass_email_sync, registration["email"], registration["participant_name"], registration["event_name"], registration_id, pass_url, qr_png(token))
    except Exception as exc:
        await audit(user, "pass.email_failed", "registrations", registration_id, {"error_type": type(exc).__name__})
        raise HTTPException(status_code=502, detail="The mail provider could not send this pass.") from exc
    await audit(user, "pass.resent", "registrations", registration_id)
    return {"ok": True, "message": "Pass email sent successfully."}


@router.get("/admin/staff", response_model=AdminStaffResponse)
async def admin_staff(request: Request):
    await require_user(request, {"admin"})
    rows = await db.euphoria_users.find({}, {"_id": 0, "password_hash": 0}).sort("created_at", 1).to_list(1000)
    return {"data": rows}


@router.post("/admin/staff", response_model=StaffRow, status_code=201)
async def create_staff(payload: StaffCreate, request: Request):
    user = await require_user(request, {"admin"})
    if await db.euphoria_users.find_one({"email": payload.email.lower()}):
        raise HTTPException(status_code=409, detail="A staff account with this email already exists.")
    row = {
        "id": f"staff-{secrets.token_hex(8)}", "name": payload.name.strip(), "email": payload.email.lower(),
        "password_hash": bcrypt.hashpw(payload.password.encode(), bcrypt.gensalt()).decode(), "role": payload.role,
        "is_active": True, "assigned_event_ids": [], "assignments": [], "created_at": datetime.now(timezone.utc),
    }
    await db.euphoria_users.insert_one(row)
    await audit(user, "staff.created", "users", row["id"], {"role": row["role"]})
    return {key: value for key, value in clean(row).items() if key != "password_hash"}


@router.put("/admin/staff/{staff_id}", response_model=StaffRow)
async def update_staff(staff_id: str, payload: StaffUpdate, request: Request):
    user = await require_user(request, {"admin"})
    existing = await db.euphoria_users.find_one({"id": staff_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Staff user not found.")
    if existing.get("role") == "admin" and existing.get("is_active") and (not payload.is_active or payload.role != "admin"):
        active_admins = await db.euphoria_users.count_documents({"role": "admin", "is_active": True})
        if active_admins <= 1:
            raise HTTPException(status_code=409, detail="Create another active Super Admin before changing this account.")
    update = {"name": payload.name.strip(), "role": payload.role, "is_active": payload.is_active, "updated_at": datetime.now(timezone.utc)}
    if payload.password:
        update["password_hash"] = bcrypt.hashpw(payload.password.encode(), bcrypt.gensalt()).decode()
    row = await db.euphoria_users.find_one_and_update({"id": staff_id}, {"$set": update}, return_document=ReturnDocument.AFTER)
    await audit(user, "staff.updated", "users", staff_id, {"role": payload.role, "is_active": payload.is_active})
    return {key: value for key, value in clean(row).items() if key != "password_hash"}


@router.post("/admin/staff/{staff_id}/assignments", response_model=dict)
async def assign_scanner(staff_id: str, payload: ScannerAssignmentInput, request: Request):
    user = await require_user(request, {"admin"})
    staff = await db.euphoria_users.find_one({"id": staff_id, "role": "scanner", "is_active": True})
    event_row = await db.euphoria_events.find_one({"id": payload.event_id}, {"_id": 0})
    if not staff or not event_row:
        raise HTTPException(status_code=404, detail="Scanner or event not found.")
    valid_days = {day["id"] for day in event_row.get("event_days", [])}
    if not set(payload.event_day_ids).issubset(valid_days) or not set(payload.gates).issubset(set(GATES)):
        raise HTTPException(status_code=422, detail="Select valid event days and gates.")
    assignment = {"event_id": payload.event_id, "event_day_ids": payload.event_day_ids, "gates": payload.gates}
    assignments = [item for item in staff.get("assignments", []) if item.get("event_id") != payload.event_id]
    assignments.append(assignment)
    await db.euphoria_users.update_one({"_id": staff["_id"]}, {"$set": {"assignments": assignments}, "$addToSet": {"assigned_event_ids": payload.event_id}})
    await audit(user, "scanner.assigned", "users", staff_id, assignment)
    return assignment


@router.get("/health", response_model=EuphoriaHealth)
async def health():
    await db.command("ping")
    return {"ok": True, "service": "euphoria-platform", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/events", response_model=EuphoriaEventsResponse)
async def events():
    rows = await db.euphoria_events.find({"status": "registration_open"}, {"_id": 0}).sort([("category_id", 1), ("name", 1)]).to_list(100)
    return {"data": rows, "meta": {"programme": "Euphoria 2026"}}


@router.get("/events/{slug}", response_model=EuphoriaEventResponse)
async def event(slug: str):
    row = await db.euphoria_events.find_one({"slug": slug}, {"_id": 0})
    if not row:
        return JSONResponse(status_code=404, content={"error": {"code": "event_not_found", "message": "Event not found."}})
    return {"data": row}


@router.get("/registration-catalogue", response_model=RegistrationCatalogueResponse)
async def registration_catalogue():
    rows = await db.euphoria_events.find({"status": "registration_open"}, {"_id": 0}).sort([("category_id", 1), ("name", 1)]).to_list(100)
    return {"categories": CATEGORIES, "events": rows}


@router.post("/registrations", response_model=RegistrationResponse, status_code=201)
async def create_registration(payload: RegistrationCreate):
    event_row = await db.euphoria_events.find_one({"id": payload.event_id, "category_id": payload.category_id, "status": "registration_open"}, {"_id": 0})
    if not event_row:
        raise HTTPException(status_code=400, detail="Select a valid event from the chosen category.")
    if event_row["registration_type"] == "team" and not (payload.team_name or "").strip():
        raise HTTPException(status_code=422, detail="Team name is required for this event.")
    if event_row.get("capacity", 0) > 0:
        active_count = await db.euphoria_registrations.count_documents({
            "event_id": event_row["id"], "status": {"$in": ["pending_payment", "confirmed"]}
        })
        if active_count >= int(event_row["capacity"]):
            raise HTTPException(status_code=409, detail="This event has reached its registration capacity.")
    if event_row["registration_type"] == "team":
        members = [line.strip() for line in (payload.team_members or "").splitlines() if line.strip()]
        size = 1 + len(members)
        if event_row.get("min_team_size") and size < int(event_row["min_team_size"]):
            raise HTTPException(status_code=422, detail=f"At least {event_row['min_team_size']} team members including the captain are required.")
        if event_row.get("max_team_size") and size > int(event_row["max_team_size"]):
            raise HTTPException(status_code=422, detail=f"At most {event_row['max_team_size']} team members including the captain are allowed.")

    counter = await db.counters.find_one_and_update(
        {"_id": "euphoria_registration"}, {"$inc": {"seq": 1}}, upsert=True, return_document=ReturnDocument.AFTER
    )
    registration_id = f"EUPHORIA-2026-{counter['seq']:06d}"
    created_at = datetime.now(timezone.utc)
    status = "confirmed" if float(event_row["fee"]) == 0 else "pending_payment"
    pass_key = secrets.token_urlsafe(32)
    qr_token = f"EUPHORIA-{secrets.token_urlsafe(32)}"
    row = {
        "registration_id": registration_id,
        "participant_name": payload.name.strip(),
        "father_name": (payload.father_name or "").strip() or None,
        "email": str(payload.email).lower(),
        "mobile": payload.mobile,
        "age": payload.age,
        "college": payload.college.strip(),
        "city": (payload.city or "").strip() or None,
        "participant_affiliation": payload.participant_affiliation,
        "event_id": event_row["id"],
        "event_name": event_row["name"],
        "category_id": event_row["category_id"],
        "category_name": event_row["category_name"],
        "registration_type": event_row["registration_type"],
        "team_name": (payload.team_name or "").strip() or None,
        "team_members": (payload.team_members or "").strip() or None,
        "total_amount": float(event_row["fee"]),
        "status": status,
        "payment": {"status": "successful" if status == "confirmed" else "created", "txnid": f"EB-{secrets.token_hex(12)}"},
        "pass_key_hash": hashlib.sha256(pass_key.encode()).hexdigest(),
        "qr_token_hash": hashlib.sha256(qr_token.encode()).hexdigest(),
        "qr_token_ciphertext": cipher().encrypt(qr_token.encode()).decode(),
        "qr_status": "active" if status == "confirmed" else "pending",
        "created_at": created_at,
        "updated_at": created_at,
    }
    await db.euphoria_registrations.insert_one(row)
    await audit(None, "registration.created", "registrations", registration_id, {"event_id": event_row["id"], "amount": row["total_amount"]})
    return registration_view(row, pass_key)


@router.get("/registrations/{registration_id}", response_model=RegistrationResponse)
async def get_registration(registration_id: str):
    row = await db.euphoria_registrations.find_one({"registration_id": registration_id})
    if not row:
        raise HTTPException(status_code=404, detail="Registration not found.")
    return registration_view(row)


async def initiate_gateway_checkout(row: dict, actor: dict | None = None) -> dict:
    if row["status"] == "confirmed" or row.get("payment", {}).get("status") in {"successful", "manual_verified"}:
        raise HTTPException(status_code=409, detail="Registration is already confirmed.")
    key, salt = os.environ.get("EASEBUZZ_KEY", ""), os.environ.get("EASEBUZZ_SALT", "")
    if not key or not salt:
        raise HTTPException(status_code=503, detail="Easebuzz is not configured.")
    app_url = os.environ.get("APP_URL", "").rstrip("/")
    product_info = os.environ.get("EASEBUZZ_PRODUCTINFO", "euphoria2026")
    transaction_id = f"EB-{secrets.token_hex(12)}"
    fields = {
        "key": key,
        "txnid": transaction_id,
        "amount": f"{row['total_amount']:.2f}",
        "productinfo": product_info,
        "firstname": row["participant_name"],
        "email": row["email"],
        "phone": row["mobile"],
        "surl": f"{app_url}/api/payments/easebuzz/callback",
        "furl": f"{app_url}/api/payments/easebuzz/callback",
        "udf1": row["registration_id"],
    }
    hash_order = ["key", "txnid", "amount", "productinfo", "firstname", "email", "udf1", "udf2", "udf3", "udf4", "udf5", "udf6", "udf7", "udf8", "udf9", "udf10"]
    fields["hash"] = hashlib.sha512(("|".join(fields.get(item, "") for item in hash_order) + "|" + salt).encode()).hexdigest()
    production = os.environ.get("EASEBUZZ_ENV") == "prod"
    endpoint = "https://pay.easebuzz.in/payment/initiateLink" if production else "https://testpay.easebuzz.in/payment/initiateLink"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(endpoint, data=fields)
    try:
        gateway = response.json()
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="Easebuzz returned an invalid initiation response.") from exc
    access_key = gateway.get("data") or gateway.get("access_key")
    if response.status_code >= 400 or gateway.get("status") != 1 or not isinstance(access_key, str):
        raise HTTPException(status_code=502, detail=gateway.get("error_desc") or "Easebuzz could not create the payment page.")
    checkout_base = "https://pay.easebuzz.in/pay" if production else "https://testpay.easebuzz.in/pay"
    checkout_url = f"{checkout_base}/{access_key}"
    await db.euphoria_registrations.update_one(
        {"_id": row["_id"]},
        {"$set": {"payment.txnid": transaction_id, "payment.status": "initiated", "payment.access_key": access_key, "payment.checkout_url": checkout_url, "updated_at": datetime.now(timezone.utc)}, "$push": {"payment.attempts": {"txnid": transaction_id, "status": "initiated", "created_at": datetime.now(timezone.utc)}}},
    )
    await audit(actor, "payment.checkout_initiated" if not actor else "payment.admin_retry_initiated", "payments", row["registration_id"], {"txnid": transaction_id})
    return {"checkout_url": checkout_url, "transaction_id": transaction_id}


@router.post("/registrations/{registration_id}/payment", response_model=PaymentInitiationResponse)
async def initiate_payment(registration_id: str):
    row = await db.euphoria_registrations.find_one({"registration_id": registration_id})
    if not row:
        raise HTTPException(status_code=404, detail="Registration not found.")
    return await initiate_gateway_checkout(row)


@router.post("/payments/easebuzz/callback")
async def easebuzz_callback(request: Request):
    body = parse_qs((await request.body()).decode())
    payload = {key: values[0] for key, values in body.items()}
    payload_key = payload.get("key", "")
    if payload_key == os.environ.get("EASEBUZZ_KEY", ""):
        salt = os.environ.get("EASEBUZZ_SALT", "")
    elif payload_key == os.environ.get("EASEBUZZ_BACKUP_KEY", ""):
        salt = os.environ.get("EASEBUZZ_BACKUP_SALT", "")
    else:
        salt = ""
    reverse = [salt, payload.get("status", ""), payload.get("udf10", ""), payload.get("udf9", ""), payload.get("udf8", ""), payload.get("udf7", ""), payload.get("udf6", ""), payload.get("udf5", ""), payload.get("udf4", ""), payload.get("udf3", ""), payload.get("udf2", ""), payload.get("udf1", ""), payload.get("email", ""), payload.get("firstname", ""), payload.get("productinfo", ""), payload.get("amount", ""), payload.get("txnid", ""), payload.get("key", "")]
    expected = hashlib.sha512("|".join(reverse).encode()).hexdigest()
    if not payload.get("hash") or not secrets.compare_digest(expected.lower(), payload["hash"].lower()):
        raise HTTPException(status_code=400, detail="Invalid payment signature.")
    registration = await db.euphoria_registrations.find_one({"payment.txnid": payload.get("txnid")})
    if not registration:
        raise HTTPException(status_code=404, detail="Payment not found.")
    if payload.get("udf1") != registration["registration_id"]:
        raise HTTPException(status_code=400, detail="Payment registration mismatch.")
    if payload.get("productinfo") != os.environ.get("EASEBUZZ_PRODUCTINFO", "euphoria2026"):
        raise HTTPException(status_code=400, detail="Payment product mismatch.")
    try:
        amount_matches = abs(float(payload.get("amount", "-1")) - float(registration["total_amount"])) < 0.001
    except ValueError:
        amount_matches = False
    if not amount_matches:
        raise HTTPException(status_code=400, detail="Payment amount mismatch.")
    success = payload.get("status", "").lower() == "success"
    event_key = f"easebuzz:{payload.get('txnid','')}:{payload.get('status','')}:{payload.get('easepayid','')}"
    try:
        await db.euphoria_payment_events.insert_one({"event_key": event_key, "registration_id": registration["registration_id"], "created_at": datetime.now(timezone.utc)})
    except DuplicateKeyError:
        return RedirectResponse(f"{os.environ.get('APP_URL','').rstrip('/')}/registration/success/{registration['registration_id']}", status_code=303)
    await db.euphoria_registrations.update_one(
        {"_id": registration["_id"]},
        {"$set": {"status": "confirmed" if success else "pending_payment", "payment.status": "successful" if success else "failed", "payment.easepayid": payload.get("easepayid"), "qr_status": "active" if success else "pending", "updated_at": datetime.now(timezone.utc)}},
    )
    await audit(None, "payment.callback_success" if success else "payment.callback_failed", "payments", registration["registration_id"])
    return RedirectResponse(f"{os.environ.get('APP_URL','').rstrip('/')}/registration/success/{registration['registration_id']}", status_code=303)


@router.get("/passes/{registration_id}", response_model=PassResponse)
async def get_pass(registration_id: str, request: Request, key: str = ""):
    registration = await db.euphoria_registrations.find_one({"registration_id": registration_id})
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found.")
    user = await session_user(request)
    key_valid = bool(key and registration.get("pass_key_hash") and secrets.compare_digest(
        registration["pass_key_hash"], hashlib.sha256(key.encode()).hexdigest()
    ))
    if not key_valid and not (user and user.get("role") in ADMIN_PORTAL_ROLES):
        raise HTTPException(status_code=403, detail="A secure pass key is required.")
    if registration.get("status") != "confirmed" or registration.get("qr_status") != "active":
        raise HTTPException(status_code=409, detail="This pass is not active yet.")
    event_row = await db.euphoria_events.find_one({"id": registration["event_id"]}, {"_id": 0})
    if not event_row:
        raise HTTPException(status_code=404, detail="Event not found.")
    token = cipher().decrypt(registration["qr_token_ciphertext"].encode()).decode()
    image = qrcode.make(token)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    qr_data_url = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
    return {
        "registration_id": registration_id,
        "participant_name": registration["participant_name"],
        "event_name": registration["event_name"],
        "category_name": registration["category_name"],
        "venue": event_row["venue"],
        "event_date": event_row["event_date"],
        "status": registration["status"],
        "qr_status": registration["qr_status"],
        "qr_token": token,
        "qr_data_url": qr_data_url,
    }


@router.get("/scanner/context", response_model=ScannerContextResponse)
async def scanner_context(request: Request):
    user = await require_user(request, {"scanner"} | EVENT_MANAGER_ROLES)
    query = {"status": {"$in": ["registration_open", "scheduled", "live"]}}
    assignments = user.get("assignments", []) if user["role"] == "scanner" else []
    if user["role"] == "scanner":
        assigned_ids = [item["event_id"] for item in assignments] or user.get("assigned_event_ids", [])
        query["id"] = {"$in": assigned_ids}
    rows = await db.euphoria_events.find(query, {"_id": 0}).sort("name", 1).to_list(1000)
    assignment_views = []
    if user["role"] == "scanner" and assignments:
        for item in assignments:
            event_row = next((row for row in rows if row["id"] == item["event_id"]), None)
            if not event_row:
                continue
            allowed_days = set(item.get("event_day_ids", []))
            event_row["event_days"] = [day for day in event_row.get("event_days", []) if day["id"] in allowed_days]
            assignment_views.append({"event_id": item["event_id"], "event_day_ids": item.get("event_day_ids", []), "gates": item.get("gates", [])})
    else:
        assignment_views = [{"event_id": row["id"], "event_day_ids": [day["id"] for day in row.get("event_days", [])], "gates": GATES} for row in rows]
    visible_gates = sorted({gate for item in assignment_views for gate in item["gates"]})
    return {"events": rows, "gates": visible_gates, "assignments": assignment_views, "demo_mode": os.environ.get("SCANNER_ALLOW_OFFDATE", "false").lower() == "true"}


async def scan_result(user: dict, status: str, message: str, payload: ScanRequest, registration: dict | None = None, first_entry_at=None):
    attempt = {
        "status": status,
        "message": message,
        "scanner_id": user["id"],
        "scanner_name": user["name"],
        "event_id": payload.event_id,
        "event_day_id": payload.event_day_id,
        "gate": payload.gate,
        "registration_id": registration.get("registration_id") if registration else None,
        "participant_name": registration.get("participant_name") if registration else None,
        "event_name": registration.get("event_name") if registration else None,
        "token_hint": payload.token[-8:],
        "created_at": datetime.now(timezone.utc),
    }
    await db.euphoria_scan_attempts.insert_one(attempt)
    participant = None
    if registration:
        participant = {
            "participant_name": registration["participant_name"],
            "registration_id": registration["registration_id"],
            "event_name": registration["event_name"],
            "payment_status": registration.get("payment", {}).get("status", "unknown"),
            "qr_status": registration.get("qr_status", "unknown"),
        }
    return {"ok": status == "allowed", "status": status, "message": message, "participant": participant, "first_entry_at": first_entry_at}


@router.post("/scanner/scan", response_model=ScanResponse)
async def scanner_scan(payload: ScanRequest, request: Request):
    user = await require_user(request, {"scanner"} | EVENT_MANAGER_ROLES)
    if payload.gate not in GATES:
        return await scan_result(user, "denied", "Select a valid assigned gate.", payload)
    event_row = await db.euphoria_events.find_one({"id": payload.event_id}, {"_id": 0})
    if not event_row or not any(day["id"] == payload.event_day_id for day in event_row.get("event_days", [])):
        return await scan_result(user, "denied", "Select a valid event and event day.", payload)
    if user["role"] == "scanner" and payload.event_id not in user.get("assigned_event_ids", []):
        return await scan_result(user, "denied", "This scanner is not assigned to this event.", payload)
    if user["role"] == "scanner" and user.get("assignments"):
        assignment = next((item for item in user["assignments"] if item.get("event_id") == payload.event_id), None)
        if not assignment or payload.event_day_id not in assignment.get("event_day_ids", []) or payload.gate not in assignment.get("gates", []):
            return await scan_result(user, "denied", "This scanner is not assigned to the selected event day and gate.", payload)
    day = next(day for day in event_row["event_days"] if day["id"] == payload.event_day_id)
    allow_offdate = os.environ.get("SCANNER_ALLOW_OFFDATE", "false").lower() == "true"
    if not allow_offdate and day["date"] != today_iso("Asia/Kolkata"):
        return await scan_result(user, "denied", "This event day is not active today.", payload)
    registration = await db.euphoria_registrations.find_one({"qr_token_hash": hashlib.sha256(payload.token.strip().encode()).hexdigest()})
    if not registration:
        return await scan_result(user, "denied", "This QR code is invalid or has been revoked.", payload)
    if registration["event_id"] != payload.event_id:
        return await scan_result(user, "denied", "This pass is not valid for this event.", payload, registration)
    if registration.get("status") != "confirmed" or registration.get("payment", {}).get("status") not in {"successful", "manual_verified"}:
        return await scan_result(user, "denied", "Payment or registration confirmation is required.", payload, registration)
    if registration.get("qr_status") != "active":
        return await scan_result(user, "denied", "This QR code is invalid or has been revoked.", payload, registration)
    attendance = {
        "registration_id": registration["registration_id"],
        "event_id": payload.event_id,
        "event_day_id": payload.event_day_id,
        "event_day_label": day["label"],
        "gate": payload.gate,
        "scanner_id": user["id"],
        "scanner_name": user["name"],
        "status": "allowed",
        "entry_at": datetime.now(timezone.utc),
    }
    try:
        await db.euphoria_attendance.insert_one(attendance)
    except DuplicateKeyError:
        existing = await db.euphoria_attendance.find_one({
            "registration_id": registration["registration_id"],
            "event_id": payload.event_id,
            "event_day_id": payload.event_day_id,
        })
        return await scan_result(user, "duplicate", "Entry already recorded for this event day.", payload, registration, existing.get("entry_at") if existing else None)
    await audit(user, "attendance.allowed", "attendance", registration["registration_id"], {"event_day_id": payload.event_day_id, "gate": payload.gate})
    return await scan_result(user, "allowed", "Entry allowed and attendance recorded.", payload, registration, attendance["entry_at"])