<?php

namespace App\Database\Seeds;

use CodeIgniter\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    public function run()
    {
        $now = date('Y-m-d H:i:s');
        $db = $this->db;
        $db->table('roles')->insertBatch(array_map(fn($name)=>['name'=>$name], ['SUPER_ADMIN','PROGRAMME_ADMIN','EVENT_ADMIN','FINANCE','SCANNER','CONTENT_MANAGER','REPORT_VIEWER']));
        $db->table('users')->insert(['name'=>'Euphoria Demo Admin','email'=>'admin@euphoria.test','password_hash'=>password_hash('EuphoriaDemo!2026', PASSWORD_DEFAULT),'is_active'=>1,'created_at'=>$now,'updated_at'=>$now]);
        $adminId = $db->insertID(); $roleId = $db->table('roles')->where('name','SUPER_ADMIN')->get()->getRow('id'); $db->table('user_roles')->insert(['user_id'=>$adminId,'role_id'=>$roleId]);
        $db->table('users')->insert(['name'=>'Gate One Scanner','email'=>'scanner@euphoria.test','password_hash'=>password_hash('ScannerDemo!2026', PASSWORD_DEFAULT),'is_active'=>1,'created_at'=>$now,'updated_at'=>$now]);
        $scannerId = $db->insertID(); $roleId = $db->table('roles')->where('name','SCANNER')->get()->getRow('id'); $db->table('user_roles')->insert(['user_id'=>$scannerId,'role_id'=>$roleId]);
        $db->table('programmes')->insert(['name'=>'Euphoria 2026','slug'=>'euphoria-2026','year'=>2026,'description'=>'A multi-day student festival at SAGE University Indore.','status'=>'published','starts_on'=>'2026-09-15','ends_on'=>'2026-09-17','created_at'=>$now,'updated_at'=>$now]);
        $programmeId = $db->insertID();
        foreach ([['Cultural','culture','A stage for the bold and expressive.'],['Sports','sports','Play hard. Play fair. Play together.'],['Hackathon','hackathon','Build the future before lunch.'],['Technical','technical','Brains, bots and beautiful problems.'],['Competitions','competitions','A little pressure makes great stories.'],['Workshops','workshops','Learn something you can use tomorrow.']] as $i=>$cat) { $db->table('categories')->insert(['programme_id'=>$programmeId,'name'=>$cat[0],'slug'=>$cat[1],'description'=>$cat[2],'display_order'=>$i+1,'is_active'=>1,'created_at'=>$now,'updated_at'=>$now]); }
        $categories = $db->table('categories')->select('id,slug')->where('programme_id',$programmeId)->get()->getResultArray(); $cat = array_column($categories,'id','slug');
        $events = [['culture','Dance Competition','dance-competition','The floor is yours.','competition',500,'registration_open','Main auditorium'],['culture','Battle of Bands','battle-of-bands','Turn the volume into a memory.','competition',800,'scheduled','Open air stage'],['sports','Cricket','cricket','Your team. Your innings.','sports',1500,'registration_open','University ground'],['sports','Football','football','Ninety minutes. One campus.','sports',1200,'registration_open','University football ground'],['sports','Chess','chess','Every move changes the room.','competition',200,'registration_open','Seminar hall 2'],['hackathon','AI Hackathon','ai-hackathon','Ship a sharp idea with your team.','hackathon',500,'registration_open','Innovation lab'],['technical','Coding Challenge','coding-challenge','Think fast. Write clean.','competition',100,'scheduled','Computer centre'],['technical','Quiz','quiz','The buzzer is waiting.','quiz',100,'registration_open','Block A auditorium'],['workshops','Campus Photography Walk','photography-walk','Frame the campus your way.','workshop',0,'registration_open','Central lawn']];
        $eventIds=[];
        foreach ($events as $event) { $db->table('events')->insert(['category_id'=>$cat[$event[0]],'name'=>$event[1],'slug'=>$event[2],'short_description'=>$event[3],'description'=>'A high-energy Euphoria experience designed for students who want to participate, not just watch.','event_type'=>$event[4],'registration_type'=>str_contains($event[2],'cricket')||str_contains($event[2],'football')||str_contains($event[2],'hackathon')?'team':'individual','fee'=>$event[5],'capacity'=>200,'venue'=>$event[7],'event_start'=>'2026-09-15 10:00:00','event_end'=>'2026-09-17 18:00:00','status'=>$event[6],'is_featured'=>in_array($event[2],['dance-competition','ai-hackathon'],true),'created_at'=>$now,'updated_at'=>$now]); $eventId=$db->insertID(); $eventIds[$event[2]]=$eventId; foreach ([['Day 1','2026-09-15'],['Day 2','2026-09-16'],['Day 3','2026-09-17']] as $day) $db->table('event_days')->insert(['event_id'=>$eventId,'label'=>$day[0],'event_date'=>$day[1],'created_at'=>$now,'updated_at'=>$now]); foreach ([['Full name','participant_name','text',1],['Email address','email','email',1],['Mobile number','mobile','phone',1],['College / institution','college','text',0]] as $n=>$field) $db->table('registration_fields')->insert(['event_id'=>$eventId,'label'=>$field[0],'field_name'=>$field[1],'field_type'=>$field[2],'is_required'=>$field[3],'display_order'=>$n+1,'created_at'=>$now,'updated_at'=>$now]); }
        $db->table('gates')->insert(['programme_id'=>$programmeId,'name'=>'Gate 1 · Main Entry','is_active'=>1,'created_at'=>$now,'updated_at'=>$now]); $gateId=$db->insertID();
        $danceDay=$db->table('event_days')->where('event_id',$eventIds['dance-competition'])->orderBy('event_date','ASC')->get()->getRow('id');
        $db->table('scanner_assignments')->insert(['user_id'=>$scannerId,'event_id'=>$eventIds['dance-competition'],'event_day_id'=>$danceDay,'gate_id'=>$gateId,'is_active'=>1,'created_at'=>$now]);
        $permissions=['events.view','events.create','events.edit','events.delete','registrations.view','registrations.edit','payments.view','payments.verify','attendance.view','attendance.scan','reports.export','users.manage'];
        $db->table('permissions')->insertBatch(array_map(fn($name)=>['name'=>$name,'description'=>ucwords(str_replace('.',' ',$name))],$permissions));
        $db->table('email_templates')->insert(['template_key'=>'event_pass','subject'=>'Euphoria 2026 – Your Event Registration is Confirmed','body_html'=>'Your registration is confirmed. Please keep the attached QR pass ready at the entry gate.','is_active'=>1,'created_at'=>$now,'updated_at'=>$now]);
    }
}