<?php

defined('FCPATH') || define('FCPATH', __DIR__ . '/../../public/');
defined('COMPOSER_PATH') || define('COMPOSER_PATH', ROOTPATH . 'vendor/autoload.php');
defined('APP_NAMESPACE') || define('APP_NAMESPACE', 'App');
defined('EXIT_SUCCESS') || define('EXIT_SUCCESS', 0);
defined('EXIT_ERROR') || define('EXIT_ERROR', 1);
defined('EXIT_CONFIG') || define('EXIT_CONFIG', 3);
defined('EXIT_NOPERMISSION') || define('EXIT_NOPERMISSION', 4);
defined('EXIT_NOT_FOUND') || define('EXIT_NOT_FOUND', 5);
defined('EXIT_UNKNOWN_FILE') || define('EXIT_UNKNOWN_FILE', 6);
defined('EXIT_UNKNOWN_CLASS') || define('EXIT_UNKNOWN_CLASS', 7);
defined('EXIT_DATABASE') || define('EXIT_DATABASE', 8);
defined('EXIT__AUTO_MIN') || define('EXIT__AUTO_MIN', 9);
defined('EXIT__AUTO_MAX') || define('EXIT__AUTO_MAX', 125);
defined('CI_DEBUG') || define('CI_DEBUG', false);