<?php

namespace App\Models;

use CodeIgniter\Model;

class RegistrationModel extends Model
{
    protected $table = 'registrations';
    protected $returnType = 'array';
    protected $allowedFields = ['event_id','registration_id','participant_name','email','mobile','college','registration_type','team_name','total_amount','status','qr_status'];
    protected $useTimestamps = true;

    public function withEvent(): array
    {
        return $this->select('registrations.*, events.name AS event_name, events.slug AS event_slug, categories.name AS category_name, payments.id AS payment_id, payments.status AS payment_status')->join('events','events.id = registrations.event_id')->join('categories','categories.id = events.category_id')->join('payments','payments.registration_id = registrations.id','left')->orderBy('registrations.created_at','DESC')->findAll(100);
    }
}