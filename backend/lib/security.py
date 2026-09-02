import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Callable

import bcrypt
from fastapi import Cookie, Depends, HTTPException, Request, Response

from lib.db import db

SESSION_COOKIE = "euphoria_session"
ADMIN_ROLES = {"super_admin", "event_admin", "finance", "report_viewer"}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def create_session(response: Response, user: dict, request: Request) -> None:
    raw = secrets.token_urlsafe(40)
    expires_at = utcnow() + timedelta(hours=12)
    await db.auth_sessions.insert_one({"token_hash": token_hash(raw), "user_id": user["id"], "role": user["role"], "expires_at": expires_at, "ip": request.client.host if request.client else None, "created_at": utcnow()})
    response.set_cookie(SESSION_COOKIE, raw, httponly=True, secure=os.environ.get("CI_ENVIRONMENT") == "production" or os.environ.get("APP_URL", "").startswith("https://"), samesite="lax", max_age=43200, path="/")


async def destroy_session(response: Response, raw: str | None) -> None:
    if raw:
        await db.auth_sessions.delete_one({"token_hash": token_hash(raw)})
    response.delete_cookie(SESSION_COOKIE, path="/")


async def get_current_user(euphoria_session: str | None = Cookie(default=None)) -> dict:
    if not euphoria_session:
        raise HTTPException(status_code=401, detail="Authentication required.")
    session = await db.auth_sessions.find_one({"token_hash": token_hash(euphoria_session), "expires_at": {"$gt": utcnow()}})
    if not session:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")
    user = await db.auth_users.find_one({"id": session["user_id"], "is_active": True}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Account is inactive.")
    return user


def require_roles(*roles: str) -> Callable:
    async def dependency(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="You do not have permission for this action.")
        return user
    return dependency


def signing_secret() -> bytes:
    secret = os.environ.get("PASS_SIGNING_SECRET", "")
    if not secret:
        raise RuntimeError("PASS_SIGNING_SECRET is not configured")
    return secret.encode()


def signed_token(kind: str, identifier: str, nonce: str) -> str:
    payload = f"{kind}:{identifier}:{nonce}".encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = hmac.new(signing_secret(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{signature}"


def verify_signed_token(token: str, kind: str, identifier: str, nonce: str) -> bool:
    expected = signed_token(kind, identifier, nonce)
    return hmac.compare_digest(expected, token)


async def audit(user_id: str | None, action: str, module: str, record_id: str | None, metadata: dict | None = None) -> None:
    await db.audit_logs.insert_one({"user_id": user_id, "action": action, "module": module, "record_id": record_id, "metadata": metadata or {}, "created_at": utcnow()})