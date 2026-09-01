<?php

namespace App\Database\Seeds;

use CodeIgniter\Database\Seeder;

class RegistrationCatalogueSeeder extends Seeder
{
    public function run()
    {
        $now = date('Y-m-d H:i:s');
        $programme = $this->db->table('programmes')->where('slug', 'euphoria-2026')->get()->getRowArray();
        if (!$programme) return;

        $catalogue = [
            'Cultural' => [
                ['Move & Groove (Solo Dance Competition)', 'move-groove-solo-dance', 299, 'individual', null, null],
                ['Move & Groove (Group Dance Competition)', 'move-groove-group-dance', 899, 'team', 2, 20],
                ['Swar Fiesta (Solo Singing Competition)', 'swar-fiesta-solo-singing', 299, 'individual', null, null],
                ['Battle of Bands', 'battle-of-bands', 2499, 'team', 3, 12],
                ['Rap Battle', 'rap-battle', 249, 'individual', null, null],
                ['Fashion-Fiesta (Fashion Show – Solo Model Round)', 'fashion-fiesta-solo-model', 799, 'individual', null, null],
                ['Fashion-Fiesta (Designer Round – Min 4 Garments)', 'fashion-fiesta-designer-round', 2499, 'individual', null, null],
                ['Model Hunt (Audition)', 'model-hunt-audition', 199, 'individual', null, null],
                ['Game Mania', 'game-mania', 99, 'individual', null, null],
                ['Reel Making Competition', 'reel-making-competition', 199, 'individual', null, null],
            ],
            'Literary and Management' => [
                ['Crack the Clue (Treasure Hunt)', 'crack-the-clue-treasure-hunt', 999, 'team', 2, 6],
                ['Bid To Win (IPL Auction)', 'bid-to-win-ipl-auction', 499, 'team', 2, 5],
                ['The Great Debate', 'the-great-debate', 249, 'individual', null, null],
                ['Vocal Ink (Slam Poetry)', 'vocal-ink-slam-poetry', 249, 'individual', null, null],
            ],
            'Sci-Pha-Agro (The Magic of Science)' => [
                ['Model/Product Making Presentation', 'model-product-making-presentation', 249, 'individual', null, null],
                ['Oral / Poster Presentation', 'oral-poster-presentation', 249, 'individual', null, null],
                ['On Spot / Attending', 'on-spot-attending', 299, 'individual', null, null],
            ],
            'Sports' => [
                ['Cricket', 'cricket', 1600, 'team', 11, 15],
                ['Football', 'football', 1000, 'team', 7, 14],
                ['Basketball', 'basketball', 1000, 'team', 5, 12],
                ['Kabaddi', 'kabaddi', 800, 'team', 7, 12],
                ['Carrom', 'carrom', 200, 'individual', null, null],
                ['Chess', 'chess', 200, 'individual', null, null],
                ['Volleyball', 'volleyball', 800, 'team', 6, 12],
                ['Table Tennis', 'table-tennis', 250, 'individual', null, null],
                ['Badminton (Singles) Men', 'badminton-singles-men', 300, 'individual', null, null],
                ['Badminton (Doubles) Men', 'badminton-doubles-men', 400, 'team', 2, 2],
                ['Badminton (Singles) Women', 'badminton-singles-women', 200, 'individual', null, null],
                ['Badminton (Doubles) Women', 'badminton-doubles-women', 400, 'team', 2, 2],
                ['Power Lifting', 'power-lifting', 300, 'individual', null, null],
                ['Weight Lifting', 'weight-lifting', 300, 'individual', null, null],
                ['Arm Wrestling', 'arm-wrestling', 150, 'individual', null, null],
            ],
        ];

        $displayOrder = 0;
        foreach ($catalogue as $categoryName => $events) {
            $displayOrder++;
            $category = $this->db->table('categories')->where('programme_id', $programme['id'])->where('name', $categoryName)->get()->getRowArray();
            if (!$category) {
                $this->db->table('categories')->insert(['programme_id'=>$programme['id'],'name'=>$categoryName,'slug'=>safe_slug($categoryName),'description'=>'Euphoria 2K26 registration category.','display_order'=>$displayOrder,'is_active'=>1,'created_at'=>$now,'updated_at'=>$now]);
                $categoryId = $this->db->insertID();
            } else {
                $categoryId = $category['id'];
                $this->db->table('categories')->where('id',$categoryId)->update(['display_order'=>$displayOrder,'is_active'=>1,'updated_at'=>$now]);
            }

            foreach ($events as [$name,$slug,$fee,$type,$minimum,$maximum]) {
                $data = ['category_id'=>$categoryId,'name'=>$name,'short_description'=>'Register for '.$name.' at Euphoria 2K26.','description'=>'Official Euphoria 2K26 event registration.','event_type'=>$categoryName === 'Sports' ? 'sports' : 'competition','registration_type'=>$type,'fee'=>$fee,'capacity'=>250,'min_team_size'=>$minimum,'max_team_size'=>$maximum,'registration_start'=>'2026-01-01 00:00:00','registration_end'=>'2026-09-14 23:59:59','event_start'=>'2026-09-15 10:00:00','event_end'=>'2026-09-17 18:00:00','venue'=>'SAGE University Indore','status'=>'registration_open','updated_at'=>$now];
                $existing = $this->db->table('events')->where('slug',$slug)->get()->getRowArray();
                if ($existing) $this->db->table('events')->where('id',$existing['id'])->update($data);
                else $this->db->table('events')->insert($data + ['slug'=>$slug,'is_featured'=>0,'created_at'=>$now]);
            }
            $approvedSlugs = array_column($events, 1);
            $this->db->table('events')->where('category_id',$categoryId)->whereNotIn('slug',$approvedSlugs)->update(['status'=>'archived','updated_at'=>$now]);
        }
    }
}