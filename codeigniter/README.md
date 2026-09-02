# SAGE University Indore — EUPHORIA 2026

CodeIgniter 4 + PHP 8.2 foundation for a reusable multi-programme event platform.

For complete Windows (Laragon/XAMPP), cPanel Terminal, cPanel File Manager-only, credential, integration, event-publishing, queue, security, and troubleshooting instructions, read [`LOCAL_AND_CPANEL_SETUP.md`](LOCAL_AND_CPANEL_SETUP.md).

The public `/registration` route is the shared Euphoria 2K26 form. Its category/event dropdowns are populated from MySQL, and event prices are never accepted from browser input; `RegistrationController` validates the selected category/event pair and `RegistrationService` reads the amount from the authoritative event row.

## Local setup

```bash
cp env .env
# set a MySQL 8 database and credentials in .env
composer install
php spark migrate
php spark db:seed DatabaseSeeder
php spark serve --host 0.0.0.0 --port 8080
```

Demo accounts seeded by `DatabaseSeeder`:

- **Admin:** `admin@euphoria.test` / `EuphoriaDemo!2026`
- **Scanner:** `scanner@euphoria.test` / `ScannerDemo!2026`

These credentials are fictional development-only accounts. Never seed them in production.

## Architecture

- `app/Database/Migrations` contains normalized programme, category, event, registration, payment, QR, gate, attendance, RBAC, settings and audit tables.
- `app/Services/RegistrationService.php` owns capacity checks, configurable registration IDs, secure random QR tokens and free/paid status transitions.
- `app/Services/AttendanceService.php` checks QR status, event ownership, payment/registration confirmation and the unique `(registration_id,event_day_id)` database constraint.
- `app/Services/Payment/EasebuzzGateway.php` implements `PaymentGatewayInterface`; Easebuzz signing and reconciliation remain isolated from controllers.
- `app/Services/PassService.php` generates a server-side QR image and PDF pass. Store generated files under `writable/passes`, never the public root.
- `app/Services/AuditService.php` records critical operations. Extend it in controllers/jobs for every sensitive admin action.
- `app/Filters` contains session authentication and role checks. Add granular permission rows before exposing new modules.

## Easebuzz and SMTP

Obtain the merchant key/salt from the Easebuzz dashboard and set them only in `.env` or the deployment secret store:

```dotenv
EASEBUZZ_ENV=test
EASEBUZZ_KEY=your-merchant-key
EASEBUZZ_SALT=your-merchant-salt
PAYMENT_MODE=gateway
email.SMTPHost=smtp.example.com
email.SMTPUser=...
email.SMTPPass=...
email.SMTPPort=587
email.SMTPCrypto=tls
email.fromEmail=noreply@example.com
```

Keep the test and production credentials separate. Configure the Easebuzz success/failure callback to `/payments/easebuzz/callback`. The callback must be reachable over HTTPS in production.

For local acceptance testing only, set `EASEBUZZ_ALLOW_SIGNED_CALLBACK_TEST=true` in a development environment. A signed fixture can then be submitted by a logged-in Super Admin to `/admin/dev/easebuzz/callback-test`. The route returns 404 in production and must never replace gateway reconciliation.

Google Workspace SMTP uses `smtp.gmail.com`, port `587`, and `tls`, with an app password. Start the durable worker with `php spark queue:work`; verify a mailbox with `php spark emails:test recipient@example.com`. Never enable SMTP debug output in production.

## Deployment

1. Provision PHP 8.2+ with `intl`, `mbstring`, `curl`, `gd`, `dom`, `zip`, `mysqli` and Composer.
2. Create a least-privilege MySQL user, create the database, copy `env` to `.env`, and set a cryptographically random `app.encryptionKey`.
3. Run `composer install --no-dev --classmap-authoritative`, `php spark migrate --all`, and `php spark cache:clear`.
4. Point Apache/Nginx document root to `/path/to/codeigniter/public`; never expose `.env`, `writable/passes`, or `writable/uploads`.
5. Set `writable` ownership to the PHP-FPM user and restrict uploaded files by server MIME validation, size limits and non-executable permissions.
6. Force HTTPS, secure cookies, CSRF protection and a rate limit on login, registration, callback and scanner endpoints.
7. Run `php spark queue:work` under Supervisor/systemd. The database-backed worker uses row locking, retry/backoff, PDF attachments, delivery logs, and a unique registration/template job key.
8. Schedule payment reconciliation for `pending`/`unknown` records and reminder jobs through the host cron calling a CI4 command.

Reference virtual-host and worker configurations live in `deploy/apache-euphoria.conf`, `deploy/nginx-euphoria.conf`, and `deploy/supervisor-euphoria-worker.conf`. Read `ASSUMPTIONS.md` before changing event-day, payment, or pass rules.

## Tests

```bash
vendor/bin/phpunit
```

The PHPUnit suite protects security/schema contracts. Final acceptance also exercises the real browser journey against a migrated MySQL database: admin event creation, paid registration, signed callback verification, pass/QR rendering, scanner authorization, same-day duplicate denial, next-day allowance, dashboard totals, and CSV export.

Emergent does not provide managed MySQL. The public preview uses pod-local MariaDB only for evaluation; production must supply an external managed MySQL 8 host through `.env`. `deploy/supervisor-codeigniter.conf` runs the PHP web process separately on a conventional Linux host. The Node wrapper under `frontend/scripts` exists only because this preview's read-only Supervisor exposes `yarn dev` as its port-3000 entrypoint.

The preview pod is still managed by a read-only React/FastAPI Supervisor configuration, so this CodeIgniter tree is the deployment-ready source and is run with `php spark serve` or a PHP-FPM/Apache/Nginx host.