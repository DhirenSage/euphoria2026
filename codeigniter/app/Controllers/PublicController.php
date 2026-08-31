<?php

namespace App\Controllers;

use App\Models\CategoryModel;
use App\Models\EventModel;

class PublicController extends BaseController
{
    public function home()
    {
        $events = new EventModel();
        $categories = new CategoryModel();
        return $this->render('public/home', ['events'=>$events->published(), 'categories'=>$categories->where('is_active',1)->orderBy('display_order','ASC')->findAll(), 'title'=>'EUPHORIA 2026 | SAGE University Indore']);
    }

    public function events()
    {
        return $this->render('public/events', ['events'=>(new EventModel())->published(), 'title'=>'Explore events']);
    }

    public function event(string $slug)
    {
        $event = (new EventModel())->bySlug($slug);
        if (!$event) throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();
        $days = db_connect()->table('event_days')->where('event_id',$event['id'])->orderBy('event_date','ASC')->get()->getResultArray();
        $fields = db_connect()->table('registration_fields')->where('event_id',$event['id'])->orderBy('display_order','ASC')->get()->getResultArray();
        return $this->render('public/event', compact('event','days','fields') + ['title'=>$event['name'].' | EUPHORIA']);
    }

    public function category(string $slug)
    {
        $category = (new CategoryModel())->where('slug',$slug)->first();
        if (!$category) throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();
        $events = (new EventModel())->where('category_id',$category['id'])->whereIn('status',['registration_open','scheduled','live'])->findAll();
        return $this->render('public/category', compact('category','events') + ['title'=>$category['name'].' events']);
    }

    public function gallery() { return $this->render('public/standard', ['eyebrow'=>'EUPHORIA ARCHIVE','heading'=>'A festival in motion.','body'=>'Gallery albums will appear here as the Content Manager publishes them.','title'=>'Gallery']); }
    public function about() { return $this->render('public/standard', ['eyebrow'=>'THE PROGRAMME','heading'=>'Made for the makers.','body'=>'EUPHORIA is SAGE University Indore’s multi-day celebration of culture, sport, technology and the people who make campus unforgettable.','title'=>'About EUPHORIA']); }
    public function contact() { return $this->render('public/standard', ['eyebrow'=>'NEED A HAND?','heading'=>'Talk to the EUPHORIA desk.','body'=>'For registrations, venue queries or accessibility support, reach the programme team through the university events office.','title'=>'Contact']); }
    public function faq() { return $this->render('public/standard', ['eyebrow'=>'QUICK ANSWERS','heading'=>'Everything before the first beat.','body'=>'Bring your registration ID and keep your digital pass ready at the gate. Event-specific rules and deadlines live on each event page.','title'=>'FAQ']); }
    public function terms() { return $this->render('public/standard', ['eyebrow'=>'LEGAL','heading'=>'Participation terms.','body'=>'Programme participation is subject to the published event rules, eligibility criteria and venue safety requirements.','title'=>'Terms']); }
    public function privacy() { return $this->render('public/standard', ['eyebrow'=>'LEGAL','heading'=>'Your data, handled carefully.','body'=>'Registration data is used for event operations, payment reconciliation, passes and attendance. Production deployments should configure retention and access policies before launch.','title'=>'Privacy']); }
    public function refund() { return $this->render('public/standard', ['eyebrow'=>'PAYMENTS','heading'=>'Refund policy.','body'=>'Refund eligibility follows the event-specific policy shown during registration. Gateway reversals are processed only after server-side verification.','title'=>'Refund policy']); }
}