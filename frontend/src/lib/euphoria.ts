export interface EuphoriaHealth {
  ok: boolean;
  service: string;
  timestamp: string;
}

export interface EuphoriaEvent {
  id: number;
  category_id: number;
  name: string;
  slug: string;
  short_description: string | null;
  event_type: string;
  registration_type: string;
  fee: number;
  capacity: number;
  venue: string | null;
  status: string;
  category_name: string | null;
}

export interface EuphoriaEventsResponse {
  data: EuphoriaEvent[];
  meta: { programme: string };
}

export interface EuphoriaEventResponse {
  data: EuphoriaEvent;
}