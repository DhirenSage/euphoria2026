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
        $lockedEvent = $this->db->query('SELECT * FROM events WHERE id = ? FOR UPDATE', [(int) $event['id']])->getRowArray();
        if (!$lockedEvent || $lockedEvent['status'] !== 'registration_open') throw new RuntimeException('Registration for this event is closed.');
        $count = $this->db->table('registrations')->where('event_id', $lockedEvent['id'])->whereIn('status', ['pending_payment','confirmed'])->countAllResults();
        if ((int) $lockedEvent['capacity'] > 0 && $count >= (int) $lockedEvent['capacity']) throw new RuntimeException('This event has reached its registration capacity.');
        $registrationId = $this->nextRegistrationId();
        $amount = max(0, (float) $lockedEvent['fee'] + (float) ($lockedEvent['tax_amount'] ?? 0) - (float) ($lockedEvent['discount_amount'] ?? 0));
        $status = !empty($lockedEvent['payment_required']) && $amount > 0 ? 'pending_payment' : 'confirmed';
        $now = date('Y-m-d H:i:s');
        $registrationType = in_array($lockedEvent['registration_type'], ['individual','team'], true) ? $lockedEvent['registration_type'] : 'individual';
        if ($registrationType === 'team' && trim($input['team_name'] ?? '') === '') throw new RuntimeException('Team name is required for this event.');
        $members = array_values(array_filter(array_map('trim', preg_split('/\r\n|\r|\n/', trim((string) ($input['team_member_names'] ?? ''))) ?: [])));
        $teamSize = 1 + count($members);
        if ($registrationType === 'team' && !empty($lockedEvent['min_team_size']) && $teamSize < (int) $lockedEvent['min_team_size']) throw new RuntimeException('This event requires at least ' . $lockedEvent['min_team_size'] . ' team members including the captain.');
        if ($registrationType === 'team' && !empty($lockedEvent['max_team_size']) && $teamSize > (int) $lockedEvent['max_team_size']) throw new RuntimeException('This event allows at most ' . $lockedEvent['max_team_size'] . ' team members including the captain.');
        $passAccess = bin2hex(random_bytes(24));
        $row = ['event_id'=>$lockedEvent['id'],'registration_id'=>$registrationId,'participant_name'=>trim($input['participant_name']),'father_name'=>trim($input['father_name'] ?? ''),'email'=>strtolower(trim($input['email'])),'mobile'=>trim($input['mobile']),'age'=>($input['age'] ?? '') !== '' ? (int)$input['age'] : null,'college'=>trim($input['college'] ?? ''),'city'=>trim($input['city'] ?? ''),'participant_affiliation'=>$input['participant_affiliation'],'registration_type'=>$registrationType,'team_name'=>$registrationType === 'team' ? trim($input['team_name'] ?? '') : null,'total_amount'=>$amount,'status'=>$status,'qr_status'=>'active','pass_access_hash'=>hash('sha256',$passAccess),'pass_access_ciphertext'=>base64_encode(service('encrypter')->encrypt($passAccess)),'created_at'=>$now,'updated_at'=>$now];
        $this->db->table('registrations')->insert($row);
        $registrationDbId = (int) $this->db->insertID();
        $rawToken = 'EUPHORIA-' . bin2hex(random_bytes(20));
        $this->db->table('qr_tokens')->insert(['registration_id'=>$registrationDbId,'token_hash'=>hash('sha256',$rawToken),'token_hint'=>substr($rawToken,-8),'token_ciphertext'=>base64_encode(service('encrypter')->encrypt($rawToken)),'status'=>'active','created_at'=>$now]);
        $productinfo = (string) env('EASEBUZZ_PRODUCTINFO','euphoria2026');
        if ($status === 'confirmed') $this->db->table('payments')->insert(['registration_id'=>$registrationDbId,'txnid'=>'FREE-' . $registrationId,'amount'=>0,'productinfo'=>$productinfo,'gateway'=>'free','status'=>'success','paid_at'=>$now,'created_at'=>$now,'updated_at'=>$now]);
        else $this->db->table('payments')->insert(['registration_id'=>$registrationDbId,'txnid'=>'EB-' . bin2hex(random_bytes(12)),'amount'=>$amount,'productinfo'=>$productinfo,'gateway'=>'easebuzz','status'=>'created','created_at'=>$now,'updated_at'=>$now]);
        $fields=$this->db->table('registration_fields')->where('event_id',$lockedEvent['id'])->where('is_active',1)->orderBy('display_order','ASC')->get()->getResultArray();
        foreach($fields as $field){$value=$input[$field['field_name']]??null;if((int)$field['is_required'] && ($value===null||$value==='')) throw new RuntimeException($field['label'].' is required.');if($value!==null&&$value!=='')$this->db->table('registration_field_values')->insert(['registration_id'=>$registrationDbId,'field_id'=>$field['id'],'value_text'=>is_array($value)?json_encode($value):trim((string)$value),'created_at'=>$now]);}
        if($registrationType==='team'){foreach($members as $member)$this->db->table('registration_members')->insert(['registration_id'=>$registrationDbId,'name'=>$member,'created_at'=>$now]);}
        $this->db->transComplete();
        if ($this->db->transStatus() === false) throw new RuntimeException('Could not complete registration.');
        if ($status === 'confirmed') (new EmailQueueService())->enqueue($registrationDbId);
        return ['registration' => [...$row, 'id' => $registrationDbId], 'token' => $rawToken, 'pass_access' => $passAccess];
    }

    private function nextRegistrationId(): string
    {
        $key = 'euphoria-2026';
        $sequence = $this->db->query('SELECT next_value FROM registration_sequences WHERE sequence_key = ? FOR UPDATE', [$key])->getRowArray();
        if (!$sequence) {
            $number = 1;
            $this->db->table('registration_sequences')->insert(['sequence_key'=>$key,'next_value'=>2]);
        } else {
            $number = (int) $sequence['next_value'];
            $this->db->table('registration_sequences')->where('sequence_key',$key)->update(['next_value'=>$number+1]);
        }
        return 'EUPHORIA-2026-' . str_pad((string)$number, 6, '0', STR_PAD_LEFT);
    }
}