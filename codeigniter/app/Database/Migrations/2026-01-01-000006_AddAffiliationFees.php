<?php

namespace App\Database\Migrations;

use CodeIgniter\Database\Migration;

class AddAffiliationFees extends Migration
{
    public function up(): void
    {
        if (! $this->db->fieldExists('sageian_fee', 'events')) {
            $this->db->query('ALTER TABLE events ADD sageian_fee DECIMAL(10,2) NOT NULL DEFAULT 0 AFTER fee, ADD non_sageian_fee DECIMAL(10,2) NOT NULL DEFAULT 0 AFTER sageian_fee');
        }
        $this->db->query('UPDATE events SET sageian_fee = fee, non_sageian_fee = fee WHERE sageian_fee = 0 AND non_sageian_fee = 0 AND fee > 0');
    }

    public function down(): void
    {
        if ($this->db->fieldExists('sageian_fee', 'events')) {
            $this->db->query('ALTER TABLE events DROP COLUMN non_sageian_fee, DROP COLUMN sageian_fee');
        }
    }
}