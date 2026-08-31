<?php

namespace App\Models;

use CodeIgniter\Model;

class UserModel extends Model
{
    protected $table = 'users';
    protected $returnType = 'array';
    protected $allowedFields = ['name','email','phone','password_hash','is_active'];
    protected $useTimestamps = true;

    public function withRolesByEmail(string $email): ?array
    {
        $user = $this->where('email', strtolower(trim($email)))->where('is_active',1)->first();
        if (!$user) return null;
        $roles = $this->db->table('user_roles ur')->select('r.name')->join('roles r','r.id=ur.role_id')->where('ur.user_id',$user['id'])->get()->getResultArray();
        $user['roles'] = array_column($roles, 'name');
        return $user;
    }
}