<?php

namespace App\Controllers;

use App\Services\Payment\EasebuzzGateway;
use App\Services\PaymentConfirmationService;

class DevCallbackController extends BaseController
{
    public function confirm()
    {
        if (ENVIRONMENT === 'production' || !filter_var(env('EASEBUZZ_ALLOW_SIGNED_CALLBACK_TEST', false), FILTER_VALIDATE_BOOL)) {
            throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();
        }
        $registrationCode = trim((string) $this->request->getPost('registration_id'));
        $payment = db_connect()->table('payments p')
            ->select('p.*, r.participant_name, r.email, r.mobile, r.registration_id AS registration_code')
            ->join('registrations r', 'r.id=p.registration_id')
            ->where('r.registration_id', $registrationCode)
            ->get()->getRowArray();
        if (!$payment) {
            return $this->response->setStatusCode(404)->setJSON(['ok' => false, 'message' => 'Registration payment not found.']);
        }
        $payload = [
            'status' => 'success',
            'udf1' => $payment['registration_code'],
            'udf2' => '', 'udf3' => '', 'udf4' => '', 'udf5' => '',
            'udf6' => '', 'udf7' => '', 'udf8' => '', 'udf9' => '', 'udf10' => '',
            'email' => $payment['email'],
            'firstname' => $payment['participant_name'],
            'productinfo' => $payment['productinfo'],
            'amount' => number_format((float) $payment['amount'], 2, '.', ''),
            'txnid' => $payment['txnid'],
            'easepayid' => 'DEV-' . bin2hex(random_bytes(6)),
        ];
        $payload = (new EasebuzzGateway())->signDevelopmentCallback($payload);
        $result = (new PaymentConfirmationService())->handle($payload);
        return $this->response->setJSON(['ok' => true, ...$result, 'pass_url' => base_url('registration/success/' . $registrationCode)]);
    }
}