<?php

namespace Config;

use CodeIgniter\Config\BaseConfig;

class Email extends BaseConfig
{
    public string $protocol = 'smtp';
    public string $SMTPHost = '';
    public string $SMTPUser = '';
    public string $SMTPPass = '';
    public int $SMTPPort = 587;
    public string $SMTPCrypto = 'tls';
    public string $mailType = 'html';
    public string $charset = 'UTF-8';
    public bool $wordWrap = true;
    public string $fromEmail = '';
    public string $fromName = 'EUPHORIA 2026';
}