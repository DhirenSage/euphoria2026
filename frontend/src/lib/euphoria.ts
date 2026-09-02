export interface EuphoriaHealth {
  ok: boolean;
  service: string;
  timestamp: string;
}

export interface EuphoriaEvent {
  id: string;
  category_id: string;
  category_name: string;
  name: string;
  slug: string;
  short_description: string | null;
  description: string;
  event_type: string;
  registration_type: string;
  fee: number;
  capacity: number;
  venue: string;
  status: string;
  min_team_size: number | null;
  max_team_size: number | null;
  banner_url: string;
  event_date: string;
  event_time: string;
  registration_deadline: string;
  eligibility: string;
  rules: string[];
  prizes: string[];
  coordinator_name: string;
  coordinator_contact: string;
  schedule: Array<{ time: string; title: string }>;
  event_days: EventDay[];
}

export interface EventDay {
  id: string;
  label: string;
  date: string;
}

export interface EuphoriaEventsResponse {
  data: EuphoriaEvent[];
  meta: { programme: string };
}

export interface EuphoriaEventResponse {
  data: EuphoriaEvent;
}

export interface EuphoriaCategory {
  id: string;
  name: string;
  order: number;
}

export interface RegistrationCatalogueResponse {
  categories: EuphoriaCategory[];
  events: EuphoriaEvent[];
}

export interface RegistrationCreate {
  category_id: string;
  event_id: string;
  name: string;
  father_name: string | null;
  email: string;
  mobile: string;
  age: number | null;
  college: string;
  city: string | null;
  participant_affiliation: "sageian" | "non_sageian";
  team_name: string | null;
  team_members: string | null;
}

export interface RegistrationResponse {
  registration_id: string;
  participant_name: string;
  event_id: string;
  event_name: string;
  category_name: string;
  registration_type: "individual" | "team";
  total_amount: number;
  status: "pending_payment" | "confirmed";
  created_at: string;
  payment_status: string;
  qr_ready: boolean;
  pass_key: string | null;
}

export interface PaymentInitiationResponse {
  checkout_url: string;
  transaction_id: string;
}

export interface SessionUser {
  id: string;
  name: string;
  email: string;
  role: "admin" | "scanner";
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface EventDayInput {
  label: string;
  date: string;
}

export interface AdminEventWrite {
  category_id: string;
  name: string;
  slug: string;
  short_description: string;
  description: string;
  event_type: string;
  registration_type: "individual" | "team";
  fee: number;
  capacity: number;
  venue: string;
  status: "draft" | "scheduled" | "registration_open" | "registration_closed" | "live" | "completed" | "cancelled";
  min_team_size: number | null;
  max_team_size: number | null;
  banner_url: string;
  event_date: string;
  event_time: string;
  registration_deadline: string;
  eligibility: string;
  rules: string[];
  prizes: string[];
  coordinator_name: string;
  coordinator_contact: string;
  schedule: Array<{ time: string; title: string }>;
  event_days: EventDayInput[];
}

export interface AdminDashboardResponse {
  stats: {
    events: number;
    registrations: number;
    confirmed: number;
    revenue: number;
    entries: number;
    duplicate_attempts: number;
  };
  events: EuphoriaEvent[];
  recent_scans: Array<{
    status: "allowed" | "duplicate" | "denied";
    participant_name: string | null;
    registration_id: string | null;
    event_name: string | null;
    gate: string;
    message: string;
    created_at: string;
  }>;
}

export interface AdminRegistrationsResponse {
  data: RegistrationResponse[];
}

export interface PassResponse {
  registration_id: string;
  participant_name: string;
  event_name: string;
  category_name: string;
  venue: string;
  event_date: string;
  status: string;
  qr_status: string;
  qr_token: string;
  qr_data_url: string;
}

export interface ScannerContextResponse {
  events: EuphoriaEvent[];
  gates: string[];
  demo_mode: boolean;
}

export interface ScanRequest {
  token: string;
  event_id: string;
  event_day_id: string;
  gate: string;
}

export interface ScanResponse {
  ok: boolean;
  status: "allowed" | "duplicate" | "denied";
  message: string;
  participant: {
    participant_name: string;
    registration_id: string;
    event_name: string;
    payment_status: string;
    qr_status: string;
  } | null;
  first_entry_at: string | null;
}