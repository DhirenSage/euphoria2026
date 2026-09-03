<?php

namespace App\Controllers;

use App\Models\CategoryModel;
use App\Models\EventModel;
use App\Models\MediaItemModel;

class PublicController extends BaseController
{
    public function home()
    {
        $events = new EventModel();
        $categories = new CategoryModel();
        $published=$events->published();$media=$this->mediaRows();$days=[];foreach($published as $event){$eventDays=db_connect()->table('event_days')->where(['event_id'=>$event['id'],'is_active'=>1])->orderBy('event_date','ASC')->get()->getResultArray();foreach($eventDays as $day)$days[$day['event_date']][]=$event+['day'=>$day];}ksort($days);
        return $this->render('public/home', ['events'=>$published, 'categories'=>$categories->where('is_active',1)->orderBy('display_order','ASC')->findAll(), 'media'=>$media, 'schedule'=>$days, 'title'=>'EUPHORIA 2026 | SAGE University Indore']);
    }

    public function events()
    {
        return $this->render('public/events', ['events'=>(new EventModel())->published(), 'title'=>'Explore events']);
    }

    public function event(string $slug)
    {
        $event = (new EventModel())->bySlug($slug);
        if (!$event) throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();
        $days = db_connect()->table('event_days')->where('event_id',$event['id'])->where('is_active',1)->orderBy('event_date','ASC')->get()->getResultArray();
        $fields = db_connect()->table('registration_fields')->where('event_id',$event['id'])->where('is_active',1)->orderBy('display_order','ASC')->get()->getResultArray();
        return $this->render('public/event', compact('event','days','fields') + ['title'=>$event['name'].' | EUPHORIA']);
    }

    public function category(string $slug)
    {
        $category = (new CategoryModel())->where('slug',$slug)->first();
        if (!$category) throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();
        $events = (new EventModel())->where('category_id',$category['id'])->whereIn('status',['registration_open','scheduled','live'])->findAll();
        return $this->render('public/category', compact('category','events') + ['title'=>$category['name'].' events']);
    }

    public function gallery() { return $this->render('public/gallery', ['media'=>$this->mediaRows(['gallery','featured','lineup']), 'title'=>'Gallery | EUPHORIA']); }
    public function mediaFile(int $id)
    {
        $row=(new MediaItemModel())->find($id);if(!$row||(!$row['is_active']&&!session('user_id'))||!$row['storage_path'])throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();$path=WRITEPATH.'uploads/media/'.$row['storage_path'];if(!is_file($path))throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();return $this->response->setHeader('Content-Type',mime_content_type($path)?:'application/octet-stream')->setHeader('Cache-Control','public, max-age=86400')->setBody(file_get_contents($path));
    }
    public function about() { return $this->render('public/standard', ['eyebrow'=>'THE PROGRAMME','heading'=>'Made for the makers.','body'=>'EUPHORIA is SAGE University Indore’s multi-day celebration of culture, sport, technology and the people who make campus unforgettable.','title'=>'About EUPHORIA']); }
    public function contact() { return $this->render('public/standard', ['eyebrow'=>'NEED A HAND?','heading'=>'Talk to the EUPHORIA desk.','body'=>'For registrations, venue queries or accessibility support, reach the programme team through the university events office.','title'=>'Contact']); }
    public function faq() { return $this->render('public/standard', ['eyebrow'=>'QUICK ANSWERS','heading'=>'Everything before the first beat.','body'=>'Bring your registration ID and keep your digital pass ready at the gate. Event-specific rules and deadlines live on each event page.','title'=>'FAQ']); }
    public function terms() { return $this->render('public/standard', ['eyebrow'=>'LEGAL','heading'=>'Participation terms.','body'=>'Programme participation is subject to the published event rules, eligibility criteria and venue safety requirements.','title'=>'Terms']); }
    public function privacy() { return $this->render('public/standard', ['eyebrow'=>'LEGAL','heading'=>'Your data, handled carefully.','body'=>'Registration data is used for event operations, payment reconciliation, passes and attendance. Production deployments should configure retention and access policies before launch.','title'=>'Privacy']); }
    public function refund() { return $this->render('public/standard', ['eyebrow'=>'PAYMENTS','heading'=>'Refund policy.','body'=>'Refund eligibility follows the event-specific policy shown during registration. Gateway reversals are processed only after server-side verification.','title'=>'Refund policy']); }
    private function mediaRows(?array $sections=null): array{$model=new MediaItemModel();$model->where('is_active',1);if($sections)$model->whereIn('section',$sections);$rows=$model->orderBy('section','ASC')->orderBy('display_order','ASC')->findAll();foreach($rows as &$row){$row['public_url']=$row['storage_path']?base_url('media/file/'.$row['id']):$row['source_url'];$row['preview_url']=$row['thumbnail_url']?:$row['public_url'];$row['embed_url']=$this->embed((string)$row['source_url'],$row['video_provider']);}return $rows;}
    private function embed(string $url,?string $provider): ?string{if($provider==='youtube'){if(preg_match('~youtu\.be/([^?&/]+)~',$url,$match)||preg_match('~[?&]v=([^?&/]+)~',$url,$match)||preg_match('~/embed/([^?&/]+)~',$url,$match))return 'https://www.youtube-nocookie.com/embed/'.$match[1];}if($provider==='vimeo'&&preg_match('~/(\d+)~',$url,$match))return 'https://player.vimeo.com/video/'.$match[1];return $provider==='direct'?$url:null;}
}