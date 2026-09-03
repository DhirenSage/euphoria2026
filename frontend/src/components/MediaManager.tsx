import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { apiDelete, apiGet, apiPostForm, apiPut } from "@/lib/api";
import { queryClient } from "@/lib/queryClient";
import type { EuphoriaEvent } from "@/lib/euphoria";
import type { MediaItem, MediaListResponse, MediaSection, MediaUpdate } from "@/lib/media";

const SECTIONS: MediaSection[] = ["hero", "highlight", "featured", "lineup", "gallery"];

function MediaRowEditor({ item, events }: { item: MediaItem; events: EuphoriaEvent[] }) {
  const [draft, setDraft] = useState<MediaUpdate>({ title: item.title, caption: item.caption, section: item.section, event_id: item.event_id, source_url: item.source_url, thumbnail_url: item.thumbnail_url, display_order: item.display_order, is_active: item.is_active });
  const save = useMutation({ mutationFn: () => apiPut<MediaItem>(`/admin/media/${item.id}`, draft), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-media"] }) });
  const remove = useMutation({ mutationFn: () => apiDelete<void>(`/admin/media/${item.id}`), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-media"] }) });
  const set = <K extends keyof MediaUpdate>(key: K, value: MediaUpdate[K]) => setDraft((current) => ({ ...current, [key]: value }));
  return <div className="media-admin-row" data-testid={`media-admin-row-${item.id}`}>
    <img src={item.thumbnail_url || item.source_url} alt="" data-testid={`media-admin-preview-${item.id}`} />
    <div className="media-admin-fields"><input value={draft.title} onChange={(event) => set("title", event.target.value)} aria-label="Media title" data-testid={`media-title-${item.id}`} /><input value={draft.caption} onChange={(event) => set("caption", event.target.value)} aria-label="Media caption" data-testid={`media-caption-${item.id}`} /><div><select value={draft.section} onChange={(event) => set("section", event.target.value as MediaSection)} aria-label="Media section" data-testid={`media-section-${item.id}`}>{SECTIONS.map((section) => <option key={section} value={section}>{section}</option>)}</select><select value={draft.event_id ?? ""} onChange={(event) => set("event_id", event.target.value || null)} aria-label="Linked event" data-testid={`media-event-${item.id}`}><option value="">No event</option>{events.map((event) => <option key={event.id} value={event.id}>{event.name}</option>)}</select><input type="number" min="0" value={draft.display_order} onChange={(event) => set("display_order", Number(event.target.value))} aria-label="Display order" data-testid={`media-order-${item.id}`} /></div></div>
    <div className="media-admin-actions"><label><input type="checkbox" checked={draft.is_active} onChange={(event) => set("is_active", event.target.checked)} data-testid={`media-active-${item.id}`} /> Active</label><button onClick={() => save.mutate()} disabled={save.isPending} data-testid={`media-save-${item.id}`}>Save</button><button className="danger" onClick={() => window.confirm("Delete this media item?") && remove.mutate()} data-testid={`media-delete-${item.id}`}>Delete</button></div>
  </div>;
}

export default function MediaManager({ events }: { events: EuphoriaEvent[] }) {
  const media = useQuery({ queryKey: ["admin-media"], queryFn: () => apiGet<MediaListResponse>("/admin/media") });
  const create = useMutation({ mutationFn: (body: FormData) => apiPostForm<MediaItem>("/admin/media", body), onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["admin-media"] }); queryClient.invalidateQueries({ queryKey: ["media"] }); } });
  return <section id="media" className="ops-panel" data-testid="admin-media-manager">
    <div className="ops-panel-heading"><div><p className="eyebrow accent">DYNAMIC GALLERY & VIDEO</p><h2>Media manager</h2><p className="ops-panel-copy">Control hero imagery, highlights, performer videos, line-up and the public gallery. Uploaded images stay private behind the media endpoint.</p></div><span>{media.data?.data.length ?? 0} assets</span></div>
    <form className="media-create-form" data-testid="media-create-form" onSubmit={(event) => { event.preventDefault(); const form = event.currentTarget; create.mutate(new FormData(form), { onSuccess: () => form.reset() }); }}>
      <label>Type<select name="media_type" data-testid="media-create-type"><option value="image">Image</option><option value="video">Video URL</option></select></label>
      <label>Section<select name="section" data-testid="media-create-section">{SECTIONS.map((section) => <option key={section} value={section}>{section}</option>)}</select></label>
      <label>Title<input name="title" required minLength={2} data-testid="media-create-title" /></label>
      <label>Caption<input name="caption" data-testid="media-create-caption" /></label>
      <label>Event<select name="event_id" data-testid="media-create-event"><option value="">No event</option>{events.map((event) => <option key={event.id} value={event.id}>{event.name}</option>)}</select></label>
      <label>Order<input name="display_order" type="number" min="0" defaultValue="0" data-testid="media-create-order" /></label>
      <label className="media-wide">Image upload / video thumbnail<input name="image" type="file" accept="image/jpeg,image/png,image/webp" data-testid="media-create-file" /></label>
      <label className="media-wide">Image URL or YouTube/Vimeo/MP4 URL<input name="source_url" type="url" placeholder="https://…" data-testid="media-create-url" /></label>
      <label className="media-wide">Optional video thumbnail URL<input name="thumbnail_url" type="url" placeholder="https://…" data-testid="media-create-thumbnail" /></label>
      <input type="hidden" name="is_active" value="true" />
      <button className="button button-yellow media-wide" type="submit" disabled={create.isPending} data-testid="media-create-submit">{create.isPending ? "Publishing…" : "Add media item"}</button>
      {create.isError && <p className="form-error media-wide" data-testid="media-create-error">Media could not be saved. For video use YouTube, Vimeo, MP4 or WEBM URL; for images upload JPG/PNG/WEBP.</p>}
    </form>
    <div className="media-admin-list">{media.data?.data.map((item) => <MediaRowEditor key={item.id} item={item} events={events} />)}</div>
  </section>;
}