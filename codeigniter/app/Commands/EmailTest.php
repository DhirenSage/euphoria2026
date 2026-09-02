<?php

namespace App\Commands;

use App\Services\EmailQueueService;
use CodeIgniter\CLI\BaseCommand;
use CodeIgniter\CLI\CLI;

class EmailTest extends BaseCommand
{
    protected $group = 'EUPHORIA';
    protected $name = 'emails:test';
    protected $description = 'Send a real SMTP configuration test email.';

    public function run(array $params)
    {
        $to = $params[0] ?? (string) env('email.SMTPUser', '');
        if ($to === '') {
            CLI::error('Recipient required: php spark emails:test recipient@example.com');
            return;
        }
        (new EmailQueueService())->sendTest($to);
        CLI::write('SMTP test accepted by the provider for ' . $to, 'green');
    }
}