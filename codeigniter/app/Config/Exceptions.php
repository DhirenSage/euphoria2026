<?php

namespace Config;

use CodeIgniter\Config\BaseConfig;
use CodeIgniter\Debug\ExceptionHandler;
use CodeIgniter\Debug\ExceptionHandlerInterface;
use Psr\Log\LogLevel;
use Throwable;

class Exceptions extends BaseConfig
{
    public string $errorViewPath = APPPATH . 'Views/errors';
    public bool $log = true;
    public array $ignoreCodes = [404];
    public bool $logDeprecations = true;
    public string $deprecationLogLevel = LogLevel::WARNING;
    public array $sensitiveDataInTrace = [];

    public function handler(int $statusCode, Throwable $exception): ExceptionHandlerInterface
    {
        return new ExceptionHandler($this);
    }
}