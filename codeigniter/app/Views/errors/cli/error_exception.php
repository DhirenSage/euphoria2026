<?php
echo ($message ?? 'CodeIgniter exception') . PHP_EOL;
if (isset($exception) && $exception instanceof Throwable) echo $exception->getTraceAsString() . PHP_EOL;