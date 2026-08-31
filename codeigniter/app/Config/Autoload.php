<?php

namespace Config;

use CodeIgniter\Config\AutoloadConfig;

class Autoload extends AutoloadConfig
{
    public $psr4 = ['App' => APPPATH];
    public $classmap = [];
    public $helpers = ['url', 'form', 'platform'];
}