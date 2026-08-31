<?php

namespace App\Models;

use CodeIgniter\Model;

class AuditLogModel extends Model
{
    protected $table = 'audit_logs';
    protected $returnType = 'array';
    protected $allowedFields = ['user_id','action','module','record_id','ip_address','metadata_json','created_at'];
    protected $useTimestamps = false;
}