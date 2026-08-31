<?php

namespace App\Controllers;

use App\Services\AttendanceService;

class ScannerController extends BaseController
{
    public function login() { return $this->render('scanner/login', ['title'=>'Scanner access']); }
    public function attempt() { return (new AuthController())->attempt(); }

    public function index()
    {
        $db=db_connect(); $roles=session('roles')??[];
        if(in_array('SUPER_ADMIN',$roles,true)||in_array('EVENT_ADMIN',$roles,true)) { $events=$db->table('events')->whereIn('status',['scheduled','registration_open','live'])->orderBy('event_start','ASC')->get()->getResultArray(); $days=$db->table('event_days')->orderBy('event_date','ASC')->get()->getResultArray(); $gates=$db->table('gates')->where('is_active',1)->get()->getResultArray(); }
        else { $assignments=$db->table('scanner_assignments sa')->select('sa.event_id,sa.event_day_id,sa.gate_id')->where('sa.user_id',(int)session('user_id'))->where('sa.is_active',1)->get()->getResultArray(); $eventIds=array_unique(array_column($assignments,'event_id'));$dayIds=array_unique(array_column($assignments,'event_day_id'));$gateIds=array_unique(array_column($assignments,'gate_id')); $events=$eventIds?$db->table('events')->whereIn('id',$eventIds)->get()->getResultArray():[]; $days=$dayIds?$db->table('event_days')->whereIn('id',$dayIds)->get()->getResultArray():[]; $gates=$gateIds?$db->table('gates')->whereIn('id',$gateIds)->get()->getResultArray():[]; }
        return $this->render('scanner/index', compact('events','days','gates') + ['title'=>'Entry scanner']);
    }

    public function scan()
    {
        $payload = $this->request->getJSON(true) ?: $this->request->getPost();
        $db=db_connect(); $eventId=(int)($payload['event_id']??0);$dayId=(int)($payload['day_id']??0);$gateId=!empty($payload['gate_id'])?(int)$payload['gate_id']:null; $roles=session('roles')??[];
        if(!array_intersect($roles,['SUPER_ADMIN','EVENT_ADMIN'])) { $assigned=$db->table('scanner_assignments')->where(['user_id'=>(int)session('user_id'),'event_id'=>$eventId,'event_day_id'=>$dayId,'gate_id'=>$gateId,'is_active'=>1])->countAllResults(); if(!$assigned) return $this->response->setStatusCode(403)->setJSON(['ok'=>false,'status'=>'denied','message'=>'You are not assigned to this event, day and gate.']); }
        $result = (new AttendanceService($db))->scan((string)($payload['token'] ?? ''),$eventId,$dayId,$gateId,(int)session('user_id'));
        (new \App\Services\AuditService())->record('attendance.scan_'.$result['status'],'attendance',$result['registration']['registration_id']??null,['event_id'=>$eventId,'day_id'=>$dayId,'gate_id'=>$gateId]);
        $result['csrf']=csrf_hash();
        return $this->response->setJSON($result);
    }

    public function logout() { session()->destroy(); return redirect()->to('/scanner/login'); }
}