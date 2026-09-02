<?php

namespace App\Controllers;

use App\Models\EventModel;
use App\Services\PassService;
use App\Services\RegistrationService;
use RuntimeException;

class RegistrationController extends BaseController
{
    public function create(?string $slug = null)
    {
        $event = $slug ? (new EventModel())->bySlug($slug) : null;
        if ($slug && (!$event || !in_array($event['status'], ['registration_open','scheduled'], true))) return redirect()->to('/events/'.$slug)->with('error','Registration for this event is closed.');
        $categories = db_connect()->table('categories c')->select('c.id,c.name')->join('programmes p','p.id=c.programme_id')->where('c.is_active',1)->where('p.status','published')->orderBy('c.display_order','ASC')->get()->getResultArray();
        $categoryIds = array_column($categories,'id');
        $events = $categoryIds ? db_connect()->table('events')->select('id,category_id,name,slug,fee,tax_amount,discount_amount,payment_required,registration_type,min_team_size,max_team_size')->whereIn('category_id',$categoryIds)->where('status','registration_open')->orderBy('name','ASC')->get()->getResultArray() : [];
        $eventIds=array_column($events,'id');
        $customFields=$eventIds?db_connect()->table('registration_fields')->whereIn('event_id',$eventIds)->where('is_active',1)->orderBy('display_order','ASC')->get()->getResultArray():[];
        return $this->render('registration/form', compact('event','categories','events','customFields') + ['title'=>'Register | Euphoria 2K26']);
    }

    public function store(?string $slug = null)
    {
        $input = $this->request->getPost();
        $input['participant_name'] = $input['participant_name'] ?? $input['name'] ?? '';
        $input['father_name'] = $input['father_name'] ?? $input['fathername'] ?? '';
        $input['email'] = $input['email'] ?? $input['mail'] ?? '';
        $input['mobile'] = $input['mobile'] ?? $input['mobile_no'] ?? '';
        $input['college'] = $input['college'] ?? $input['school_clg_name'] ?? '';
        $categoryId = (int)($input['category_id'] ?? 0);
        $eventId = (int)($input['event_id'] ?? 0);
        $event = (new EventModel())->select('events.*, categories.name AS category_name, categories.slug AS category_slug')->join('categories','categories.id=events.category_id')->where('events.id',$eventId)->where('events.category_id',$categoryId)->where('events.status','registration_open')->first();
        $rules = ['category_id'=>'required|is_natural_no_zero','event_id'=>'required|is_natural_no_zero','participant_name'=>'required|min_length[2]|max_length[160]','father_name'=>'permit_empty|min_length[2]|max_length[160]','email'=>'required|valid_email|max_length[190]','mobile'=>'required|regex_match[/^[6-9][0-9]{9}$/]','age'=>'permit_empty|integer|greater_than_equal_to[10]|less_than_equal_to[100]','college'=>'required|max_length[180]','city'=>'permit_empty|max_length[120]','participant_affiliation'=>'required|in_list[sageian,non_sageian]','terms'=>'required|in_list[1]'];
        if (! $this->validateData($input, $rules)) return redirect()->back()->withInput()->with('error', implode(' ', $this->validator->getErrors()));
        if (!$event) return redirect()->back()->withInput()->with('error','Select a valid event from the chosen category.');
        foreach(db_connect()->table('registration_fields')->where(['event_id'=>$eventId,'is_active'=>1,'field_type'=>'file'])->get()->getResultArray() as $field){$file=$this->request->getFile($field['field_name']);if(!$file||!$file->isValid()){if((int)$field['is_required'])return redirect()->back()->withInput()->with('error',$field['label'].' is required.');continue;}if($file->getSize()>5*1024*1024||!in_array($file->getMimeType(),['image/jpeg','image/png','application/pdf'],true))return redirect()->back()->withInput()->with('error',$field['label'].' must be a JPG, PNG or PDF up to 5 MB.');$name=bin2hex(random_bytes(18)).'.'.$file->getExtension();$file->move(WRITEPATH.'uploads/registrations',$name);$input[$field['field_name']]='registrations/'.$name;}
        try {
            $result = (new RegistrationService(db_connect()))->create($event, $input);
            session()->set('registration_token_'.$result['registration']['registration_id'], $result['token']);
            session()->set('pass_access_'.$result['registration']['registration_id'], $result['pass_access']);
            return redirect()->to('/registration/success/'.$result['registration']['registration_id']);
        } catch (RuntimeException $e) { return redirect()->back()->withInput()->with('error',$e->getMessage()); }
    }

    public function success(string $id)
    {
        $registration = db_connect()->table('registrations r')->select('r.*, e.name AS event_name, e.slug AS event_slug, c.name AS category_name, e.event_start, e.venue')->join('events e','e.id=r.event_id')->join('categories c','c.id=e.category_id')->where('r.registration_id',$id)->get()->getRowArray();
        if (!$registration) throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();
        $passAccess = session('pass_access_'.$id);
        return $this->render('registration/success', compact('registration','passAccess') + ['title'=>'Registration status']);
    }

    public function pass(string $id)
    {
        [$registration,$token]=$this->authorizedPass($id);
        if (!$registration || !$token) return redirect()->to('/events')->with('error','Use the secure pass link sent to the registered email address.');
        $pass = new PassService();
        $access=(string)($this->request->getGet('key')?:session('pass_access_'.$id));
        return $this->render('registration/pass', ['registration'=>$registration,'qr'=>$pass->qrDataUri($token),'token'=>$token,'passAccess'=>$access,'title'=>'Digital pass']);
    }

    public function downloadPass(string $id)
    {
        [$registration,$token]=$this->authorizedPass($id);
        if(!$registration||!$token) return redirect()->to('/events')->with('error','The secure pass link is invalid.');
        $path=(new PassService())->pdf($registration,$token);
        return $this->response->download($path,null)->setFileName($id.'-event-pass.pdf')->setContentType('application/pdf');
    }

    private function authorizedPass(string $id): array
    {
        $registration = db_connect()->table('registrations r')->select('r.*, e.name AS event_name, c.name AS category_name, e.event_start, e.venue, q.token_ciphertext')->join('events e','e.id=r.event_id')->join('categories c','c.id=e.category_id')->join('qr_tokens q','q.registration_id=r.id')->where('r.registration_id',$id)->where('r.status','confirmed')->where('r.qr_status','active')->where('q.status','active')->get()->getRowArray();
        if(!$registration)return [null,null];
        $access=(string)($this->request->getGet('key')?:session('pass_access_'.$id));
        $authorized=session('user_id')||($access!==''&&$registration['pass_access_hash']&&hash_equals($registration['pass_access_hash'],hash('sha256',$access)));
        if(!$authorized)return [null,null];
        $token=service('encrypter')->decrypt(base64_decode($registration['token_ciphertext'],true));
        return [$registration,$token];
    }
}