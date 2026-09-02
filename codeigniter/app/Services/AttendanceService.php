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
        $token = trim($rawToken);
        $registration = $this->db->table('registrations r')->select('r.*, e.name AS event_name, p.status AS payment_status, q.status AS token_status')->join('events e','e.id=r.event_id')->join('payments p','p.registration_id=r.id','left')->join('qr_tokens q','q.registration_id=r.id')->where('q.token_hash',hash('sha256',$token))->get()->getRowArray();
        if (!$registration) return $this->result(false,'denied','This QR code is invalid or has been revoked.',null,$eventId,$dayId,$gateId,$scannerId,$token);
        if ($registration['token_status'] !== 'active' || $registration['qr_status'] !== 'active') return $this->result(false,'denied','This QR code is invalid or has been revoked.',$registration,$eventId,$dayId,$gateId,$scannerId,$token);
        if ((int)$registration['event_id'] !== $eventId) return $this->result(false,'denied','This pass is not valid for this event.',$registration,$eventId,$dayId,$gateId,$scannerId,$token);
        $day = $this->db->table('event_days')->where(['id'=>$dayId,'event_id'=>$eventId])->get()->getRowArray();
        if (!$day) return $this->result(false,'denied','The selected event day does not belong to this event.',$registration,$eventId,$dayId,$gateId,$scannerId,$token);
        $allowOffDate = ENVIRONMENT !== 'production' && filter_var(env('SCANNER_ALLOW_OFFDATE', true), FILTER_VALIDATE_BOOL);
        if (!$allowOffDate && $day['event_date'] !== date('Y-m-d')) return $this->result(false,'denied','This pass is not valid for the selected event day today.',$registration,$eventId,$dayId,$gateId,$scannerId,$token);
        if ($registration['status'] !== 'confirmed' || ($registration['payment_status'] ?? '') !== 'success') return $this->result(false,'denied','Payment or registration confirmation is required.',$registration,$eventId,$dayId,$gateId,$scannerId,$token);
        $existing = $this->db->table('attendance')->where(['registration_id'=>$registration['id'],'event_day_id'=>$dayId])->get()->getRowArray();
        if ($existing) return $this->result(false,'duplicate','Entry already recorded for this event day.',$registration,$eventId,$dayId,$gateId,$scannerId,$token,$existing);
        try {
            $inserted = $this->db->table('attendance')->insert(['registration_id'=>$registration['id'],'event_id'=>$eventId,'event_day_id'=>$dayId,'gate_id'=>$gateId,'scanner_user_id'=>$scannerId,'entry_time'=>date('Y-m-d H:i:s'),'status'=>'allowed']);
            if (!$inserted) throw new \RuntimeException('Attendance insert failed');
        } catch (\Throwable $e) {
            if ((int)($this->db->error()['code'] ?? 0) === 1062 || str_contains($e->getMessage(),'Duplicate')) {
                $existing=$this->db->table('attendance')->where(['registration_id'=>$registration['id'],'event_day_id'=>$dayId])->get()->getRowArray();
                return $this->result(false,'duplicate','Entry already recorded for this event day.',$registration,$eventId,$dayId,$gateId,$scannerId,$token,$existing);
            }
            throw $e;
        }
        return $this->result(true,'allowed','Entry allowed.',$registration,$eventId,$dayId,$gateId,$scannerId,$token,['id'=>$this->db->insertID(),'entry_time'=>date('Y-m-d H:i:s')]);
    }

    private function result(bool $ok, string $status, string $message, ?array $registration, int $eventId, int $dayId, ?int $gateId, ?int $scannerId, string $token, ?array $entry = null): array
    {
        $this->db->table('scan_attempts')->insert(['registration_id'=>$registration['id']??null,'event_id'=>$eventId?:null,'event_day_id'=>$dayId?:null,'gate_id'=>$gateId,'scanner_user_id'=>$scannerId,'token_hint'=>$token!==''?substr($token,-8):null,'status'=>$status,'reason'=>$message,'attempted_at'=>date('Y-m-d H:i:s')]);
        $result=['ok'=>$ok,'status'=>$status,'message'=>$message];
        if($registration)$result['registration']=['participant_name'=>$registration['participant_name'],'registration_id'=>$registration['registration_id'],'event_name'=>$registration['event_name'],'payment_status'=>$registration['payment_status'],'qr_status'=>$registration['qr_status']];
        if($entry)$result['entry']=$entry;
        return $result;
    }
}