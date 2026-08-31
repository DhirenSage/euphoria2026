<?php

namespace App\Services;

use CodeIgniter\Database\ConnectionInterface;

final class AttendanceService
{
    public function __construct(private ConnectionInterface $db)
    {
    }

    public function scan(string $rawToken, int $eventId, int $dayId, ?int $gateId, ?int $scannerId): array
    {
        $registration = $this->db->table('registrations r')->select('r.*, e.name AS event_name')->join('events e','e.id=r.event_id')->join('qr_tokens q','q.registration_id=r.id')->where('q.token_hash',hash('sha256',$rawToken))->where('q.status','active')->get()->getRowArray();
        if (!$registration) return ['ok'=>false,'status'=>'denied','message'=>'This QR code is invalid or has been revoked.'];
        if ((int)$registration['event_id'] !== $eventId) return ['ok'=>false,'status'=>'denied','message'=>'This pass is not valid for this event.','registration'=>$registration];
        if ($registration['status'] !== 'confirmed') return ['ok'=>false,'status'=>'denied','message'=>'Payment or registration confirmation is required.','registration'=>$registration];
        $existing = $this->db->table('attendance')->where(['registration_id'=>$registration['id'],'event_day_id'=>$dayId])->get()->getRowArray();
        if ($existing) return ['ok'=>false,'status'=>'duplicate','message'=>'Entry already recorded for today.','registration'=>$registration,'entry'=>$existing];
        $inserted = $this->db->table('attendance')->insert(['registration_id'=>$registration['id'],'event_id'=>$eventId,'event_day_id'=>$dayId,'gate_id'=>$gateId,'scanner_user_id'=>$scannerId,'entry_time'=>date('Y-m-d H:i:s'),'status'=>'allowed']);
        if (!$inserted && $this->db->error()['code'] === 1062) return ['ok'=>false,'status'=>'duplicate','message'=>'Entry already recorded for today.','registration'=>$registration];
        return ['ok'=>true,'status'=>'allowed','message'=>'Entry allowed.','registration'=>$registration,'entry'=>$this->db->insertID()];
    }
}