<?php
/**
 * Auth handlers: login, verify-token, forgot-password, reset-password
 */

function auth_forgot_password() {
    $data = getJsonBody();
    $email = trim((string)($data['email'] ?? ''));
    if ($email === '') {
        jsonResp(['success' => false, 'error' => 'Email required'], 400);
    }

    $pdo = db();
    // Find user by registered email (gmail column)
    $st = $pdo->prepare("SELECT id, username, gmail FROM Users WHERE LOWER(TRIM(gmail)) = LOWER(?) AND gmail IS NOT NULL AND gmail != ''");
    $st->execute([$email]);
    $user = $st->fetch(PDO::FETCH_ASSOC);

    // Always return success to avoid revealing whether email exists
    if (!$user) {
        jsonResp(['success' => true, 'message' => 'If an account exists with this email, you will receive a password reset link.']);
        return;
    }

    $cfg = getConfig();
    $baseUrl = rtrim($cfg['dashboard_base_url'] ?? 'https://abhinavpaudel.com', '/');
    $mailFrom = $cfg['mail_from'] ?? 'noreply@abhinavpaudel.com';

    $rawToken = bin2hex(random_bytes(32));
    $tokenHash = hash('sha256', $rawToken);
    $expiresAt = date('Y-m-d H:i:s', time() + 3600); // 1 hour

    try {
        $pdo->prepare("INSERT INTO PasswordResetTokens (user_id, token_hash, expires_at) VALUES (?, ?, ?)")
            ->execute([$user['id'], $tokenHash, $expiresAt]);
    } catch (Throwable $e) {
        jsonResp(['success' => false, 'error' => 'Unable to create reset token. Ensure PasswordResetTokens table exists.'], 500);
        return;
    }

    $resetLink = $baseUrl . '/reset-password?token=' . urlencode($rawToken);
    $to = $user['gmail'];
    $subject = 'Reset your DCES password';
    $body = "Hello " . ($user['username'] ?? '') . ",\n\n"
        . "You requested a password reset for your DCES account.\n\n"
        . "Click the link below to set a new password (link expires in 1 hour):\n"
        . $resetLink . "\n\n"
        . "If you did not request this, you can ignore this email.\n\n"
        . "— DCES";

    sendMail($to, $subject, $body, $mailFrom);

    jsonResp(['success' => true, 'message' => 'If an account exists with this email, you will receive a password reset link.']);
}

function auth_reset_password() {
    $data = getJsonBody();
    $token = trim((string)($data['token'] ?? ''));
    $newPassword = $data['newPassword'] ?? $data['new_password'] ?? '';
    if ($token === '' || $newPassword === '') {
        jsonResp(['success' => false, 'error' => 'Token and new password required'], 400);
    }
    if (strlen($newPassword) < 6) {
        jsonResp(['success' => false, 'error' => 'Password must be at least 6 characters'], 400);
    }

    $tokenHash = hash('sha256', $token);
    $pdo = db();

    try {
        $st = $pdo->prepare("SELECT id, user_id FROM PasswordResetTokens WHERE token_hash = ? AND expires_at > NOW()");
        $st->execute([$tokenHash]);
        $row = $st->fetch(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        jsonResp(['success' => false, 'error' => 'Invalid or expired reset link. Request a new one.'], 400);
        return;
    }

    if (!$row) {
        jsonResp(['success' => false, 'error' => 'Invalid or expired reset link. Request a new one.'], 400);
        return;
    }

    $userId = (int)$row['user_id'];
    $passwordHash = hashPassword($newPassword);

    $pdo->prepare("UPDATE Users SET password_hash = ? WHERE id = ?")->execute([$passwordHash, $userId]);
    $pdo->prepare("DELETE FROM PasswordResetTokens WHERE token_hash = ?")->execute([$tokenHash]);

    jsonResp(['success' => true, 'message' => 'Password has been reset. You can now log in with your new password.']);
}

function auth_login() {
    $data = getJsonBody();
    $username = $data['username'] ?? '';
    $password = $data['password'] ?? '';
    if ($username === '' || $password === '') {
        jsonResp(['success' => false, 'error' => 'Username and password required'], 400);
    }

    $pdo = db();
    $st = $pdo->prepare("SELECT id, username, password_hash, role, gmail, is_active, created_at, last_login FROM Users WHERE username = ?");
    $st->execute([$username]);
    $user = $st->fetch(PDO::FETCH_ASSOC);
    if (!$user) {
        jsonResp(['success' => false, 'error' => 'Invalid username or password'], 401);
    }

    $hash = hashPassword($password);
    if (($user['password_hash'] ?? '') !== $hash && ($user['password_hash'] ?? '') !== $password) {
        jsonResp(['success' => false, 'error' => 'Invalid username or password'], 401);
    }

    if (!((int)($user['is_active'] ?? 1))) {
        jsonResp(['success' => false, 'error' => 'Account is inactive'], 401);
    }

    $role = ($user['role'] ?? 'student') === 'superadmin' ? 'super-admin' : ($user['role'] ?? 'student');
    $payload = [
        'userId' => (int)$user['id'],
        'user_id' => (int)$user['id'],
        'username' => $user['username'],
        'role' => $role,
        'iat' => time(),
        'exp' => time() + 86400,
    ];
    $token = jwtEncode($payload);

    try {
        $pdo->prepare("UPDATE Users SET last_login = NOW() WHERE id = ?")->execute([$user['id']]);
    } catch (Throwable $e) {}

    $userData = [
        'id' => (string)$user['id'],
        'username' => $user['username'],
        'email' => $user['gmail'] ?? '',
        'role' => $role,
        'adminId' => null,
        'isActive' => (bool)($user['is_active'] ?? true),
        'createdAt' => $user['created_at'] ?? date('c'),
        'lastLogin' => $user['last_login'] ?? null,
    ];

    jsonResp(['success' => true, 'data' => ['token' => $token, 'user' => $userData]]);
}

function auth_verify() {
    $user = requireAuth();
    $userId = $user['userId'] ?? $user['user_id'] ?? null;
    if ($userId === null) {
        jsonResp(['success' => false, 'error' => 'Invalid token'], 401);
    }

    $pdo = db();
    $st = $pdo->prepare("SELECT id, username, gmail, role, is_active, created_at, last_login FROM Users WHERE id = ?");
    $st->execute([$userId]);
    $row = $st->fetch(PDO::FETCH_ASSOC);
    if (!$row) {
        jsonResp(['success' => false, 'error' => 'User not found'], 404);
    }

    $role = ($row['role'] ?? 'student') === 'superadmin' ? 'super-admin' : ($row['role'] ?? 'student');
    $userData = [
        'id' => (string)$row['id'],
        'username' => $row['username'],
        'email' => $row['gmail'] ?? '',
        'role' => $role,
        'adminId' => null,
        'isActive' => (bool)($row['is_active'] ?? true),
        'createdAt' => $row['created_at'] ?? '',
        'lastLogin' => $row['last_login'] ?? null,
    ];

    jsonResp(['success' => true, 'data' => ['valid' => true, 'user' => $userData]]);
}
