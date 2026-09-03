<?php

namespace App\Controllers;

use App\Services\AttendanceService;
use App\Services\AuthenticationService;
use RuntimeException;

class ScannerController extends BaseController
{
    public function login() { return $this->render('scanner/login', ['title'=>'Scanner access']); }
    public function attempt()
    {
        try {
            (new AuthenticationService())->authenticate((string)$this->request->getPost('email'), (string)$this->request->getPost('password'), ['SCANNER','SUPER_ADMIN','EVENT_ADMIN'], 'scanner');
            return redirect()->to(base_url('scanner'));
        } catch (RuntimeException $e) {
            return redirect()->back()->withInput()->with('error', $e->getMessage());
        }
    }
    public function index()
    {
        return $this->render('scanner/index', ['title'=>'Automatic entry scanner', 'serverDate'=>date('Y-m-d'), 'demoMode'=>ENVIRONMENT !== 'production' && filter_var(env('SCANNER_ALLOW_OFFDATE', true), FILTER_VALIDATE_BOOL)]);
    }
    public function scan()
    {
        $payload = $this->request->getJSON(true) ?: $this->request->getPost();
        $token = trim((string)($payload['token'] ?? ''));
        if ($token === '') return $this->response->setStatusCode(422)->setJSON(['ok'=>false, 'status'=>'denied', 'message'=>'A QR token is required.', 'csrf'=>csrf_hash()]);
        $result = (new AttendanceService(db_connect()))->scan($token, (int)session('user_id'));
        (new \App\Services\AuditService())->record('attendance.scan_'.$result['status'], 'attendance', $result['registration']['registration_id']??null, ['event_id'=>$result['event_id']??null, 'day_id'=>$result['event_day_id']??null]);
        $result['csrf'] = csrf_hash();
        return $this->response->setJSON($result);
    }
    public function logout() { session()->destroy(); return redirect()->to(base_url('scanner/login')); }
}