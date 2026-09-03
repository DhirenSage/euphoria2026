import type { MediaItem } from "@/lib/media";

interface MediaViewerProps { item: MediaItem | null; onClose: () => void; }

export default function MediaViewer({ item, onClose }: MediaViewerProps) {
  if (!item) return null;
  return <div className="media-modal" role="dialog" aria-modal="true" aria-label={item.title} data-testid="media-lightbox" onClick={onClose}>
    <div className="media-modal-panel" onClick={(event) => event.stopPropagation()}>
      <button className="media-modal-close" onClick={onClose} aria-label="Close media" data-testid="media-lightbox-close">×</button>
      {item.media_type === "video" && item.video_provider === "direct" ? <video controls autoPlay src={item.embed_url ?? item.source_url} data-testid="media-video-player" /> : item.media_type === "video" && item.embed_url ? <iframe src={`${item.embed_url}?autoplay=1`} title={item.title} allow="autoplay; fullscreen; picture-in-picture" allowFullScreen data-testid="media-video-embed" /> : <img src={item.source_url} alt={item.caption || item.title} data-testid="media-lightbox-image" />}
      <div className="media-modal-copy"><span>{item.section} {item.event_name ? `· ${item.event_name}` : ""}</span><h2>{item.title}</h2><p>{item.caption}</p></div>
    </div>
  </div>;
}