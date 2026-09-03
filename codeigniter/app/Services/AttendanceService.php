<?php

namespace App\Services;

use CodeIgniter\Database\ConnectionInterface;

final class AttendanceService
{
    public function __construct(private ConnectionInterface $db)
    {
    }

    public function scan(string $rawToken, ?int $scannerId): array
    {
        $token = trim($rawToken);
        $registration = $this->db->table('registrations r')
            ->select('r.*, e.name AS event_name, e.id AS linked_event_id, e.event_start, e.event_end, e.venue, p.status AS payment_status, q.status AS token_status')
            ->join('events e', 'e.id=r.event_id')
            ->join('payments p', 'p.registration_id=r.id', 'left')
            ->join('qr_tokens q', 'q.registration_id=r.id')
            ->where('q.token_hash', hash('sha256', $token))->get()->getRowArray();
        if (!$registration) return $this->result(false, 'denied', 'This QR code is invalid or has been revoked.', null, null, $scannerId, $token);
        $eventId = (int) $registration['event_id'];
        if ($registration['token_status'] !== 'active' || $registration['qr_status'] !== 'active') return $this->result(false, 'denied', 'This QR code is invalid, expired, or has been revoked.', $registration, null, $scannerId, $token);
        if ($registration['status'] !== 'confirmed' || ($registration['payment_status'] ?? '') !== 'success') return $this->result(false, 'denied', 'Payment or registration confirmation is required.', $registration, null, $scannerId, $token);

        $days = $this->db->table('event_days')->where(['event_id'=>$eventId, 'is_active'=>1])->orderBy('event_date', 'ASC')->get()->getResultArray();
        $today = date('Y-m-d');
        $day = null;
        foreach ($days as $candidate) if ($candidate['event_date'] === $today) { $day = $candidate; break; }
        if (!$day) {
            if ($days && $today > end($days)['event_date']) {
                $this->db->table('registrations')->where('id', $registration['id'])->update(['qr_status'=>'expired', 'updated_at'=>date('Y-m-d H:i:s')]);
                $this->db->table('qr_tokens')->where('registration_id', $registration['id'])->update(['status'=>'expired']);
                $registration['qr_status'] = 'expired';
                return $this->result(false, 'denied', 'This pass has expired because all configured event days are over.', $registration, null, $scannerId, $token);
            }
            $nextDay = null; foreach($days as $candidate) if($candidate['event_date'] > $today){$nextDay=$candidate;break;}
            $message = $nextDay ? 'Upcoming event — entry is not open. This pass is valid on '.$nextDay['event_date'].' for '.$registration['event_name'].'.' : 'This event has no entry scheduled for today.';
            return $this->result(false, $nextDay?'upcoming':'denied', $message, $registration, $nextDay, $scannerId, $token);
        }
        $dayId = (int) $day['id'];
        $existing = $this->db->table('attendance')->where(['registration_id'=>$registration['id'], 'event_day_id'=>$dayId])->get()->getRowArray();
        if ($existing) return $this->result(false, 'duplicate', 'Entry already recorded for this event day.', $registration, $day, $scannerId, $token, $existing);
        try {
            $inserted = $this->db->table('attendance')->insert(['registration_id'=>$registration['id'], 'event_id'=>$eventId, 'event_day_id'=>$dayId, 'gate_id'=>null, 'scanner_user_id'=>$scannerId, 'entry_time'=>date('Y-m-d H:i:s'), 'status'=>'allowed']);
            if (!$inserted) throw new \RuntimeException('Attendance insert failed');
        } catch (\Throwable $e) {
            if ((int)($this->db->error()['code'] ?? 0) === 1062 || str_contains($e->getMessage(), 'Duplicate')) {
                $existing = $this->db->table('attendance')->where(['registration_id'=>$registration['id'], 'event_day_id'=>$dayId])->get()->getRowArray();
                return $this->result(false, 'duplicate', 'Entry already recorded for this event day.', $registration, $day, $scannerId, $token, $existing);
            }
            throw $e;
        }
        return $this->result(true, 'allowed', 'Entry allowed and attendance recorded for today.', $registration, $day, $scannerId, $token, ['id'=>$this->db->insertID(), 'entry_time'=>date('Y-m-d H:i:s')]);
    }

    private function result(bool $ok, string $status, string $message, ?array $registration, ?array $day, ?int $scannerId, string $token, ?array $entry = null): array
    {
        $eventId = $registration ? (int)$registration['event_id'] : null;
        $dayId = $day ? (int)$day['id'] : null;
        $attemptStatus=in_array($status,['allowed','duplicate','denied'],true)?$status:'denied';
        $this->db->table('scan_attempts')->insert(['registration_id'=>$registration['id']??null, 'event_id'=>$eventId, 'event_day_id'=>$dayId, 'gate_id'=>null, 'scanner_user_id'=>$scannerId, 'token_hint'=>$token!==''?substr($token,-8):null, 'status'=>$attemptStatus, 'reason'=>$message, 'attempted_at'=>date('Y-m-d H:i:s')]);
        $result = ['ok'=>$ok, 'status'=>$status, 'message'=>$message, 'event_id'=>$eventId, 'event_day_id'=>$dayId];
        if ($registration) $result['registration'] = ['participant_name'=>$registration['participant_name'], 'registration_id'=>$registration['registration_id'], 'event_name'=>$registration['event_name'], 'payment_status'=>$registration['payment_status'], 'qr_status'=>$registration['qr_status'], 'email'=>$registration['email'], 'mobile'=>$registration['mobile'], 'college'=>$registration['college'], 'event_day_label'=>$day['label']??null, 'event_day_date'=>$day['event_date']??null, 'event_time'=>$registration['event_start']??null, 'venue'=>$registration['venue']??null];
        if ($entry) $result['entry'] = $entry;
        return $result;
    }
}