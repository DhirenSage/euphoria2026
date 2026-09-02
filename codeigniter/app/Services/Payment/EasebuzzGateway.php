<?php

namespace App\Services\Payment;

use App\Services\SettingsService;
use RuntimeException;

final class EasebuzzGateway implements PaymentGatewayInterface
{
    private string $key;
    private string $salt;
    private string $environment;
    private string $mode;

    public function __construct()
    {
        $settings = new SettingsService();
        $this->key = $settings->value('EASEBUZZ_KEY', 'EASEBUZZ_KEY');
        $this->salt = $settings->value('EASEBUZZ_SALT', 'EASEBUZZ_SALT');
        $this->environment = $settings->value('easebuzz_environment', null, (string) env('EASEBUZZ_ENV', 'test'));
        $this->mode = $settings->value('payment_mode', null, (string) env('PAYMENT_MODE', 'gateway'));
    }

    public function initiate(array $order): array
    {
        if ($this->mode === 'demo') throw new RuntimeException('Demo payment requires an admin verification action');
        if ($this->key === '' || $this->salt === '') throw new RuntimeException('Easebuzz is not configured. Add credentials in the deployment environment.');
        $required = ['txnid','amount','firstname','email','phone','productinfo','surl','furl'];
        foreach ($required as $field) if (empty($order[$field])) throw new RuntimeException("Missing payment field: {$field}");
        $hashFields = ['key','txnid','amount','productinfo','firstname','email','udf1','udf2','udf3','udf4','udf5','udf6','udf7','udf8','udf9','udf10'];
        $payload = $order;
        $payload['key'] = $this->key;
        $values = array_map(fn (string $field) => (string) ($payload[$field] ?? ''), $hashFields);
        $payload['hash'] = hash('sha512', implode('|', [...$values, $this->salt]));
        unset($payload['udf8'], $payload['udf9'], $payload['udf10']);
        $ch = curl_init($this->baseUrl() . 'payment/initiateLink');
        curl_setopt_array($ch, [CURLOPT_POST=>true,CURLOPT_POSTFIELDS=>http_build_query($payload),CURLOPT_RETURNTRANSFER=>true,CURLOPT_TIMEOUT=>(int)env('EASEBUZZ_TIMEOUT',20),CURLOPT_SSL_VERIFYPEER=>true]);
        $raw = curl_exec($ch);
        if ($raw === false) throw new RuntimeException(curl_error($ch));
        $statusCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        $gateway = json_decode($raw, true);
        $accessKey = $gateway['data'] ?? $gateway['access_key'] ?? null;
        if ($statusCode >= 400 || ($gateway['status'] ?? 0) != 1 || !is_string($accessKey)) throw new RuntimeException($gateway['error_desc'] ?? 'Easebuzz could not create the payment page.');
        return ['checkout_url'=>$this->baseUrl().'pay/'.rawurlencode($accessKey),'access_key'=>$accessKey];
    }

    public function verifyCallback(array $payload): bool
    {
        $callbackSalt = $this->salt;
        if (($payload['key'] ?? '') !== $this->key && ($payload['key'] ?? '') === (string)env('EASEBUZZ_BACKUP_KEY','')) $callbackSalt = (string)env('EASEBUZZ_BACKUP_SALT','');
        if ($callbackSalt === '' || !in_array(($payload['key'] ?? ''),[$this->key,(string)env('EASEBUZZ_BACKUP_KEY','')],true)) return false;
        $fields = ['salt','status','udf10','udf9','udf8','udf7','udf6','udf5','udf4','udf3','udf2','udf1','email','firstname','productinfo','amount','txnid','key'];
        $values = array_map(fn (string $field) => $field === 'salt' ? $callbackSalt : (string) ($payload[$field] ?? ''), $fields);
        $expected = hash('sha512', implode('|', $values));
        return isset($payload['hash']) && hash_equals(strtolower($expected), strtolower((string) $payload['hash']));
    }

    public function signDevelopmentCallback(array $payload): array
    {
        if (ENVIRONMENT === 'production' || !filter_var(env('EASEBUZZ_ALLOW_SIGNED_CALLBACK_TEST', false), FILTER_VALIDATE_BOOL)) {
            throw new RuntimeException('Signed callback fixtures are disabled.');
        }
        $payload['key'] = $this->key;
        $fields = ['salt','status','udf10','udf9','udf8','udf7','udf6','udf5','udf4','udf3','udf2','udf1','email','firstname','productinfo','amount','txnid','key'];
        $values = array_map(fn (string $field) => $field === 'salt' ? $this->salt : (string) ($payload[$field] ?? ''), $fields);
        $payload['hash'] = hash('sha512', implode('|', $values));
        return $payload;
    }

    public function reconcile(string $txnid): array
    {
        if ($this->key === '' || $this->salt === '') throw new RuntimeException('Easebuzz is not configured');
        $payload = ['key' => $this->key, 'txnid' => $txnid];
        $payload['hash'] = hash('sha512', $this->key . '|' . $txnid . '|' . $this->salt);
        $ch = curl_init($this->baseUrl() . 'transaction/v2/retrieve');
        curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_POSTFIELDS => http_build_query($payload), CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => (int) env('EASEBUZZ_TIMEOUT', 20), CURLOPT_SSL_VERIFYPEER => true]);
        $raw = curl_exec($ch);
        if ($raw === false) throw new RuntimeException(curl_error($ch));
        curl_close($ch);
        return json_decode($raw, true) ?: ['status' => 'unknown'];
    }

    private function baseUrl(): string
    {
        return $this->environment === 'prod' ? 'https://pay.easebuzz.in/' : 'https://testpay.easebuzz.in/';
    }
}