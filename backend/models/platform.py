from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from models.euphoria import EuphoriaCategory, EuphoriaEvent


Role = Literal["super_admin", "event_admin", "finance", "scanner", "report_viewer"]


class AuthLogin(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)
    portal: Literal["admin", "scanner"]


class AuthUser(BaseModel):
    id: str
    name: str
    email: str
    role: Role


class LoginResponse(BaseModel):
    user: AuthUser


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    slug: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=500)
    is_active: bool = True


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    slug: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class CategoryAdminResponse(EuphoriaCategory):
    description: str = ""
    is_active: bool = True


class CategoryListResponse(BaseModel):
    data: list[CategoryAdminResponse]


class EventUpsert(BaseModel):
    category_id: str
    name: str = Field(min_length=2, max_length=180)
    slug: str = Field(min_length=2, max_length=180, pattern=r"^[a-z0-9-]+$")
    short_description: str = Field(min_length=5, max_length=300)
    description: str = Field(min_length=10, max_length=3000)
    event_type: str = "competition"
    registration_type: Literal["individual", "team"] = "individual"
    fee: float = Field(ge=0, le=1000000)
    capacity: int = Field(ge=0, le=100000)
    venue: str = Field(min_length=2, max_length=220)
    status: Literal["registration_open", "disabled", "draft", "completed", "cancelled"] = "registration_open"
    min_team_size: int | None = Field(default=None, ge=1, le=100)
    max_team_size: int | None = Field(default=None, ge=1, le=100)
    banner_url: str
    event_date: str
    event_time: str
    registration_deadline: str
    eligibility: str
    rules: list[str]
    prizes: list[str]
    coordinator_name: str
    coordinator_contact: str
    schedule: list[dict[str, str]]


class EventAdminResponse(EuphoriaEvent):
    pass


class EventAdminListResponse(BaseModel):
    data: list[EventAdminResponse]


class DeleteResponse(BaseModel):
    ok: bool
    message: str


class DashboardSummary(BaseModel):
    total_events: int
    active_events: int
    total_registrations: int
    paid_registrations: int
    pending_payments: int
    failed_payments: int
    total_revenue: float
    passes_generated: int
    total_entries: int
    duplicate_attempts: int
    event_performance: list[dict]


class RegistrationAdminItem(BaseModel):
    registration_id: str
    participant_name: str
    email: str
    mobile: str
    event_id: str
    event_name: str
    category_name: str
    total_amount: float
    status: str
    payment_status: str
    pass_status: str | None = None
    created_at: datetime


class RegistrationAdminList(BaseModel):
    data: list[RegistrationAdminItem]


class ConfirmRegistrationRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=250)


class EntryHistoryItem(BaseModel):
    event_day: str
    entry_time: datetime
    gate: str
    scanner_name: str


class GatePassResponse(BaseModel):
    pass_id: str
    registration_id: str
    participant_name: str
    event_id: str
    event_name: str
    category_name: str
    event_date: str
    venue: str
    payment_status: str
    status: str
    qr_token: str
    issued_at: datetime
    entry_history: list[EntryHistoryItem]


class ParticipantAccessRequest(BaseModel):
    access_token: str


class ScanRequest(BaseModel):
    token: str
    event_id: str
    event_day: str
    gate: str = Field(min_length=2, max_length=100)


class ScanResult(BaseModel):
    allowed: bool
    status: Literal["allowed", "duplicate", "denied"]
    message: str
    participant_name: str | None = None
    registration_id: str | None = None
    event_name: str | None = None
    payment_status: str | None = None
    pass_status: str | None = None
    entry_time: datetime | None = None
    first_entry_time: datetime | None = None