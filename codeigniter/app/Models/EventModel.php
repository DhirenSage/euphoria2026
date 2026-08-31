<?php

namespace App\Models;

use CodeIgniter\Model;

class EventModel extends Model
{
    protected $table = 'events';
    protected $returnType = 'array';
    protected $allowedFields = ['category_id','name','slug','short_description','description','banner_path','thumbnail_path','event_type','registration_type','fee','capacity','min_team_size','max_team_size','registration_start','registration_end','event_start','event_end','venue','eligibility','rules','prizes','contact_details','status','is_featured'];
    protected $useTimestamps = true;

    public function published(): array
    {
        return $this->select('events.*, categories.name AS category_name, categories.slug AS category_slug')->join('categories', 'categories.id = events.category_id')->whereIn('events.status', ['registration_open','scheduled','live'])->orderBy('is_featured','DESC')->orderBy('event_start','ASC')->findAll();
    }

    public function bySlug(string $slug): ?array
    {
        return $this->select('events.*, categories.name AS category_name, categories.slug AS category_slug, programmes.name AS programme_name')->join('categories', 'categories.id = events.category_id')->join('programmes', 'programmes.id = categories.programme_id')->where('events.slug',$slug)->first();
    }
}