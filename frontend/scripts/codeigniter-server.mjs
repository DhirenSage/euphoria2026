import { spawn, spawnSync } from 'node:child_process';
import { resolve } from 'node:path';

const codeigniterRoot = resolve(import.meta.dirname, '../../codeigniter');

// Emergent's preview supervisor only exposes the frontend process. Keep the
// preview's local MariaDB process available, while production uses external
// MySQL and a dedicated PHP-FPM/Supervisor service.
spawnSync('/usr/sbin/service', ['mariadb', 'start'], { stdio: 'inherit' });

const php = spawn('/usr/bin/php', ['spark', 'serve', '--host', '0.0.0.0', '--port', '3000'], {
  cwd: codeigniterRoot,
  env: process.env,
  stdio: 'inherit',
});

const stop = (signal) => {
  if (!php.killed) php.kill(signal);
};

process.on('SIGTERM', () => stop('SIGTERM'));
process.on('SIGINT', () => stop('SIGINT'));
php.on('exit', (code, signal) => process.exit(signal ? 1 : (code ?? 1)));