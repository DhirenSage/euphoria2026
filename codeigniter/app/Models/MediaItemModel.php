<?php

namespace App\Models;

use CodeIgniter\Model;

class MediaItemModel extends Model
{
    protected $table='media_items';
    protected $returnType='array';
    protected $allowedFields=['event_id','media_type','section','title','caption','source_url','storage_path','thumbnail_url','video_provider','display_order','is_active'];
    protected $useTimestamps=true;
}