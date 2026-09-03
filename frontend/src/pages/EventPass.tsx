import { useQuery } from "@tanstack/react-query";
import { Link, useParams, useSearchParams } from "react-router-dom";
import DigitalPassCard from "@/components/pass/DigitalPassCard";
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
  const pdfUrl = `/api/passes/${registrationId}/pdf?key=${encodeURIComponent(key)}`;
  return <main className="pass-shell"><div className="pass-page-intro"><p className="eyebrow">EUPHORIA 2026 · DIGITAL WALLET</p><h1>Your festival<br /><em>entry pass.</em></h1><p>Show this QR at the assigned gate or download the complete mobile-ticket PDF.</p></div><DigitalPassCard pass={data} /><div className="pass-page-actions"><a className="button pass-download-button" href={pdfUrl} download={`${registrationId}-complete-event-pass.pdf`} data-testid="pass-download-pdf-button">Download complete PDF ↓</a><button className="button button-ghost" onClick={() => window.print()} data-testid="print-pass-button">Print pass</button><Link className="button button-ghost" to="/events">Back to events</Link></div></main>;
}