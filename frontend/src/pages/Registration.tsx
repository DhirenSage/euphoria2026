import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate, useParams } from "react-router-dom";
import BrandLockup from "@/components/BrandLockup";
import SiteHeader from "@/components/SiteHeader";
import { apiGet, apiPost } from "@/lib/api";
import type { RegistrationCatalogueResponse, RegistrationCreate, RegistrationResponse } from "@/lib/euphoria";

const money = (amount: number) => `₹${amount.toLocaleString("en-IN")}`;

export default function Registration() {
  const navigate = useNavigate();
  const { eventSlug } = useParams();
  const { data, isLoading } = useQuery({ queryKey: ["registration-catalogue"], queryFn: () => apiGet<RegistrationCatalogueResponse>("/registration-catalogue") });
  const preselected = data?.events.find((event) => event.slug === eventSlug);
  const [categoryId, setCategoryId] = useState("");
  const [eventId, setEventId] = useState("");
  const [affiliation, setAffiliation] = useState<"" | "sageian" | "non_sageian">("");
  useEffect(() => {
    if (preselected && categoryId === "" && eventId === "") {
      setCategoryId(preselected.category_id);
      setEventId(preselected.id);
    }
  }, [preselected, categoryId, eventId]);
  const effectiveCategory = categoryId;
  const effectiveEvent = eventId;
  const selectedEvent = data?.events.find((event) => event.id === effectiveEvent);
  const filteredEvents = useMemo(() => data?.events.filter((event) => event.category_id === effectiveCategory) ?? [], [data, effectiveCategory]);
  const mutation = useMutation({ mutationFn: (payload: RegistrationCreate) => apiPost<RegistrationResponse>("/registrations", payload), onSuccess: (registration) => navigate(`/registration/success/${registration.registration_id}`, { state: registration }) });

  const submit = (form: HTMLFormElement) => {
    const values = new FormData(form);
    mutation.mutate({
      category_id: effectiveCategory, event_id: effectiveEvent, name: String(values.get("name") ?? ""), father_name: String(values.get("father_name") ?? "") || null,
      email: String(values.get("email") ?? ""), mobile: String(values.get("mobile") ?? ""), age: values.get("age") ? Number(values.get("age")) : null,
      college: String(values.get("college") ?? ""), city: String(values.get("city") ?? "") || null, participant_affiliation: String(values.get("participant_affiliation")) as "sageian" | "non_sageian",
      team_name: String(values.get("team_name") ?? "") || null, team_members: String(values.get("team_members") ?? "") || null,
    });
  };

  return (
    <div className="app-shell registration-bg">
      <SiteHeader />
      <main className="registration-page">
        <section className="registration-intro" data-testid="registration-page-header">
          <div><BrandLockup variant="compact" /><p className="eyebrow accent">EUPHORIA 2K26 / REGISTRATION</p><h1>Register for<br /><em>your event.</em></h1></div>
          <div className="intro-notes"><div><span>01</span> Details</div><div><span>02</span> Event</div><div><span>03</span> Payment</div><p>Choose from 32 cultural, literary, science and sports events.</p></div>
        </section>

        <form className="registration-layout" data-testid="registration-form" onSubmit={(event) => { event.preventDefault(); submit(event.currentTarget); }}>
          <div className="registration-card">
            <header className="card-heading"><p className="eyebrow">PARTICIPANT INFORMATION</p><h2>Tell us about yourself</h2><span>Fields marked with an asterisk are required.</span></header>
            <section className="form-block"><b className="block-number">01</b><div className="form-grid">
              <label>Your name *<input name="name" required placeholder="Your full name" data-testid="registration-name-input" /></label>
              <label>Father&apos;s name <small>Optional</small><input name="father_name" placeholder="Father's name" data-testid="registration-father-name-input" /></label>
              <label>Email address *<input name="email" type="email" required placeholder="name@example.com" data-testid="registration-email-input" /></label>
              <label>Mobile number *<input name="mobile" type="tel" pattern="[6-9][0-9]{9}" required placeholder="10-digit mobile number" data-testid="registration-mobile-input" /></label>
              <label>Your age <small>Optional</small><input name="age" type="number" min="10" max="100" placeholder="Age" data-testid="registration-age-input" /></label>
              <label>School / college name *<input name="college" required placeholder="Institution name" data-testid="registration-college-input" /></label>
              <label>City <small>Optional</small><input name="city" placeholder="Your city" data-testid="registration-city-input" /></label>
              <label>Participant type *<select name="participant_affiliation" required value={affiliation} onChange={(event) => setAffiliation(event.target.value as "" | "sageian" | "non_sageian")} data-testid="registration-affiliation-select"><option value="" disabled>Select affiliation</option><option value="sageian">SAGEian</option><option value="non_sageian">Non-SAGEian</option></select></label>
            </div></section>
            <section className="form-block event-block"><b className="block-number">02</b><div className="block-heading"><p className="eyebrow">EVENT SELECTION</p><h3>Choose where you want to compete</h3></div>
              <div className="form-grid"><label>Event category *<select value={effectiveCategory} required onChange={(e) => { setCategoryId(e.target.value); setEventId(""); }} data-testid="registration-category-select"><option value="">Select Event Category</option>{data?.categories.map((category) => <option key={category.id} value={category.id} label={category.name} />)}</select></label>
                <label className={`event-select-wrap ${effectiveCategory ? "visible" : ""}`}>Event *<select value={effectiveEvent} required disabled={!effectiveCategory || isLoading} onChange={(e) => setEventId(e.target.value)} data-testid="registration-event-select"><option value="">Choose an event</option>{filteredEvents.map((event) => <option key={event.id} value={event.id} label={`${event.name} – ${money(event.fee)}`} />)}</select></label>
              </div>
              {selectedEvent && <><div className="selected-event" data-testid="registration-event-details"><div><span>SELECTED EVENT</span><strong>{selectedEvent.name}</strong></div><div><span>FEE</span><strong>{money(selectedEvent.fee)}</strong></div><div><span>ENTRY</span><strong>{selectedEvent.registration_type.toUpperCase()}</strong></div></div><p className="affiliation-fee-note" data-testid="affiliation-fee-note">The displayed fee remains the same for SAGEian and Non-SAGEian registrations.</p></>}
              {selectedEvent?.registration_type === "team" && <div className="team-panel" data-testid="registration-team-panel"><div className="block-heading"><p className="eyebrow">TEAM DETAILS</p><h3>Register your team captain now</h3></div><div className="form-grid"><label>Team name *<input name="team_name" required placeholder="Your team name" data-testid="registration-team-input" /></label><label>Team members <small>Optional now</small><textarea name="team_members" placeholder="One member per line" data-testid="registration-team-members-input" /></label></div><p data-testid="registration-team-size">TEAM SIZE / {selectedEvent.min_team_size}–{selectedEvent.max_team_size} MEMBERS</p></div>}
            </section>
          </div>

          <aside className="registration-summary" data-testid="registration-fee-display"><div className="summary-title"><p className="eyebrow">REGISTRATION SUMMARY</p><span>● LIVE</span></div><div className="summary-price"><span>Entry fee</span><strong data-testid="registration-fee-value">{selectedEvent ? money(selectedEvent.fee) : "₹—"}</strong><small>Final amount is verified from the event database.</small></div><ul><li>✓ Secure server-side pricing</li><li>✓ Unique registration ID</li><li>✓ QR pass after confirmation</li></ul><label className="consent"><input type="checkbox" required data-testid="registration-terms-checkbox" /><span>I agree to the event rules, privacy policy and refund terms.</span></label>{mutation.isError && <p className="form-error" data-testid="registration-error">Registration could not be completed. Check your details and try again.</p>}<button className="button button-yellow full" disabled={mutation.isPending} type="submit" data-testid="registration-submit-button">{mutation.isPending ? "Submitting…" : "Continue to payment ↗"}</button><p className="support-note">NEED HELP? CONTACT THE EUPHORIA DESK</p></aside>
        </form>
      </main>
    </div>
  );
}