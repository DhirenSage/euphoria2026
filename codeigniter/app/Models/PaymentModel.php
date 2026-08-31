<?php

namespace App\Models;

use CodeIgniter\Model;

class PaymentModel extends Model
{
    protected $table = 'payments';
    protected $returnType = 'array';
    protected $allowedFields = ['registration_id','txnid','amount','gateway','gateway_order_id','gateway_payment_id','status','raw_reference','paid_at'];
    protected $useTimestamps = true;
}