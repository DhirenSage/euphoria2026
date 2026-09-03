import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import BrandLockup from "@/components/BrandLockup";
import MediaViewer from "@/components/MediaViewer";
import SiteHeader from "@/components/SiteHeader";
import { apiGet } from "@/lib/api";
import type { EuphoriaEventsResponse } from "@/lib/euphoria";
import type { MediaItem, MediaListResponse } from "@/lib/media";

export default function Home() {
  const eventsQuery = useQuery({ queryKey: ["events"], queryFn: () => apiGet<EuphoriaEventsResponse>("/events") });
  const mediaQuery = useQuery({ queryKey: ["media"], queryFn: () => apiGet<MediaListResponse>("/media") });
  const [viewer, setViewer] = useState<MediaItem | null>(null);
  const events = eventsQuery.data?.data ?? [];
  const media = mediaQuery.data?.data ?? [];
  const hero = media.find((item) => item.section === "hero");
  const featured = media.find((item) => item.section === "featured");
  const lineup = media.filter((item) => item.section === "lineup").slice(0, 6);
  const gallery = media.filter((item) => item.section === "gallery").slice(0, 8);
  const categories = [...new Map(events.map((event) => [event.category_id, event.category_name])).entries()];
  const schedule = useMemo(() => {
    const grouped = new Map<string, { label: string; events: typeof events }>();
    events.forEach((event) => event.event_days.forEach((day) => { const existing = grouped.get(day.date) ?? { label: day.label, events: [] }; existing.events.push(event); grouped.set(day.date, existing); }));
    return [...grouped.entries()].sort(([left], [right]) => left.localeCompare(right)).slice(0, 3);
  }, [events]);
  const heroImage = hero?.source_url || "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=1900&q=85";

  return <div className="app-shell festival-home">
    <SiteHeader />
    <main>
      <section className="festival-hero" data-testid="home-hero" style={{ backgroundImage: `url(${heroImage})` }}><div className="festival-hero-scrim" /><div className="festival-hero-grid" /><div className="festival-hero-content"><BrandLockup variant="hero" /><p className="eyebrow cyan" data-testid="hero-organizer">SAGE UNIVERSITY INDORE · EUPHORIA 2026</p><h1 data-testid="hero-title">EXPERIENCE THE<br /><span>ENERGY.</span> LIVE THE<br /><em>EUPHORIA.</em></h1><p data-testid="hero-caption">{hero?.caption || "Three days of performance, competition, technology and campus culture on one electric stage."}</p><div className="hero-actions"><Link to="/registration" className="button button-neon" data-testid="hero-register-button">Get your pass ↗</Link><a href="#schedule" className="button button-ghost" data-testid="hero-schedule-button">Explore schedule</a>{featured && <button className="hero-play" onClick={() => setViewer(featured)} data-testid="hero-video-button"><span>▶</span> Watch teaser</button>}</div></div><div className="festival-hero-meta"><div><span>PROGRAMME</span><strong>EUPHORIA 2026</strong></div><div><span>VENUE</span><strong>SAGE University Indore</strong></div><div><span>LIVE EVENTS</span><strong>{events.length}</strong></div></div></section>
      <div className="festival-ribbon" data-testid="festival-ribbon"><div>SAGE <i>EUPHORIA</i> SAGE <i>EUPHORIA</i> SAGE <i>EUPHORIA</i></div></div>

      <section id="highlights" className="festival-section"><div className="festival-heading"><div><p className="eyebrow cyan">01 / EUPHORIA HIGHLIGHTS</p><h2>EVERY TALENT<br /><em>HAS A STAGE.</em></h2></div><p>From artistic expression to technical innovation and competitive sport—find your frequency.</p></div><div className="highlight-grid" data-testid="highlight-grid">{categories.slice(0, 6).map(([id, name], index) => { const categoryEvents = events.filter((event) => event.category_id === id); return <Link to={`/registration`} className={`highlight-card highlight-${index + 1}`} key={id} data-testid={`highlight-${id}`}><span>0{index + 1}</span><div><p>{categoryEvents.length} LIVE EVENTS</p><h3>{name}</h3><small>{categoryEvents.slice(0, 3).map((event) => event.name).join(" · ")}</small></div><b>↗</b></Link>; })}</div></section>

      {featured && <section className="festival-section performer-section" data-testid="featured-performer"><div className="performer-copy"><p className="eyebrow pink">SPECIAL SPOTLIGHT</p><h2>{featured.title}</h2><p>{featured.caption}</p><button className="button button-neon" onClick={() => setViewer(featured)} data-testid="featured-video-button">Play featured video ▶</button></div><button className="performer-visual" onClick={() => setViewer(featured)} data-testid="featured-media-preview" style={{ backgroundImage: `url(${featured.thumbnail_url || featured.source_url})` }}><span>▶</span><small>WATCH NOW</small></button></section>}

      <section id="lineup" className="festival-section"><div className="festival-heading"><div><p className="eyebrow pink">02 / LINE-UP</p><h2>RHYTHM<br /><em>REVELATIONS.</em></h2></div><p>Featured stages, performers and the moments that will define EUPHORIA 2026.</p></div><div className="lineup-grid" data-testid="lineup-grid">{lineup.map((item, index) => <button className="lineup-card" key={item.id} onClick={() => setViewer(item)} data-testid={`lineup-item-${item.id}`}><img src={item.thumbnail_url || item.source_url} alt={item.caption || item.title} /><span>0{index + 1}</span><div><h3>{item.title}</h3><p>{item.caption}</p></div>{item.media_type === "video" && <b>▶</b>}</button>)}</div></section>

      <section id="schedule" className="festival-section schedule-section" data-testid="schedule-section"><div className="festival-heading"><div><p className="eyebrow cyan">03 / DAY-WISE DISPATCH</p><h2>THREE DAYS.<br /><em>NO DULL MOMENTS.</em></h2></div><Link to="/events" className="text-link">View complete event details ↗</Link></div><div className="schedule-days">{schedule.map(([date, group], index) => <article key={date} data-testid={`schedule-day-${index + 1}`}><div className="schedule-date"><span>DAY {index + 1}</span><strong>{new Date(`${date}T00:00:00`).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })}</strong></div><div className="schedule-event-list">{group.events.slice(0, 8).map((event) => <Link to={`/events/${event.slug}`} key={event.id} data-testid={`schedule-event-${event.id}`}><span>{event.event_time.split("–")[0]}</span><strong>{event.name}</strong><small>{event.venue}</small><b>↗</b></Link>)}</div></article>)}</div></section>

      <section className="festival-gallery-section" data-testid="home-gallery-strip"><div className="festival-gallery-heading"><div><p className="eyebrow pink">04 / FESTIVAL IN MOTION</p><h2>THE<br /><em>AFTERGLOW.</em></h2></div><Link to="/gallery" className="button button-neon" data-testid="gallery-view-all-button">View all media ↗</Link></div><div className="gallery-strip">{gallery.map((item) => <button key={item.id} onClick={() => setViewer(item)} data-testid={`gallery-strip-item-${item.id}`}><img src={item.thumbnail_url || item.source_url} alt={item.caption || item.title} />{item.media_type === "video" && <span>▶</span>}</button>)}</div></section>
    </main>
    <footer className="site-footer"><div><BrandLockup variant="footer" /><h2>MAKE YOUR<br /><em>MOMENT.</em></h2></div><div><span>EUPHORIA / 2026</span><p>Culture · Literature · Science · Sport</p><small>© SAGE University Indore</small></div></footer>
    <MediaViewer item={viewer} onClose={() => setViewer(null)} />
  </div>;
}