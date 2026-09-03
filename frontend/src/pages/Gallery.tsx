import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import BrandLockup from "@/components/BrandLockup";
import MediaViewer from "@/components/MediaViewer";
import SiteHeader from "@/components/SiteHeader";
import { apiGet } from "@/lib/api";
import type { MediaItem, MediaListResponse } from "@/lib/media";

export default function Gallery() {
  const { data, isLoading } = useQuery({ queryKey: ["media"], queryFn: () => apiGet<MediaListResponse>("/media") });
  const [filter, setFilter] = useState<"all" | "image" | "video">("all");
  const [viewer, setViewer] = useState<MediaItem | null>(null);
  const items = (data?.data ?? []).filter((item) => ["gallery", "featured", "lineup"].includes(item.section) && (filter === "all" || item.media_type === filter));
  return <div className="app-shell festival-gallery-page"><SiteHeader /><main><section className="gallery-page-hero"><BrandLockup variant="compact" /><p className="eyebrow pink">EUPHORIA ARCHIVE / DYNAMIC MEDIA</p><h1 data-testid="gallery-page-title">A FESTIVAL<br /><em>IN MOTION.</em></h1><p>Photos, video teasers and stage moments published directly by the EUPHORIA team.</p></section><div className="gallery-filter-bar" data-testid="gallery-filters">{(["all", "image", "video"] as const).map((value) => <button className={filter === value ? "active" : ""} onClick={() => setFilter(value)} key={value} data-testid={`gallery-filter-${value}`}>{value === "all" ? "All media" : value === "image" ? "Photos" : "Videos"}</button>)}</div><section className="gallery-masonry" data-testid="gallery-grid">{items.map((item, index) => <button className={`gallery-media-card gallery-size-${index % 5}`} key={item.id} onClick={() => setViewer(item)} data-testid={`gallery-item-${item.id}`}><img src={item.thumbnail_url || item.source_url} alt={item.caption || item.title} /><div><span>{item.media_type} {item.event_name ? `· ${item.event_name}` : ""}</span><h2>{item.title}</h2><p>{item.caption}</p></div>{item.media_type === "video" && <b>▶</b>}</button>)}</section>{!isLoading && !items.length && <p className="gallery-empty" data-testid="gallery-empty">No active media matches this filter.</p>}</main><MediaViewer item={viewer} onClose={() => setViewer(null)} /></div>;
}