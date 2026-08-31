<?php

namespace App\Controllers;

use App\Models\EventModel;
use App\Services\PassService;
use App\Services\RegistrationService;
use RuntimeException;

class RegistrationController extends BaseController
{
    public function create(string $slug)
    {
        $event = (new EventModel())->bySlug($slug);
        if (!$event || !in_array($event['status'], ['registration_open','scheduled'], true)) return redirect()->to('/events/'.$slug)->with('error','Registration for this event is closed.');
        $fields = db_connect()->table('registration_fields')->where('event_id',$event['id'])->orderBy('display_order','ASC')->get()->getResultArray();
        return $this->render('registration/form', compact('event','fields') + ['title'=>'Register | '.$event['name']]);
    }

    public function store(string $slug)
    {
        $event = (new EventModel())->bySlug($slug);
        if (!$event) throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();
        $rules = ['participant_name'=>'required|min_length[2]','email'=>'required|valid_email','mobile'=>'required|min_length[10]','college'=>'permit_empty|max_length[180]'];
        if (! $this->validate($rules)) return redirect()->back()->withInput()->with('error', implode(' ', $this->validator->getErrors()));
        try {
            $result = (new RegistrationService(db_connect()))->create($event, $this->request->getPost());
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