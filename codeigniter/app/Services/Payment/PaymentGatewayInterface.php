<?php

namespace App\Services\Payment;

interface PaymentGatewayInterface
{
    public function initiate(array $order): array;
    public function verifyCallback(array $payload): bool;
    public function reconcile(string $txnid): array;
}