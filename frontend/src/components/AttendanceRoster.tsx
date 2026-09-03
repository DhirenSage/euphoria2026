import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import type { AdminAttendanceResponse } from "@/lib/euphoria";

export default function AttendanceRoster() {
  const [date, setDate] = useState("");
  const [eventId, setEventId] = useState("");
  const [status, setStatus] = useState("all");
  const params = new URLSearchParams();
  if (date) params.set("date", date);
  if (eventId) params.set("event_id", eventId);
  if (status !== "all") params.set("status", status);
  const roster = useQuery({ queryKey: ["attendance-roster", date, eventId, status], queryFn: () => apiGet<AdminAttendanceResponse>(`/admin/attendance-roster?${params.toString()}`) });

  return <section id="attendance" className="ops-panel" data-testid="attendance-roster">
    <div className="ops-panel-heading"><div><p className="eyebrow accent">DATE-WISE PARTICIPANT LIST</p><h2>Entry roster</h2><p className="ops-panel-copy">Choose a date and event to separate entered participants from those still expected.</p></div><span data-testid="attendance-roster-date">{roster.data?.date ?? "Loading…"}</span></div>
    <div className="roster-controls">
      <label>Date<input type="date" value={date || roster.data?.date || ""} onChange={(event) => setDate(event.target.value)} data-testid="attendance-date-filter" /></label>
      <label>Event<select value={eventId} onChange={(event) => setEventId(event.target.value)} data-testid="attendance-event-filter"><option value="">All events</option>{roster.data?.events.map((event) => <option key={event.id} value={event.id}>{event.name}</option>)}</select></label>
      <label>Entry status<select value={status} onChange={(event) => setStatus(event.target.value)} data-testid="attendance-status-filter"><option value="all">All participants</option><option value="entered">Entered</option><option value="not_entered">Not entered</option></select></label>
    </div>
    <div className="roster-stats"><div><span>EXPECTED</span><strong data-testid="attendance-total-count">{roster.data?.total ?? 0}</strong></div><div><span>ENTERED</span><strong data-testid="attendance-entered-count">{roster.data?.entered ?? 0}</strong></div><div><span>NOT ENTERED</span><strong data-testid="attendance-not-entered-count">{roster.data?.not_entered ?? 0}</strong></div></div>
    <div className="responsive-table"><table><thead><tr><th>Participant</th><th>Registration</th><th>Event / day</th><th>Institute</th><th>Contact</th><th>Entry</th></tr></thead><tbody>{roster.data?.rows.map((row) => <tr key={row.registration_id} data-testid={`attendance-roster-row-${row.registration_id}`}><td><strong>{row.participant_name}</strong></td><td>{row.registration_id}</td><td>{row.event_name}<small>{row.event_day_label} · {row.event_date}</small></td><td>{row.college}</td><td>{row.mobile}<small>{row.email}</small></td><td><span className={`ops-status ${row.entered ? "status-live" : "status-registration_closed"}`} data-testid={`attendance-state-${row.registration_id}`}>{row.entered ? "ENTERED" : "NOT ENTERED"}</span>{row.entry_at && <small>{new Date(row.entry_at).toLocaleString("en-IN")} · {row.scanner_name}</small>}</td></tr>)}</tbody></table>{!roster.isLoading && !roster.data?.rows.length && <p className="empty-copy" data-testid="attendance-roster-empty">No participants match this date and filter.</p>}</div>
  </section>;
}