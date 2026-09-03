# EUPHORIA 2026 — cPanel Split-Directory Deployment (Alternative)

**Production URL:** `https://sageuniversity.in/euphoria/`  
**Application:** CodeIgniter 4 + PHP 8.2 + MySQL  
**Hosting access:** cPanel File Manager + phpMyAdmin, without SSH/Terminal  
**Web server:** Apache with `.htaccess`

This is the safer alternative layout that keeps source outside `public_html`. The primary guide requested for a single `/public_html/euphoria` upload is [`CPANEL_SINGLE_FOLDER_DEPLOYMENT.md`](CPANEL_SINGLE_FOLDER_DEPLOYMENT.md). Do not upload the FastAPI/React preview source to standard PHP cPanel hosting.

---

## 1. Production folder architecture

Keep application code and secrets outside `public_html`.

```text
/home/CPANEL_USER/
├── euphoria_app/                    PRIVATE — never web-accessible
│   ├── app/
│   ├── vendor/
│   ├── writable/
│   ├── spark
│   ├── composer.json
│   ├── composer.lock
│   └── .env
└── public_html/
    └── euphoria/                    PUBLIC URL /euphoria
        ├── index.php
        ├── .htaccess
        ├── css/
        ├── js/
        └── favicon.ico (optional)
```

Replace `CPANEL_USER` everywhere with the username displayed in cPanel File Manager, for example `/home/sageuser/`.

Never place `.env`, `app`, `vendor`, `writable`, SQL backups, merchant salts, or SMTP passwords inside `public_html`.

---

## 2. Prepare the package on Windows before uploading

Because the cPanel account has no Terminal/Composer, dependencies and the initial SQL database must be prepared locally.

### 2.1 Required local software

Use Laragon or XAMPP with:

- PHP 8.2 or newer
- MySQL/MariaDB
- Composer 2
- PHP extensions: `curl`, `dom`, `fileinfo`, `gd`, `intl`, `mbstring`, `mysqli`, `openssl`, `zip`

### 2.2 Install production dependencies locally

Open Command Prompt or Laragon Terminal:

```bat
cd C:\laragon\www\euphoria
composer install --no-dev --optimize-autoloader
```

Confirm this file exists afterward:

```text
vendor/autoload.php
```

The `vendor` directory must be included in the upload ZIP. A GitHub clone normally excludes it.

### 2.3 Build a clean local database

Create a clean database named `euphoria_release`, configure the local `.env`, then run:

```bat
php spark migrate --all
php spark db:seed DatabaseSeeder
php spark migrate:status
```

All migrations must show as applied.

### 2.4 Export the initial SQL with phpMyAdmin

1. Open local phpMyAdmin.
2. Select `euphoria_release`.
3. Choose **Export → Custom**.
4. Select every table.
5. Format: **SQL**.
6. Include structure and data.
7. Enable `DROP TABLE / VIEW / PROCEDURE / FUNCTION / EVENT` only for the first clean installation file.
8. Include `AUTO_INCREMENT`, indexes, foreign keys, and `SET FOREIGN_KEY_CHECKS` statements.
9. Compression: **gzip** if the file is large.
10. Save as `euphoria_initial.sql` or `euphoria_initial.sql.gz`.

Do not place this SQL file in the public web directory.

### 2.5 Create two ZIP files

#### Private application ZIP

Create `euphoria_app.zip` containing the contents of the CodeIgniter project except:

```text
public/
.env
tests/
writable/logs/*
writable/session/*
writable/cache/*
```

It must include:

```text
app/
vendor/
writable/
spark
composer.json
composer.lock
```

#### Public web ZIP

Create `euphoria_public.zip` from the contents of `public/`:

```text
css/
js/
index.php (replace during deployment)
.htaccess (replace during deployment)
```

In Windows Explorer, enable **View → Hidden items** so `.htaccess` is included.

---

## 3. cPanel server capability check

In **Select PHP Version** or **MultiPHP Manager**:

1. Assign PHP 8.2 or newer to `sageuniversity.in`.
2. Enable `curl`, `dom`, `fileinfo`, `gd`, `intl`, `mbstring`, `mysqli`, `openssl`, and `zip`.
3. Set `memory_limit` to at least `256M`; `512M` is preferred for PDF generation.
4. Set `upload_max_filesize=8M` or greater.
5. Set `post_max_size=10M` or greater.
6. Set `max_execution_time=120`.
7. Confirm Apache `mod_rewrite` and `AllowOverride` are enabled with the hosting provider.

### Optional temporary preflight

1. Copy `deploy/cpanel-preflight.php` to `public_html/euphoria/preflight.php`.
2. Replace `CPANEL_USER` inside it.
3. Open `https://sageuniversity.in/euphoria/preflight.php`.
4. Resolve every FAIL.
5. **Delete `preflight.php` immediately.**

Do not use `phpinfo()` on the public server.

---

## 4. Create the production MySQL database

In **cPanel → MySQL Databases**:

1. Create a database, for example `CPANEL_USER_euphoria`.
2. Create a user, for example `CPANEL_USER_euphoria_user`.
3. Generate a unique strong password.
4. Add the user to the database.
5. Grant **ALL PRIVILEGES**.
6. Record the exact cPanel-prefixed database name and username.

In **phpMyAdmin**:

1. Select the new production database.
2. Choose **Import**.
3. Upload `euphoria_initial.sql` or `.sql.gz`.
4. Wait for the green success message.
5. Confirm these tables exist:

```text
users
roles
user_roles
programmes
categories
events
event_days
registration_fields
registrations
payments
qr_tokens
attendance
gates
scanner_assignments
email_jobs
email_logs
audit_logs
migrations
```

If import fails because of file size, use gzip export or ask the host to increase phpMyAdmin upload limits. Do not split SQL inside a foreign-key transaction unless you understand dependency order.

---

## 5. Upload private application files

1. Open **cPanel File Manager**.
2. Go to `/home/CPANEL_USER/`, one level above `public_html`.
3. Create directory `euphoria_app`.
4. Upload `euphoria_app.zip` into it.
5. Extract it.
6. Confirm:

```text
/home/CPANEL_USER/euphoria_app/app/Config/Paths.php
/home/CPANEL_USER/euphoria_app/vendor/autoload.php
/home/CPANEL_USER/euphoria_app/writable
```

7. Delete the uploaded ZIP from the server after extraction.

If File Manager created an extra nested directory such as `euphoria_app/codeigniter/app`, move the inner files up so `app` is directly inside `euphoria_app`.

---

## 6. Upload public files for `/euphoria`

1. Open `/home/CPANEL_USER/public_html/`.
2. Create directory `euphoria`.
3. Upload and extract `euphoria_public.zip` inside it.
4. Delete the ZIP after extraction.
5. Copy `deploy/cpanel-public-index.php.example` to:

```text
/home/CPANEL_USER/public_html/euphoria/index.php
```

6. Edit `index.php` and replace `CPANEL_USER` in:

```php
$pathsFile = '/home/CPANEL_USER/euphoria_app/app/Config/Paths.php';
```

7. Copy `deploy/cpanel-subdirectory.htaccess` to:

```text
/home/CPANEL_USER/public_html/euphoria/.htaccess
```

8. Confirm `.htaccess` contains:

```apache
RewriteBase /euphoria/
```

9. Confirm File Manager is configured to show hidden files.

The public `index.php` is the only PHP entrypoint. It loads CodeIgniter from the private directory.

---

## 7. Create production `.env`

1. Copy `deploy/cpanel.env.example` to:

```text
/home/CPANEL_USER/euphoria_app/.env
```

2. Replace every placeholder.
3. Set permissions to `600` if File Manager supports it; otherwise use the most restrictive readable permission supported by the host.

Minimum production values:

```dotenv
CI_ENVIRONMENT = production
app.baseURL = 'https://sageuniversity.in/euphoria/'
app.indexPage = ''
app.appTimezone = 'Asia/Kolkata'
app.forceGlobalSecureRequests = true

database.default.hostname = localhost
database.default.database = CPANEL_USER_euphoria
database.default.username = CPANEL_USER_euphoria_user
database.default.password = YOUR_DATABASE_PASSWORD
database.default.DBDriver = MySQLi
database.default.port = 3306

cookie.secure = true
cookie.httponly = true
cookie.samesite = Lax

EASEBUZZ_ENV = prod
PAYMENT_MODE = gateway
EASEBUZZ_PRODUCTINFO = euphoria2026
EASEBUZZ_ALLOW_SIGNED_CALLBACK_TEST = false
SCANNER_ALLOW_OFFDATE = false
```

### Generate an encryption key locally

On Windows local PHP:

```bat
php -r "echo bin2hex(random_bytes(32)), PHP_EOL;"
```

Put the 64-character output in:

```dotenv
encryption.key = hex2bin:YOUR_64_CHARACTER_OUTPUT
```

Never reuse the preview/local encryption key in production.

---

## 8. Configure Easebuzz production payment

Add the live key and salt only to the private `.env`:

```dotenv
EASEBUZZ_ENV = prod
EASEBUZZ_KEY = YOUR_LIVE_EASEBUZZ_KEY
EASEBUZZ_SALT = YOUR_LIVE_EASEBUZZ_SALT
PAYMENT_MODE = gateway
EASEBUZZ_TIMEOUT = 20
EASEBUZZ_PRODUCTINFO = euphoria2026
EASEBUZZ_ALLOW_SIGNED_CALLBACK_TEST = false
```

The exact product value must remain:

```text
euphoria2026
```

Configure Easebuzz callback/success/failure URLs as required by the merchant dashboard:

```text
https://sageuniversity.in/euphoria/payments/easebuzz/callback
```

Production rules:

- Never expose the salt in HTML, JavaScript, GitHub, screenshots, or support messages.
- Never mark a payment successful from a browser redirect.
- Keep the signed development callback flag `false`.
- First test with the provider's approved test/sandbox process.
- Perform a low-value real payment only after Easebuzz approves the production domain.

---

## 9. Configure Google Workspace SMTP

Use a Google App Password, not the mailbox's normal password.

```dotenv
email.protocol = smtp
email.SMTPHost = smtp.gmail.com
email.SMTPUser = registrations@sageuniversity.in
email.SMTPPass = YOUR_GOOGLE_APP_PASSWORD
email.SMTPPort = 587
email.SMTPCrypto = tls
email.fromEmail = registrations@sageuniversity.in
email.fromName = 'SAGE EUPHORIA Registrations'
```

Google Workspace checklist:

1. Two-step verification enabled.
2. App Password created for the website.
3. Workspace administrator allows SMTP authentication.
4. SPF includes Google's mail servers.
5. DKIM is enabled for `sageuniversity.in`.
6. DMARC is configured and monitored.

SMTP acceptance does not guarantee inbox placement. Check spam/quarantine and ask university IT to allow the sender.

---

## 10. Queue/cron requirement

Pass and confirmation emails are queued. A worker must run, otherwise registrations can confirm but emails remain pending.

Check whether cPanel has **Cron Jobs**. Terminal access is not required to add a cron from the UI.

Example every-minute cron:

```cron
* * * * * /opt/cpanel/ea-php82/root/usr/bin/php /home/CPANEL_USER/euphoria_app/spark queue:work --once >> /home/CPANEL_USER/euphoria_app/writable/logs/queue-cron.log 2>&1
```

Alternative PHP paths:

```text
/usr/local/bin/php
/usr/bin/php
/opt/cpanel/ea-php82/root/usr/bin/php
/opt/cpanel/ea-php83/root/usr/bin/php
```

Ask hosting support for the exact PHP CLI path.

If cPanel has no Cron Jobs and the host refuses to run a worker, queued email delivery is **not operational**. Upgrade hosting or ask the provider to run the command every minute. Do not claim email is live until `email_jobs` changes from `pending` to `sent`.

---

## 11. File permissions

Use File Manager → **Change Permissions**:

```text
Directories: 755
Files:       644
.env:        600 (or most restrictive supported)
writable/:   755 or 775, depending on host PHP ownership
```

These subdirectories must be writable by PHP:

```text
writable/cache
writable/logs
writable/session
writable/uploads
writable/passes
```

Do not use `777` permanently.

---

## 12. Change demo credentials before launch

Initial development accounts:

```text
Admin:   admin@euphoria.test / EuphoriaDemo!2026
Scanner: scanner@euphoria.test / ScannerDemo!2026
```

They are for first login only and must not remain on production.

### Generate new hashes locally

```bat
php -r "echo password_hash('YOUR-NEW-ADMIN-PASSWORD', PASSWORD_DEFAULT), PHP_EOL;"
php -r "echo password_hash('YOUR-NEW-SCANNER-PASSWORD', PASSWORD_DEFAULT), PHP_EOL;"
```

Use unique passwords of at least 14 characters. Avoid leaving them in command history.

### Update with cPanel phpMyAdmin

```sql
UPDATE users
SET email = 'your-admin@sageuniversity.in',
    password_hash = 'PASTE_ADMIN_HASH',
    updated_at = NOW()
WHERE email = 'admin@euphoria.test';

UPDATE users
SET email = 'gate1@sageuniversity.in',
    password_hash = 'PASTE_SCANNER_HASH',
    updated_at = NOW()
WHERE email = 'scanner@euphoria.test';
```

The role mappings remain unchanged.

Production login URLs:

```text
Admin:   https://sageuniversity.in/euphoria/admin/login
Scanner: https://sageuniversity.in/euphoria/scanner/login
```

---

## 13. First browser launch

Open in this order:

1. `https://sageuniversity.in/euphoria/`
2. `https://sageuniversity.in/euphoria/events`
3. `https://sageuniversity.in/euphoria/admin/login`
4. `https://sageuniversity.in/euphoria/scanner/login`

If the home page shows but inner pages return 404, `.htaccess`, `mod_rewrite`, `AllowOverride`, or `RewriteBase /euphoria/` is incorrect.

If every page returns 500, inspect:

```text
/home/CPANEL_USER/euphoria_app/writable/logs/
```

Temporarily set `CI_ENVIRONMENT = development` only while diagnosing privately, then restore `production` immediately. Never leave stack traces public.

---

## 14. Create and publish the first live event

1. Sign in at `/euphoria/admin/login`.
2. Open **Categories** and create/activate the event category.
3. Open **Events → New event**.
4. Enter event name and unique lowercase slug.
5. Set registration type: Individual or Team.
6. Set fee, capacity, dates, venue, eligibility, rules, prizes, refund policy, and coordinator.
7. Add every event day. QR permits one entry per configured day.
8. Add event-specific registration fields.
9. For free events: fee `0`, payment not required.
10. For paid events: enter fee and enable payment required.
11. Choose **Registration Open** to show the public Register button.
12. Save.
13. Open the public event URL in an incognito window.
14. Complete one test registration before promotion.
15. Open **Scanner access** and assign scanner, event day, and gate.

Status behavior:

```text
Draft              Hidden
Scheduled          Publicly visible, registration closed
Registration Open  Publicly visible and registration enabled
Live               Event-day visible; new registration closed
Completed          Registration closed
Cancelled          Registration closed
Archived           Hidden
```

---

## 15. Production acceptance test

Complete this entire flow before announcing the site:

### Public

- [ ] Home and Events load over HTTPS.
- [ ] No mixed-content browser warnings.
- [ ] Event fee comes from the database.
- [ ] Free registration confirms without payment.
- [ ] Paid registration opens Easebuzz hosted checkout.
- [ ] Browser redirect alone does not confirm payment.
- [ ] Valid Easebuzz callback confirms registration.
- [ ] Registration ID is unique.
- [ ] Digital pass opens from its secure link.
- [ ] Complete PDF pass downloads and prints on one page.
- [ ] Branded email arrives with complete PDF attachment.

### Scanner

- [ ] Scanner can sign in only at `/scanner/login`.
- [ ] Assigned event/day/gate is visible.
- [ ] Camera opens on HTTPS.
- [ ] QR image/manual token fallback works.
- [ ] First scan returns Entry Allowed.
- [ ] Same-day second scan returns Entry Already Recorded.
- [ ] Same QR on a second configured day returns Entry Allowed.
- [ ] Wrong event, unpaid, revoked, and invalid QR are denied.

### Admin

- [ ] Dashboard counts update after registration/payment/scan.
- [ ] Event price edits update the public event page.
- [ ] Participant cancel and QR revoke take effect immediately.
- [ ] Attendance report and CSV export contain the entry.
- [ ] Audit logs record event, payment, participant, and scanner actions.

---

## 16. Security launch checklist

- [ ] `CI_ENVIRONMENT=production`
- [ ] HTTPS and AutoSSL active
- [ ] `app.forceGlobalSecureRequests=true`
- [ ] Secure HTTP-only cookies active
- [ ] Unique encryption key
- [ ] Production database credentials unique
- [ ] Demo accounts renamed and passwords changed
- [ ] Easebuzz signed callback test disabled
- [ ] Scanner off-date test disabled
- [ ] `.env` outside `public_html`
- [ ] SQL/ZIP/preflight files removed from `public_html`
- [ ] Directory listing disabled
- [ ] `writable` not public
- [ ] Cron worker active
- [ ] Database backups scheduled
- [ ] SPF, DKIM, and DMARC checked
- [ ] Error display disabled

---

## 17. Backups and rollback

Before every release:

1. Export the production MySQL database from phpMyAdmin.
2. Download a private copy of `.env` securely.
3. Back up `writable/uploads` and retained passes.
4. Keep the previously working `euphoria_app` ZIP.

Rollback:

1. Put the site in a maintenance window.
2. Restore the previous private application files.
3. Restore the matching SQL backup only if the release changed schema and rollback migrations are safe.
4. Restore `.env`.
5. Confirm public, Admin, Scanner, payment callback, and queue.

Never restore an old database over new paid registrations without reconciling transactions first.

---

## 18. Updating without Terminal

For every future version:

1. Clone/copy production database locally.
2. Back up production.
3. Run new CodeIgniter migrations locally.
4. Export the exact SQL schema/data changes.
5. Build `vendor` locally with production Composer flags.
6. Upload a new versioned private directory, for example `euphoria_app_v2`.
7. Import migrations through phpMyAdmin.
8. Update the public `index.php` private path only when the new version is ready.
9. Test.
10. Keep the prior version briefly for rollback.

Request SSH/Terminal access from the hosting provider for safer long-term updates.

---

## 19. Common cPanel errors

### 404 on inner routes

- `.htaccess` missing because hidden files were not uploaded.
- `mod_rewrite` disabled.
- `AllowOverride` disabled.
- `RewriteBase` is not `/euphoria/`.
- `app.baseURL` missing the `/euphoria/` path or trailing slash.

### 500 application path error

- `CPANEL_USER` not replaced in public `index.php`.
- Private ZIP extracted into an extra nested directory.
- `vendor/autoload.php` missing.
- PHP version/extensions incorrect.
- `.env` malformed.

### Database error

- cPanel prefix missing from database/user.
- User not assigned to database.
- Password contains special characters but `.env` formatting is invalid.
- SQL import incomplete or foreign keys failed.

### CSS/JavaScript missing

- Public ZIP extracted into `public_html/euphoria/public` instead of directly into `public_html/euphoria`.
- `app.baseURL` incorrect.
- Browser/CDN cache stale.

### Camera does not open

- Page is not HTTPS.
- Browser permission denied.
- Camera is already used by another app/tab.
- Use QR image upload/manual token fallback.

### Payment remains pending

- Callback URL not approved/reachable.
- Key/salt environment mismatch.
- Amount/product/transaction mismatch.
- Never mark it successful from JavaScript.

### Email not delivered

- Cron worker not running.
- Google App Password/Workspace SMTP blocked.
- `email_jobs` remains pending or failed.
- Message accepted but filtered into spam/quarantine.
- SPF/DKIM/DMARC missing.

---

## 20. Optional GitHub/SSH deployment if enabled later

If the host later enables SSH:

```bash
cd /home/CPANEL_USER
git clone YOUR_PRIVATE_REPOSITORY euphoria_app
cd euphoria_app
composer install --no-dev --optimize-autoloader
php spark migrate --all
php spark cache:clear
php spark optimize
```

Never commit `.env`, Easebuzz salt, SMTP app password, database password, or encryption key. Keep the repository private.

---

## 21. Go-live URLs

```text
Public:        https://sageuniversity.in/euphoria/
Events:        https://sageuniversity.in/euphoria/events
Registration:  https://sageuniversity.in/euphoria/registration
Admin:         https://sageuniversity.in/euphoria/admin/login
Scanner:       https://sageuniversity.in/euphoria/scanner/login
Payment hook:  https://sageuniversity.in/euphoria/payments/easebuzz/callback
```

Do not add Admin or Scanner links to public navigation. Authorized staff should bookmark the direct login URLs.

---

## 22. Final decision gate

Do not make the site public until all are true:

1. Private/public paths are separated.
2. Preflight checks pass and preflight file is deleted.
3. SQL import and migrations table are complete.
4. Demo credentials are changed.
5. HTTPS works.
6. Easebuzz callback is production-approved.
7. SMTP and cron worker deliver a real complete pass email.
8. QR first scan, duplicate scan, and next-day scan pass.
9. Backups and rollback files exist.

If any item is false, the deployment is not production-ready.