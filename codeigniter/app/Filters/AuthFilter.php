<?php

namespace App\Filters;

use CodeIgniter\HTTP\RequestInterface;
use CodeIgniter\HTTP\ResponseInterface;
use CodeIgniter\Filters\FilterInterface;

class AuthFilter implements FilterInterface
{
    public function before(RequestInterface $request, $arguments = null)
    {
        if (! session('user_id')) return redirect()->to('/login')->with('error','Please sign in to continue.');
    }

    public function after(RequestInterface $request, ResponseInterface $response, $arguments = null) {}
}