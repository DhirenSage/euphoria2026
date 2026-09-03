<?php

namespace App\Services;

use CodeIgniter\Database\ConnectionInterface;
use RuntimeException;

final class EventDeletionService
{
    public function __construct(private ConnectionInterface $db)
    {
    }

    public function deleteMany(array $eventIds): array
    {
        $eventIds = array_values(array_unique(array_filter(array_map('intval', $eventIds), fn($id) => $id > 0)));
        if (!$eventIds) throw new RuntimeException('Select at least one event.');
        if (count($eventIds) > 100) throw new RuntimeException('Delete a maximum of 100 events at once.');
        $events = $this->db->table('events')->whereIn('id', $eventIds)->get()->getResultArray();
        if (count($events) !== count($eventIds)) throw new RuntimeException('One or more selected events no longer exist.');

        $registrations = $this->db->table('registrations')->select('id,registration_id,event_id')->whereIn('event_id', $eventIds)->get()->getResultArray();
        $registrationIds = array_map('intval', array_column($registrations, 'id'));
        $paymentIds = $registrationIds ? array_map('intval', array_column($this->db->table('payments')->select('id')->whereIn('registration_id', $registrationIds)->get()->getResultArray(), 'id')) : [];
        $mediaFiles = array_filter(array_column($this->db->table('media_items')->select('storage_path')->whereIn('event_id', $eventIds)->get()->getResultArray(), 'storage_path'));
        $galleryFiles = array_filter(array_column($this->db->table('event_galleries')->select('image_path')->whereIn('event_id', $eventIds)->get()->getResultArray(), 'image_path'));

        $this->db->transStart();
        if ($paymentIds) $this->db->table('payment_transactions')->whereIn('payment_id', $paymentIds)->delete();
        if ($registrationIds) {
            foreach (['coupon_usages','email_jobs','email_logs','registration_field_values','registration_members','attendance','qr_tokens','payments'] as $table) $this->db->table($table)->whereIn('registration_id', $registrationIds)->delete();
        }
        $this->db->table('scan_attempts')->whereIn('event_id', $eventIds)->delete();
        foreach (['scanner_assignments','event_schedules','event_speakers','event_galleries','registration_forms','registration_fields','event_days','media_items'] as $table) $this->db->table($table)->whereIn('event_id', $eventIds)->delete();
        if ($registrationIds) $this->db->table('registrations')->whereIn('id', $registrationIds)->delete();
        $this->db->table('events')->whereIn('id', $eventIds)->delete();
        $this->db->transComplete();
        if (!$this->db->transStatus()) throw new RuntimeException('Permanent deletion failed and was rolled back.');

        foreach ($registrations as $registration) foreach (glob(WRITEPATH.'passes/'.basename($registration['registration_id']).'*') ?: [] as $path) @unlink($path);
        foreach ($mediaFiles as $path) @unlink(WRITEPATH.'uploads/media/'.basename($path));
        foreach ($galleryFiles as $path) {
            $candidate = str_starts_with($path, WRITEPATH) ? $path : WRITEPATH.'uploads/'.ltrim($path, '/');
            if (is_file($candidate)) @unlink($candidate);
        }
        return ['events'=>count($events), 'registrations'=>count($registrations), 'event_names'=>array_column($events, 'name')];
    }
}