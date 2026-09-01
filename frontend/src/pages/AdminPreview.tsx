import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import BrandLockup from "@/components/BrandLockup";
import { apiGet } from "@/lib/api";
import type { EuphoriaEventsResponse } from "@/lib/euphoria";

export default function AdminPreview() {
  const { data } = useQuery({ queryKey: ["events"], queryFn: () => apiGet<EuphoriaEventsResponse>("/events") });
  return <main className="ops-shell"><aside className="ops-sidebar"><Link to="/"><BrandLockup variant="compact" /></Link><nav><a href="#overview">Overview</a><a href="#events">Events</a><Link to="/registration">Registrations</Link><Link to="/scanner">Scanner</Link></nav></aside><section className="ops-content"><header><div><p className="eyebrow accent">EUPHORIA OPERATIONS</p><h1>Command centre</h1></div><Link to="/" className="text-link">Public site ↗</Link></header><div className="ops-kpis"><div><span>LIVE EVENTS</span><strong>{data?.data.length ?? 32}</strong></div><div><span>CATEGORIES</span><strong>04</strong></div><div><span>GATEWAYS</span><strong>01</strong></div><div><span>PROGRAMME</span><strong>26</strong></div></div><div className="ops-panel"><h2>Registration catalogue</h2><div className="responsive-table"><table><thead><tr><th>Event</th><th>Category</th><th>Entry</th><th>Fee</th></tr></thead><tbody>{data?.data.slice(0,10).map((event)=><tr key={event.id}><td>{event.name}</td><td>{event.category_name}</td><td>{event.registration_type}</td><td>₹{event.fee.toLocaleString("en-IN")}</td></tr>)}</tbody></table></div></div></section></main>;
}