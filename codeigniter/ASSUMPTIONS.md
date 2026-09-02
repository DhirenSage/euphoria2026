# EUPHORIA 2026 assumptions

- The authoritative deliverable is CodeIgniter 4 on PHP 8.2+ with MySQL 8/InnoDB, HTTPS, and private writable storage. The Emergent public preview is not the PHP runtime.
- EUPHORIA 2026 is the first programme. Categories, events, days, gates, registrations, payments, passes, and attendance retain programme/event relationships for future programmes.
- Event passes are event-specific in V1. One participant may hold multiple independent event registrations, payments, QR tokens, and attendance histories.
- A confirmed QR permits one entry per configured active event day. Production rejects off-date scanning; `SCANNER_ALLOW_OFFDATE` exists only for non-production acceptance testing.
- Easebuzz `productinfo` is exactly `euphoria2026`. Browser redirects never confirm payments; only a verified callback/status result or an audited Finance/Super Admin manual verification can confirm them.
- The signed callback fixture is non-production only, requires an authenticated admin session, and returns 404 in production.
- Google Workspace SMTP uses STARTTLS on port 587. Confirmation queues one idempotent pass email; workers run outside the payment callback request.
- Core participant fields are always collected. Event-specific fields are admin-configured; uploads accept only JPG, PNG, or PDF files up to 5 MB in private storage.
- Camera scanning uses browser `BarcodeDetector` where available and always retains manual secure-token fallback.
- Demo credentials and fictional seed data are development-only and must be removed before production.