# EUPHORIA cPanel release

Prepared for `https://sageuniversity.in/euphoria/` using cPanel File Manager, phpMyAdmin, PHP 8.2, and MySQL without server-side Composer.

## Download/upload artifacts

- `euphoria-cpanel-single-folder.zip` — extract directly inside `/public_html/euphoria`
- `euphoria_initial.sql` — import into a new empty database through phpMyAdmin; never upload it into `public_html`
- `SHA256SUMS.txt` — integrity hashes for both artifacts

The full step-by-step handbook is `/app/codeigniter/CPANEL_SINGLE_FOLDER_DEPLOYMENT.md`.

## Verified locally

- Production dependency bundle contains `vendor/autoload.php` and excludes PHPUnit/dev dependencies
- ZIP contains the root front controller, hardened `.htaccess`, assets, application source, empty writable directories, environment template, and temporary preflight checker
- SQL re-import created 35 tables, 37 events, two development-only users, and all four migration records
- The packaged root, Events page, and API health endpoint booted successfully against the imported database; an unknown route returned 404

Live Easebuzz callback, SMTP delivery, cron, HTTPS camera permission, and Apache rewrite behavior must still be validated on the actual cPanel host.