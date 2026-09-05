# EUPHORIA 2026 — cPanel Single-Folder Live Deployment

**Target:** `https://sageuniversity.in/euphoria/`  
**Hosting:** cPanel File Manager + phpMyAdmin, no SSH/Terminal/Composer  
**Runtime:** PHP 8.2 + MySQL 8-compatible InnoDB + Apache `mod_rewrite`

This is the primary deployment method requested for the prepared release. The complete application is extracted into `/public_html/euphoria`; a hardened root `.htaccess` denies direct web access to `app`, `vendor`, `writable`, `.env`, Composer files, and other internals. The safer split-directory method is still available in [`CPANEL_LIVE_DEPLOYMENT.md`](CPANEL_LIVE_DEPLOYMENT.md).

> This package is the CodeIgniter/MySQL application. The React/FastAPI preview is not uploaded to cPanel.

## 1. Files supplied

Use these release artifacts:

```text
euphoria-cpanel-single-folder.zip   Upload and extract in /public_html/euphoria
euphoria_initial.sql               Import with phpMyAdmin into an empty database
```

The ZIP includes `vendor/`; Composer is not needed on cPanel. It intentionally excludes `.env`, tests, development dependencies, logs, sessions, caches, generated passes, and uploads.

After extraction, the structure must be exactly:

```text
/home/CPANEL_USER/public_html/euphoria/
├── .htaccess
├── index.php
├── app/
├── vendor/
├── writable/
├── css/
├── js/
├── spark
├── composer.json
├── composer.lock
├── env.production.example
└── preflight.php
```

There must not be an extra level such as `/euphoria/euphoria-cpanel-single-folder/app`.

## 2. Back up the existing website

Before changing anything:

1. In File Manager, compress and download the current `/public_html/euphoria` directory if it exists.
2. In phpMyAdmin, export the current Euphoria database with structure and data.
3. Record the active database name/user and current callback URLs.
4. Use a maintenance window; do not overwrite a database that already contains real payments or registrations.

## 3. Select PHP 8.2 and extensions

In **MultiPHP Manager** or **Select PHP Version**, assign PHP 8.2 or newer to `sageuniversity.in` and enable:

```text
curl  dom  fileinfo  gd  intl  mbstring  mysqli  openssl  simplexml  zip
```

Recommended PHP limits:

```text
memory_limit = 512M
upload_max_filesize = 8M
post_max_size = 10M
max_execution_time = 120
```

Ask the host to confirm Apache `mod_rewrite` and `.htaccess` overrides are enabled.

## 4. Create MySQL database and user

In **cPanel → MySQL Databases**:

1. Create a database, for example `CPANEL_USER_euphoria`.
2. Create a separate user, for example `CPANEL_USER_euphoria_user`.
3. Generate a strong unique password.
4. Add that user to the database with **ALL PRIVILEGES**.
5. Keep the full cPanel-prefixed names; entering only `euphoria` is a common error.

## 5. Import the ready SQL

1. Open **phpMyAdmin** and select the new empty database.
2. Open **Import**.
3. Select `euphoria_initial.sql`.
4. Keep format **SQL** and character set **utf-8**.
5. Start the import and wait for the green success message.
6. Do not upload the SQL file into `public_html`.

Confirm at least these tables exist:

```text
migrations, users, roles, user_roles, programmes, categories, events,
event_days, registration_fields, registrations, payments, qr_tokens, media_items,
attendance, scan_attempts, gates, scanner_assignments, email_jobs,
email_logs, audit_logs
```

The SQL contains development demo accounts and fictional catalogue data. Account credentials must be changed before launch (section 10).

## 6. Upload the application ZIP

1. Open **File Manager → Settings** and enable **Show Hidden Files**.
2. Go to `/home/CPANEL_USER/public_html`.
3. Create folder `euphoria`.
4. Upload `euphoria-cpanel-single-folder.zip` inside it.
5. Extract the ZIP in that folder.
6. Confirm `app`, `vendor`, `writable`, `index.php`, and `.htaccess` are directly inside `/euphoria`.
7. Delete the uploaded ZIP from the server.

Do not use CodeIgniter's original `public/index.php` at the package root. The release already supplies the single-folder front controller.

## 7. Create production `.env`

Inside `/public_html/euphoria`:

1. Copy `env.production.example`.
2. Rename the copy to exactly `.env`.
3. Edit every `REPLACE_...` and `CPANEL_USER_...` placeholder.
4. Keep quotes around values containing spaces or special characters.
5. Set `.env` permission to `600` when supported, otherwise the most restrictive readable setting.

Required values:

```dotenv
CI_ENVIRONMENT = production
app.baseURL = 'https://sageuniversity.in/euphoria/'
app.indexPage = ''
app.appTimezone = 'Asia/Kolkata'
app.forceGlobalSecureRequests = true

database.default.hostname = localhost
database.default.database = CPANEL_USER_euphoria
database.default.username = CPANEL_USER_euphoria_user
database.default.password = REPLACE_WITH_STRONG_DATABASE_PASSWORD
database.default.DBDriver = MySQLi
database.default.port = 3306
database.default.DBDebug = false

cookie.secure = true
cookie.httponly = true
cookie.samesite = Lax

EASEBUZZ_ENV = prod
PAYMENT_MODE = gateway
EASEBUZZ_PRODUCTINFO = euphoria2026
EASEBUZZ_ALLOW_SIGNED_CALLBACK_TEST = false
SCANNER_ALLOW_OFFDATE = false
```

Generate the encryption key on any trusted computer with PHP 8.2:

```bash
php -r "echo bin2hex(random_bytes(32)), PHP_EOL;"
```

Then set:

```dotenv
encryption.key = hex2bin:PASTE_THE_64_HEX_CHARACTERS
```

Never reuse a preview key or place real database, payment, SMTP, or encryption secrets in Git/chat/documentation.

Live Easebuzz and Google Workspace credentials must remain only in this cPanel `.env`. Do not paste them into controllers, services, JavaScript, SQL, GitHub, or the ZIP. The temporary preflight page reports only whether required values are configured; it never displays the values.

## 8. Verify the security blocks before login

Open these URLs. Every one must return **403 Forbidden** (404 is also acceptable), never file contents:

```text
https://sageuniversity.in/euphoria/.env
https://sageuniversity.in/euphoria/composer.json
https://sageuniversity.in/euphoria/spark
https://sageuniversity.in/euphoria/app/Config/Database.php
https://sageuniversity.in/euphoria/vendor/autoload.php
https://sageuniversity.in/euphoria/writable/logs/
```

If any file is readable, stop deployment. Confirm `.htaccess` was uploaded, `mod_rewrite` is enabled, and `AllowOverride` is permitted. The single-folder layout must not run without these protections.

## 9. Run and delete the preflight checker

Open:

```text
https://sageuniversity.in/euphoria/preflight.php
```

Resolve every FAIL, then **delete `preflight.php` immediately**. It checks PHP, extensions, dependencies, `.env`, and writable paths without displaying secrets.

Permissions:

```text
Directories: 755
Files:       644
.env:        600 when supported
writable/:   755 or 775, depending on PHP ownership
```

Ensure these are writable by PHP: `writable/cache`, `logs`, `session`, `uploads`, `uploads/media`, and `passes`. Do not leave any path at `777`.

### Dynamic Gallery & Video

After Admin login, open **Gallery & video**. Admin/Content Manager can upload JPG/PNG/WEBP images or add YouTube, Vimeo, MP4, and WEBM URLs; each item has a homepage section, caption, optional event, display order, and active switch. Uploaded images are stored under protected `writable/uploads/media` and served through the controlled `/media/file/{id}` route.

### Bulk complimentary passes

Open **Bulk passes**, download the template, and upload a `.csv` or `.xlsx` list with `participant_name`, `mobile`, `institute_name`, `email`, and `event_name` (or safer `event_slug`). Valid rows are confirmed as complimentary, receive individual QR passes, and enter the email queue. The one-minute cron in section 13 is required for delivery.

### Admin navigation and permanent deletion

Admin modules are separate routes, so opening Events, Participants, Attendance, Payments, Entry Tracking, Media, Bulk Passes, or Scanner Users loads only that module's data. The Events page is searchable, filterable, paginated, and supports checkbox bulk cleanup.

`Permanent Delete` is SUPER ADMIN only. A single deletion requires typing the exact event name; bulk deletion requires `DELETE SELECTED`. It irreversibly removes the event's registrations, payment records, QR/pass data, attendance, scan attempts, queued email records, schedules, custom fields, event media links, and stored pass/media files. Export/backup MySQL before using it on production data.

### SAGEian / Non-SAGEian event pricing

Each event has separate **SAGEian fee** and **Non-SAGEian fee** fields. Existing fee values are copied into both fields by migration 000006. Event-specific registration URLs lock the event/category; selecting affiliation updates the visible amount, while the server independently recalculates the authoritative payment amount before creating the registration.

### Mobile layouts

Public, Registration, Pass, Scanner, Admin, Reports, Media and authentication pages are responsive. On mobile, Admin uses a sticky top header with horizontally scrollable module tabs; tables scroll horizontally and forms/cards collapse to one column.

## 10. Replace demo accounts before launch

The import contains first-login development accounts documented in the project README. Generate new password hashes on a trusted PHP 8.2 computer:

```bash
php -r "echo password_hash('YOUR-NEW-ADMIN-PASSWORD', PASSWORD_DEFAULT), PHP_EOL;"
php -r "echo password_hash('YOUR-NEW-SCANNER-PASSWORD', PASSWORD_DEFAULT), PHP_EOL;"
```

In phpMyAdmin, replace emails and hashes:

```sql
UPDATE users
SET email='your-admin@sageuniversity.in', password_hash='PASTE_ADMIN_HASH', updated_at=NOW()
WHERE email='admin@euphoria.test';

UPDATE users
SET email='gate1@sageuniversity.in', password_hash='PASTE_SCANNER_HASH', updated_at=NOW()
WHERE email='scanner@euphoria.test';
```

Use unique passwords of at least 14 characters. Keep role mappings unchanged.

## 11. Configure Easebuzz

Put the live key/salt only in `.env`:

```dotenv
EASEBUZZ_ENV = prod
EASEBUZZ_KEY = REPLACE_WITH_LIVE_EASEBUZZ_KEY
EASEBUZZ_SALT = REPLACE_WITH_LIVE_EASEBUZZ_SALT
PAYMENT_MODE = gateway
EASEBUZZ_TIMEOUT = 20
EASEBUZZ_PRODUCTINFO = euphoria2026
EASEBUZZ_ALLOW_SIGNED_CALLBACK_TEST = false
```

Register this HTTPS callback/success/failure URL with Easebuzz:

```text
https://sageuniversity.in/euphoria/payments/easebuzz/callback
```

The product info must remain exactly `euphoria2026`. Browser redirection alone does not confirm payment; the server verifies callback signature, transaction, product, and amount. Use the provider-approved sandbox/test process first, then a controlled low-value live payment only after domain approval.

## 12. Configure Google Workspace SMTP

Use a Google **App Password**, not the mailbox password:

```dotenv
email.protocol = smtp
email.SMTPHost = smtp.gmail.com
email.SMTPUser = registrations@sageuniversity.in
email.SMTPPass = REPLACE_WITH_GOOGLE_APP_PASSWORD
email.SMTPPort = 587
email.SMTPCrypto = tls
email.fromEmail = registrations@sageuniversity.in
email.fromName = 'SAGE EUPHORIA Registrations'
```

University IT should verify two-step verification, SMTP authentication, SPF, DKIM, DMARC, spam, and quarantine. SMTP acceptance alone does not prove inbox delivery.

## 13. Queue email with cPanel Cron Jobs

Terminal is not required if cPanel provides **Cron Jobs**. Ask the host for the exact PHP 8.2 CLI path, then run once per minute:

```cron
* * * * * /opt/cpanel/ea-php82/root/usr/bin/php /home/CPANEL_USER/public_html/euphoria/spark queue:work --once >> /home/CPANEL_USER/public_html/euphoria/writable/logs/queue-cron.log 2>&1
```

Possible PHP paths include `/usr/local/bin/php`, `/usr/bin/php`, and `/opt/cpanel/ea-php82/root/usr/bin/php`.

If the account has neither Cron Jobs nor host-managed PHP CLI, queued pass email is **not operational**. Registrations/payments may still complete, but email jobs remain pending. Ask the hosting provider to enable cron/CLI or move to hosting that supports workers; do not claim email delivery is live until `email_jobs.status` becomes `sent` and the email reaches the mailbox.

## 14. First launch and route check

Open in this order:

```text
https://sageuniversity.in/euphoria/
https://sageuniversity.in/euphoria/events
https://sageuniversity.in/euphoria/registration
https://sageuniversity.in/euphoria/admin/login
https://sageuniversity.in/euphoria/scanner/login
```

If home works but inner routes return 404, check `.htaccess`, `mod_rewrite`, `AllowOverride`, `RewriteBase /euphoria/`, and the trailing slash in `app.baseURL`.

If pages return 500, inspect `/public_html/euphoria/writable/logs/`. Temporarily use `CI_ENVIRONMENT = development` only during private diagnosis, then restore `production` immediately.

## 15. End-to-end production acceptance

Do not announce the site until this real flow passes:

1. Admin logs in and creates/edits a category and event.
2. The published event and database-owned fee appear publicly.
3. A free registration confirms without opening payment.
4. A paid registration opens hosted Easebuzz checkout.
5. Browser redirect alone leaves payment pending; valid callback confirms it.
6. Registration ID, QR, digital pass, and one-page PDF are generated.
7. Cron changes the pass email job from `pending` to `sent`; the complete PDF arrives.
8. Any active Scanner logs in over HTTPS and immediately sees camera/manual token input—there is no event, day, assignment, or gate selection.
9. Before the event date, the scanner shows participant/event/date/time/venue with “UPCOMING EVENT — ENTRY NOT OPEN” and saves no attendance. On the configured date, the QR automatically resolves its event/day, first scan is allowed, and same QR/day is rejected as duplicate.
10. The same QR on a second configured event day is allowed.
11. Before-date, expired, unpaid, invalid, and revoked passes are denied; a multi-day pass is allowed once on each configured date.
12. Dashboard totals and CSV attendance export contain the entry.

## 16. Production checklist

- [ ] AutoSSL is active and HTTP redirects to HTTPS
- [ ] `CI_ENVIRONMENT=production` and `database.default.DBDebug=false`
- [ ] `.env`, `app`, `vendor`, `writable`, `spark`, and Composer files are blocked over HTTP
- [ ] ZIP, SQL, and `preflight.php` were deleted from `public_html`
- [ ] Database user is dedicated and least-exposure
- [ ] Demo emails/passwords were changed
- [ ] Easebuzz test callback flag and scanner off-date flag are false
- [ ] Live callback URL is approved and signature verification tested
- [ ] SMTP plus cron delivery is proven in `email_jobs`/`email_logs`
- [ ] Writable permissions work without `777`
- [ ] Admin and Scanner links remain absent from public navigation
- [ ] Homepage and Gallery show only active, ordered Admin media; image upload and video playback were checked
- [ ] CSV and XLSX complimentary-pass imports create QR passes and queue participant emails
- [ ] Database/files backups and rollback copy exist

## 17. Backups, updates, and rollback without SSH

Before every update, export MySQL from phpMyAdmin and download `.env`, uploads, and the current application ZIP. Build the next release locally with dependencies, test against a database copy, and import only the required schema changes during a maintenance window.

Rollback application files from the previous ZIP. Restore an older database only when the matching schema requires it and after reconciling any newer registrations/payments; never overwrite live paid transactions blindly.

For long-term production maintenance, request SSH/Terminal access even though the initial package does not require it.

## 18. Common failures

| Symptom | Check |
|---|---|
| 403 on the whole site | Root `.htaccess` syntax/host compatibility; ask host to inspect Apache error log |
| 404 on inner routes | `mod_rewrite`, `AllowOverride`, `RewriteBase /euphoria/`, hidden `.htaccess` upload |
| 500 on every page | PHP extensions, `vendor/autoload.php`, `.env` syntax, writable permissions/logs |
| Database connection error | Full cPanel-prefixed DB/user, assigned privileges, password quoting, hostname |
| CSS/JS missing | `css` and `js` must be directly under `/euphoria`; exact base URL with trailing slash |
| Camera unavailable | HTTPS, browser permission, supported device; use image/manual-token fallback |
| Payment pending | Approved callback URL, environment/key/salt pair, amount/product/transaction match |
| Email pending | Cron/PHP CLI path, SMTP App Password/Workspace policy, `email_jobs` and logs |

## 19. Live URLs

```text
Public:       https://sageuniversity.in/euphoria/
Events:       https://sageuniversity.in/euphoria/events
Registration: https://sageuniversity.in/euphoria/registration
Admin:        https://sageuniversity.in/euphoria/admin/login
Scanner:      https://sageuniversity.in/euphoria/scanner/login
Callback:     https://sageuniversity.in/euphoria/payments/easebuzz/callback
```

The deployment is not proven live until the actual cPanel host passes the security URLs and complete acceptance flow above.