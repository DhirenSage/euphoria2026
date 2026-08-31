<?php

namespace App\Controllers;

use App\Models\EventModel;

class ApiController extends BaseController
{
    public function health()
    {
        $database = db_connect()->simpleQuery('SELECT 1') !== false;
        return $this->response->setJSON(['ok'=>$database,'service'=>'euphoria-platform','timestamp'=>date(DATE_ATOM)]);
    }

    public function events()
    {
        return $this->response->setJSON(['data'=>(new EventModel())->published(),'meta'=>['programme'=>'Euphoria 2026']]);
    }

    public function event(string $slug)
    {
        $event=(new EventModel())->bySlug($slug);
        if(!$event) return $this->response->setStatusCode(404)->setJSON(['error'=>['code'=>'event_not_found','message'=>'Event not found.']]);
        return $this->response->setJSON(['data'=>$event]);
    }
}