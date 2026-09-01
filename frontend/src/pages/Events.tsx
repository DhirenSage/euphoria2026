import { useQuery } from "@tanstack/react-query";
import BrandLockup from "@/components/BrandLockup";
import EventCard from "@/components/EventCard";
import SiteHeader from "@/components/SiteHeader";
import { apiGet } from "@/lib/api";
import type { EuphoriaEventsResponse } from "@/lib/euphoria";

export default function Events() {
  const { data, isLoading } = useQuery({ queryKey: ["events"], queryFn: () => apiGet<EuphoriaEventsResponse>("/events") });
  return <div className="app-shell"><SiteHeader /><main className="events-page"><section className="events-intro"><BrandLockup variant="compact" /><p className="eyebrow accent">EUPHORIA 2K26 / ALL EVENTS</p><h1>Choose your<br /><em>arena.</em></h1><p>Explore complete details, fees, rules, schedules and team requirements before you register.</p></section>{isLoading ? <div className="events-loading" data-testid="events-loading">Loading the EUPHORIA lineup…</div> : <div className="event-grid events-page-grid" data-testid="all-events-grid">{data?.data.map((event,index)=><EventCard key={event.id} event={event} index={index}/>)}</div>}</main></div>;
}