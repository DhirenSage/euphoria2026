import hashlib
import os
import secrets
from datetime import datetime, timezone
from urllib.parse import parse_qs

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pymongo import ReturnDocument

from lib.catalogue import CATEGORIES, ensure_catalogue
from lib.db import db
from models.euphoria import (
    EuphoriaEvent,
    EuphoriaEventResponse,
    EuphoriaEventsResponse,
    EuphoriaHealth,
    PaymentInitiationResponse,
    RegistrationCatalogueResponse,
    RegistrationCreate,
    RegistrationResponse,
)

router = APIRouter()


def clean(document: dict) -> dict:
    document.pop("_id", None)
    return document


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

    counter = await db.counters.find_one_and_update(
        {"_id": "euphoria_registration"}, {"$inc": {"seq": 1}}, upsert=True, return_document=ReturnDocument.AFTER
    )
    registration_id = f"EUPHORIA-2026-{counter['seq']:06d}"
    created_at = datetime.now(timezone.utc)
    status = "confirmed" if float(event_row["fee"]) == 0 else "pending_payment"
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
        "created_at": created_at,
        "updated_at": created_at,
    }
    await db.euphoria_registrations.insert_one(row)
    return clean(row)


@router.get("/registrations/{registration_id}", response_model=RegistrationResponse)
async def get_registration(registration_id: str):
    row = await db.euphoria_registrations.find_one({"registration_id": registration_id}, {"_id": 0})
    if not row:
        raise HTTPException(status_code=404, detail="Registration not found.")
    return row


@router.post("/registrations/{registration_id}/payment", response_model=PaymentInitiationResponse)
async def initiate_payment(registration_id: str):
    row = await db.euphoria_registrations.find_one({"registration_id": registration_id}, {"_id": 0})
    if not row:
        raise HTTPException(status_code=404, detail="Registration not found.")
    if row["status"] == "confirmed":
        raise HTTPException(status_code=409, detail="Registration is already confirmed.")
    key, salt = os.environ.get("EASEBUZZ_KEY", ""), os.environ.get("EASEBUZZ_SALT", "")
    if not key or not salt:
        raise HTTPException(status_code=503, detail="Easebuzz is not configured.")
    app_url = os.environ.get("APP_URL", "").rstrip("/")
    fields = {
        "key": key,
        "txnid": row["payment"]["txnid"],
        "amount": f"{row['total_amount']:.2f}",
        "productinfo": f"EUPHORIA 2026 · {row['event_name']}",
        "firstname": row["participant_name"],
        "email": row["email"],
        "phone": row["mobile"],
        "surl": f"{app_url}/api/payments/easebuzz/callback",
        "furl": f"{app_url}/api/payments/easebuzz/callback",
        "udf1": registration_id,
    }
    hash_order = ["key", "txnid", "amount", "productinfo", "firstname", "email", "udf1", "udf2", "udf3", "udf4", "udf5", "udf6", "udf7", "udf8", "udf9", "udf10"]
    fields["hash"] = hashlib.sha512(("|".join(fields.get(item, "") for item in hash_order) + "|" + salt).encode()).hexdigest()
    endpoint = "https://pay.easebuzz.in/payment/initiateLink" if os.environ.get("EASEBUZZ_ENV") == "prod" else "https://testpay.easebuzz.in/payment/initiateLink"
    return {"action": endpoint, "fields": {key: str(value) for key, value in fields.items()}}


@router.post("/payments/easebuzz/callback")
async def easebuzz_callback(request: Request):
    body = parse_qs((await request.body()).decode())
    payload = {key: values[0] for key, values in body.items()}
    salt = os.environ.get("EASEBUZZ_SALT", "")
    reverse = [salt, payload.get("status", ""), payload.get("udf10", ""), payload.get("udf9", ""), payload.get("udf8", ""), payload.get("udf7", ""), payload.get("udf6", ""), payload.get("udf5", ""), payload.get("udf4", ""), payload.get("udf3", ""), payload.get("udf2", ""), payload.get("udf1", ""), payload.get("email", ""), payload.get("firstname", ""), payload.get("productinfo", ""), payload.get("amount", ""), payload.get("txnid", ""), payload.get("key", "")]
    expected = hashlib.sha512("|".join(reverse).encode()).hexdigest()
    if not payload.get("hash") or not secrets.compare_digest(expected.lower(), payload["hash"].lower()):
        raise HTTPException(status_code=400, detail="Invalid payment signature.")
    registration = await db.euphoria_registrations.find_one({"payment.txnid": payload.get("txnid")})
    if not registration:
        raise HTTPException(status_code=404, detail="Payment not found.")
    success = payload.get("status", "").lower() == "success"
    await db.euphoria_registrations.update_one(
        {"_id": registration["_id"]},
        {"$set": {"status": "confirmed" if success else "pending_payment", "payment.status": "successful" if success else "failed", "payment.easepayid": payload.get("easepayid"), "updated_at": datetime.now(timezone.utc)}},
    )
    return RedirectResponse(f"{os.environ.get('APP_URL','').rstrip('/')}/registration/success/{registration['registration_id']}", status_code=303)