import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import BrandLockup from "@/components/BrandLockup";
import SiteHeader from "@/components/SiteHeader";
import { apiGet } from "@/lib/api";
import type { EuphoriaEventResponse } from "@/lib/euphoria";

export default function EventDetail() {
  const { eventSlug = "" } = useParams();
  const { data, isLoading, isError } = useQuery({ queryKey: ["event",eventSlug], queryFn: () => apiGet<EuphoriaEventResponse>(`/events/${eventSlug}`), enabled: Boolean(eventSlug) });
  const event = data?.data;
  useEffect(()=>{ if(event) document.title=`${event.name} | EUPHORIA 2026`; return()=>{document.title="EUPHORIA 2026 | SAGE University Indore"};},[event]);
  if(isLoading) return <div className="app-shell"><SiteHeader/><main className="event-state" data-testid="event-detail-loading">Loading event details…</main></div>;
  if(isError||!event) return <div className="app-shell"><SiteHeader/><main className="event-state"><p className="eyebrow accent">EVENT NOT FOUND</p><h1>This event<br/><em>moved.</em></h1><Link className="button button-yellow" to="/events">Explore all events</Link></main></div>;
  const teamSize=event.registration_type==="team"&&event.min_team_size?`${event.min_team_size}–${event.max_team_size} members`:"Individual entry";
  return <div className="app-shell"><SiteHeader/><main className="event-detail" data-testid="event-detail-page">
    <section className="event-detail-hero" style={{backgroundImage:`url(${event.banner_url})`}}><div className="event-detail-overlay"/><div className="event-detail-top"><Link to="/events" data-testid="event-back-link">← All events</Link><span>{event.status.replace("_"," ")}</span></div><div className="event-detail-title"><BrandLockup variant="compact"/><p className="eyebrow accent" data-testid="event-category">{event.category_name} / {event.event_type}</p><h1 data-testid="event-title">{event.name}</h1><p data-testid="event-short-description">{event.short_description}</p></div></section>
    <section className="event-detail-layout"><div className="event-detail-content">
      <article className="event-overview" data-testid="event-description"><p className="eyebrow">THE EVENT</p><h2>{event.description}</h2><div className="event-facts"><div><span>ELIGIBILITY</span><strong data-testid="event-eligibility">{event.eligibility}</strong></div><div><span>CAPACITY</span><strong data-testid="event-capacity">{event.capacity} participants</strong></div><div><span>ENTRY FORMAT</span><strong data-testid="event-team-size">{teamSize}</strong></div><div><span>REGISTRATION CLOSES</span><strong data-testid="event-deadline">{event.registration_deadline}</strong></div></div></article>
      <article className="event-info-section" data-testid="event-schedule"><div className="detail-section-heading"><p className="eyebrow accent">01 / EVENT DAY</p><h2>Schedule</h2></div><div className="schedule-list">{event.schedule.map((item,index)=><div key={`${item.time}-${index}`}><span>{item.time}</span><strong>{item.title}</strong></div>)}</div></article>
      <article className="event-info-grid"><div data-testid="event-rules"><div className="detail-section-heading"><p className="eyebrow accent">02 / BEFORE YOU ENTER</p><h2>Rules</h2></div><ol>{event.rules.map((rule,index)=><li key={rule}><span>{String(index+1).padStart(2,"0")}</span>{rule}</li>)}</ol></div><div data-testid="event-prizes"><div className="detail-section-heading"><p className="eyebrow accent">03 / RECOGNITION</p><h2>Prizes</h2></div><ul>{event.prizes.map(prize=><li key={prize}>✳ <span>{prize}</span></li>)}</ul></div></article>
      <article className="event-coordinator" data-testid="event-coordinator"><p className="eyebrow">EVENT COORDINATION</p><div><h3>{event.coordinator_name}</h3><p>{event.coordinator_contact}</p></div></article>
    </div>
    <aside className="event-registration-card" data-testid="event-registration-summary"><div className="event-card-status"><span>REGISTRATION</span><b>OPEN</b></div><div className="event-price"><span>Entry fee</span><strong data-testid="event-fee">₹{event.fee.toLocaleString("en-IN")}</strong></div><div className="event-register-facts"><div><span>DATE</span><strong data-testid="event-date">{event.event_date}</strong></div><div><span>TIME</span><strong data-testid="event-time">{event.event_time}</strong></div><div><span>VENUE</span><strong data-testid="event-venue">{event.venue}</strong></div><div><span>ENTRY</span><strong>{teamSize}</strong></div></div><Link to={`/registration/${event.slug}`} className="button button-yellow full" data-testid="event-register-button">Register now <span>↗</span></Link><small>Fee and event selection are verified by the server.</small></aside>
    </section>
  </main></div>;
}