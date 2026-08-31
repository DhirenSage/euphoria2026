<?php

namespace App\Models;

use CodeIgniter\Model;

class AttendanceModel extends Model
{
    protected $table = 'attendance';
    protected $returnType = 'array';
    protected $allowedFields = ['registration_id','event_id','event_day_id','gate_id','scanner_user_id','entry_time','status','reason'];
    protected $useTimestamps = false;
}