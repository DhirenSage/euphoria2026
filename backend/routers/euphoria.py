import hashlib
import os
import secrets
import base64
from io import BytesIO
from datetime import datetime, timedelta, timezone
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
    AdminRegistrationsResponse,
    EuphoriaEvent,
    EuphoriaEventResponse,
    EuphoriaEventsResponse,
    EuphoriaHealth,
    LoginRequest,
    PaymentInitiationResponse,
    PassResponse,
    RegistrationCatalogueResponse,
    RegistrationCreate,
    RegistrationResponse,
    ScanRequest,
    ScannerContextResponse,
    ScanResponse,
    SessionUser,
)

router = APIRouter()


def clean(document: dict) -> dict:
    document.pop("_id", None)
    return document


SESSION_COOKIE = "euphoria_session"
SESSION_HOURS = 8
GATES = ["Gate 1 · Main Entry", "Gate 2 · Sports Entry", "Gate 3 · Auditorium"]


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


async def login(payload: LoginRequest, response: Response, required_role: str) -> SessionUser:
    email = payload.email.strip().lower()
    user = await db.euphoria_users.find_one({"email": email, "is_active": True})
    if not user or user.get("role") != required_role or not bcrypt.checkpw(payload.password.encode(), user["password_hash"].encode()):
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
    return await login(payload, response, "admin")


@router.post("/auth/scanner/login", response_model=SessionUser)
async def scanner_login(payload: LoginRequest, response: Response):
    return await login(payload, response, "scanner")


@router.get("/auth/me", response_model=SessionUser)
async def auth_me(request: Request):
    user = await require_user(request, {"admin", "scanner"})
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
    await require_user(request, {"admin"})
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
    await require_user(request, {"admin"})
    rows = await db.euphoria_events.find({}, {"_id": 0}).sort("name", 1).to_list(1000)
    return {"data": rows, "meta": {"programme": "Euphoria 2026"}}


@router.post("/admin/events", response_model=EuphoriaEvent, status_code=201)
async def create_admin_event(payload: AdminEventWrite, request: Request):
    user = await require_user(request, {"admin"})
    if await db.euphoria_events.find_one({"slug": payload.slug}):
        raise HTTPException(status_code=409, detail="An event with this slug already exists.")
    event_id = f"evt-{secrets.token_hex(8)}"
    row = event_document(payload, event_id)
    row["created_at"] = datetime.now(timezone.utc)
    await db.euphoria_events.insert_one(row)
    await db.euphoria_users.update_many({"role": "scanner"}, {"$addToSet": {"assigned_event_ids": event_id}})
    await audit(user, "event.created", "events", event_id, {"fee": payload.fee, "status": payload.status})
    return clean(row)


@router.put("/admin/events/{event_id}", response_model=EuphoriaEvent)
async def update_admin_event(event_id: str, payload: AdminEventWrite, request: Request):
    user = await require_user(request, {"admin"})
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
    user = await require_user(request, {"admin"})
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
    await require_user(request, {"admin"})
    rows = await db.euphoria_registrations.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return {"data": [registration_view(row) for row in rows]}


@router.post("/admin/registrations/{registration_id}/confirm", response_model=RegistrationResponse)
async def admin_confirm_registration(registration_id: str, request: Request):
    user = await require_user(request, {"admin"})
    row = await db.euphoria_registrations.find_one_and_update(
        {"registration_id": registration_id},
        {"$set": {"status": "confirmed", "payment.status": "manual_verified", "qr_status": "active", "updated_at": datetime.now(timezone.utc)}},
        return_document=ReturnDocument.AFTER,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Registration not found.")
    await audit(user, "registration.manual_confirmed", "registrations", registration_id)
    return registration_view(row)


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


@router.post("/registrations/{registration_id}/payment", response_model=PaymentInitiationResponse)
async def initiate_payment(registration_id: str):
    row = await db.euphoria_registrations.find_one({"registration_id": registration_id})
    if not row:
        raise HTTPException(status_code=404, detail="Registration not found.")
    if row["status"] == "confirmed":
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
        "udf1": registration_id,
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
        {"$set": {"payment.txnid": transaction_id, "payment.status": "initiated", "payment.access_key": access_key, "payment.checkout_url": checkout_url, "updated_at": datetime.now(timezone.utc)}},
    )
    return {"checkout_url": checkout_url, "transaction_id": transaction_id}


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
    if not key_valid and not (user and user.get("role") == "admin"):
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
    user = await require_user(request, {"scanner", "admin"})
    query = {"status": {"$in": ["registration_open", "scheduled", "live"]}}
    if user["role"] == "scanner":
        query["id"] = {"$in": user.get("assigned_event_ids", [])}
    rows = await db.euphoria_events.find(query, {"_id": 0}).sort("name", 1).to_list(1000)
    return {"events": rows, "gates": GATES, "demo_mode": os.environ.get("SCANNER_ALLOW_OFFDATE", "false").lower() == "true"}


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
    user = await require_user(request, {"scanner", "admin"})
    if payload.gate not in GATES:
        return await scan_result(user, "denied", "Select a valid assigned gate.", payload)
    event_row = await db.euphoria_events.find_one({"id": payload.event_id}, {"_id": 0})
    if not event_row or not any(day["id"] == payload.event_day_id for day in event_row.get("event_days", [])):
        return await scan_result(user, "denied", "Select a valid event and event day.", payload)
    if user["role"] == "scanner" and payload.event_id not in user.get("assigned_event_ids", []):
        return await scan_result(user, "denied", "This scanner is not assigned to this event.", payload)
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