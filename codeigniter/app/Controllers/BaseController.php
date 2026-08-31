<?php

namespace App\Controllers;

use CodeIgniter\Controller;

abstract class BaseController extends Controller
{
    protected function render(string $view, array $data = [])
    {
        return view('layouts/main', ['content' => view($view, $data), ...$data]);
    }
}