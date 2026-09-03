import mimetypes
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from pymongo import ReturnDocument

from lib.db import db
from models.media import MediaItem, MediaListResponse, MediaUpdate
from routers.euphoria import audit, require_user


router = APIRouter()
UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads" / "media"
ALLOWED_IMAGE_MIMES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
SECTIONS = {"hero", "highlight", "featured", "lineup", "gallery"}


DEFAULT_MEDIA = [
    {"id": "media-hero-stage", "media_type": "image", "section": "hero", "title": "EUPHORIA main stage", "caption": "Experience the energy. Live the Euphoria.", "source_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=1900&q=85", "thumbnail_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=1900&q=85", "display_order": 1},
    {"id": "media-featured-performer", "media_type": "video", "section": "featured", "title": "Celebrity Pro Night", "caption": "A live headline performance built for the EUPHORIA main stage.", "source_url": "https://www.youtube.com/watch?v=0O2aH4XLbto", "thumbnail_url": "https://images.unsplash.com/photo-1526218626217-dc65a29bb444?auto=format&fit=crop&w=1400&q=85", "display_order": 1},
    {"id": "media-lineup-one", "media_type": "image", "section": "lineup", "title": "Live Music", "caption": "Main-stage sound and student performances.", "source_url": "https://images.unsplash.com/photo-1493676304819-0d7a8d026dcf?auto=format&fit=crop&w=1000&q=85", "thumbnail_url": "https://images.unsplash.com/photo-1493676304819-0d7a8d026dcf?auto=format&fit=crop&w=1000&q=85", "display_order": 1},
    {"id": "media-lineup-two", "media_type": "image", "section": "lineup", "title": "Battle of Bands", "caption": "Amplified energy from campus bands.", "source_url": "https://images.unsplash.com/photo-1663668566971-afaa3f07903d?auto=format&fit=crop&w=1000&q=85", "thumbnail_url": "https://images.unsplash.com/photo-1663668566971-afaa3f07903d?auto=format&fit=crop&w=1000&q=85", "display_order": 2},
    {"id": "media-lineup-three", "media_type": "image", "section": "lineup", "title": "Dance Arena", "caption": "Movement, colour and competition.", "source_url": "https://images.unsplash.com/photo-1619229725920-ac8b63b0631a?auto=format&fit=crop&w=1000&q=85", "thumbnail_url": "https://images.unsplash.com/photo-1619229725920-ac8b63b0631a?auto=format&fit=crop&w=1000&q=85", "display_order": 3},
    {"id": "media-gallery-dance", "media_type": "image", "section": "gallery", "title": "Cultural stage", "caption": "Move & Groove performances", "source_url": "https://images.unsplash.com/photo-1463592177119-bab2a00f3ccb?auto=format&fit=crop&w=1200&q=85", "thumbnail_url": "https://images.unsplash.com/photo-1463592177119-bab2a00f3ccb?auto=format&fit=crop&w=1200&q=85", "display_order": 1},
    {"id": "media-gallery-crowd", "media_type": "image", "section": "gallery", "title": "Festival crowd", "caption": "One campus, one shared frequency", "source_url": "https://images.unsplash.com/photo-1450044804117-534ccd6e6a3a?auto=format&fit=crop&w=1200&q=85", "thumbnail_url": "https://images.unsplash.com/photo-1450044804117-534ccd6e6a3a?auto=format&fit=crop&w=1200&q=85", "display_order": 2},
    {"id": "media-gallery-stage", "media_type": "image", "section": "gallery", "title": "Stage lights", "caption": "EUPHORIA after dark", "source_url": "https://images.unsplash.com/photo-1563841930606-67e2bce48b78?auto=format&fit=crop&w=1200&q=85", "thumbnail_url": "https://images.unsplash.com/photo-1563841930606-67e2bce48b78?auto=format&fit=crop&w=1200&q=85", "display_order": 3},
]


def video_details(url: str) -> tuple[str | None, str | None]:
    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.")
    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]
        return "youtube", f"https://www.youtube-nocookie.com/embed/{video_id}" if video_id else None
    if host in {"youtube.com", "m.youtube.com"}:
        video_id = parse_qs(parsed.query).get("v", [""])[0]
        if parsed.path.startswith("/embed/"):
            video_id = parsed.path.split("/embed/", 1)[1].split("/", 1)[0]
        return "youtube", f"https://www.youtube-nocookie.com/embed/{video_id}" if video_id else None
    if host in {"vimeo.com", "player.vimeo.com"}:
        match = re.search(r"/(?:video/)?(\d+)", parsed.path)
        return "vimeo", f"https://player.vimeo.com/video/{match.group(1)}" if match else None
    if parsed.path.lower().endswith((".mp4", ".webm")):
        return "direct", url
    return None, None


def media_view(row: dict) -> dict:
    result = {key: value for key, value in row.items() if key not in {"_id", "storage_filename"}}
    if row.get("storage_filename"):
        uploaded_url = f"/api/media/files/{row['storage_filename']}"
        if row.get("media_type") == "image":
            result["source_url"] = uploaded_url
        result["thumbnail_url"] = uploaded_url
    return result


async def ensure_media() -> None:
    now = datetime.now(timezone.utc)
    for item in DEFAULT_MEDIA:
        provider, embed_url = video_details(item["source_url"]) if item["media_type"] == "video" else (None, None)
        await db.euphoria_media.update_one(
            {"id": item["id"]},
            {"$setOnInsert": {**item, "event_id": None, "event_name": None, "video_provider": provider, "embed_url": embed_url, "is_active": True, "created_at": now, "updated_at": now}},
            upsert=True,
        )
    await db.euphoria_media.create_index([("section", 1), ("display_order", 1)])


@router.get("/media", response_model=MediaListResponse)
async def public_media(section: str = ""):
    query: dict = {"is_active": True}
    if section:
        if section not in SECTIONS:
            raise HTTPException(status_code=422, detail="Select a valid media section.")
        query["section"] = section
    rows = await db.euphoria_media.find(query).sort([("section", 1), ("display_order", 1), ("created_at", -1)]).to_list(500)
    return {"data": [media_view(row) for row in rows]}


@router.get("/media/files/{filename}")
async def media_file(filename: str, request: Request):
    if not re.fullmatch(r"[a-zA-Z0-9_-]+\.(?:jpg|png|webp)", filename):
        raise HTTPException(status_code=404, detail="Media not found.")
    row = await db.euphoria_media.find_one({"storage_filename": filename})
    user = await require_user(request, {"admin", "event_admin"}) if row and not row.get("is_active") else None
    if not row or (not row.get("is_active") and not user):
        raise HTTPException(status_code=404, detail="Media not found.")
    path = UPLOAD_DIR / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Media not found.")
    return FileResponse(path, media_type=mimetypes.guess_type(filename)[0] or "application/octet-stream")


@router.get("/admin/media", response_model=MediaListResponse)
async def admin_media(request: Request):
    await require_user(request, {"admin", "event_admin"})
    rows = await db.euphoria_media.find({}).sort([("section", 1), ("display_order", 1), ("created_at", -1)]).to_list(1000)
    return {"data": [media_view(row) for row in rows]}


@router.post("/admin/media", response_model=MediaItem, status_code=201)
async def create_media(
    request: Request,
    media_type: str = Form(...),
    section: str = Form(...),
    title: str = Form(...),
    caption: str = Form(""),
    event_id: str = Form(""),
    source_url: str = Form(""),
    thumbnail_url: str = Form(""),
    display_order: int = Form(0),
    is_active: bool = Form(True),
    image: UploadFile | None = File(default=None),
):
    user = await require_user(request, {"admin", "event_admin"})
    if media_type not in {"image", "video"} or section not in SECTIONS:
        raise HTTPException(status_code=422, detail="Select a valid media type and section.")
    if len(title.strip()) < 2:
        raise HTTPException(status_code=422, detail="A media title is required.")
    event = await db.euphoria_events.find_one({"id": event_id}, {"_id": 0, "id": 1, "name": 1}) if event_id else None
    if event_id and not event:
        raise HTTPException(status_code=422, detail="Select a valid event.")
    media_id = f"media-{secrets.token_hex(8)}"
    storage_filename = None
    if image and image.filename:
        content = await image.read()
        extension = ALLOWED_IMAGE_MIMES.get(image.content_type or "")
        if not extension or not content or len(content) > 8 * 1024 * 1024:
            raise HTTPException(status_code=422, detail="Images must be JPG, PNG, or WEBP up to 8 MB.")
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        storage_filename = f"{media_id}{extension}"
        (UPLOAD_DIR / storage_filename).write_bytes(content)
    if media_type == "image" and not storage_filename and not source_url.startswith(("https://", "http://")):
        raise HTTPException(status_code=422, detail="Upload an image or provide an image URL.")
    provider, embed_url = video_details(source_url) if media_type == "video" else (None, None)
    if media_type == "video" and not embed_url:
        raise HTTPException(status_code=422, detail="Use a valid YouTube, Vimeo, MP4, or WEBM URL.")
    now = datetime.now(timezone.utc)
    default_video_thumbnail = "https://images.unsplash.com/photo-1526218626217-dc65a29bb444?auto=format&fit=crop&w=1200&q=85"
    row = {"id": media_id, "media_type": media_type, "section": section, "title": title.strip(), "caption": caption.strip(), "event_id": event_id or None, "event_name": event.get("name") if event else None, "source_url": source_url.strip(), "thumbnail_url": thumbnail_url.strip() or (default_video_thumbnail if media_type == "video" else source_url.strip()), "storage_filename": storage_filename, "video_provider": provider, "embed_url": embed_url, "display_order": display_order, "is_active": is_active, "created_at": now, "updated_at": now}
    await db.euphoria_media.insert_one(row)
    await audit(user, "media.created", "media", media_id, {"section": section, "media_type": media_type})
    return media_view(row)


@router.put("/admin/media/{media_id}", response_model=MediaItem)
async def update_media(media_id: str, payload: MediaUpdate, request: Request):
    user = await require_user(request, {"admin", "event_admin"})
    existing = await db.euphoria_media.find_one({"id": media_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Media item not found.")
    event = await db.euphoria_events.find_one({"id": payload.event_id}, {"_id": 0, "name": 1}) if payload.event_id else None
    if payload.event_id and not event:
        raise HTTPException(status_code=422, detail="Select a valid event.")
    provider, embed_url = video_details(payload.source_url) if existing["media_type"] == "video" else (None, None)
    if existing["media_type"] == "video" and not embed_url:
        raise HTTPException(status_code=422, detail="Use a valid YouTube, Vimeo, MP4, or WEBM URL.")
    update = {**payload.model_dump(), "event_name": event.get("name") if event else None, "video_provider": provider, "embed_url": embed_url, "updated_at": datetime.now(timezone.utc)}
    if existing["media_type"] == "video" and not update["thumbnail_url"]:
        update["thumbnail_url"] = existing.get("thumbnail_url") or "https://images.unsplash.com/photo-1526218626217-dc65a29bb444?auto=format&fit=crop&w=1200&q=85"
    row = await db.euphoria_media.find_one_and_update({"id": media_id}, {"$set": update}, return_document=ReturnDocument.AFTER)
    await audit(user, "media.updated", "media", media_id, {"section": payload.section, "is_active": payload.is_active})
    return media_view(row)


@router.delete("/admin/media/{media_id}", status_code=204)
async def delete_media(media_id: str, request: Request):
    user = await require_user(request, {"admin", "event_admin"})
    row = await db.euphoria_media.find_one_and_delete({"id": media_id})
    if not row:
        raise HTTPException(status_code=404, detail="Media item not found.")
    if row.get("storage_filename"):
        (UPLOAD_DIR / row["storage_filename"]).unlink(missing_ok=True)
    await audit(user, "media.deleted", "media", media_id)