<?php

namespace App\Services;

use CodeIgniter\HTTP\Files\UploadedFile;

final class BulkPassService
{
    public function import(UploadedFile $file): array
    {
        $db=db_connect(); $rows=(new SpreadsheetReader())->read($file);
        $events=$db->table('events')->whereNotIn('status',['cancelled','completed','archived'])->get()->getResultArray();
        $bySlug=[];$byName=[];foreach($events as $event){$bySlug[strtolower($event['slug'])]=$event;$byName[strtolower($event['name'])][]=$event;}
        $service=new RegistrationService($db);$created=[];$errors=[];$skipped=0;
        foreach($rows as $index=>$row){$line=$index+2;$name=trim($row['participant_name']??$row['name']??'');$mobile=preg_replace('/\s+/','',$row['mobile']??$row['mobile_no']??$row['phone']??$row['no']??'');$college=trim($row['institute_name']??$row['college']??$row['institution']??'');$email=strtolower(trim($row['email']??$row['email_id']??''));$slug=strtolower(trim($row['event_slug']??''));$eventName=strtolower(trim($row['event_name']??$row['event']??''));$event=$slug?($bySlug[$slug]??null):null;if(!$event&&isset($byName[$eventName])&&count($byName[$eventName])===1)$event=$byName[$eventName][0];
            if($name===''||!filter_var($email,FILTER_VALIDATE_EMAIL)||!preg_match('/^[0-9]{10}$/',$mobile)||$college===''||!$event){$errors[]=['row'=>$line,'message'=>'Name, valid 10-digit mobile, institute, email, and an exact event name/slug are required.'];continue;}
            try{$result=$service->createComplimentary($event,['participant_name'=>$name,'mobile'=>$mobile,'college'=>$college,'email'=>$email,'city'=>$row['city']??'','participant_affiliation'=>$row['participant_affiliation']??'non_sageian']);$created[]=$result['registration']['registration_id'];}catch(\Throwable $e){$skipped++;$errors[]=['row'=>$line,'message'=>$e->getMessage()];}
        }
        return ['total_rows'=>count($rows),'created'=>count($created),'skipped'=>$skipped,'emails_scheduled'=>count($created),'registration_ids'=>$created,'errors'=>$errors];
    }
}