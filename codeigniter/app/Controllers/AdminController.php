<?php

namespace App\Controllers;

use App\Models\CategoryModel;
use App\Models\EventModel;
use App\Models\RegistrationModel;
use App\Services\AuditService;
use App\Services\EmailQueueService;
use App\Services\EventDeletionService;
use RuntimeException;

class AdminController extends BaseController
{
    public function dashboard()
    {
        $db = db_connect();
        $today=date('Y-m-d');
        $expected=(int)$db->table('registrations r')->join('event_days d','d.event_id=r.event_id')->where('r.status','confirmed')->where('d.event_date',$today)->countAllResults();
        $todayEntries=(int)$db->table('attendance a')->join('event_days d','d.id=a.event_day_id')->where('d.event_date',$today)->where('a.status','allowed')->countAllResults();
        $stats = [
            'events'=>(new EventModel())->countAllResults(),
            'categories'=>(new CategoryModel())->where('is_active',1)->countAllResults(),
            'registrations'=>(new RegistrationModel())->countAllResults(),
            'confirmed'=>$db->table('registrations')->where('status','confirmed')->countAllResults(),
            'pending'=>$db->table('registrations')->where('status','pending_payment')->countAllResults(),
            'revenue'=>(float)($db->table('payments')->selectSum('amount')->where('status','success')->get()->getRow('amount')??0),
            'expected'=>$expected,
            'entries'=>$todayEntries,
            'attendance_percent'=>$expected>0?round(($todayEntries/$expected)*100,1):0,
            'duplicates'=>$db->table('scan_attempts')->where('status','duplicate')->where('attempted_at >=',$today.' 00:00:00')->countAllResults(),
            'invalid'=>$db->table('scan_attempts')->where('status','denied')->where('attempted_at >=',$today.' 00:00:00')->countAllResults(),
        ];
        $topEvents=$db->table('events e')->select('e.name, COUNT(r.id) AS registrations, COALESCE(SUM(CASE WHEN p.status="success" THEN p.amount ELSE 0 END),0) AS revenue')->join('registrations r','r.event_id=e.id','left')->join('payments p','p.registration_id=r.id','left')->groupBy('e.id')->orderBy('registrations','DESC')->get(6)->getResultArray();
        $recentScans=$db->table('scan_attempts s')->select('s.*, r.participant_name, r.registration_id, e.name AS event_name, g.name AS gate_name, u.name AS scanner_name')->join('registrations r','r.id=s.registration_id','left')->join('events e','e.id=s.event_id','left')->join('gates g','g.id=s.gate_id','left')->join('users u','u.id=s.scanner_user_id','left')->orderBy('s.attempted_at','DESC')->get(8)->getResultArray();
        return $this->render('admin/dashboard', ['stats'=>$stats,'recent'=>(new RegistrationModel())->withEvent(),'topEvents'=>$topEvents,'recentScans'=>$recentScans,'today'=>$today,'title'=>'Command centre']);
    }

    public function categories()
    {
        $categories=(new CategoryModel())->select('categories.*, programmes.name AS programme_name, COUNT(events.id) AS event_count')->join('programmes','programmes.id=categories.programme_id')->join('events','events.category_id=categories.id','left')->groupBy('categories.id')->orderBy('display_order','ASC')->findAll();
        return $this->render('admin/categories',['categories'=>$categories,'programmes'=>db_connect()->table('programmes')->where('status !=','archived')->get()->getResultArray(),'title'=>'Categories']);
    }

    public function storeCategory()
    {
        $this->requireAny(['SUPER_ADMIN','PROGRAMME_ADMIN','EVENT_ADMIN']);
        $data=$this->categoryData();
        if(!(new CategoryModel())->insert($data))return redirect()->back()->withInput()->with('error','Could not create category. Check the name and slug.');
        (new AuditService())->record('category.created','categories',(string)db_connect()->insertID());
        return redirect()->to('/admin/categories')->with('message','Category created.');
    }

    public function updateCategory(int $id)
    {
        $this->requireAny(['SUPER_ADMIN','PROGRAMME_ADMIN','EVENT_ADMIN']);
        if(!(new CategoryModel())->find($id))throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();
        (new CategoryModel())->update($id,$this->categoryData());
        (new AuditService())->record('category.updated','categories',(string)$id);
        return redirect()->to('/admin/categories')->with('message','Category updated.');
    }

    public function deleteCategory(int $id)
    {
        $this->requireAny(['SUPER_ADMIN','PROGRAMME_ADMIN']);
        $count=db_connect()->table('events')->where('category_id',$id)->countAllResults();
        if($count>0)return redirect()->back()->with('error','Archive or move this category’s events before deleting it.');
        (new CategoryModel())->delete($id);
        (new AuditService())->record('category.deleted','categories',(string)$id);
        return redirect()->to('/admin/categories')->with('message','Category deleted.');
    }

    public function events()
    {
        $query=trim((string)$this->request->getGet('q'));$status=(string)$this->request->getGet('status');$categoryId=(int)$this->request->getGet('category_id');$model=(new EventModel())->select('events.*, categories.name AS category_name')->join('categories','categories.id=events.category_id');if($query!=='')$model->groupStart()->like('events.name',$query)->orLike('events.slug',$query)->groupEnd();if($status!=='')$model->where('events.status',$status);if($categoryId)$model->where('events.category_id',$categoryId);$events=$model->orderBy('events.created_at','DESC')->paginate(25,'events');
        return $this->render('admin/events',['events'=>$events,'pager'=>$model->pager,'categories'=>$this->activeCategories(),'filters'=>['q'=>$query,'status'=>$status,'category_id'=>$categoryId],'title'=>'Events','active'=>'events']);
    }

    public function newEvent()
    {
        $this->requireAny(['SUPER_ADMIN','PROGRAMME_ADMIN','EVENT_ADMIN']);
        return $this->render('admin/event_form', ['event'=>null,'categories'=>$this->activeCategories(),'days'=>[],'fields'=>[],'title'=>'New event']);
    }

    public function storeEvent()
    {
        $this->requireAny(['SUPER_ADMIN','PROGRAMME_ADMIN','EVENT_ADMIN']);
        try { $id=$this->persistEvent(); return redirect()->to('/admin/events/'.$id.'/edit')->with('message','Event created and published configuration saved.'); }
        catch(RuntimeException $e){return redirect()->back()->withInput()->with('error',$e->getMessage());}
    }

    public function editEvent(int $id)
    {
        $event=(new EventModel())->find($id);if(!$event)throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();
        $this->requireAny(['SUPER_ADMIN','PROGRAMME_ADMIN','EVENT_ADMIN']);
        $db=db_connect();return $this->render('admin/event_form',['event'=>$event,'categories'=>$this->activeCategories(),'days'=>$db->table('event_days')->where('event_id',$id)->where('is_active',1)->orderBy('event_date','ASC')->get()->getResultArray(),'fields'=>$db->table('registration_fields')->where('event_id',$id)->where('is_active',1)->orderBy('display_order','ASC')->get()->getResultArray(),'title'=>'Edit '.$event['name']]);
    }

    public function updateEvent(int $id)
    {
        $this->requireAny(['SUPER_ADMIN','PROGRAMME_ADMIN','EVENT_ADMIN']);
        if(!(new EventModel())->find($id))throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();
        try{$this->persistEvent($id);return redirect()->to('/admin/events/'.$id.'/edit')->with('message','Event configuration updated.');}
        catch(RuntimeException $e){return redirect()->back()->withInput()->with('error',$e->getMessage());}
    }

    public function deleteEvent(int $id)
    {
        $this->requireAny(['SUPER_ADMIN']);$event=(new EventModel())->find($id);if(!$event)throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();if(!hash_equals($event['name'],trim((string)$this->request->getPost('confirm_name'))))return redirect()->back()->with('error','Permanent deletion cancelled: type the exact event name.');try{$result=(new EventDeletionService(db_connect()))->deleteMany([$id]);(new AuditService())->record('event.permanently_deleted','events',(string)$id,['event_name'=>$event['name'],'registrations'=>$result['registrations']]);return redirect()->to(base_url('admin/events'))->with('message','Event and '.$result['registrations'].' related registrations permanently deleted.');}catch(RuntimeException $e){return redirect()->back()->with('error',$e->getMessage());}
    }

    public function bulkDeleteEvents()
    {
        $this->requireAny(['SUPER_ADMIN']);if((string)$this->request->getPost('confirm_phrase')!=='DELETE SELECTED')return redirect()->back()->with('error','Bulk deletion cancelled: type DELETE SELECTED exactly.');try{$result=(new EventDeletionService(db_connect()))->deleteMany((array)$this->request->getPost('event_ids'));(new AuditService())->record('events.bulk_permanently_deleted','events',null,$result);return redirect()->to(base_url('admin/events'))->with('message',$result['events'].' events and '.$result['registrations'].' related registrations permanently deleted.');}catch(RuntimeException $e){return redirect()->back()->with('error',$e->getMessage());}
    }

    public function registrations() { return $this->render('admin/registrations', ['registrations'=>(new RegistrationModel())->withEvent(),'title'=>'Registrations']); }

    public function registration(string $code)
    {
        $db=db_connect();$registration=$db->table('registrations r')->select('r.*,e.name AS event_name,e.slug AS event_slug,c.name AS category_name,p.status AS payment_status,p.txnid,p.gateway_payment_id,p.paid_at,q.status AS token_status,q.token_hint')->join('events e','e.id=r.event_id')->join('categories c','c.id=e.category_id')->join('payments p','p.registration_id=r.id','left')->join('qr_tokens q','q.registration_id=r.id','left')->where('r.registration_id',$code)->get()->getRowArray();
        if(!$registration)throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();
        $attendance=$db->table('event_days d')->select('d.label,d.event_date,a.entry_time,a.status,g.name AS gate_name,u.name AS scanner_name')->join('attendance a','a.event_day_id=d.id AND a.registration_id='.(int)$registration['id'],'left')->join('gates g','g.id=a.gate_id','left')->join('users u','u.id=a.scanner_user_id','left')->where('d.event_id',$registration['event_id'])->orderBy('d.event_date','ASC')->get()->getResultArray();
        $members=$db->table('registration_members')->where('registration_id',$registration['id'])->get()->getResultArray();
        $values=$db->table('registration_field_values v')->select('f.label,v.value_text')->join('registration_fields f','f.id=v.field_id')->where('v.registration_id',$registration['id'])->orderBy('f.display_order','ASC')->get()->getResultArray();
        return $this->render('admin/registration_detail',compact('registration','attendance','members','values')+['title'=>'Registration '.$code]);
    }

    public function registrationStatus(string $code)
    {
        $this->requireAny(['SUPER_ADMIN','PROGRAMME_ADMIN','EVENT_ADMIN']);
        $action=(string)$this->request->getPost('action');$db=db_connect();$registration=$db->table('registrations')->where('registration_id',$code)->get()->getRowArray();if(!$registration)throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();
        if($action==='cancel'){$db->table('registrations')->where('id',$registration['id'])->update(['status'=>'cancelled','qr_status'=>'cancelled','updated_at'=>date('Y-m-d H:i:s')]);$db->table('qr_tokens')->where('registration_id',$registration['id'])->update(['status'=>'revoked','revoked_at'=>date('Y-m-d H:i:s')]);}
        elseif($action==='revoke'){$db->table('registrations')->where('id',$registration['id'])->update(['qr_status'=>'suspended','updated_at'=>date('Y-m-d H:i:s')]);$db->table('qr_tokens')->where('registration_id',$registration['id'])->update(['status'=>'revoked','revoked_at'=>date('Y-m-d H:i:s')]);}
        elseif($action==='restore'){$paid=$db->table('payments')->where('registration_id',$registration['id'])->where('status','success')->countAllResults();if(!$paid)return redirect()->back()->with('error','A successful payment is required before restoring this registration.');$db->table('registrations')->where('id',$registration['id'])->update(['status'=>'confirmed','qr_status'=>'active','updated_at'=>date('Y-m-d H:i:s')]);$db->table('qr_tokens')->where('registration_id',$registration['id'])->update(['status'=>'active','revoked_at'=>null]);}
        elseif($action==='resend'){(new EmailQueueService())->enqueue((int)$registration['id']);}
        else return redirect()->back()->with('error','Unknown registration action.');
        (new AuditService())->record('registration.'.$action,'registrations',$code);
        return redirect()->back()->with('message','Registration action completed.');
    }

    public function attendance()
    {
        $db=db_connect();$date=(string)$this->request->getGet('date');if(!preg_match('/^\d{4}-\d{2}-\d{2}$/',$date))$date=date('Y-m-d');$eventId=(int)$this->request->getGet('event_id');$status=(string)$this->request->getGet('status');$events=$db->table('events')->select('id,name')->orderBy('name','ASC')->get()->getResultArray();
        $builder=$db->table('registrations r')->select('r.registration_id,r.participant_name,r.email,r.mobile,r.college,e.id event_id,e.name event_name,d.id event_day_id,d.label event_day_label,d.event_date,a.entry_time,u.name scanner_name')->join('events e','e.id=r.event_id')->join('event_days d','d.event_id=e.id AND d.event_date='.$db->escape($date).' AND d.is_active=1')->join('attendance a','a.registration_id=r.id AND a.event_day_id=d.id','left')->join('users u','u.id=a.scanner_user_id','left')->where('r.status','confirmed');if($eventId)$builder->where('e.id',$eventId);if($status==='entered')$builder->where('a.id IS NOT NULL',null,false);if($status==='not_entered')$builder->where('a.id IS NULL',null,false);$roster=$builder->orderBy('e.name','ASC')->orderBy('r.participant_name','ASC')->get()->getResultArray();
        $summaryBuilder=$db->table('registrations r')->select('COUNT(*) total, SUM(CASE WHEN a.id IS NULL THEN 0 ELSE 1 END) entered',false)->join('event_days d','d.event_id=r.event_id AND d.event_date='.$db->escape($date).' AND d.is_active=1')->join('attendance a','a.registration_id=r.id AND a.event_day_id=d.id','left')->where('r.status','confirmed');if($eventId)$summaryBuilder->where('r.event_id',$eventId);$summary=$summaryBuilder->get()->getRowArray()?:['total'=>0,'entered'=>0];
        return $this->render('admin/attendance',['roster'=>$roster,'events'=>$events,'selectedDate'=>$date,'selectedEvent'=>$eventId,'selectedStatus'=>$status?:'all','summary'=>['total'=>(int)$summary['total'],'entered'=>(int)$summary['entered'],'not_entered'=>(int)$summary['total']-(int)$summary['entered']],'title'=>'Date-wise attendance','active'=>'attendance']);
    }

    public function scanners()
    {
        $this->requireAny(['SUPER_ADMIN']);$db=db_connect();$scanners=$db->table('users u')->select('u.id,u.name,u.email,u.is_active,u.created_at')->join('user_roles ur','ur.user_id=u.id')->join('roles r','r.id=ur.role_id')->where('r.name','SCANNER')->orderBy('u.name','ASC')->get()->getResultArray();return $this->render('admin/scanners',['scanners'=>$scanners,'title'=>'Scanner users','active'=>'scanners']);
    }

    public function storeScanner()
    {
        $this->requireAny(['SUPER_ADMIN']);$name=trim((string)$this->request->getPost('name'));$email=strtolower(trim((string)$this->request->getPost('email')));$password=(string)$this->request->getPost('password');if(mb_strlen($name)<2||!filter_var($email,FILTER_VALIDATE_EMAIL)||strlen($password)<12)return redirect()->back()->withInput()->with('error','Enter a name, unique email and password of at least 12 characters.');$db=db_connect();if($db->table('users')->where('email',$email)->countAllResults())return redirect()->back()->with('error','That login email already exists.');$db->transStart();$db->table('users')->insert(['name'=>$name,'email'=>$email,'password_hash'=>password_hash($password,PASSWORD_DEFAULT),'is_active'=>1,'created_at'=>date('Y-m-d H:i:s'),'updated_at'=>date('Y-m-d H:i:s')]);$userId=(int)$db->insertID();$roleId=(int)$db->table('roles')->where('name','SCANNER')->get()->getRow('id');$db->table('user_roles')->insert(['user_id'=>$userId,'role_id'=>$roleId]);$db->transComplete();(new AuditService())->record('scanner.created','users',(string)$userId,['email'=>$email]);return redirect()->back()->with('message','Scanner login created. It can scan every event automatically.');
    }

    public function toggleScanner(int $id)
    {
        $this->requireAny(['SUPER_ADMIN']);$db=db_connect();$scanner=$db->table('users u')->select('u.id,u.is_active')->join('user_roles ur','ur.user_id=u.id')->join('roles r','r.id=ur.role_id')->where(['u.id'=>$id,'r.name'=>'SCANNER'])->get()->getRowArray();if(!$scanner)throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();$active=(int)!((int)$scanner['is_active']);$db->table('users')->where('id',$id)->update(['is_active'=>$active,'updated_at'=>date('Y-m-d H:i:s')]);(new AuditService())->record('scanner.'.($active?'enabled':'disabled'),'users',(string)$id);return redirect()->back()->with('message','Scanner access updated.');
    }

    public function storeGate()
    {
        $this->requireAny(['SUPER_ADMIN','PROGRAMME_ADMIN']);$name=trim((string)$this->request->getPost('name'));$programmeId=(int)$this->request->getPost('programme_id');if($name===''||$programmeId<1)return redirect()->back()->with('error','Programme and gate name are required.');$db=db_connect();$db->table('gates')->insert(['programme_id'=>$programmeId,'name'=>$name,'is_active'=>1,'created_at'=>date('Y-m-d H:i:s'),'updated_at'=>date('Y-m-d H:i:s')]);(new AuditService())->record('gate.created','gates',(string)$db->insertID());return redirect()->back()->with('message','Gate created.');
    }

    public function storeScannerAssignment()
    {
        $this->requireAny(['SUPER_ADMIN','PROGRAMME_ADMIN','EVENT_ADMIN']);$db=db_connect();$userId=(int)$this->request->getPost('user_id');$eventId=(int)$this->request->getPost('event_id');$dayId=(int)$this->request->getPost('event_day_id');$gateId=(int)$this->request->getPost('gate_id');$validScanner=$db->table('user_roles ur')->join('roles r','r.id=ur.role_id')->where(['ur.user_id'=>$userId,'r.name'=>'SCANNER'])->countAllResults();$validDay=$db->table('event_days')->where(['id'=>$dayId,'event_id'=>$eventId,'is_active'=>1])->countAllResults();$validGate=$db->table('gates')->where(['id'=>$gateId,'is_active'=>1])->countAllResults();if(!$validScanner||!$validDay||!$validGate)return redirect()->back()->with('error','Select a valid scanner, event day and active gate.');try{$db->table('scanner_assignments')->insert(['user_id'=>$userId,'event_id'=>$eventId,'event_day_id'=>$dayId,'gate_id'=>$gateId,'is_active'=>1,'created_at'=>date('Y-m-d H:i:s')]);}catch(\Throwable){return redirect()->back()->with('error','That scanner assignment already exists.');}(new AuditService())->record('scanner.assignment_created','scanner_assignments',(string)$db->insertID(),['event_id'=>$eventId,'day_id'=>$dayId,'gate_id'=>$gateId]);return redirect()->back()->with('message','Scanner assignment created.');
    }

    public function deleteScannerAssignment(int $id)
    {
        $this->requireAny(['SUPER_ADMIN','PROGRAMME_ADMIN','EVENT_ADMIN']);db_connect()->table('scanner_assignments')->where('id',$id)->update(['is_active'=>0]);(new AuditService())->record('scanner.assignment_revoked','scanner_assignments',(string)$id);return redirect()->back()->with('message','Scanner assignment revoked.');
    }

    public function reports()
    {
        $db=db_connect();$eventId=(int)$this->request->getGet('event_id');$dayId=(int)$this->request->getGet('day_id');
        $builder=$db->table('attendance a')->select('a.*,r.participant_name,r.registration_id,r.registration_type,e.name AS event_name,c.name AS category_name,d.label AS day_label,d.event_date,g.name AS gate_name,u.name AS scanner_name')->join('registrations r','r.id=a.registration_id')->join('events e','e.id=a.event_id')->join('categories c','c.id=e.category_id')->join('event_days d','d.id=a.event_day_id')->join('gates g','g.id=a.gate_id','left')->join('users u','u.id=a.scanner_user_id','left');if($eventId)$builder->where('a.event_id',$eventId);if($dayId)$builder->where('a.event_day_id',$dayId);$rows=$builder->orderBy('a.entry_time','DESC')->get(500)->getResultArray();
        return $this->render('admin/reports',['rows'=>$rows,'events'=>(new EventModel())->orderBy('name')->findAll(),'days'=>$db->table('event_days')->orderBy('event_date')->get()->getResultArray(),'filters'=>['event_id'=>$eventId,'day_id'=>$dayId],'title'=>'Reports']);
    }

    public function payments()
    {
        $this->requireAny(['SUPER_ADMIN','PROGRAMME_ADMIN','FINANCE']);$db=db_connect();$status=(string)$this->request->getGet('status');$eventId=(int)$this->request->getGet('event_id');$builder=$db->table('payments p')->select('p.*,r.registration_id,r.participant_name,r.email,e.name event_name')->join('registrations r','r.id=p.registration_id')->join('events e','e.id=r.event_id');if($status!=='')$builder->where('p.status',$status);if($eventId)$builder->where('e.id',$eventId);$rows=$builder->orderBy('p.created_at','DESC')->limit(500)->get()->getResultArray();return $this->render('admin/payments',['payments'=>$rows,'events'=>(new EventModel())->orderBy('name')->findAll(),'filters'=>['status'=>$status,'event_id'=>$eventId],'title'=>'Payments','active'=>'payments']);
    }

    public function entryTracking()
    {
        $this->requireAny(['SUPER_ADMIN','PROGRAMME_ADMIN','EVENT_ADMIN','REPORT_VIEWER']);$db=db_connect();$date=(string)$this->request->getGet('date');if(!preg_match('/^\d{4}-\d{2}-\d{2}$/',$date))$date=date('Y-m-d');$status=(string)$this->request->getGet('status');$eventId=(int)$this->request->getGet('event_id');$builder=$db->table('scan_attempts a')->select('a.*,r.participant_name,r.registration_id,e.name event_name,d.label day_label,d.event_date,u.name scanner_name')->join('registrations r','r.id=a.registration_id','left')->join('events e','e.id=a.event_id','left')->join('event_days d','d.id=a.event_day_id','left')->join('users u','u.id=a.scanner_user_id','left')->where('DATE(a.attempted_at)',$date);if($status!=='')$builder->where('a.status',$status);if($eventId)$builder->where('a.event_id',$eventId);$rows=$builder->orderBy('a.attempted_at','DESC')->limit(500)->get()->getResultArray();return $this->render('admin/entry_tracking',['rows'=>$rows,'events'=>(new EventModel())->orderBy('name')->findAll(),'filters'=>['date'=>$date,'status'=>$status,'event_id'=>$eventId],'title'=>'Entry tracking','active'=>'entry-tracking']);
    }

    public function exportAttendance()
    {
        $db=db_connect();$rows=$db->table('attendance a')->select('r.participant_name,r.registration_id,r.email,r.mobile,e.name AS event_name,c.name AS category_name,d.label AS day_label,d.event_date,a.entry_time,g.name AS gate_name,u.name AS scanner_name,a.status')->join('registrations r','r.id=a.registration_id')->join('events e','e.id=a.event_id')->join('categories c','c.id=e.category_id')->join('event_days d','d.id=a.event_day_id')->join('gates g','g.id=a.gate_id','left')->join('users u','u.id=a.scanner_user_id','left')->orderBy('a.entry_time','DESC')->get()->getResultArray();
        $stream=fopen('php://temp','r+');fputcsv($stream,['Participant','Registration ID','Email','Mobile','Event','Category','Day','Date','Entry time','Gate','Scanner','Status']);foreach($rows as $row)fputcsv($stream,array_values($row));rewind($stream);$csv=stream_get_contents($stream);fclose($stream);(new AuditService())->record('report.exported','attendance',null,['rows'=>count($rows)]);return $this->response->download('euphoria-attendance-'.date('Ymd-His').'.csv',$csv);
    }

    public function settings() { $this->requireAny(['SUPER_ADMIN']);$service=new \App\Services\SettingsService(); return $this->render('admin/settings', ['settings'=>db_connect()->table('settings')->orderBy('setting_key','ASC')->get()->getResultArray(),'easebuzzConfigured'=>$service->isConfigured('EASEBUZZ_KEY','EASEBUZZ_KEY')&&$service->isConfigured('EASEBUZZ_SALT','EASEBUZZ_SALT'),'smtpConfigured'=>$service->isConfigured('SMTP_HOST','email.SMTPHost')&&$service->isConfigured('SMTP_USER','email.SMTPUser')&&$service->isConfigured('SMTP_PASSWORD','email.SMTPPass'),'title'=>'Platform settings']); }
    public function saveSettings() { $this->requireAny(['SUPER_ADMIN']);(new \App\Services\SettingsService())->save($this->request->getPost('settings') ?? [],$this->request->getPost('secrets') ?? [],(int)session('user_id')); (new AuditService())->record('settings.updated','settings'); return redirect()->back()->with('message','Settings saved securely.'); }
    public function testEmail(){$this->requireAny(['SUPER_ADMIN']);try{(new EmailQueueService())->sendTest((string)$this->request->getPost('recipient'));(new AuditService())->record('smtp.test_sent','settings');return redirect()->back()->with('message','SMTP test message accepted by the provider.');}catch(\Throwable $e){return redirect()->back()->with('error','SMTP test failed: '.$e->getMessage());}}
    public function verifyPayment(string $id) { if(!array_intersect(session('roles')??[],['SUPER_ADMIN','FINANCE'])) return service('response')->setStatusCode(403)->setBody('Finance permission required'); $db=db_connect(); $payment=$db->table('payments')->where('id',(int)$id)->get()->getRowArray(); if(!$payment) throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound(); $db->transStart(); $changed=$db->table('payments')->where('id',(int)$id)->whereIn('status',['created','pending','initiated','unknown'])->update(['status'=>'success','paid_at'=>date('Y-m-d H:i:s'),'updated_at'=>date('Y-m-d H:i:s')]); $db->table('registrations')->where('id',$payment['registration_id'])->update(['status'=>'confirmed','updated_at'=>date('Y-m-d H:i:s')]); $db->transComplete(); if($changed){(new AuditService())->record('payment.manual_verified','payments',$id,['reason'=>(string)$this->request->getPost('reason')]);(new \App\Services\EmailQueueService())->enqueue((int)$payment['registration_id']);} return redirect()->back()->with('message','Payment marked successful manually. Audit recorded.'); }

    private function persistEvent(?int $id=null): int
    {
        $post=$this->request->getPost();$name=trim((string)($post['name']??''));$categoryId=(int)($post['category_id']??0);if($name===''||$categoryId<1)throw new RuntimeException('Event name and category are required.');if(!(new CategoryModel())->find($categoryId))throw new RuntimeException('Select a valid category.');
        $data=[];foreach(['category_id','name','slug','short_description','description','banner_path','thumbnail_path','event_type','registration_type','sageian_fee','non_sageian_fee','tax_amount','discount_amount','capacity','min_team_size','max_team_size','registration_start','registration_end','event_start','event_end','venue','eligibility','rules','prizes','refund_policy','contact_details','status'] as $field)$data[$field]=$post[$field]??null;
        $data['category_id']=$categoryId;$data['name']=$name;$data['slug']=safe_slug((string)($data['slug']?:$name));$data['sageian_fee']=max(0,(float)$data['sageian_fee']);$data['non_sageian_fee']=max(0,(float)$data['non_sageian_fee']);$data['fee']=$data['non_sageian_fee'];$data['tax_amount']=max(0,(float)$data['tax_amount']);$data['discount_amount']=max(0,(float)$data['discount_amount']);$data['capacity']=max(0,(int)$data['capacity']);$data['payment_required']=!empty($post['payment_required'])&&max($data['sageian_fee'],$data['non_sageian_fee'])>0?1:0;$data['is_featured']=!empty($post['is_featured'])?1:0;foreach(['registration_start','registration_end','event_start','event_end'] as $field)$data[$field]=$this->dateTimeOrNull($data[$field]);
        $db=db_connect();$db->transStart();$model=new EventModel();if($id){if(!$model->update($id,$data))throw new RuntimeException('Could not update event. Check that the slug is unique.');}else{if(!$model->insert($data))throw new RuntimeException('Could not create event. Check that the slug is unique.');$id=(int)$model->getInsertID();}
        $db->table('event_days')->where('event_id',$id)->update(['is_active'=>0,'updated_at'=>date('Y-m-d H:i:s')]);$labels=$post['day_label']??[];$dates=$post['day_date']??[];foreach($dates as $index=>$date){if(!$date)continue;$dayData=['label'=>trim((string)($labels[$index]??('Day '.($index+1)))),'is_active'=>1,'updated_at'=>date('Y-m-d H:i:s')];$existingDay=$db->table('event_days')->where(['event_id'=>$id,'event_date'=>$date])->get()->getRowArray();if($existingDay)$db->table('event_days')->where('id',$existingDay['id'])->update($dayData);else$db->table('event_days')->insert($dayData+['event_id'=>$id,'event_date'=>$date,'created_at'=>date('Y-m-d H:i:s')]);}
        $db->table('registration_fields')->where('event_id',$id)->update(['is_active'=>0,'updated_at'=>date('Y-m-d H:i:s')]);$fieldLabels=$post['field_label']??[];$fieldNames=$post['field_name']??[];$fieldTypes=$post['field_type']??[];$fieldOptions=$post['field_options']??[];$required=$post['field_required']??[];foreach($fieldLabels as $index=>$label){$label=trim((string)$label);if($label==='')continue;$fieldName=safe_slug((string)($fieldNames[$index]??$label));$fieldName=str_replace('-','_',$fieldName);$type=in_array(($fieldTypes[$index]??'text'),['text','number','email','phone','date','select','radio','checkbox','textarea','file'],true)?$fieldTypes[$index]:'text';$options=array_values(array_filter(array_map('trim',explode(',',(string)($fieldOptions[$index]??'')))));$fieldData=['label'=>$label,'field_type'=>$type,'options_json'=>$options?json_encode($options):null,'is_required'=>in_array((string)$index,array_map('strval',(array)$required),true)?1:0,'is_active'=>1,'display_order'=>$index+1,'updated_at'=>date('Y-m-d H:i:s')];$existingField=$db->table('registration_fields')->where(['event_id'=>$id,'field_name'=>$fieldName])->get()->getRowArray();if($existingField)$db->table('registration_fields')->where('id',$existingField['id'])->update($fieldData);else$db->table('registration_fields')->insert($fieldData+['event_id'=>$id,'field_name'=>$fieldName,'created_at'=>date('Y-m-d H:i:s')]);}
        $db->transComplete();if(!$db->transStatus())throw new RuntimeException('Could not save the complete event configuration.');(new AuditService())->record($post['id']??null?'event.updated':'event.created','events',(string)$id);return $id;
    }

    private function categoryData(): array
    {
        $post=$this->request->getPost();$name=trim((string)($post['name']??''));if($name==='')throw new RuntimeException('Category name is required.');return ['programme_id'=>(int)($post['programme_id']??1),'name'=>$name,'slug'=>safe_slug((string)($post['slug']?:$name)),'description'=>trim((string)($post['description']??'')),'icon'=>trim((string)($post['icon']??'')),'display_order'=>(int)($post['display_order']??0),'is_active'=>!empty($post['is_active'])?1:0];
    }

    private function activeCategories(): array{return (new CategoryModel())->where('is_active',1)->orderBy('display_order','ASC')->findAll();}
    private function dateTimeOrNull($value): ?string{$value=trim((string)$value);if($value==='')return null;return str_replace('T',' ',$value).(strlen($value)===16?':00':'');}
    private function requireAny(array $roles): void{if(!array_intersect($roles,session('roles')??[]))throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();}
}