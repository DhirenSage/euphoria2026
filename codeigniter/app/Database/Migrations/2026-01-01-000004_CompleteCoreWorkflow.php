<?php

namespace App\Database\Migrations;

use CodeIgniter\Database\Migration;

class CompleteCoreWorkflow extends Migration
{
    public function up(): void
    {
        $this->db->query("ALTER TABLE categories ADD COLUMN icon VARCHAR(80) NULL AFTER image_path");
        $this->db->query("ALTER TABLE registration_fields ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1 AFTER is_required");
        $this->db->query("UPDATE registration_fields SET is_active=0 WHERE field_name IN ('participant_name','email','mobile','college')");
        $this->db->query("ALTER TABLE event_days ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1 AFTER event_date");
        $this->db->query("ALTER TABLE events
            ADD COLUMN payment_required TINYINT(1) NOT NULL DEFAULT 1 AFTER fee,
            ADD COLUMN tax_amount DECIMAL(10,2) NOT NULL DEFAULT 0 AFTER payment_required,
            ADD COLUMN discount_amount DECIMAL(10,2) NOT NULL DEFAULT 0 AFTER tax_amount,
            ADD COLUMN refund_policy TEXT NULL AFTER prizes");
        $this->db->query("UPDATE events SET payment_required = CASE WHEN fee > 0 THEN 1 ELSE 0 END");
        $this->db->query("ALTER TABLE registrations
            ADD COLUMN pass_access_hash CHAR(64) NULL AFTER qr_status,
            ADD COLUMN pass_access_ciphertext TEXT NULL AFTER pass_access_hash,
            ADD UNIQUE KEY registration_pass_access (pass_access_hash)");
        $this->db->query("ALTER TABLE payments ADD COLUMN productinfo VARCHAR(100) NOT NULL DEFAULT 'euphoria2026' AFTER amount");
        $this->db->query("DELETE j1 FROM email_jobs j1 INNER JOIN email_jobs j2 ON j1.registration_id=j2.registration_id AND j1.template_key=j2.template_key AND j1.id>j2.id");
        $this->db->query("ALTER TABLE email_jobs ADD UNIQUE KEY email_registration_template (registration_id,template_key)");

        $this->db->query("CREATE TABLE IF NOT EXISTS registration_sequences (
            sequence_key VARCHAR(80) PRIMARY KEY,
            next_value BIGINT UNSIGNED NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");

        $this->db->query("CREATE TABLE IF NOT EXISTS scan_attempts (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            registration_id BIGINT UNSIGNED NULL,
            event_id BIGINT UNSIGNED NULL,
            event_day_id BIGINT UNSIGNED NULL,
            gate_id BIGINT UNSIGNED NULL,
            scanner_user_id BIGINT UNSIGNED NULL,
            token_hint VARCHAR(20) NULL,
            status ENUM('allowed','duplicate','denied') NOT NULL,
            reason VARCHAR(255) NOT NULL,
            attempted_at DATETIME NOT NULL,
            KEY scan_attempt_status_time(status,attempted_at),
            KEY scan_attempt_event(event_id,event_day_id),
            CONSTRAINT fk_scan_attempt_registration FOREIGN KEY(registration_id) REFERENCES registrations(id) ON DELETE SET NULL,
            CONSTRAINT fk_scan_attempt_event FOREIGN KEY(event_id) REFERENCES events(id) ON DELETE SET NULL,
            CONSTRAINT fk_scan_attempt_day FOREIGN KEY(event_day_id) REFERENCES event_days(id) ON DELETE SET NULL,
            CONSTRAINT fk_scan_attempt_gate FOREIGN KEY(gate_id) REFERENCES gates(id) ON DELETE SET NULL,
            CONSTRAINT fk_scan_attempt_scanner FOREIGN KEY(scanner_user_id) REFERENCES users(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
    }

    public function down(): void
    {
        $this->db->query('DROP TABLE IF EXISTS scan_attempts');
        $this->db->query('DROP TABLE IF EXISTS registration_sequences');
        $this->db->query('ALTER TABLE email_jobs ADD KEY email_job_registration (registration_id), DROP INDEX email_registration_template');
        $this->db->query('ALTER TABLE payments DROP COLUMN productinfo');
        $this->db->query('ALTER TABLE registrations DROP INDEX registration_pass_access, DROP COLUMN pass_access_ciphertext, DROP COLUMN pass_access_hash');
        $this->db->query('ALTER TABLE events DROP COLUMN refund_policy, DROP COLUMN discount_amount, DROP COLUMN tax_amount, DROP COLUMN payment_required');
        $this->db->query('ALTER TABLE registration_fields DROP COLUMN is_active');
        $this->db->query('ALTER TABLE event_days DROP COLUMN is_active');
        $this->db->query('ALTER TABLE categories DROP COLUMN icon');
    }
}