<?php

namespace App\Database\Migrations;

use CodeIgniter\Database\Migration;

class CreateMediaLibrary extends Migration
{
    public function up(): void
    {
        $this->db->query("CREATE TABLE IF NOT EXISTS media_items (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            event_id BIGINT UNSIGNED NULL,
            media_type ENUM('image','video') NOT NULL,
            section ENUM('hero','highlight','featured','lineup','gallery') NOT NULL DEFAULT 'gallery',
            title VARCHAR(180) NOT NULL,
            caption VARCHAR(500) NULL,
            source_url VARCHAR(1000) NULL,
            storage_path VARCHAR(500) NULL,
            thumbnail_url VARCHAR(1000) NULL,
            video_provider VARCHAR(40) NULL,
            display_order INT UNSIGNED NOT NULL DEFAULT 0,
            is_active TINYINT(1) NOT NULL DEFAULT 1,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            KEY media_public_order(is_active,section,display_order),
            KEY media_event(event_id),
            CONSTRAINT fk_media_event FOREIGN KEY(event_id) REFERENCES events(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
    }
    public function down(): void { $this->db->query('DROP TABLE IF EXISTS media_items'); }
}