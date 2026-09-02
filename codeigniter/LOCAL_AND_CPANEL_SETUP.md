# SAGE EUPHORIA Platform — Local Windows and cPanel Setup

This handbook applies to the CodeIgniter application in the `codeigniter/` directory.

## 1. What you are installing

- CodeIgniter 4.7 application
- PHP 8.2 or newer
- MySQL 8-compatible InnoDB database
- Composer dependencies for QR generation and PDF passes
- Apache with `mod_rewrite`
- Database-backed email queue
- Easebuzz hosted checkout integration

The PHP project is independent of the Emergent React preview. Your real PHP website must point its document root to the `codeigniter/public` directory.

---

## 2. Development login credentials

Run the migrations and `DatabaseSeeder` before using these accounts.

### Admin portal

- URL: `/admin/login`
- Email: `admin@euphoria.test`
- Password: `EuphoriaDemo!2026`

### Scanner portal

- URL: `/scanner/login`
- Email: `scanner@euphoria.test`
- Password: `ScannerDemo!2026`

These are **development-only demo credentials**. Change both email addresses and passwords immediately after the first production deployment. Never continue using `.test` accounts on a live system.

---

## 3. Software requirements

### Required PHP version

Use PHP 8.2, 8.3, or 8.4.

### Required PHP extensions

Enable:

- `curl`
- `dom`
- `fileinfo`
- `gd`
- `intl`
- `mbstring`
- `mysqli`
- `openssl`
- `zip`

Verify from a terminal:

```bash
php -v
php -m
composer --version
```

### Database

- MySQL 8 is recommended.
- MariaDB with MySQL 8-compatible InnoDB behavior can be used for development.
- Use `utf8mb4` and `utf8mb4_unicode_ci`.

---

## 4. Local setup on Windows with Laragon

Laragon is the simplest recommended Windows option because PHP, Apache, MySQL, and local virtual hosts work together cleanly.

### Step 1 — Install tools

1. Install Laragon Full.
2. Select PHP 8.2 or newer.
3. Install Composer if it is not already available.
4. Start Apache and MySQL from Laragon.

### Step 2 — Copy the project

Copy the complete `codeigniter` directory to:

```text
C:\laragon\www\euphoria
```

Do not copy only the `public` directory. The complete application, `vendor`, `writable`, migrations, and configuration are required.

### Step 3 — Install PHP packages

Open Laragon Terminal:

```bash
cd C:\laragon\www\euphoria
composer install
```

### Step 4 — Create the database

Open HeidiSQL or phpMyAdmin and run:

```sql
CREATE DATABASE euphoria
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'euphoria_user'@'localhost'
  IDENTIFIED BY 'choose-a-strong-local-password';

GRANT ALL PRIVILEGES ON euphoria.*
  TO 'euphoria_user'@'localhost';

FLUSH PRIVILEGES;
```

If your local MySQL allows the `root` account without a password, you may use it only for local development. Use a dedicated user in production.

### Step 5 — Create `.env`

Copy `env` to `.env`:

```bash
copy env .env
```

Edit `.env`:

```dotenv
CI_ENVIRONMENT = development
app.baseURL = 'http://localhost:8080/'
app.indexPage = ''
app.appTimezone = 'Asia/Kolkata'

database.default.hostname = localhost
database.default.database = euphoria
database.default.username = euphoria_user
database.default.password = your-local-database-password
database.default.DBDriver = MySQLi
database.default.port = 3306

app.forceGlobalSecureRequests = false
cookie.secure = false
cookie.httponly = true
cookie.samesite = Lax

EASEBUZZ_ALLOW_SIGNED_CALLBACK_TEST = true
SCANNER_ALLOW_OFFDATE = true
```

Generate an encryption key:

```bash
php spark key:generate
```

If your installed CodeIgniter version does not expose that command, generate a key with:

```bash
php -r "echo 'hex2bin:'.bin2hex(random_bytes(32)).PHP_EOL;"
```

Copy the output to:

```dotenv
encryption.key = hex2bin:generated-value-here
```

Never copy a production encryption key into chat, email, source control, or a public support ticket.

### Step 6 — Create tables and demo data

```bash
php spark migrate --all
php spark db:seed DatabaseSeeder
```

Run the seeder only once on a clean database. It creates the EUPHORIA programme, categories, sample events, gate, roles, Admin account, and Scanner account.

### Step 7 — Start the application

```bash
php spark serve --host 127.0.0.1 --port 8080
```

Open:

```text
Public website: http://localhost:8080/
Admin login:    http://localhost:8080/admin/login
Scanner login:  http://localhost:8080/scanner/login
```

### Step 8 — Start the email worker

Open another terminal:

```bash
cd C:\laragon\www\euphoria
php spark queue:work
```

Keep that terminal open while testing confirmation emails.

---

## 5. Local setup on Windows with XAMPP

### Step 1 — Install and enable modules

1. Install a XAMPP build containing PHP 8.2 or newer.
2. Start Apache and MySQL.
3. Open the active `php.ini` from the XAMPP Control Panel.
4. Enable the required extensions listed in section 3.
5. Restart Apache.

### Step 2 — Copy the project

```text
C:\xampp\htdocs\euphoria
```

### Step 3 — Install dependencies and database

Open Command Prompt:

```bash
cd C:\xampp\htdocs\euphoria
composer install
```

Create the `euphoria` database in `http://localhost/phpmyadmin`, then follow the same `.env`, migration, seeding, and `spark serve` steps from the Laragon section.

Using `php spark serve` is recommended during development because it avoids XAMPP virtual-host and rewrite configuration issues.

### Optional Apache virtual host

For a local URL such as `http://euphoria.test`, set the Apache document root to:

```text
C:/xampp/htdocs/euphoria/public
```

Example virtual host:

```apache
<VirtualHost *:80>
    ServerName euphoria.test
    DocumentRoot "C:/xampp/htdocs/euphoria/public"
    <Directory "C:/xampp/htdocs/euphoria/public">
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```

Add this to the Windows hosts file as Administrator:

```text
127.0.0.1 euphoria.test
```

Then set:

```dotenv
app.baseURL = 'http://euphoria.test/'
```

---

## 6. cPanel deployment — recommended Terminal/SSH method

### Step 1 — Create the domain or subdomain

In cPanel, create a subdomain such as:

```text
euphoria.yourdomain.com
```

Set its document root to:

```text
/home/CPANEL_USER/euphoria/public
```

This is the safest layout. Only the `public` directory is web-accessible; `.env`, `app`, `vendor`, and `writable` stay outside the web root.

### Step 2 — Select PHP

In **MultiPHP Manager** or **Select PHP Version**:

1. Select PHP 8.2 or newer for the domain.
2. Enable the required extensions from section 3.
3. Set `memory_limit` to at least `256M`; PDF generation may require `512M` for large content.
4. Set `upload_max_filesize` and `post_max_size` to at least `8M` if registration uploads are enabled.

### Step 3 — Upload the source

Upload and extract the complete project to:

```text
/home/CPANEL_USER/euphoria
```

The resulting paths should include:

```text
/home/CPANEL_USER/euphoria/app
/home/CPANEL_USER/euphoria/public
/home/CPANEL_USER/euphoria/spark
/home/CPANEL_USER/euphoria/writable
/home/CPANEL_USER/euphoria/composer.json
```

### Step 4 — Install production packages

Open cPanel Terminal or SSH:

```bash
cd /home/CPANEL_USER/euphoria
composer install --no-dev --optimize-autoloader
```

If `composer` is not globally available:

```bash
php composer.phar install --no-dev --optimize-autoloader
```

### Step 5 — Create MySQL database and user

In **MySQL Databases**:

1. Create a database, for example `CPANEL_USER_euphoria`.
2. Create a database user with a strong random password.
3. Add the user to the database with all privileges.
4. Keep the full cPanel-prefixed database and username values.

### Step 6 — Create production `.env`

Create `/home/CPANEL_USER/euphoria/.env` with permissions `0600` or the most restrictive cPanel option available.

```dotenv
CI_ENVIRONMENT = production
app.baseURL = 'https://euphoria.yourdomain.com/'
app.indexPage = ''
app.appTimezone = 'Asia/Kolkata'

database.default.hostname = localhost
database.default.database = CPANEL_USER_euphoria
database.default.username = CPANEL_USER_euphoria_user
database.default.password = your-strong-database-password
database.default.DBDriver = MySQLi
database.default.DBPrefix =
database.default.port = 3306

app.forceGlobalSecureRequests = true
cookie.secure = true
cookie.httponly = true
cookie.samesite = Lax
security.tokenName = csrf_token

encryption.key = hex2bin:generate-a-unique-64-hex-character-value

EASEBUZZ_ENV = prod
EASEBUZZ_KEY = your-live-merchant-key
EASEBUZZ_SALT = your-live-merchant-salt
PAYMENT_MODE = gateway
EASEBUZZ_TIMEOUT = 20
EASEBUZZ_PRODUCTINFO = euphoria2026
EASEBUZZ_ALLOW_SIGNED_CALLBACK_TEST = false
SCANNER_ALLOW_OFFDATE = false

email.protocol = smtp
email.SMTPHost = smtp.gmail.com
email.SMTPUser = your-google-workspace-mailbox@example.com
email.SMTPPass = your-google-app-password
email.SMTPPort = 587
email.SMTPCrypto = tls
email.fromEmail = your-google-workspace-mailbox@example.com
email.fromName = 'SAGE EUPHORIA Registrations'
```

Do not paste actual Easebuzz salts, SMTP app passwords, database passwords, or encryption keys into documentation or source files.

### Step 7 — Set permissions

```bash
cd /home/CPANEL_USER/euphoria
chmod 600 .env
find writable -type d -exec chmod 775 {} \;
find writable -type f -exec chmod 664 {} \;
```

If the cPanel PHP process runs as your account, `755` directories and `644` files may be sufficient. Do not use `777` unless the host explicitly requires it temporarily for diagnosis.

### Step 8 — Migrate and seed

```bash
php spark migrate --all
php spark db:seed DatabaseSeeder
```

Seed only on the first clean installation. Immediately change the demo account credentials using section 9.

### Step 9 — Clear and optimize caches

```bash
php spark cache:clear
php spark optimize
```

### Step 10 — Enable SSL

1. Run cPanel AutoSSL for the domain.
2. Confirm `https://euphoria.yourdomain.com/` opens without certificate warnings.
3. Confirm HTTP redirects to HTTPS.
4. Keep `app.forceGlobalSecureRequests=true` and `cookie.secure=true` only after HTTPS works.

### Step 11 — Configure cron for queued emails

In **Cron Jobs**, run one queue job every minute:

```cron
* * * * * cd /home/CPANEL_USER/euphoria && /usr/local/bin/php spark queue:work --once >> /home/CPANEL_USER/euphoria/writable/logs/queue-cron.log 2>&1
```

Your PHP binary may instead be one of:

```text
/usr/bin/php
/opt/cpanel/ea-php82/root/usr/bin/php
/opt/cpanel/ea-php83/root/usr/bin/php
```

Ask the hosting provider or run `which php` in Terminal.

---

## 7. cPanel deployment — File Manager only, without Terminal/SSH

Use this method only when Composer and `spark` cannot run on cPanel.

### Step 1 — Prepare a production package locally

On Windows:

```bash
cd C:\laragon\www\euphoria
composer install --no-dev --optimize-autoloader
```

The upload package must include the generated `vendor` directory and `composer.lock`.

### Step 2 — Prepare the database locally

On a clean local database:

```bash
php spark migrate --all
php spark db:seed DatabaseSeeder
```

Export the complete database from local phpMyAdmin:

1. Select `euphoria`.
2. Choose **Export**.
3. Choose **Custom**.
4. Format: SQL.
5. Include structure, data, indexes, constraints, triggers if shown, and `AUTO_INCREMENT` values.
6. Save as `euphoria-initial.sql`.

### Step 3 — Upload files

Upload the complete prepared project, including `vendor`, to:

```text
/home/CPANEL_USER/euphoria
```

Create the subdomain document root as:

```text
/home/CPANEL_USER/euphoria/public
```

### Step 4 — Import the database

1. Create the database/user in cPanel MySQL Databases.
2. Open cPanel phpMyAdmin.
3. Select the new database.
4. Import `euphoria-initial.sql`.
5. Confirm tables such as `programmes`, `events`, `registrations`, `payments`, `qr_tokens`, `attendance`, and `migrations` exist.

### Step 5 — Create `.env`

Use File Manager to create `.env` one level above `public`, using the production example in section 6. Never put `.env` inside `public_html`.

### Step 6 — Queue processing without Terminal

Most cPanel installations still provide **Cron Jobs** even without Terminal. Add:

```cron
* * * * * cd /home/CPANEL_USER/euphoria && /opt/cpanel/ea-php82/root/usr/bin/php spark queue:work --once >/dev/null 2>&1
```

If Cron Jobs are not available, ask the host to enable cron or a persistent worker. Registration remains confirmed after payment, but queued email cannot be delivered until a worker runs.

### Updating later without SSH

1. Put the site in a maintenance window.
2. Back up files and database.
3. Run new migrations on an exact copy locally.
4. Export only the required schema changes carefully, or temporarily obtain Terminal access and run `php spark migrate --all`.
5. Upload changed application files and the matching `vendor` directory.

Terminal access is strongly recommended for safe future migrations.

---

## 8. If cPanel cannot point the domain to `public`

Preferred solution: ask the host to set the domain/subdomain document root to `/home/CPANEL_USER/euphoria/public`.

Fallback layout:

1. Keep the application in `/home/CPANEL_USER/euphoria`.
2. Copy the contents of `euphoria/public` into `/home/CPANEL_USER/public_html/euphoria`.
3. Edit `/home/CPANEL_USER/public_html/euphoria/index.php`.
4. Replace:

```php
require FCPATH . '../app/Config/Paths.php';
```

with:

```php
require '/home/CPANEL_USER/euphoria/app/Config/Paths.php';
```

5. Keep the supplied `.htaccess` beside that `index.php`.
6. Set `app.baseURL` to the exact public URL, including any `/euphoria/` subdirectory.

Never copy `.env`, `app`, `vendor`, or `writable` into the public document root.

---

## 9. Change Admin and Scanner credentials for production

### Generate password hashes locally

For each account, choose a unique password of at least 14 characters and generate a hash:

```bash
php -r "echo password_hash('REPLACE-WITH-A-STRONG-PASSWORD', PASSWORD_DEFAULT), PHP_EOL;"
```

Do not reuse the password and avoid leaving it in terminal history. A safer alternative is to run the command in a temporary local terminal and close/clear its history afterward.

### Update in phpMyAdmin

Replace the example emails and generated hashes:

```sql
UPDATE users
SET email = 'admin@yourdomain.com',
    password_hash = 'PASTE_GENERATED_ADMIN_HASH',
    updated_at = NOW()
WHERE email = 'admin@euphoria.test';

UPDATE users
SET email = 'scanner1@yourdomain.com',
    password_hash = 'PASTE_GENERATED_SCANNER_HASH',
    updated_at = NOW()
WHERE email = 'scanner@euphoria.test';
```

Then test both direct URLs in a private/incognito browser window.

### Do not change roles accidentally

The seeded role mappings are already correct:

- Demo Admin → `SUPER_ADMIN`
- Demo Scanner → `SCANNER`

Changing the `users` email/password fields does not remove those role assignments.

---

## 10. Configure Easebuzz safely

### Production values

Add the values supplied by Easebuzz only to production `.env`:

```dotenv
EASEBUZZ_ENV = prod
EASEBUZZ_KEY = your-live-key
EASEBUZZ_SALT = your-live-salt
PAYMENT_MODE = gateway
EASEBUZZ_PRODUCTINFO = euphoria2026
EASEBUZZ_ALLOW_SIGNED_CALLBACK_TEST = false
```

The `productinfo` value must remain exactly:

```text
euphoria2026
```

### Callback URL

Configure both success and failure/callback handling in Easebuzz as:

```text
https://euphoria.yourdomain.com/payments/easebuzz/callback
```

The application verifies the reverse hash, merchant key, transaction ID, stored amount, and product before confirming a registration. A browser redirect alone never confirms payment.

### Production rules

- Do not enable `EASEBUZZ_ALLOW_SIGNED_CALLBACK_TEST` in production.
- Do not expose `EASEBUZZ_SALT` in JavaScript, HTML, Git, screenshots, or support messages.
- Do not test a production charge until Easebuzz has approved the domain and callback URL.
- Keep gateway access logs, but never log full secret-bearing payloads.

---

## 11. Configure Google Workspace SMTP safely

### Google account preparation

1. Enable two-step verification on the sending Google Workspace account.
2. Create a Google **App Password** for the website.
3. Do not use the main mailbox password.

### `.env` settings

```dotenv
email.protocol = smtp
email.SMTPHost = smtp.gmail.com
email.SMTPUser = registrations@yourdomain.com
email.SMTPPass = your-16-character-google-app-password
email.SMTPPort = 587
email.SMTPCrypto = tls
email.fromEmail = registrations@yourdomain.com
email.fromName = 'SAGE EUPHORIA Registrations'
```

### Test SMTP

From Terminal:

```bash
php spark emails:test recipient@example.com
```

Then run one queued job:

```bash
php spark queue:work --once
```

Check:

- Inbox and spam folder
- `email_jobs` status in MySQL
- `email_logs` status in MySQL
- `writable/logs` for delivery errors

Common Google error `535 Username and Password not accepted` means the app password, Workspace policy, or SMTP access needs correction.

---

## 12. How to create an event and make it live

### Step 1 — Sign in

Open:

```text
https://euphoria.yourdomain.com/admin/login
```

Use the Admin account, not the Scanner account.

### Step 2 — Create or verify the category

1. Open **Categories** in the Admin sidebar.
2. Select the Euphoria programme.
3. Enter category name, slug, description, display order, and active status.
4. Click **Create category**.

The category must be active to appear publicly and in the event builder.

### Step 3 — Create the event

1. Open **Events**.
2. Click **New event**.
3. Complete the event builder.

#### Identity

- Category
- Event name
- Unique URL slug
- Event type
- Short and full description
- Banner and thumbnail URL

#### Registration and payment

- Individual or team registration
- Capacity; `0` means unlimited
- Fee
- Tax and discount when applicable
- Minimum and maximum team size
- Registration opening and closing date/time
- **Payment required** for paid events

For a free event:

```text
Fee = 0
Payment required = unchecked
```

For a paid event:

```text
Fee = required amount
Payment required = checked
```

#### Event operations

- Event start and end
- Venue
- Eligibility
- Rules
- Prizes
- Refund policy
- Coordinator/contact

#### Event days

Add every day on which this QR may be used. The same QR allows one entry on each configured day and rejects a second scan on the same day.

#### Dynamic registration fields

Add event-specific questions such as dance style, GitHub URL, technical skills, course, or department. Mark required fields carefully.

### Step 4 — Choose the correct status

- **Draft**: hidden from the public event catalogue.
- **Scheduled**: visible publicly, but registration is not open.
- **Registration Open**: visible publicly and the **Register Now** flow works.
- **Live**: visible publicly for event-day operations; new public registration is closed.
- **Completed/Cancelled/Archived**: not available for new registration.

To publish an event and accept registrations, choose:

```text
Status = Registration Open
```

Then click **Create event** or **Save event**.

### Step 5 — Verify public visibility

1. Open **Events** in a private/incognito window.
2. Find the event card.
3. Open the event page.
4. Confirm fee, date, venue, capacity, rules, and registration button.
5. Submit one test registration before advertising the event.

### Step 6 — Assign scanner access

1. Open **Scanner access** in Admin.
2. Create a gate if needed.
3. Select the Scanner user.
4. Select the event.
5. Select one event day.
6. Select the gate.
7. Save the assignment.
8. Repeat for each additional event day or gate.

Scanner staff use:

```text
https://euphoria.yourdomain.com/scanner/login
```

They can access only their assigned event/day/gate combinations.

### Step 7 — Event-day operation

1. Change the event status to **Live** when registration should close.
2. Scanner signs in and chooses assigned event/day/gate.
3. Scan the participant QR with camera or use the secure token fallback.
4. First valid scan for the day → **Entry Allowed**.
5. Same QR and same event day → **Entry Already Recorded**.
6. Same QR on another configured event day → **Entry Allowed**.
7. Admin checks **Attendance**, **Reports**, and CSV export.

---

## 13. Production launch checklist

Before sharing the public URL:

- [ ] PHP 8.2+ and every required extension enabled
- [ ] Domain document root points to `public`
- [ ] HTTPS/AutoSSL working
- [ ] `CI_ENVIRONMENT=production`
- [ ] `app.baseURL` exactly matches the HTTPS domain
- [ ] Unique production encryption key configured
- [ ] MySQL production user uses a strong unique password
- [ ] Demo Admin and Scanner credentials changed
- [ ] `.env` is outside web root and not downloadable
- [ ] `writable` can be written by PHP but is not public
- [ ] `EASEBUZZ_ENV=prod`
- [ ] `EASEBUZZ_PRODUCTINFO=euphoria2026`
- [ ] Signed callback test flag is `false`
- [ ] Off-date scanner flag is `false`
- [ ] Easebuzz callback URL uses the production HTTPS domain
- [ ] SMTP test accepted by the provider
- [ ] Cron/queue worker processes email jobs
- [ ] One free-event registration tested
- [ ] One paid test/sandbox payment tested
- [ ] QR pass and PDF download tested
- [ ] Scanner first entry, duplicate entry, and next-day entry tested
- [ ] Attendance CSV export tested
- [ ] Database and file backups enabled

---

## 14. Backup and update procedure

### Before every update

1. Export the MySQL database.
2. Back up `.env` separately and securely.
3. Back up `writable/uploads` and any retained pass files.
4. Record the current application version/commit.

### Terminal update

```bash
cd /home/CPANEL_USER/euphoria
composer install --no-dev --optimize-autoloader
php spark migrate --all
php spark cache:clear
php spark optimize
```

Test Admin login, one public event, registration, scanner access, and reports after every update.

---

## 15. Troubleshooting

### 404 on every page except the home page

- Confirm Apache `mod_rewrite` is enabled.
- Confirm `public/.htaccess` was uploaded; File Manager may hide dotfiles.
- Confirm **AllowOverride All** is enabled by the host.
- Confirm the domain document root is the `public` directory.

### 500 error

- Check `writable/logs`.
- Confirm `writable` permissions.
- Confirm PHP extensions.
- Confirm the production `.env` syntax and encryption key.
- Confirm `vendor/autoload.php` exists.

### Database connection error

- cPanel database names and usernames usually include the account prefix.
- Confirm the database user is assigned to the database.
- Confirm the host; cPanel commonly uses `localhost`.
- Confirm MySQLi is enabled.

### CSS or images missing

- Confirm `app.baseURL` has the exact HTTPS URL and trailing slash.
- Confirm the domain points to `public`.
- Clear browser cache and run `php spark cache:clear`.

### Registration works but no email arrives

- Run `php spark emails:test recipient@example.com`.
- Verify the cPanel cron command and PHP binary.
- Check `email_jobs`, `email_logs`, spam folder, and `writable/logs`.

### Payment remains pending

- Confirm Easebuzz callback uses HTTPS and the exact callback route.
- Confirm key/salt match the selected Easebuzz environment.
- Confirm the stored event fee matches the callback amount.
- Keep the registration pending until server-side verification succeeds; never update it from browser success alone.

### Scanner denies a valid pass

- Confirm payment and registration are confirmed.
- Confirm QR/pass status is active.
- Confirm Scanner assignment matches event, day, and gate.
- In production, confirm the selected event day is today.
- Check Attendance for a previous same-day entry.

---

## 16. Quick command reference

```bash
# Install
composer install

# Production install
composer install --no-dev --optimize-autoloader

# Database
php spark migrate --all
php spark db:seed DatabaseSeeder
php spark migrate:status

# Local server
php spark serve --host 127.0.0.1 --port 8080

# Email
php spark emails:test recipient@example.com
php spark queue:work
php spark queue:work --once

# Cache and optimization
php spark cache:clear
php spark optimize

# Tests
vendor/bin/phpunit

# Routes
php spark routes
```

Keep this file with the deployment package and update domain names, PHP paths, and operational contacts for your hosting account.