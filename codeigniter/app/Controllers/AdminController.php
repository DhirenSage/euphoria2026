<?php

namespace App\Controllers;

use App\Models\EventModel;
use App\Models\RegistrationModel;
use App\Services\AuditService;

class AdminController extends BaseController
{
    public function dashboard()
    {
        $db = db_connect();
        $stats = ['events'=>(new EventModel())->countAllResults(),'registrations'=>(new RegistrationModel())->countAllResults(),'confirmed'=>$db->table('registrations')->where('status','confirmed')->countAllResults(),'revenue'=>(float)$db->table('payments')->selectSum('amount')->where('status','success')->get()->getRow('amount'),'entries'=>$db->table('attendance')->where('status','allowed')->countAllResults()];
        return $this->render('admin/dashboard', ['stats'=>$stats,'recent'=>(new RegistrationModel())->withEvent(),'title'=>'Command centre']);
    }

    public function events() { return $this->render('admin/events', ['events'=>(new EventModel())->orderBy('created_at','DESC')->findAll(),'title'=>'Events']); }
    public function newEvent() { return $this->render('admin/event_form', ['title'=>'New event']); }
    public function storeEvent()
    {
        $data = $this->request->getPost(['category_id','name','slug','short_description','description','event_type','registration_type','fee','capacity','venue','status','is_featured']);
        if (empty($data['slug'])) $data['slug'] = safe_slug($data['name'] ?? 'event');
        $data['fee'] = (float)($data['fee'] ?? 0); $data['capacity'] = (int)($data['capacity'] ?? 0); $data['is_featured'] = !empty($data['is_featured']) ? 1 : 0;
        if ((new EventModel())->insert($data)) { (new AuditService())->record('event.created','events',(string)(new EventModel())->getInsertID()); return redirect()->to('/admin/events')->with('message','Event created.'); }
        return redirect()->back()->withInput()->with('error','Could not create event. Check the category and slug.');
    }
    public function registrations() { return $this->render('admin/registrations', ['registrations'=>(new RegistrationModel())->withEvent(),'title'=>'Registrations']); }
    public function attendance() { return $this->render('admin/attendance', ['entries'=>db_connect()->table('attendance a')->select('a.*, r.participant_name, r.registration_id, e.name AS event_name, g.name AS gate_name')->join('registrations r','r.id=a.registration_id')->join('events e','e.id=a.event_id')->join('gates g','g.id=a.gate_id','left')->orderBy('a.entry_time','DESC')->get(100)->getResultArray(),'title'=>'Live attendance']); }
    public function settings() { $service=new \App\Services\SettingsService(); return $this->render('admin/settings', ['settings'=>db_connect()->table('settings')->orderBy('setting_key','ASC')->get()->getResultArray(),'easebuzzConfigured'=>$service->isConfigured('EASEBUZZ_KEY','EASEBUZZ_KEY')&&$service->isConfigured('EASEBUZZ_SALT','EASEBUZZ_SALT'),'smtpConfigured'=>$service->isConfigured('SMTP_HOST','email.SMTPHost')&&$service->isConfigured('SMTP_USER','email.SMTPUser')&&$service->isConfigured('SMTP_PASSWORD','email.SMTPPass'),'title'=>'Platform settings']); }
    public function saveSettings() { (new \App\Services\SettingsService())->save($this->request->getPost('settings') ?? [],$this->request->getPost('secrets') ?? [],(int)session('user_id')); (new AuditService())->record('settings.updated','settings'); return redirect()->back()->with('message','Settings saved securely.'); }
    public function verifyPayment(string $id) { if(!array_intersect(session('roles')??[],['SUPER_ADMIN','FINANCE'])) return service('response')->setStatusCode(403)->setBody('Finance permission required'); $db=db_connect(); $payment=$db->table('payments')->where('id',(int)$id)->get()->getRowArray(); if(!$payment) throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound(); $db->transStart(); $changed=$db->table('payments')->where('id',(int)$id)->whereIn('status',['created','pending','initiated','unknown'])->update(['status'=>'success','paid_at'=>date('Y-m-d H:i:s'),'updated_at'=>date('Y-m-d H:i:s')]); $db->table('registrations')->where('id',$payment['registration_id'])->update(['status'=>'confirmed','updated_at'=>date('Y-m-d H:i:s')]); $db->transComplete(); if($changed){(new AuditService())->record('payment.manual_verified','payments',$id,['reason'=>(string)$this->request->getPost('reason')]);(new \App\Services\EmailQueueService())->enqueue((int)$payment['registration_id']);} return redirect()->back()->with('message','Payment marked successful manually. Audit recorded.'); }
}