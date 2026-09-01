from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class EuphoriaHealth(BaseModel):
    ok: bool
    service: str
    timestamp: str


class EuphoriaCategory(BaseModel):
    id: str
    name: str
    order: int


class EventScheduleItem(BaseModel):
    time: str
    title: str


class EuphoriaEvent(BaseModel):
    id: str
    category_id: str
    category_name: str
    name: str
    slug: str
    short_description: str
    description: str
    event_type: str
    registration_type: Literal["individual", "team"]
    fee: float
    capacity: int
    venue: str
    status: str
    min_team_size: int | None = None
    max_team_size: int | None = None
    banner_url: str
    event_date: str
    event_time: str
    registration_deadline: str
    eligibility: str
    rules: list[str]
    prizes: list[str]
    coordinator_name: str
    coordinator_contact: str
    schedule: list[EventScheduleItem]


class EuphoriaEventsMeta(BaseModel):
    programme: str


class EuphoriaEventsResponse(BaseModel):
    data: list[EuphoriaEvent]
    meta: EuphoriaEventsMeta


class EuphoriaEventResponse(BaseModel):
    data: EuphoriaEvent


class RegistrationCatalogueResponse(BaseModel):
    categories: list[EuphoriaCategory]
    events: list[EuphoriaEvent]


class RegistrationCreate(BaseModel):
    category_id: str
    event_id: str
    name: str = Field(min_length=2, max_length=160)
    father_name: str | None = Field(default=None, max_length=160)
    email: str = Field(pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$", max_length=190)
    mobile: str = Field(pattern=r"^[6-9][0-9]{9}$")
    age: int | None = Field(default=None, ge=10, le=100)
    college: str = Field(min_length=2, max_length=180)
    city: str | None = Field(default=None, max_length=120)
    participant_affiliation: Literal["sageian", "non_sageian"]
    team_name: str | None = Field(default=None, max_length=160)
    team_members: str | None = None


class RegistrationResponse(BaseModel):
    registration_id: str
    participant_name: str
    event_id: str
    event_name: str
    category_name: str
    registration_type: Literal["individual", "team"]
    total_amount: float
    status: Literal["pending_payment", "confirmed"]
    created_at: datetime


class PaymentInitiationResponse(BaseModel):
    checkout_url: str
    transaction_id: str