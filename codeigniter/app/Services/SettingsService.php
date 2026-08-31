<?php

namespace App\Services;

final class SettingsService
{
    public function value(string $key, ?string $environmentKey = null, string $default = ''): string
    {
        if ($environmentKey !== null && (string) env($environmentKey, '') !== '') return (string) env($environmentKey);
        $row = db_connect()->table('settings')->where('setting_key', $key)->get()->getRowArray();
        if (!$row || $row['setting_value'] === null || $row['setting_value'] === '') return $default;
        if (!(int) $row['is_secret']) return (string) $row['setting_value'];
        try { return service('encrypter')->decrypt(base64_decode((string) $row['setting_value'], true)); } catch (\Throwable) { return ''; }
    }

    public function save(array $values, array $secrets, int $userId): void
    {
        $db = db_connect();
        foreach ($values as $key => $value) $db->table('settings')->replace(['setting_key'=>$key,'setting_value'=>(string)$value,'is_secret'=>0,'updated_by'=>$userId,'updated_at'=>date('Y-m-d H:i:s')]);
        foreach ($secrets as $key => $value) {
            if (trim((string)$value) === '') continue;
            $ciphertext = base64_encode(service('encrypter')->encrypt((string)$value));
            $db->table('settings')->replace(['setting_key'=>$key,'setting_value'=>$ciphertext,'is_secret'=>1,'updated_by'=>$userId,'updated_at'=>date('Y-m-d H:i:s')]);
        }
    }

    public function isConfigured(string $key, ?string $environmentKey = null): bool
    {
        return $this->value($key, $environmentKey) !== '';
    }
}