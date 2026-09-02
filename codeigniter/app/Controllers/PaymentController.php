<?php

namespace App\Controllers;

use App\Services\AuditService;
use App\Services\Payment\EasebuzzGateway;
use App\Services\PaymentConfirmationService;
use RuntimeException;

class PaymentController extends BaseController
{
    public function checkout(string $registrationCode)
    {
        $db = db_connect();
        $registration = $db->table('registrations r')->select('r.*, e.name AS event_name, p.txnid, p.status AS payment_status')->join('events e','e.id=r.event_id')->join('payments p','p.registration_id=r.id')->where('r.registration_id',$registrationCode)->get()->getRowArray();
        if (!$registration) throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();
        if ($registration['status'] === 'confirmed') return redirect()->to('/registration/success/'.$registrationCode);
        try {
            $transactionId='EB-'.bin2hex(random_bytes(12));
            $productinfo=(string)env('EASEBUZZ_PRODUCTINFO','euphoria2026');
            $result = (new EasebuzzGateway())->initiate(['txnid'=>$transactionId,'amount'=>number_format((float)$registration['total_amount'],2,'.',''),'firstname'=>$registration['participant_name'],'email'=>$registration['email'],'phone'=>$registration['mobile'],'productinfo'=>$productinfo,'surl'=>base_url('payments/easebuzz/callback'),'furl'=>base_url('payments/easebuzz/callback'),'udf1'=>$registrationCode]);
            $db->table('payments')->where('registration_id',$registration['id'])->whereIn('status',['created','pending','initiated'])->update(['txnid'=>$transactionId,'productinfo'=>$productinfo,'status'=>'initiated','gateway_order_id'=>$result['access_key'],'updated_at'=>date('Y-m-d H:i:s')]);
            return redirect()->to($result['checkout_url']);
        } catch (\RuntimeException $e) {
            return $this->render('payments/unavailable',['registration'=>$registration,'message'=>$e->getMessage(),'title'=>'Payment setup required']);
        }
    }

    public function callback()
    {
        $payload = $this->request->getPost() ?: $this->request->getGet();
        try {
            $result=(new PaymentConfirmationService())->handle($payload);
            return redirect()->to('/registration/success/'.$result['registration_id']);
        } catch (RuntimeException $e) {
            (new AuditService())->record('payment.callback_rejected','payments',(string)($payload['txnid'] ?? null),['reason'=>$e->getMessage()]);
            return $this->response->setStatusCode(400)->setBody('Payment verification failed');
        }
    }

}