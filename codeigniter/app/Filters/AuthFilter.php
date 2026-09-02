<?php

namespace App\Filters;

use CodeIgniter\HTTP\RequestInterface;
use CodeIgniter\HTTP\ResponseInterface;
use CodeIgniter\Filters\FilterInterface;

class AuthFilter implements FilterInterface
{
    public function before(RequestInterface $request, $arguments = null)
    {
        if (! session('user_id')) {
            $portal = str_starts_with(trim($request->getUri()->getPath(), '/'), 'scanner') ? '/scanner/login' : '/admin/login';
            return redirect()->to($portal)->with('error','Please sign in to continue.');
        }
        if ((int) session('last_activity') < time() - 28800) {
            session()->destroy();
            return redirect()->to('/admin/login')->with('error','Your secure session expired. Please sign in again.');
        }
        session()->set('last_activity',time());
        if ($arguments && !array_intersect($arguments, session('roles') ?? [])) {
            return service('response')->setStatusCode(403)->setBody('Access denied');
        }
    }

    public function after(RequestInterface $request, ResponseInterface $response, $arguments = null) {}
}