# EUPHORIA 2026 living spec

## Product
CodeIgniter 4 + PHP 8.2 source for SAGE University Indore's reusable multi-programme event platform. The current programme is EUPHORIA 2026.

The public Emergent preview uses the supported Vite/React + FastAPI/Mongo runtime as a durable companion because the host does not preserve PHP/MySQL packages. The CodeIgniter source remains under `/app/codeigniter` with matching registration logic and deployment files for a PHP 8.2 + external MySQL host.

## Current flow
Public visitor browses database-driven programme categories and events → submits core plus event-configured fields → receives an atomic unique registration ID → free events confirm immediately and paid events remain `pending_payment` until server-side Easebuzz reverse-hash, key, product, transaction and amount verification → confirmed registrations receive a secure emailed pass link, QR pass and PDF. Authorized staff use the separate scanner login, select only permitted event/day/gate assignments, then scan by camera or manual token. Attendance uses a database unique key `(event_id, registration_id, event_day_id)` plus attempt logs, so one day allows one entry while the same QR remains eligible on another configured day.

The shared `/registration` form now loads exactly four registration categories and their approved event/fee catalogue from MySQL: Cultural (10), Literary and Management (4), Sci-Pha-Agro (3), and Sports (15). Event-specific registration URLs reuse the same form with the event preselected. Category changes clear the previous event; server validation confirms the event belongs to the chosen category and always calculates payment from `events.fee`. Core participant data includes name, optional father name, email, mobile, optional age, school/college, optional city, and required SAGEian/Non-SAGEian affiliation. Team events derive team status and configured min/max sizes from the event record.

The active public preview now provides a real database-connected operations flow rather than demo screens. Separate `/admin/login` and `/scanner/login` routes use HTTP-only Mongo-backed sessions and role checks. Admin can create, edit, price, publish, close, or delete/cancel events; every published change feeds the public catalogue and registration pricing. New events are assigned to the development scanner account automatically.

Every registration receives a random pass-access key and encrypted unpredictable QR token. Free registrations activate immediately; paid registrations activate only after verified Easebuzz callback or an audited Admin complimentary/manual confirmation. `/pass/{registration-id}` renders the real QR from the protected pass API. Scanner camera decoding uses `html5-qrcode`, with QR-image upload and manual token fallbacks. The scan API checks role, assignment, event, configured day, payment, registration, and QR status before an atomic unique attendance insert; duplicate and denied attempts feed the Admin dashboard.

Operations now include role-based staff accounts (`admin`, `event_admin`, `finance`, `scanner`, `report_viewer`), active/deactivated state, and event/day/gate scanner assignments enforced by the scan API. Finance users can filter payment states, review masked participant/payment data, initiate a fresh Easebuzz retry transaction, or manually verify with a mandatory reference and reason; every override is audited. Participant controls cover profile correction, cancellation/restoration, immediate QR revoke/restore, attendance history, and real SMTP pass resend with a rotated secure pass-access key.

The scanner includes success/error sound, vibration, camera torch capability checks, and fullscreen controls. Hardware-dependent controls degrade to clear fallback messages while QR image upload and manual token verification remain available.

Digital pass delivery uses one cohesive colourful youth-festival landscape design across web, Download PDF, Print and email attachment. The server PDF is a single custom landscape page matching the compact web card: white official-logo header, pink-purple event hero, dark participant/details panel, large unobstructed black-on-white QR stub, enlarged print-viewer-safe event/participant/detail typography, payment/pass state, date/time, venue, institution and three short gate instructions. “Print same design” opens this exact inline server PDF instead of printing the HTML page, avoiding faded backgrounds, broken two-page layouts and browser URL content; the UI also reminds users to disable browser “Headers and footers.” Pass resend sends a branded HTML email with this complete PDF, never a QR-only PNG.

Every event card links to `/events/{event-slug}`. Event records include a banner, full description, date/time, deadline, venue, eligibility, fee, capacity, registration/team configuration, schedule, rules, prizes, and coordinator details. The detail-page Register Now CTA opens the shared registration form with that event preselected.

## Roles
`SUPER_ADMIN`, `PROGRAMME_ADMIN`, `EVENT_ADMIN`, `FINANCE`, `SCANNER`, `CONTENT_MANAGER`, `REPORT_VIEWER`. Authentication uses bcrypt-compatible password hashes, regenerated HTTP-only sessions, an eight-hour idle limit, five-attempt login throttling, portal-specific role checks, separate `/admin/login` and `/scanner/login`, CSRF-protected mutations, and POST-only logout.

Admin and Scanner access are intentionally absent from all public navigation. Authorized staff use the direct `/admin/login` and `/scanner/login` URLs.

## Data model
Programme → Categories → Events → active/historical event days and dynamic registration fields → registrations → field values, members, payments, revocable QR tokens, attendance and scan attempts. Registration sequences generate concurrency-safe IDs. Gates belong to programmes. Users map to roles and scanner assignments. Settings, email outbox/logs, payment transactions and audit logs support operations and compliance.

## Integrations
Easebuzz is isolated behind `PaymentGatewayInterface`. Production initiation uses the selected active merchant pair; the other pair remains an inactive backup. Callback verification selects salt by callback key and checks the exact stored transaction, `euphoria2026` product, and amount before an idempotent database-locked confirmation. A signed callback fixture exists only when the development-only environment flag is enabled and is Super-Admin protected.

SMTP is configured for the supplied Google Workspace mailbox through environment-only credentials. Confirmed registrations enqueue one idempotent pass-email job with secure digital link and generated PDF attachment. `php spark queue:work` performs delivery with retry/backoff and email logs; `php spark emails:test` verifies provider acceptance.

Easebuzz `productinfo` is the merchant-approved alphanumeric value `euphoria2026` in both payment implementations and is included unchanged in SHA-512 request/callback verification. Registration affiliation is presentation-only for current pricing: switching between SAGEian and Non-SAGEian never clears the selected event or changes/hides its server-owned fee.

Payment initiation is a two-step server flow: the backend posts the signed payload to Easebuzz `payment/initiateLink`, validates the returned status/access key, stores a fresh retry-safe transaction ID, and returns only `checkout_url=https://pay.easebuzz.in/pay/{access_key}` to the browser. The participant button pre-opens a new tab and navigates that tab to hosted checkout; it never opens the raw JSON initiation endpoint.

The registration confirmation card renders the authoritative server amount in a dedicated high-contrast yellow cell with a large responsive value and `confirmation-server-amount` test identifier.

## Demo credentials
See `memory/test_credentials.md`. Remove seeded demo accounts before production.