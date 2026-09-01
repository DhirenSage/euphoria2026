<?php

namespace App\Services;

use CodeIgniter\Database\ConnectionInterface;
use RuntimeException;

final class RegistrationService
{
    public function __construct(private ConnectionInterface $db)
    {
    }

    public function create(array $event, array $input): array
    {
        $this->db->transStart();
        $count = $this->db->table('registrations')->where('event_id', $event['id'])->whereIn('status', ['pending_payment','confirmed'])->countAllResults();
        if ((int) $event['capacity'] > 0 && $count >= (int) $event['capacity']) throw new RuntimeException('This event has reached its registration capacity.');
        $registrationId = $this->nextRegistrationId();
        $status = (float) $event['fee'] > 0 ? 'pending_payment' : 'confirmed';
        $now = date('Y-m-d H:i:s');
        $registrationType = in_array($event['registration_type'], ['individual','team'], true) ? $event['registration_type'] : 'individual';
        if ($registrationType === 'team' && trim($input['team_name'] ?? '') === '') throw new RuntimeException('Team name is required for this event.');
        $row = ['event_id'=>$event['id'],'registration_id'=>$registrationId,'participant_name'=>trim($input['participant_name']),'father_name'=>trim($input['father_name'] ?? ''),'email'=>strtolower(trim($input['email'])),'mobile'=>trim($input['mobile']),'age'=>($input['age'] ?? '') !== '' ? (int)$input['age'] : null,'college'=>trim($input['college'] ?? ''),'city'=>trim($input['city'] ?? ''),'participant_affiliation'=>$input['participant_affiliation'],'registration_type'=>$registrationType,'team_name'=>$registrationType === 'team' ? trim($input['team_name'] ?? '') : null,'total_amount'=>(float)$event['fee'],'status'=>$status,'qr_status'=>'active','created_at'=>$now,'updated_at'=>$now];
        $this->db->table('registrations')->insert($row);
        $registrationDbId = (int) $this->db->insertID();
        $rawToken = 'EUPHORIA-' . bin2hex(random_bytes(20));
        $this->db->table('qr_tokens')->insert(['registration_id'=>$registrationDbId,'token_hash'=>hash('sha256',$rawToken),'token_hint'=>substr($rawToken,-8),'token_ciphertext'=>base64_encode(service('encrypter')->encrypt($rawToken)),'status'=>'active','created_at'=>$now]);
        if ($status === 'confirmed') $this->db->table('payments')->insert(['registration_id'=>$registrationDbId,'txnid'=>'FREE-' . $registrationId,'amount'=>0,'gateway'=>'free','status'=>'success','paid_at'=>$now,'created_at'=>$now,'updated_at'=>$now]);
        else $this->db->table('payments')->insert(['registration_id'=>$registrationDbId,'txnid'=>'EB-' . bin2hex(random_bytes(12)),'amount'=>(float)$event['fee'],'gateway'=>'easebuzz','status'=>'created','created_at'=>$now,'updated_at'=>$now]);
        $fields=$this->db->table('registration_fields')->where('event_id',$event['id'])->get()->getResultArray();
        foreach($fields as $field){$value=$input[$field['field_name']]??null;if($value!==null&&$value!=='')$this->db->table('registration_field_values')->insert(['registration_id'=>$registrationDbId,'field_id'=>$field['id'],'value_text'=>is_array($value)?json_encode($value):trim((string)$value),'created_at'=>$now]);}
        if(($row['registration_type']??'individual')==='team'&&!empty($input['team_member_names'])){foreach(preg_split('/\r\n|\r|\n/',trim((string)$input['team_member_names'])) as $member){$member=trim($member);if($member!=='')$this->db->table('registration_members')->insert(['registration_id'=>$registrationDbId,'name'=>$member,'created_at'=>$now]);}}
        $this->db->transComplete();
        if ($this->db->transStatus() === false) throw new RuntimeException('Could not complete registration.');
        if ($status === 'confirmed') (new EmailQueueService())->enqueue($registrationDbId);
        return ['registration' => [...$row, 'id' => $registrationDbId], 'token' => $rawToken];
    }

    private function nextRegistrationId(): string
    {
        $last = $this->db->table('registrations')->select('registration_id')->orderBy('id','DESC')->get(1)->getRowArray();
        $number = $last && preg_match('/(\d+)$/', $last['registration_id'], $m) ? ((int) $m[1] + 1) : 1;
        return 'EUPHORIA-2026-' . str_pad((string)$number, 6, '0', STR_PAD_LEFT);
    }
}