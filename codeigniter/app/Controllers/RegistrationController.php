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
        $categoryNames = ['Cultural','Literary and Management','Sci-Pha-Agro (The Magic of Science)','Sports'];
        $categories = db_connect()->table('categories')->select('id,name')->whereIn('name',$categoryNames)->where('is_active',1)->orderBy('display_order','ASC')->get()->getResultArray();
        $categoryIds = array_column($categories,'id');
        $events = $categoryIds ? db_connect()->table('events')->select('id,category_id,name,slug,fee,registration_type,min_team_size,max_team_size')->whereIn('category_id',$categoryIds)->where('status','registration_open')->orderBy('name','ASC')->get()->getResultArray() : [];
        return $this->render('registration/form', compact('event','categories','events') + ['title'=>'Register | Euphoria 2K26']);
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
        $rules = ['category_id'=>'required|is_natural_no_zero','event_id'=>'required|is_natural_no_zero','participant_name'=>'required|min_length[2]|max_length[160]','father_name'=>'permit_empty|min_length[2]|max_length[160]','email'=>'required|valid_email|max_length[190]','mobile'=>'required|regex_match[/^[6-9][0-9]{9}$/]','age'=>'permit_empty|integer|greater_than_equal_to[10]|less_than_equal_to[100]','college'=>'required|max_length[180]','city'=>'permit_empty|max_length[120]','participant_affiliation'=>'required|in_list[sageian,non_sageian]'];
        if (! $this->validateData($input, $rules)) return redirect()->back()->withInput()->with('error', implode(' ', $this->validator->getErrors()));
        if (!$event) return redirect()->back()->withInput()->with('error','Select a valid event from the chosen category.');
        try {
            $result = (new RegistrationService(db_connect()))->create($event, $input);
            session()->set('registration_token_'.$result['registration']['registration_id'], $result['token']);
            return redirect()->to('/registration/success/'.$result['registration']['registration_id']);
        } catch (RuntimeException $e) { return redirect()->back()->withInput()->with('error',$e->getMessage()); }
    }

    public function success(string $id)
    {
        $registration = db_connect()->table('registrations r')->select('r.*, e.name AS event_name, e.slug AS event_slug, c.name AS category_name, e.event_start, e.venue')->join('events e','e.id=r.event_id')->join('categories c','c.id=e.category_id')->where('r.registration_id',$id)->get()->getRowArray();
        if (!$registration) throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();
        $token = session('registration_token_'.$id);
        return $this->render('registration/success', compact('registration','token') + ['title'=>'Registration confirmed']);
    }

    public function pass(string $id)
    {
        $registration = db_connect()->table('registrations r')->select('r.*, e.name AS event_name, c.name AS category_name, e.event_start, e.venue, q.token_ciphertext')->join('events e','e.id=r.event_id')->join('categories c','c.id=e.category_id')->join('qr_tokens q','q.registration_id=r.id')->where('r.registration_id',$id)->where('r.status','confirmed')->get()->getRowArray();
        $token = session('registration_token_'.$id);
        if (!$token && session('user_id') && $registration && $registration['token_ciphertext']) $token = service('encrypter')->decrypt(base64_decode($registration['token_ciphertext'], true));
        if (!$registration || !$token) return redirect()->to('/events')->with('error','This pass is available from the confirmation device only.');
        $pass = new PassService();
        return $this->render('registration/pass', ['registration'=>$registration,'qr'=>$pass->qrDataUri($token),'token'=>$token,'title'=>'Digital pass']);
    }
}