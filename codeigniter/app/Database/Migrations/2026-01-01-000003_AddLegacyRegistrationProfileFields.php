<?php

namespace App\Database\Migrations;

use CodeIgniter\Database\Migration;

class AddLegacyRegistrationProfileFields extends Migration
{
    public function up(): void
    {
        $this->db->query("ALTER TABLE registrations
            ADD COLUMN father_name VARCHAR(160) NULL AFTER participant_name,
            ADD COLUMN age TINYINT UNSIGNED NULL AFTER mobile,
            ADD COLUMN city VARCHAR(120) NULL AFTER college,
            ADD COLUMN participant_affiliation ENUM('sageian','non_sageian') NOT NULL DEFAULT 'non_sageian' AFTER city,
            ADD KEY registration_affiliation (participant_affiliation)");
    }

    public function down(): void
    {
        $this->db->query("ALTER TABLE registrations DROP INDEX registration_affiliation, DROP COLUMN participant_affiliation, DROP COLUMN city, DROP COLUMN age, DROP COLUMN father_name");
    }
}