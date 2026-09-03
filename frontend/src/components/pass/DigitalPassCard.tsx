import BrandLockup from "@/components/BrandLockup";
import type { PassResponse } from "@/lib/euphoria";

interface DigitalPassCardProps { pass: PassResponse; }

export default function DigitalPassCard({ pass }: DigitalPassCardProps) {
  const securityCode = pass.registration_id.replace(/[^A-Z0-9]/g, "").slice(-10);
  return <section className="festival-pass" data-testid="digital-pass">
    <div className="festival-pass-foil" aria-hidden="true" />
    <header className="festival-pass-header"><BrandLockup variant="compact" /><div className="pass-live-badge"><span aria-hidden="true" /> <b data-testid="pass-status">{pass.qr_status.toUpperCase()}</b></div></header>
    <div className="festival-pass-hero"><div className="pass-orbit pass-orbit-one" aria-hidden="true" /><div className="pass-orbit pass-orbit-two" aria-hidden="true" /><p className="pass-kicker" data-testid="pass-category">{pass.category_name} · OFFICIAL EVENT PASS</p><h1 data-testid="pass-event-name">{pass.event_name}</h1><span className="pass-tier" data-testid="pass-tier">PARTICIPANT / 2026</span></div>
    <div className="festival-pass-attendee"><p>THIS PASS BELONGS TO</p><h2 data-testid="pass-participant-name">{pass.participant_name}</h2><div className="pass-detail-grid"><div><span>REGISTRATION ID</span><strong data-testid="pass-registration-id">{pass.registration_id}</strong></div><div><span>PAYMENT / PASS</span><strong data-testid="pass-payment-status">{pass.payment_status.replaceAll("_", " ").toUpperCase()} · ACTIVE</strong></div><div><span>DATE & TIME</span><strong data-testid="pass-event-date">{pass.event_date}<br />{pass.event_time}</strong></div><div><span>VENUE</span><strong data-testid="pass-venue">{pass.venue}</strong></div><div className="pass-detail-wide"><span>COLLEGE / INSTITUTION</span><strong data-testid="pass-college">{pass.college}</strong></div></div></div>
    <div className="festival-pass-perforation" aria-hidden="true"><span /><i /></div>
    <div className="festival-pass-qr-stub"><div className="pass-qr-heading"><div><p>SECURE ENTRY CODE</p><strong>Scan at authorized gate</strong></div><span data-testid="pass-security-code">#{securityCode}</span></div><div className="pass-qr-frame"><img src={pass.qr_data_url} alt={`Secure QR event pass for ${pass.registration_id}`} data-testid="pass-qr-image" /><i className="pass-scan-line" aria-hidden="true" /></div><p className="pass-qr-note">Pure black-on-white QR · Keep screen brightness high</p><details className="pass-token"><summary>Manual scanner token</summary><code data-testid="pass-qr-token">{pass.qr_token}</code></details></div>
    <footer className="festival-pass-footer"><div><span>01</span><p>Carry a valid institutional photo ID</p></div><div><span>02</span><p>Non-transferable; valid for this event only</p></div><div><span>03</span><p>One entry per configured event day</p></div></footer>
  </section>;
}