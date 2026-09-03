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
- SQL re-import creates 36 tables, 37 events, eight starter media items, two development-only users, and all five migration records
- The packaged root, Events page, and API health endpoint booted successfully against the imported database; an unknown route returned 404

This release also includes automatic event/day QR routing with no gate selector, simple scanner-user creation, date-wise complete attendance rosters, CSV/XLSX complimentary pass generation, and Admin-managed homepage/gallery images and video URLs.

Latest Admin update: Events now support exact-name single permanent deletion and confirmation-protected checkbox bulk deletion with full related-data cleanup. Admin modules use separate routes, and a pre-event QR shows participant/event/date/time/venue as UPCOMING without saving attendance.

Live Easebuzz callback, SMTP delivery, cron, HTTPS camera permission, and Apache rewrite behavior must still be validated on the actual cPanel host.