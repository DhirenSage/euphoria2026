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


class EventDay(BaseModel):
    id: str
    label: str
    date: str


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
    event_days: list[EventDay] = []


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
    payment_status: str = "created"
    qr_ready: bool = False
    pass_key: str | None = None


class PaymentInitiationResponse(BaseModel):
    checkout_url: str
    transaction_id: str


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=190)
    password: str = Field(min_length=8, max_length=128)


class SessionUser(BaseModel):
    id: str
    name: str
    email: str
    role: Literal["admin", "scanner"]


class EventDayInput(BaseModel):
    label: str = Field(min_length=2, max_length=80)
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")


class AdminEventWrite(BaseModel):
    category_id: str
    name: str = Field(min_length=2, max_length=180)
    slug: str = Field(min_length=2, max_length=180, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    short_description: str = Field(min_length=5, max_length=300)
    description: str = Field(min_length=5, max_length=5000)
    event_type: str = Field(default="competition", max_length=80)
    registration_type: Literal["individual", "team"] = "individual"
    fee: float = Field(ge=0, le=1000000)
    capacity: int = Field(ge=0, le=1000000)
    venue: str = Field(min_length=2, max_length=300)
    status: Literal["draft", "scheduled", "registration_open", "registration_closed", "live", "completed", "cancelled"]
    min_team_size: int | None = Field(default=None, ge=1, le=100)
    max_team_size: int | None = Field(default=None, ge=1, le=100)
    banner_url: str = ""
    event_date: str = Field(min_length=2, max_length=100)
    event_time: str = Field(min_length=2, max_length=100)
    registration_deadline: str = Field(min_length=2, max_length=100)
    eligibility: str = Field(default="Open to eligible students.", max_length=1000)
    rules: list[str] = []
    prizes: list[str] = []
    coordinator_name: str = Field(default="EUPHORIA Event Desk", max_length=180)
    coordinator_contact: str = Field(default="SAGE University Indore", max_length=300)
    schedule: list[EventScheduleItem] = []
    event_days: list[EventDayInput] = Field(min_length=1, max_length=10)


class AdminDashboardStats(BaseModel):
    events: int
    registrations: int
    confirmed: int
    revenue: float
    entries: int
    duplicate_attempts: int


class AdminDashboardResponse(BaseModel):
    stats: AdminDashboardStats
    events: list[EuphoriaEvent]
    recent_scans: list[dict]


class AdminRegistrationsResponse(BaseModel):
    data: list[RegistrationResponse]


class PassResponse(BaseModel):
    registration_id: str
    participant_name: str
    event_name: str
    category_name: str
    venue: str
    event_date: str
    status: str
    qr_status: str
    qr_token: str
    qr_data_url: str


class ScannerContextResponse(BaseModel):
    events: list[EuphoriaEvent]
    gates: list[str]
    demo_mode: bool


class ScanRequest(BaseModel):
    token: str = Field(min_length=20, max_length=300)
    event_id: str
    event_day_id: str
    gate: str = Field(min_length=2, max_length=120)


class ScanParticipant(BaseModel):
    participant_name: str
    registration_id: str
    event_name: str
    payment_status: str
    qr_status: str


class ScanResponse(BaseModel):
    ok: bool
    status: Literal["allowed", "duplicate", "denied"]
    message: str
    participant: ScanParticipant | None = None
    first_entry_at: datetime | None = None