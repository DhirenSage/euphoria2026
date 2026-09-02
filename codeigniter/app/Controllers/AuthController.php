<?php

namespace App\Controllers;

use App\Services\AuthenticationService;
use RuntimeException;

class AuthController extends BaseController
{
    private const ADMIN_ROLES = ['SUPER_ADMIN','PROGRAMME_ADMIN','EVENT_ADMIN','FINANCE','CONTENT_MANAGER','REPORT_VIEWER'];

    public function login() { return $this->render('auth/login', ['title'=>'Admin sign in']); }

    public function attempt()
    {
        try {
            (new AuthenticationService())->authenticate((string)$this->request->getPost('email'),(string)$this->request->getPost('password'),self::ADMIN_ROLES,'admin');
            return redirect()->to('/admin');
        } catch (RuntimeException $e) {
            return redirect()->back()->withInput()->with('error',$e->getMessage());
        }
    }

    public function logout() { session()->destroy(); return redirect()->to('/admin/login')->with('message','You have been signed out.'); }
}