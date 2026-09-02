<?php

namespace App\Models;

use CodeIgniter\Model;

class CategoryModel extends Model
{
    protected $table = 'categories';
    protected $returnType = 'array';
    protected $allowedFields = ['programme_id','name','slug','description','image_path','icon','display_order','is_active'];
    protected $useTimestamps = true;
}