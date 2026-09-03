<?php

namespace Config;

use CodeIgniter\Router\RouteCollection;

/** @var RouteCollection $routes */
$routes->get('/', 'PublicController::home');
$routes->get('events', 'PublicController::events');
$routes->get('events/(:segment)', 'PublicController::event/$1');
$routes->get('category/(:segment)', 'PublicController::category/$1');
$routes->get('gallery', 'PublicController::gallery');
$routes->get('media/file/(:num)', 'PublicController::mediaFile/$1');
$routes->get('about-euphoria', 'PublicController::about');
$routes->get('contact', 'PublicController::contact');
$routes->get('faq', 'PublicController::faq');
$routes->get('terms', 'PublicController::terms');
$routes->get('privacy', 'PublicController::privacy');
$routes->get('refund-policy', 'PublicController::refund');

$routes->group('api', static function ($routes) {
    $routes->get('health', 'ApiController::health');
    $routes->get('events', 'ApiController::events');
    $routes->get('events/(:segment)', 'ApiController::event/$1');
});

$routes->get('registration', 'RegistrationController::create');
$routes->post('registration', 'RegistrationController::store');
$routes->get('registration/(:segment)', 'RegistrationController::create/$1');
$routes->post('registration/(:segment)', 'RegistrationController::store/$1');
$routes->get('registration/success/(:segment)', 'RegistrationController::success/$1');
$routes->get('payment/(:segment)', 'PaymentController::checkout/$1');
$routes->get('pass/(:segment)/download', 'RegistrationController::downloadPass/$1');
$routes->get('pass/(:segment)', 'RegistrationController::pass/$1');

$routes->get('login', 'AuthController::login');
$routes->get('admin/login', 'AuthController::login');
$routes->post('admin/login', 'AuthController::attempt');
$routes->post('logout', 'AuthController::logout');

$routes->group('admin', ['filter' => 'auth:SUPER_ADMIN,PROGRAMME_ADMIN,EVENT_ADMIN,FINANCE,CONTENT_MANAGER,REPORT_VIEWER'], static function ($routes) {
    $routes->get('/', 'AdminController::dashboard');
    $routes->get('categories', 'AdminController::categories');
    $routes->post('categories', 'AdminController::storeCategory');
    $routes->post('categories/(:num)', 'AdminController::updateCategory/$1');
    $routes->post('categories/(:num)/delete', 'AdminController::deleteCategory/$1');
    $routes->get('events', 'AdminController::events');
    $routes->get('events/new', 'AdminController::newEvent');
    $routes->post('events', 'AdminController::storeEvent');
    $routes->get('events/(:num)/edit', 'AdminController::editEvent/$1');
    $routes->post('events/(:num)', 'AdminController::updateEvent/$1');
    $routes->post('events/(:num)/delete', 'AdminController::deleteEvent/$1');
    $routes->get('registrations', 'AdminController::registrations');
    $routes->get('registrations/(:segment)', 'AdminController::registration/$1');
    $routes->post('registrations/(:segment)/status', 'AdminController::registrationStatus/$1');
    $routes->get('attendance', 'AdminController::attendance');
    $routes->get('bulk-passes', 'BulkPassController::index');
    $routes->get('bulk-passes/template.csv', 'BulkPassController::downloadTemplate');
    $routes->post('bulk-passes/import', 'BulkPassController::import');
    $routes->get('media', 'MediaController::index');
    $routes->post('media', 'MediaController::store');
    $routes->post('media/(:num)', 'MediaController::update/$1');
    $routes->post('media/(:num)/delete', 'MediaController::delete/$1');
    $routes->get('scanners', 'AdminController::scanners');
    $routes->post('scanners', 'AdminController::storeScanner');
    $routes->post('scanners/(:num)/toggle', 'AdminController::toggleScanner/$1');
    $routes->get('reports', 'AdminController::reports');
    $routes->get('reports/attendance.csv', 'AdminController::exportAttendance');
    $routes->get('settings', 'AdminController::settings');
    $routes->post('settings', 'AdminController::saveSettings');
    $routes->post('settings/test-email', 'AdminController::testEmail');
    $routes->post('payments/(:segment)/verify', 'AdminController::verifyPayment/$1');
    $routes->post('dev/easebuzz/callback-test', 'DevCallbackController::confirm');
});

$routes->get('scanner/login', 'ScannerController::login');
$routes->post('scanner/login', 'ScannerController::attempt');
$routes->group('scanner', ['filter' => 'auth:SCANNER,SUPER_ADMIN,EVENT_ADMIN'], static function ($routes) {
    $routes->get('/', 'ScannerController::index');
    $routes->post('scan', 'ScannerController::scan');
    $routes->post('logout', 'ScannerController::logout');
});

$routes->post('payments/easebuzz/callback', 'PaymentController::callback');
$routes->get('payments/easebuzz/callback', 'PaymentController::callback');