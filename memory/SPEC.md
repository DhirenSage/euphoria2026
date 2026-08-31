# EUPHORIA 2026 living spec

## Product
CodeIgniter 4 + PHP 8.2 source for SAGE University Indore's reusable multi-programme event platform. The current programme is EUPHORIA 2026.

## Current flow
Public visitor browses programme categories and events → submits configurable registration fields → receives a unique registration ID → free events confirm immediately and paid events remain `pending_payment` until server-side Easebuzz callback verification → confirmed registrations can display a secure token-backed QR pass and PDF pass. Authorized staff sign in to scanner, select event/day/gate and validate a token. Attendance uses a database unique key per registration/day to prevent duplicates.

## Roles
`SUPER_ADMIN`, `PROGRAMME_ADMIN`, `EVENT_ADMIN`, `FINANCE`, `SCANNER`, `CONTENT_MANAGER`, `REPORT_VIEWER`. Authentication is session-based with password hashes; scanner/admin routes are protected by CodeIgniter filters.

## Data model
Programme → Categories → Events → Event days, registration fields, registrations → field values, members, payments, QR tokens, attendance. Gates belong to programmes. Users map to roles. Settings and audit logs support deployment configuration and compliance.

## Integrations
Easebuzz is isolated behind `PaymentGatewayInterface`; credentials are deployment secrets and absent from this workspace. SMTP/PDF/pass email is deployment-configured; QR/PDF generation is server-side. **MOCKED/UNAVAILABLE:** no live Easebuzz or SMTP credentials were provided, so live gateway callbacks and email delivery are not enabled in this preview source.

## Demo credentials
See `memory/test_credentials.md`. Remove seeded demo accounts before production.