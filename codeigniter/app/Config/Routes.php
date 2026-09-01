<?php

namespace Config;

use CodeIgniter\Router\RouteCollection;

/** @var RouteCollection $routes */
$routes->get('/', 'PublicController::home');
$routes->get('events', 'PublicController::events');
$routes->get('events/(:segment)', 'PublicController::event/$1');
$routes->get('category/(:segment)', 'PublicController::category/$1');
$routes->get('gallery', 'PublicController::gallery');
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
$routes->get('pass/(:segment)', 'RegistrationController::pass/$1');

$routes->get('login', 'AuthController::login');
$routes->post('login', 'AuthController::attempt');
$routes->get('logout', 'AuthController::logout');

$routes->group('admin', ['filter' => 'auth'], static function ($routes) {
    $routes->get('/', 'AdminController::dashboard');
    $routes->get('events', 'AdminController::events');
    $routes->get('events/new', 'AdminController::newEvent');
    $routes->post('events', 'AdminController::storeEvent');
    $routes->get('registrations', 'AdminController::registrations');
    $routes->get('attendance', 'AdminController::attendance');
    $routes->get('settings', 'AdminController::settings');
    $routes->post('settings', 'AdminController::saveSettings');
    $routes->post('payments/(:segment)/verify', 'AdminController::verifyPayment/$1');
});

$routes->get('scanner/login', 'ScannerController::login');
$routes->post('scanner/login', 'ScannerController::attempt');
$routes->group('scanner', ['filter' => 'role:SCANNER,SUPER_ADMIN,EVENT_ADMIN'], static function ($routes) {
    $routes->get('/', 'ScannerController::index');
    $routes->post('scan', 'ScannerController::scan');
    $routes->get('logout', 'ScannerController::logout');
});

$routes->post('payments/easebuzz/callback', 'PaymentController::callback');
$routes->get('payments/easebuzz/callback', 'PaymentController::callback');