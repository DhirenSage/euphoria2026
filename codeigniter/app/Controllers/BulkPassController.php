<?php

namespace App\Controllers;

use App\Services\AuditService;
use App\Services\BulkPassService;

class BulkPassController extends BaseController
{
    public function index(){$this->guard();return $this->render('admin/bulk_passes',['title'=>'Bulk complimentary passes','active'=>'bulk-passes','result'=>session('bulk_result')]);}
    public function downloadTemplate()
    {
        $this->guard();
        $content="participant_name,mobile,institute_name,email,event_name,event_slug,city,participant_affiliation\nAarav Sharma,9876543210,SAGE University Indore,aarav@example.com,Dance Competition,dance-competition,Indore,sageian\n";
        return $this->response->setHeader('Content-Type','text/csv')->setHeader('Content-Disposition','attachment; filename="euphoria-bulk-pass-template.csv"')->setBody($content);
    }
    public function import()
    {
        $this->guard();
        $file=$this->request->getFile('participants_file');
        if(!$file||!$file->isValid())return redirect()->back()->with('error','Choose a valid CSV or XLSX participant list.');
        try{$result=(new BulkPassService())->import($file);(new AuditService())->record('bulk_pass.imported','registrations',null,['created'=>$result['created'],'rows'=>$result['total_rows']]);return redirect()->back()->with('message',$result['created'].' complimentary passes created and queued for email.')->with('bulk_result',$result);}catch(\Throwable $e){return redirect()->back()->with('error',$e->getMessage());}
    }
    private function guard(): void { if(!array_intersect(session('roles')??[],['SUPER_ADMIN','PROGRAMME_ADMIN','EVENT_ADMIN']))throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound(); }
}