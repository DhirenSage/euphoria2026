<?php

namespace App\Controllers;

use App\Services\AuditService;
use App\Services\Payment\EasebuzzGateway;

class PaymentController extends BaseController
{
    public function checkout(string $registrationCode)
    {
        $db = db_connect();
        $registration = $db->table('registrations r')->select('r.*, e.name AS event_name, p.txnid, p.status AS payment_status')->join('events e','e.id=r.event_id')->join('payments p','p.registration_id=r.id')->where('r.registration_id',$registrationCode)->get()->getRowArray();
        if (!$registration) throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();
        if ($registration['status'] === 'confirmed') return redirect()->to('/registration/success/'.$registrationCode);
        try {
            $result = (new EasebuzzGateway())->initiate(['txnid'=>$registration['txnid'],'amount'=>number_format((float)$registration['total_amount'],2,'.',''),'firstname'=>$registration['participant_name'],'email'=>$registration['email'],'phone'=>$registration['mobile'],'productinfo'=>'EUPHORIA 2026 · '.$registration['event_name'],'surl'=>base_url('payments/easebuzz/callback'),'furl'=>base_url('payments/easebuzz/callback'),'udf1'=>$registrationCode]);
            $db->table('payments')->where('txnid',$registration['txnid'])->whereIn('status',['created','pending'])->update(['status'=>'initiated','updated_at'=>date('Y-m-d H:i:s')]);
            return view('payments/redirect_form', $result);
        } catch (\RuntimeException $e) {
            return $this->render('payments/unavailable',['registration'=>$registration,'message'=>$e->getMessage(),'title'=>'Payment setup required']);
        }
    }

    public function callback()
    {
        $payload = $this->request->getPost() ?: $this->request->getGet();
        if (!(new EasebuzzGateway())->verifyCallback($payload)) {
            (new AuditService())->record('payment.invalid_signature','payments',(string)($payload['txnid'] ?? null));
            return $this->response->setStatusCode(400)->setBody('Invalid payment callback');
        }
        $payment = db_connect()->table('payments')->where('txnid',$payload['txnid'])->get()->getRowArray();
        if (!$payment) return $this->response->setStatusCode(404)->setBody('Payment not found');
        $status = strtolower((string)($payload['status'] ?? 'unknown')) === 'success' ? 'success' : 'failed';
        db_connect()->table('payments')->where('id',$payment['id'])->whereIn('status',['created','pending','initiated','unknown'])->update(['status'=>$status,'gateway_payment_id'=>$payload['easepayid'] ?? null,'raw_reference'=>json_encode(['status'=>$payload['status'] ?? null]),'paid_at'=>$status==='success'?date('Y-m-d H:i:s'):null,'updated_at'=>date('Y-m-d H:i:s')]);
        if ($status === 'success') {
            db_connect()->table('registrations')->where('id',$payment['registration_id'])->update(['status'=>'confirmed','updated_at'=>date('Y-m-d H:i:s')]);
            (new \App\Services\EmailQueueService())->enqueue((int)$payment['registration_id']);
        }
        return redirect()->to('/registration/success/'.$this->registrationCode((int)$payment['registration_id']));
    }

    private function registrationCode(int $id): string { return (string)db_connect()->table('registrations')->select('registration_id')->where('id',$id)->get()->getRow('registration_id'); }
}