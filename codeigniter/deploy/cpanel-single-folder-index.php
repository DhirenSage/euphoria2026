<?php

use CodeIgniter\Boot;
use Config\Paths;

/*
 * EUPHORIA cPanel single-folder front controller.
 * Upload this file as /public_html/euphoria/index.php.
 */

define('FCPATH', __DIR__ . DIRECTORY_SEPARATOR);

if (getcwd() . DIRECTORY_SEPARATOR !== FCPATH) {
    chdir(FCPATH);
}

$pathsFile = FCPATH . 'app/Config/Paths.php';

if (! is_file($pathsFile)) {
    http_response_code(500);
    exit('EUPHORIA application files are incomplete. Confirm app/Config/Paths.php was uploaded.');
}

require $pathsFile;

$paths = new Paths();

require rtrim($paths->systemDirectory, '\\/ ') . DIRECTORY_SEPARATOR . 'Boot.php';

exit(Boot::bootWeb($paths));