import { useMutation, useQuery } from "@tanstack/react-query";
import { Link, useLocation, useParams } from "react-router-dom";
import BrandLockup from "@/components/BrandLockup";
import SiteHeader from "@/components/SiteHeader";
import { apiGet, apiPost } from "@/lib/api";
import type { PaymentInitiationResponse, RegistrationResponse } from "@/lib/euphoria";

export default function RegistrationSuccess() {
  const { registrationId = "" } = useParams();
  const location = useLocation();
  const initial = location.state as RegistrationResponse | null;
  if (initial?.pass_key) sessionStorage.setItem(`euphoria-pass-${registrationId}`, initial.pass_key);
  const { data } = useQuery({ queryKey: ["registration", registrationId], queryFn: () => apiGet<RegistrationResponse>(`/registrations/${registrationId}`), initialData: initial ?? undefined });
  const payment = useMutation({ mutationFn: () => apiPost<PaymentInitiationResponse>(`/registrations/${registrationId}/payment`) });
  const openPayment = () => {
    const paymentWindow = window.open("about:blank", "_blank");
    if (paymentWindow) {
      paymentWindow.opener = null;
      paymentWindow.document.title = "Opening Easebuzz…";
      paymentWindow.document.body.innerHTML = '<p style="font:16px sans-serif;padding:32px">Opening secure Easebuzz checkout…</p>';
    }
    payment.mutate(undefined, {
      onSuccess: ({ checkout_url }) => paymentWindow ? paymentWindow.location.replace(checkout_url) : window.location.assign(checkout_url),
      onError: () => paymentWindow?.close(),
    });
  };
  const confirmed = data?.status === "confirmed";
  return <div className="app-shell registration-bg"><SiteHeader /><main className="success-page"><BrandLockup variant="compact" /><div className="success-icon">✓</div><p className="eyebrow accent">{confirmed ? "REGISTRATION CONFIRMED" : "REGISTRATION CREATED"}</p><h1>{confirmed ? <>You&apos;re<br /><em>in.</em></> : <>Almost<br /><em>there.</em></>}</h1><p>{confirmed ? <>Your secure QR pass for <strong>{data?.event_name}</strong> is ready.</> : <>Your place for <strong>{data?.event_name}</strong> is held. Complete verified payment to unlock the QR pass.</>}</p><div className="success-card" data-testid="registration-confirmation-card"><div><span>REGISTRATION ID</span><strong data-testid="registration-id">{data?.registration_id}</strong></div><div><span>PARTICIPANT</span><strong>{data?.participant_name}</strong></div><div className="success-amount-cell"><span>SERVER AMOUNT</span><strong data-testid="confirmation-server-amount" aria-label={`Server amount ₹${data?.total_amount.toLocaleString("en-IN")}`}>₹{data?.total_amount.toLocaleString("en-IN")}</strong></div><div><span>STATUS</span><b data-testid="confirmation-status">{data?.status.replace("_", " ").toUpperCase()}</b></div></div><div className="success-actions">{confirmed ? <Link className="button button-yellow" to={`/pass/${registrationId}`} data-testid="view-pass-button">View QR pass ↗</Link> : <button className="button button-yellow" onClick={openPayment} disabled={payment.isPending} data-testid="complete-payment-button">{payment.isPending ? "Opening…" : "Complete secure payment ↗"}</button>}<Link className="button button-ghost" to="/">Back to home</Link></div>{payment.isError && <p className="form-error">Payment could not be opened. Please try again.</p>}</main></div>;
}