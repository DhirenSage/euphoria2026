<?php

use PHPUnit\Framework\TestCase;

final class CoreWorkflowContractsTest extends TestCase
{
    public function testAttendanceHasDatabaseLevelEventDayUniqueness(): void
    {
        $migration=file_get_contents(__DIR__.'/../../app/Database/Migrations/2026-01-01-000001_CreatePlatformTables.php');
        $this->assertStringContainsString('UNIQUE KEY daily_entry (event_id,registration_id,event_day_id)', $migration);
    }

    public function testPaymentConfirmationChecksStoredProductAndAmount(): void
    {
        $service=file_get_contents(__DIR__.'/../../app/Services/PaymentConfirmationService.php');
        $this->assertStringContainsString("hash_equals((string) \$payment['productinfo']", $service);
        $this->assertStringContainsString("\$payment['amount']", $service);
        $this->assertStringContainsString('SELECT * FROM payments WHERE id = ? FOR UPDATE', $service);
    }

    public function testSignedCallbackFixtureCannotRunInProduction(): void
    {
        $controller=file_get_contents(__DIR__.'/../../app/Controllers/DevCallbackController.php');
        $gateway=file_get_contents(__DIR__.'/../../app/Services/Payment/EasebuzzGateway.php');
        $this->assertStringContainsString("ENVIRONMENT === 'production'", $controller);
        $this->assertStringContainsString("ENVIRONMENT === 'production'", $gateway);
    }

    public function testSecretsAreExcludedFromVersionControl(): void
    {
        $ignore=file_get_contents(__DIR__.'/../../.gitignore');
        $this->assertMatchesRegularExpression('/^\.env$/m', $ignore);
        $example=file_get_contents(__DIR__.'/../../env');
        $this->assertStringNotContainsString('vegk', $example);
    }
}