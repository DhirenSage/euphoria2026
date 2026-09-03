<?php

namespace App\Controllers;

use App\Models\EventModel;
use App\Models\MediaItemModel;
use App\Services\AuditService;

class MediaController extends BaseController
{
    public function index(){$this->guard();return $this->render('admin/media',['title'=>'Gallery & video','active'=>'media','media'=>(new MediaItemModel())->orderBy('section','ASC')->orderBy('display_order','ASC')->findAll(),'events'=>(new EventModel())->orderBy('name','ASC')->findAll()]);}
    public function store()
    {
        $this->guard();
        try{$data=$this->data();$file=$this->request->getFile('image');if($file&&$file->isValid()&&!$file->hasMoved()){$this->validateImage($file);$directory=WRITEPATH.'uploads/media';if(!is_dir($directory))mkdir($directory,0775,true);$name=$file->getRandomName();$file->move($directory,$name);$data['storage_path']=$name;}$this->validateMedia($data);$id=(new MediaItemModel())->insert($data,true);(new AuditService())->record('media.created','media_items',(string)$id,['section'=>$data['section']]);return redirect()->back()->with('message','Media item published.');}catch(\Throwable $e){return redirect()->back()->withInput()->with('error',$e->getMessage());}
    }
    public function update(int $id)
    {
        $this->guard();
        $model=new MediaItemModel();$existing=$model->find($id);if(!$existing)throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();try{$data=$this->data();$data['storage_path']=$existing['storage_path'];$this->validateMedia($data);$model->update($id,$data);(new AuditService())->record('media.updated','media_items',(string)$id,['active'=>$data['is_active']]);return redirect()->back()->with('message','Media item updated.');}catch(\Throwable $e){return redirect()->back()->with('error',$e->getMessage());}
    }
    public function delete(int $id)
    {
        $this->guard();
        $model=new MediaItemModel();$row=$model->find($id);if($row){if($row['storage_path'])@unlink(WRITEPATH.'uploads/media/'.$row['storage_path']);$model->delete($id);(new AuditService())->record('media.deleted','media_items',(string)$id);}return redirect()->back()->with('message','Media item deleted.');
    }
    private function data(): array{$type=(string)$this->request->getPost('media_type');$thumbnail=trim((string)$this->request->getPost('thumbnail_url'));if($type==='video'&&$thumbnail==='')$thumbnail='https://images.unsplash.com/photo-1526218626217-dc65a29bb444?auto=format&fit=crop&w=1200&q=85';return ['event_id'=>$this->request->getPost('event_id')?:null,'media_type'=>$type,'section'=>$this->request->getPost('section'),'title'=>trim((string)$this->request->getPost('title')),'caption'=>trim((string)$this->request->getPost('caption')),'source_url'=>trim((string)$this->request->getPost('source_url')),'thumbnail_url'=>$thumbnail,'video_provider'=>$this->provider((string)$this->request->getPost('source_url')),'display_order'=>max(0,(int)$this->request->getPost('display_order')),'is_active'=>$this->request->getPost('is_active')?1:0];}
    private function validateMedia(array $data): void{if(!in_array($data['media_type'],['image','video'],true)||!in_array($data['section'],['hero','highlight','featured','lineup','gallery'],true)||mb_strlen($data['title'])<2)throw new \RuntimeException('Select a valid type/section and enter a title.');if($data['media_type']==='video'&&!$data['video_provider'])throw new \RuntimeException('Use a valid YouTube, Vimeo, MP4, or WEBM URL.');if($data['media_type']==='image'&&empty($data['storage_path'])&&!filter_var($data['source_url'],FILTER_VALIDATE_URL))throw new \RuntimeException('Upload an image or provide an image URL.');}
    private function validateImage($file): void{if($file->getSize()>8*1024*1024||!in_array($file->getMimeType(),['image/jpeg','image/png','image/webp'],true))throw new \RuntimeException('Images must be JPG, PNG, or WEBP up to 8 MB.');}
    private function provider(string $url): ?string{$host=strtolower(parse_url($url,PHP_URL_HOST)??'');$path=strtolower(parse_url($url,PHP_URL_PATH)??'');if(str_contains($host,'youtube.com')||str_contains($host,'youtu.be'))return 'youtube';if(str_contains($host,'vimeo.com'))return 'vimeo';if(str_ends_with($path,'.mp4')||str_ends_with($path,'.webm'))return 'direct';return null;}
    private function guard(): void { if(!array_intersect(session('roles')??[],['SUPER_ADMIN','PROGRAMME_ADMIN','EVENT_ADMIN','CONTENT_MANAGER']))throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound(); }
}