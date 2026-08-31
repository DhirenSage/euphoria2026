<?php

namespace App\Controllers;

use App\Models\UserModel;

class AuthController extends BaseController
{
    public function login() { return $this->render('auth/login', ['title'=>'Admin sign in']); }

    public function attempt()
    {
        $user = (new UserModel())->withRolesByEmail((string)$this->request->getPost('email'));
        if (!$user || !password_verify((string)$this->request->getPost('password'), $user['password_hash'])) return redirect()->back()->withInput()->with('error','Email or password is incorrect.');
        session()->regenerate(true);
        session()->set(['user_id'=>$user['id'],'user_name'=>$user['name'],'roles'=>$user['roles']]);
        return redirect()->to(in_array('SCANNER',$user['roles'],true) ? '/scanner' : '/admin');
    }

    public function logout() { session()->destroy(); return redirect()->to('/')->with('message','You have been signed out.'); }
}