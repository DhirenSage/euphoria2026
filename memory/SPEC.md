# EUPHORIA 2026 living spec

## Product
CodeIgniter 4 + PHP 8.2 source for SAGE University Indore's reusable multi-programme event platform. The current programme is EUPHORIA 2026.

The public Emergent preview uses the supported Vite/React + FastAPI/Mongo runtime as a durable companion because the host does not preserve PHP/MySQL packages. The CodeIgniter source remains under `/app/codeigniter` with matching registration logic and deployment files for a PHP 8.2 + external MySQL host.

## Current flow
Public visitor browses programme categories and events → submits configurable registration fields → receives a unique registration ID → free events confirm immediately and paid events remain `pending_payment` until server-side Easebuzz callback verification → confirmed registrations can display a secure token-backed QR pass and PDF pass. Authorized staff sign in to scanner, select event/day/gate and validate a token. Attendance uses a database unique key per registration/day to prevent duplicates.

The shared `/registration` form now loads exactly four registration categories and their approved event/fee catalogue from MySQL: Cultural (10), Literary and Management (4), Sci-Pha-Agro (3), and Sports (15). Event-specific registration URLs reuse the same form with the event preselected. Category changes clear the previous event; server validation confirms the event belongs to the chosen category and always calculates payment from `events.fee`. Core participant data includes name, optional father name, email, mobile, optional age, school/college, optional city, and required SAGEian/Non-SAGEian affiliation. Team events derive team status and configured min/max sizes from the event record.

The public preview mirrors that 32-event catalogue in Mongo and offers the same server-owned pricing contract through `/api/registration-catalogue`, `/api/registrations`, and `/api/registrations/{id}/payment`. The responsive UI uses the supplied official SAGE University Indore and EUPHORIA logo assets across public, registration, operations, scanner, pass, PDF, and email surfaces.

## Roles
`SUPER_ADMIN`, `PROGRAMME_ADMIN`, `EVENT_ADMIN`, `FINANCE`, `SCANNER`, `CONTENT_MANAGER`, `REPORT_VIEWER`. Authentication is session-based with password hashes; scanner/admin routes are protected by CodeIgniter filters.

## Data model
Programme → Categories → Events → Event days, registration fields, registrations → field values, members, payments, QR tokens, attendance. Gates belong to programmes. Users map to roles. Settings and audit logs support deployment configuration and compliance.

## Integrations
Easebuzz is isolated behind `PaymentGatewayInterface` in CodeIgniter and a matching server-side payment route in the preview API. Easebuzz production initiation is configured with the user-confirmed first merchant pair; the second pair is retained as inactive backup configuration. Payment success is accepted only through server-side callback signature verification. **UNAVAILABLE:** SMTP delivery remains disabled until SMTP credentials are provided.

Easebuzz `productinfo` is the merchant-approved alphanumeric value `euphoria2026` in both payment implementations and is included unchanged in SHA-512 request/callback verification. Registration affiliation is presentation-only for current pricing: switching between SAGEian and Non-SAGEian never clears the selected event or changes/hides its server-owned fee.

Payment initiation is a two-step server flow: the backend posts the signed payload to Easebuzz `payment/initiateLink`, validates the returned status/access key, stores a fresh retry-safe transaction ID, and returns only `checkout_url=https://pay.easebuzz.in/pay/{access_key}` to the browser. The participant button pre-opens a new tab and navigates that tab to hosted checkout; it never opens the raw JSON initiation endpoint.

The registration confirmation card renders the authoritative server amount in a dedicated high-contrast yellow cell with a large responsive value and `confirmation-server-amount` test identifier.

## Demo credentials
See `memory/test_credentials.md`. Remove seeded demo accounts before production.