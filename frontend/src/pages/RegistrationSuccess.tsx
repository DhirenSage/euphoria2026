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
  return <div className="app-shell registration-bg"><SiteHeader /><main className="success-page"><BrandLockup variant="compact" /><div className="success-icon">✓</div><p className="eyebrow accent">REGISTRATION CREATED</p><h1>Almost<br /><em>there.</em></h1><p>Your place for <strong>{data?.event_name}</strong> is held. Complete the verified payment to unlock your QR pass.</p><div className="success-card" data-testid="registration-confirmation-card"><div><span>REGISTRATION ID</span><strong data-testid="registration-id">{data?.registration_id}</strong></div><div><span>PARTICIPANT</span><strong>{data?.participant_name}</strong></div><div className="success-amount-cell"><span>SERVER AMOUNT</span><strong data-testid="confirmation-server-amount" aria-label={`Server amount ₹${data?.total_amount.toLocaleString("en-IN")}`}>₹{data?.total_amount.toLocaleString("en-IN")}</strong></div><div><span>STATUS</span><b>{data?.status.replace("_", " ").toUpperCase()}</b></div></div><div className="success-actions"><button className="button button-yellow" onClick={openPayment} disabled={payment.isPending} data-testid="complete-payment-button">{payment.isPending ? "Opening…" : "Complete secure payment ↗"}</button><Link className="button button-ghost" to="/">Back to home</Link></div>{payment.isError && <p className="form-error">Payment could not be opened. Please try again.</p>}</main></div>;
}