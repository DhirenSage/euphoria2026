export type MediaSection = "hero" | "highlight" | "featured" | "lineup" | "gallery";
export type MediaType = "image" | "video";

export interface MediaItem {
  id: string;
  media_type: MediaType;
  section: MediaSection;
  title: string;
  caption: string;
  event_id: string | null;
  event_name: string | null;
  source_url: string;
  thumbnail_url: string;
  video_provider: string | null;
  embed_url: string | null;
  display_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MediaListResponse {
  data: MediaItem[];
}

export interface MediaUpdate {
  title: string;
  caption: string;
  section: MediaSection;
  event_id: string | null;
  source_url: string;
  thumbnail_url: string;
  display_order: number;
  is_active: boolean;
}