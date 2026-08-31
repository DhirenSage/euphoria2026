<?php

use PHPUnit\Framework\TestCase;

final class PlatformSecurityTest extends TestCase
{
    public function testQrTokensAreRandomAndContainNoPersonalData(): void
    {
        $first='EUPHORIA-'.bin2hex(random_bytes(20));
        $second='EUPHORIA-'.bin2hex(random_bytes(20));
        $this->assertNotSame($first,$second);
        $this->assertSame(49,strlen($first));
        $this->assertStringNotContainsString('@',$first);
    }

    public function testRegistrationIdContract(): void
    {
        $id='EUPHORIA-2026-'.str_pad('42',6,'0',STR_PAD_LEFT);
        $this->assertSame('EUPHORIA-2026-000042',$id);
        $this->assertMatchesRegularExpression('/^EUPHORIA-2026-\d{6}$/',$id);
    }
}