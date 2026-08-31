<?php

namespace App\Services;

use App\Models\AuditLogModel;

final class AuditService
{
    public function record(string $action, string $module, ?string $recordId = null, array $metadata = []): void
    {
        model(AuditLogModel::class)->insert([
            'user_id' => session('user_id'),
            'action' => $action,
            'module' => $module,
            'record_id' => $recordId,
            'ip_address' => service('request')->getIPAddress(),
            'metadata_json' => json_encode($metadata, JSON_THROW_ON_ERROR),
            'created_at' => date('Y-m-d H:i:s'),
        ]);
    }
}