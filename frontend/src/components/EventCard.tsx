import { Link } from "react-router-dom";
import type { EuphoriaEvent } from "@/lib/euphoria";

interface EventCardProps {
  event: EuphoriaEvent;
  index: number;
}

export default function EventCard({ event, index }: EventCardProps) {
  return (
    <Link to={`/events/${event.slug}`} className="event-card" data-testid={`event-card-${event.slug}`} aria-label={`View complete details for ${event.name}`}>
      <div className="event-image" style={{ backgroundImage: `url(${event.banner_url})` }}>
        <span>{String(index + 1).padStart(2, "0")}</span>
        <b>{event.category_name}</b>
      </div>
      <div className="event-body">
        <div className="event-meta"><span>{event.registration_type}</span><strong>₹{event.fee.toLocaleString("en-IN")}</strong></div>
        <h3>{event.name}</h3>
        <p>{event.short_description}</p>
        <div className="event-card-link" data-testid={`event-details-link-${event.slug}`}>View complete details <span>↗</span></div>
      </div>
    </Link>
  );
}