<?php

namespace App\Services;

final class EmailQueueService
{
    public function enqueue(int $registrationId, string $templateKey = 'event_pass'): void
    {
        db_connect()->table('email_jobs')->insert(['registration_id'=>$registrationId,'template_key'=>$templateKey,'status'=>'pending','attempts'=>0,'available_at'=>date('Y-m-d H:i:s'),'created_at'=>date('Y-m-d H:i:s'),'updated_at'=>date('Y-m-d H:i:s')]);
    }

    public function processOne(): bool
    {
        $db = db_connect();
        $job = $db->table('email_jobs')->where('status','pending')->where('available_at <=',date('Y-m-d H:i:s'))->orderBy('id','ASC')->get()->getRowArray();
        if (!$job) return false;
        $db->table('email_jobs')->where('id',$job['id'])->where('status','pending')->update(['status'=>'processing','locked_at'=>date('Y-m-d H:i:s'),'attempts'=>(int)$job['attempts']+1,'updated_at'=>date('Y-m-d H:i:s')]);
        $registration = $db->table('registrations r')->select('r.*, e.name AS event_name, e.event_start, e.venue, c.name AS category_name, q.token_ciphertext')->join('events e','e.id=r.event_id')->join('categories c','c.id=e.category_id')->join('qr_tokens q','q.registration_id=r.id')->where('r.id',$job['registration_id'])->get()->getRowArray();
        if (!$registration || $registration['status'] !== 'confirmed' || !$registration['token_ciphertext']) return $this->fail($job, 'Confirmed registration or pass token not found');
        $settings = new SettingsService();
        $smtpHost = $settings->value('SMTP_HOST','email.SMTPHost');
        $smtpUser = $settings->value('SMTP_USER','email.SMTPUser');
        $smtpPass = $settings->value('SMTP_PASSWORD','email.SMTPPass');
        if ($smtpHost === '' || $smtpUser === '' || $smtpPass === '') return $this->fail($job, 'SMTP is not configured');
        try {
            $token = service('encrypter')->decrypt(base64_decode($registration['token_ciphertext'], true));
            $path = (new PassService())->pdf($registration, $token);
            $email = service('email');
            $email->initialize(['protocol'=>'smtp','SMTPHost'=>$smtpHost,'SMTPUser'=>$smtpUser,'SMTPPass'=>$smtpPass,'SMTPPort'=>(int)$settings->value('SMTP_PORT','email.SMTPPort','587'),'SMTPCrypto'=>$settings->value('SMTP_CRYPTO','email.SMTPCrypto','tls'),'mailType'=>'html']);
            $subject = $settings->value('email_subject', null, 'Euphoria 2026 – Your Event Registration is Confirmed');
            $email->setFrom($settings->value('SMTP_FROM_EMAIL','email.fromEmail','noreply@example.com'),$settings->value('SMTP_FROM_NAME','email.fromName','EUPHORIA 2026'))->setTo($registration['email'])->setSubject($subject)->setMessage(view('emails/event_pass',['registration'=>$registration]))->attach($path,'attachment','euphoria-pass.pdf','application/pdf');
            if (!$email->send()) throw new \RuntimeException('SMTP delivery failed');
            @unlink($path);
            $db->table('email_jobs')->where('id',$job['id'])->update(['status'=>'sent','updated_at'=>date('Y-m-d H:i:s')]);
            $db->table('email_logs')->insert(['registration_id'=>$registration['id'],'recipient'=>$registration['email'],'template_key'=>$job['template_key'],'subject'=>$subject,'status'=>'sent','created_at'=>date('Y-m-d H:i:s')]);
            return true;
        } catch (\Throwable $e) { return $this->fail($job, $e->getMessage()); }
    }

    private function fail(array $job, string $error): bool
    {
        $status = (int)$job['attempts'] + 1 >= 3 ? 'failed' : 'pending';
        db_connect()->table('email_jobs')->where('id',$job['id'])->update(['status'=>$status,'available_at'=>date('Y-m-d H:i:s',time()+300),'last_error'=>substr($error,0,1000),'updated_at'=>date('Y-m-d H:i:s')]);
        return false;
    }
}