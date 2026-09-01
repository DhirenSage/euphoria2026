import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import BrandLockup from "@/components/BrandLockup";
import SiteHeader from "@/components/SiteHeader";
import { apiGet } from "@/lib/api";
import type { EuphoriaEventsResponse } from "@/lib/euphoria";

const EVENT_IMAGE: Record<string, string> = {
  cultural: "https://images.unsplash.com/photo-1506157786151-b8491531f063?auto=format&fit=crop&w=900&q=80",
  sports: "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=900&q=80",
  "literary-management": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=900&q=80",
  "sci-pha-agro": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=900&q=80",
};

export default function Home() {
  const { data } = useQuery({ queryKey: ["events"], queryFn: () => apiGet<EuphoriaEventsResponse>("/events") });
  const events = data?.data ?? [];
  const categories = [...new Map(events.map((event) => [event.category_id, event.category_name])).entries()];

  return (
    <div className="app-shell">
      <SiteHeader />
      <main>
        <section className="home-hero" data-testid="home-hero">
          <div className="home-hero-media" />
          <div className="home-hero-grid" />
          <div className="home-hero-content">
            <BrandLockup variant="hero" />
            <p className="eyebrow accent" data-testid="hero-organizer">SAGE UNIVERSITY INDORE · 2026</p>
            <h1 data-testid="hero-title">THE CAMPUS<br /><span>COMES ALIVE.</span></h1>
            <p className="hero-copy">A multi-day collision of culture, sport, ideas and everything that makes student life unforgettable.</p>
            <div className="hero-actions">
              <Link to="/registration" className="button button-yellow" data-testid="hero-register-button">Register now <span>↗</span></Link>
              <a href="#events" className="button button-ghost" data-testid="hero-events-button">Explore events</a>
            </div>
          </div>
          <div className="hero-coordinate">INDORE<br /><span>22.7196° N · 75.8577° E</span></div>
        </section>

        <div className="ticker"><div>MAKE NOISE <i>✳</i> MAKE MOVES <i>✳</i> MAKE MEMORIES <i>✳</i> MAKE NOISE <i>✳</i></div></div>

        <section id="categories" className="content-section">
          <div className="section-heading"><div><p className="eyebrow">01 / THE PLAYGROUND</p><h2>Pick your<br /><em>frequency.</em></h2></div><p>Four worlds. Thirty-two events. Find the thing that makes you forget to check the time.</p></div>
          <div className="category-grid" data-testid="category-grid">
            {categories.map(([id, name], index) => <Link to="/registration" className={`category-card category-card-${index + 1}`} key={id} data-testid={`category-card-${id}`}><span>0{index + 1}</span><h3>{name}</h3><b>↗</b></Link>)}
          </div>
        </section>

        <section id="events" className="content-section event-section">
          <div className="section-heading"><div><p className="eyebrow">02 / THE LINEUP</p><h2>Find your<br /><em>moment.</em></h2></div><Link to="/registration" className="text-link">Register for an event ↗</Link></div>
          <div className="event-grid" data-testid="event-grid">
            {events.slice(0, 8).map((event, index) => (
              <article className="event-card" key={event.id} data-testid={`event-card-${event.slug}`}>
                <div className="event-image" style={{ backgroundImage: `url(${EVENT_IMAGE[event.category_id]})` }}><span>0{index + 1}</span><b>{event.category_name}</b></div>
                <div className="event-body"><div className="event-meta"><span>{event.registration_type}</span><strong>₹{event.fee.toLocaleString("en-IN")}</strong></div><h3>{event.name}</h3><p>{event.short_description}</p><Link to={`/registration/${event.slug}`} data-testid={`event-register-${event.slug}`}>Register <span>↗</span></Link></div>
              </article>
            ))}
          </div>
        </section>
      </main>
      <footer className="site-footer"><div><BrandLockup variant="footer" /><h2>Make your<br /><em>moment.</em></h2></div><div><span>EUPHORIA / 2026</span><p>Culture · Literature · Science · Sport</p><small>© SAGE University Indore</small></div></footer>
    </div>
  );
}