<?php

namespace App\Services;

use App\Services\Payment\EasebuzzGateway;
use RuntimeException;

final class PaymentConfirmationService
{
    public function handle(array $payload): array
    {
        $gateway = new EasebuzzGateway();
        if (!$gateway->verifyCallback($payload)) {
            throw new RuntimeException('Invalid payment callback signature.');
        }

        $db = db_connect();
        $payment = $db->table('payments p')
            ->select('p.*, r.registration_id AS registration_code, r.status AS registration_status')
            ->join('registrations r', 'r.id=p.registration_id')
            ->where('p.txnid', (string) ($payload['txnid'] ?? ''))
            ->get()->getRowArray();
        if (!$payment) {
            throw new RuntimeException('Payment not found.');
        }
        if (!hash_equals((string) $payment['productinfo'], (string) ($payload['productinfo'] ?? ''))
            || number_format((float) $payment['amount'], 2, '.', '') !== number_format((float) ($payload['amount'] ?? -1), 2, '.', '')) {
            throw new RuntimeException('Payment amount or product mismatch.');
        }

        $status = strtolower((string) ($payload['status'] ?? '')) === 'success' ? 'success' : 'failed';
        $db->transStart();
        $locked = $db->query('SELECT * FROM payments WHERE id = ? FOR UPDATE', [(int) $payment['id']])->getRowArray();
        $changed = false;
        if ($locked && $locked['status'] !== 'success') {
            $db->table('payments')->where('id', $locked['id'])->update([
                'status' => $status,
                'gateway_payment_id' => substr((string) ($payload['easepayid'] ?? ''), 0, 120) ?: null,
                'raw_reference' => json_encode([
                    'status' => $payload['status'] ?? null,
                    'unmappedstatus' => $payload['unmappedstatus'] ?? null,
                    'bank_ref_num' => $payload['bank_ref_num'] ?? null,
                ], JSON_THROW_ON_ERROR),
                'paid_at' => $status === 'success' ? date('Y-m-d H:i:s') : null,
                'updated_at' => date('Y-m-d H:i:s'),
            ]);
            $db->table('payment_transactions')->insert([
                'payment_id' => $locked['id'],
                'action' => 'callback',
                'gateway_reference' => substr((string) ($payload['easepayid'] ?? ''), 0, 160) ?: null,
                'status' => $status,
                'response_digest' => hash('sha256', json_encode($payload, JSON_THROW_ON_ERROR)),
                'created_at' => date('Y-m-d H:i:s'),
            ]);
            if ($status === 'success') {
                $db->table('registrations')->where('id', $locked['registration_id'])->update([
                    'status' => 'confirmed',
                    'qr_status' => 'active',
                    'updated_at' => date('Y-m-d H:i:s'),
                ]);
            }
            $changed = true;
        }
        $db->transComplete();
        if (!$db->transStatus()) {
            throw new RuntimeException('Payment confirmation could not be committed.');
        }
        if ($changed && $status === 'success') {
            (new EmailQueueService())->enqueue((int) $payment['registration_id']);
        }

        (new AuditService())->record('payment.callback_' . $status, 'payments', (string) $payment['id'], ['changed' => $changed]);
        return [
            'status' => $locked['status'] === 'success' ? 'success' : $status,
            'registration_id' => $payment['registration_code'],
            'changed' => $changed,
        ];
    }
}