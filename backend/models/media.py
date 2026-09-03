from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


MediaType = Literal["image", "video"]
MediaSection = Literal["hero", "highlight", "featured", "lineup", "gallery"]


class MediaItem(BaseModel):
    id: str
    media_type: MediaType
    section: MediaSection
    title: str
    caption: str
    event_id: str | None = None
    event_name: str | None = None
    source_url: str
    thumbnail_url: str
    video_provider: str | None = None
    embed_url: str | None = None
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MediaListResponse(BaseModel):
    data: list[MediaItem]


class MediaUpdate(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    caption: str = Field(default="", max_length=500)
    section: MediaSection
    event_id: str | None = None
    source_url: str = Field(default="", max_length=1000)
    thumbnail_url: str = Field(default="", max_length=1000)
    display_order: int = Field(default=0, ge=0, le=10000)
    is_active: bool = True