import { useQuery } from "@tanstack/react-query";
import { Link, useParams, useSearchParams } from "react-router-dom";
import BrandLockup from "@/components/BrandLockup";
import { apiGet } from "@/lib/api";
import type { PassResponse } from "@/lib/euphoria";

export default function EventPass() {
  const { registrationId = "" } = useParams();
  const [search] = useSearchParams();
  const queryKey = search.get("key") ?? "";
  if (queryKey) sessionStorage.setItem(`euphoria-pass-${registrationId}`, queryKey);
  const key = queryKey || sessionStorage.getItem(`euphoria-pass-${registrationId}`) || "";
  const { data, isLoading, isError } = useQuery({
    queryKey: ["pass", registrationId, key],
    queryFn: () => apiGet<PassResponse>(`/passes/${registrationId}?key=${encodeURIComponent(key)}`),
    retry: false,
  });
  if (isLoading) return <main className="pass-shell"><p data-testid="pass-loading">Preparing secure pass…</p></main>;
  if (isError || !data) return <main className="pass-shell"><div className="pass-error" data-testid="pass-error"><p className="eyebrow accent">PASS UNAVAILABLE</p><h1>This pass is not active.</h1><p>Complete payment verification or open the pass from the original confirmation session.</p><Link className="button button-yellow" to="/events">Back to events</Link></div></main>;
  return <main className="pass-shell"><section className="digital-pass" data-testid="digital-pass"><header><BrandLockup variant="compact" /><span data-testid="pass-status">{data.qr_status.toUpperCase()}</span></header><div className="pass-grid"><div><p className="eyebrow accent">EUPHORIA 2026 / EVENT PASS</p><h1 data-testid="pass-participant-name">{data.participant_name}</h1><dl><div><dt>Registration</dt><dd data-testid="pass-registration-id">{data.registration_id}</dd></div><div><dt>Event</dt><dd data-testid="pass-event-name">{data.event_name}</dd></div><div><dt>Category</dt><dd>{data.category_name}</dd></div><div><dt>Date</dt><dd>{data.event_date}</dd></div><div><dt>Venue</dt><dd>{data.venue}</dd></div></dl></div><div className="pass-qr"><img src={data.qr_data_url} alt={`QR pass for ${data.registration_id}`} data-testid="pass-qr-image" /><span>SCAN AT AUTHORIZED GATE</span></div></div><footer><span>Manual scanner token</span><code data-testid="pass-qr-token">{data.qr_token}</code></footer></section><div className="pass-page-actions"><button className="button button-yellow" onClick={() => window.print()} data-testid="print-pass-button">Print / save PDF</button><Link className="button button-ghost" to="/events">Back to events</Link></div></main>;
}