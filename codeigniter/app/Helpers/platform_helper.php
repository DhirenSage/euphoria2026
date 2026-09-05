<?php

if (! function_exists('money')) {
    function money(float|int|string $amount): string
    {
        return '₹' . number_format((float) $amount, 0);
    }
}

if (! function_exists('status_class')) {
    function status_class(string $status): string
    {
        return match (strtolower($status)) {
            'confirmed', 'success', 'active', 'registration open' => 'status status-success',
            'pending', 'pending payment', 'scheduled' => 'status status-warning',
            'cancelled', 'failed', 'revoked' => 'status status-danger',
            default => 'status',
        };
    }
}

if (! function_exists('event_affiliation_fee')) {
    function event_affiliation_fee(array $event, string $affiliation): float
    {
        $legacy = (float) ($event['fee'] ?? 0);
        return max(0, (float) ($affiliation === 'sageian'
            ? ($event['sageian_fee'] ?? $legacy)
            : ($event['non_sageian_fee'] ?? $legacy)));
    }
}

if (! function_exists('event_fee_label')) {
    function event_fee_label(array $event): string
    {
        $sageian = event_affiliation_fee($event, 'sageian');
        $nonSageian = event_affiliation_fee($event, 'non_sageian');
        if ($sageian === $nonSageian) return $sageian > 0 ? money($sageian) : 'FREE';
        return 'SAGEian ' . ($sageian > 0 ? money($sageian) : 'FREE') . ' · Non-SAGEian ' . ($nonSageian > 0 ? money($nonSageian) : 'FREE');
    }
}

if (! function_exists('safe_slug')) {
    function safe_slug(string $value): string
    {
        return trim(preg_replace('/[^a-z0-9]+/i', '-', strtolower($value)), '-');
    }
}