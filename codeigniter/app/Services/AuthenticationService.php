<?php

namespace App\Services;

use App\Models\UserModel;
use RuntimeException;

final class AuthenticationService
{
    public function authenticate(string $email, string $password, array $allowedRoles, string $scope): array
    {
        $email = strtolower(trim($email));
        $key = 'login_' . hash('sha256', service('request')->getIPAddress() . '|' . $scope . '|' . $email);
        $attempts = (int) (cache($key) ?? 0);
        if ($attempts >= 5) {
            throw new RuntimeException('Too many sign-in attempts. Try again in 15 minutes.');
        }

        $user = (new UserModel())->withRolesByEmail($email);
        if (!$user || !password_verify($password, (string) $user['password_hash']) || !array_intersect($allowedRoles, $user['roles'])) {
            cache()->save($key, $attempts + 1, 900);
            throw new RuntimeException('Email or password is incorrect for this portal.');
        }

        cache()->delete($key);
        session()->regenerate(true);
        session()->set([
            'user_id' => (int) $user['id'],
            'user_name' => (string) $user['name'],
            'roles' => $user['roles'],
            'last_activity' => time(),
        ]);
        return $user;
    }
}