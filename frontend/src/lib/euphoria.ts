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
  event_type: string;
  registration_type: string;
  fee: number;
  capacity: number;
  venue: string;
  status: string;
  min_team_size: number | null;
  max_team_size: number | null;
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
}

export interface PaymentInitiationResponse {
  checkout_url: string;
  transaction_id: string;
}