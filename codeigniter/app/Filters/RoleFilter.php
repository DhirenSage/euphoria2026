<?php

namespace App\Filters;

use CodeIgniter\HTTP\RequestInterface;
use CodeIgniter\HTTP\ResponseInterface;
use CodeIgniter\Filters\FilterInterface;

class RoleFilter implements FilterInterface
{
    public function before(RequestInterface $request, $arguments = null)
    {
        $roles = session('roles') ?? [];
        if (! array_intersect($arguments ?? [], $roles)) return service('response')->setStatusCode(403)->setBody('Access denied');
    }

    public function after(RequestInterface $request, ResponseInterface $response, $arguments = null) {}
}