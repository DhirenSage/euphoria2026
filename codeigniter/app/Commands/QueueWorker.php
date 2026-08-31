<?php

namespace App\Commands;

use App\Services\EmailQueueService;
use CodeIgniter\CLI\CLI;
use CodeIgniter\CLI\BaseCommand;

class QueueWorker extends BaseCommand
{
    protected $group = 'EUPHORIA';
    protected $name = 'queue:work';
    protected $description = 'Process queued pass emails and reminders.';

    public function run(array $params)
    {
        $once = in_array('--once', $params, true);
        CLI::write('EUPHORIA email queue worker started.', 'green');
        do {
            $processed = (new EmailQueueService())->processOne();
            if (!$processed && !$once) sleep(5);
        } while (!$once);
    }
}