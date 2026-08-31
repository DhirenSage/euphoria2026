# EUPHORIA platform assumptions

- The authoritative application is CodeIgniter 4 on PHP 8.2 with MySQL 8-compatible InnoDB. The existing React/FastAPI skeleton remains separate because its supervisor entrypoint is read-only in this pod.
- Easebuzz credentials are intentionally not stored in source. Production operators add `EASEBUZZ_KEY`, `EASEBUZZ_SALT`, `EASEBUZZ_ENV` and `PAYMENT_MODE=gateway` to the host environment. The admin settings screen explains this state instead of exposing secrets.
- Payment callbacks are accepted only after reverse-hash verification. The client redirect is never treated as payment proof. The gateway adapter is ready, but no live credential is present in this workspace.
- SMTP, PDF and QR service boundaries are implemented. A production queue worker should connect the command to the selected queue backend and Supervisor; a pass PDF is generated outside the public web root.
- The demo seeder is development-only and uses fictional credentials and fictional participant data. Disable or remove demo seeding before production.
- The first milestone includes the public programme/event journey, registration, confirmation/pass, admin operations and scanner attendance workflow. Advanced modules such as coupons, exports, speakers and certificate eligibility are represented by schema-ready boundaries but should be expanded in the next delivery phase.