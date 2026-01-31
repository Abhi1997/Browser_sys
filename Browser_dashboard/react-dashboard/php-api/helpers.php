<?php
function getConfig() {
    static $c = null;
    if ($c === null) {
        $c = require __DIR__ . '/config.php';
    }
    return $c;
}

function db() {
    static $pdo = null;
    if ($pdo === null) {
        $cfg = getConfig()['db'];
        $dsn = "mysql:host={$cfg['host']};port={$cfg['port']};dbname={$cfg['database']};charset=utf8mb4";
        $pdo = new PDO($dsn, $cfg['user'], $cfg['password'], [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
    }
    return $pdo;
}

function jsonResp($data, $code = 200) {
    http_response_code($code);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_UNESCAPED_SLASHES);
    exit;
}

function getBearerToken() {
    $h = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
    if ($h === '' && function_exists('apache_request_headers')) {
        $headers = apache_request_headers();
        $h = $headers['Authorization'] ?? $headers['authorization'] ?? '';
    }
    if (preg_match('/Bearer\s+(\S+)/', $h, $m)) {
        return $m[1];
    }
    return null;
}

function getJsonBody() {
    $raw = file_get_contents('php://input');
    if ($raw === '' || $raw === false) return [];
    $d = json_decode($raw, true);
    return is_array($d) ? $d : [];
}

function jwtDecode($token) {
    $rawSecret = getConfig()['jwt_secret'];
    $secret = is_string($rawSecret) ? $rawSecret : (string) $rawSecret;
    $parts = explode('.', $token);
    if (count($parts) !== 3) return null;
    $payload = @base64_decode(strtr($parts[1], '-_', '+/'));
    if ($payload === false) return null;
    $data = json_decode($payload, true);
    if (!is_array($data)) return null;
    if (!empty($data['exp']) && $data['exp'] < time()) return null;
    $sig = hash_hmac('sha256', $parts[0] . '.' . $parts[1], $secret, true);
    $expected = strtr(base64_encode($sig), '+/', '-_');
    $expected = rtrim($expected, '=');
    if (!hash_equals($expected, $parts[2])) return null;
    return $data;
}

function requireAuth() {
    $token = getBearerToken();
    if (!$token) {
        jsonResp(['success' => false, 'error' => 'Missing authentication token'], 401);
    }
    $user = jwtDecode($token);
    if (!$user) {
        jsonResp(['success' => false, 'error' => 'Invalid or expired token'], 401);
    }
    return $user;
}

function hashPassword($password) {
    return hash('sha256', $password);
}

/**
 * Role Hierarchy & Data Isolation Helpers
 * ========================================
 * superuser:  View + modify ALL data across ALL admins (god mode)
 * superadmin: Read-only view of all admins, can ONLY create new admins
 * admin: Full operational authority for their own data
 * teacher: Manages only their assigned students
 * student: End user
 */

/**
 * Check if user is superuser (ultimate superuser - can do everything)
 */
function isSuperuser($user) {
    $role = strtolower($user['role'] ?? '');
    return $role === 'superuser';
}

/**
 * Check if user is superadmin (read-only oversight)
 */
function isSuperAdmin($user) {
    $role = strtolower($user['role'] ?? '');
    return $role === 'superadmin' || $role === 'super-admin';
}

/**
 * Check if user can modify data (superadmin cannot modify, only view + create admin)
 * Superuser can modify everything.
 */
function canModify($user) {
    if (isSuperuser($user)) return true;
    return !isSuperAdmin($user);
}

/**
 * Get the admin_id for data isolation.
 * - superuser: returns null (can see and modify all)
 * - superadmin: returns null (can see all, but can't modify)
 * - admin: returns their own user id
 * - teacher: returns their admin_id from Users table
 * - student: returns their admin_id from Students table
 */
function getUserAdminId($user) {
    $role = strtolower($user['role'] ?? '');
    $userId = $user['user_id'] ?? $user['userId'] ?? null;
    
    if (isSuperuser($user) || isSuperAdmin($user)) {
        return null; // Can see all
    }
    
    if ($role === 'admin') {
        return $userId; // Admin's own data
    }
    
    // Teacher or student: look up admin_id from DB
    if (!$userId) return null;
    
    $pdo = db();
    if ($role === 'teacher') {
        $stmt = $pdo->prepare("SELECT admin_id FROM Users WHERE id = ?");
        $stmt->execute([$userId]);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row ? ($row['admin_id'] ?? null) : null;
    }
    
    if ($role === 'student') {
        $stmt = $pdo->prepare("SELECT admin_id FROM Students WHERE user_id = ?");
        $stmt->execute([$userId]);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row ? ($row['admin_id'] ?? null) : null;
    }
    
    return null;
}

/**
 * Get the teacher_id for a teacher user (their own id), or null for others.
 */
function getUserTeacherId($user) {
    $role = strtolower($user['role'] ?? '');
    if ($role === 'teacher') {
        return $user['user_id'] ?? $user['userId'] ?? null;
    }
    return null;
}

/**
 * Enforce read-only for superadmin on modify operations.
 * Call this at the start of any POST/PATCH/DELETE handler that superadmin should not use.
 * Superuser bypasses this check (can modify everything).
 */
function enforceSuperAdminReadOnly($user, $action = 'modify') {
    if (isSuperuser($user)) {
        return; // Superuser can do everything
    }
    if (isSuperAdmin($user)) {
        jsonResp([
            'success' => false,
            'error' => "Super admins can only view data and create new admins. Cannot $action."
        ], 403);
    }
}

/**
 * Build WHERE clause for admin_id filtering.
 * Returns [clause, params] where clause is " AND admin_id = ?" or "" for superadmin.
 */
function adminIdFilter($user, $tableAlias = '') {
    $adminId = getUserAdminId($user);
    if ($adminId === null) {
        return ['', []]; // Superadmin sees all
    }
    $col = $tableAlias ? "$tableAlias.admin_id" : "admin_id";
    return [" AND $col = ?", [$adminId]];
}

/**
 * Build WHERE clause for teacher_id filtering (teachers see only their students).
 * Returns [clause, params].
 */
function teacherIdFilter($user, $tableAlias = '') {
    $role = strtolower($user['role'] ?? '');
    if ($role !== 'teacher') {
        return ['', []]; // Admins/superadmins don't filter by teacher_id
    }
    $teacherId = getUserTeacherId($user);
    if (!$teacherId) {
        return [" AND 1=0", []]; // No teacher_id = no results
    }
    $col = $tableAlias ? "$tableAlias.teacher_id" : "teacher_id";
    return [" AND $col = ?", [$teacherId]];
}

/** Build JWT (header.payload.signature) for login response */
function jwtEncode($payload) {
    $secret = getConfig()['jwt_secret'];
    $header = ['typ' => 'JWT', 'alg' => 'HS256'];
    $h = rtrim(strtr(base64_encode(json_encode($header)), '+/', '-_'), '=');
    $p = rtrim(strtr(base64_encode(json_encode($payload)), '+/', '-_'), '=');
    $sig = hash_hmac('sha256', $h . '.' . $p, $secret, true);
    $s = rtrim(strtr(base64_encode($sig), '+/', '-_'), '=');
    return $h . '.' . $p . '.' . $s;
}

/**
 * Send email. Uses SMTP if config has smtp_host/smtp_username/smtp_password, else PHP mail().
 * @param string $to Recipient email
 * @param string $subject Subject
 * @param string $body Plain text body
 * @param string $from From address (e.g. noreply@abhinavpaudel.com)
 * @return bool True if sent, false on failure
 */
function sendMail($to, $subject, $body, $from) {
    $cfg = getConfig();
    $smtpHost = $cfg['smtp_host'] ?? null;
    $smtpPort = (int)($cfg['smtp_port'] ?? 587);
    $smtpUser = $cfg['smtp_username'] ?? null;
    $smtpPass = $cfg['smtp_password'] ?? null;
    $smtpSecure = $cfg['smtp_secure'] ?? 'tls';

    if ($smtpHost && $smtpUser !== null && $smtpPass !== null) {
        return sendMailSmtp($to, $subject, $body, $from, $smtpHost, $smtpPort, $smtpSecure, $smtpUser, $smtpPass);
    }
    $headers = "From: " . $from . "\r\nReply-To: " . $from . "\r\nContent-Type: text/plain; charset=UTF-8\r\n";
    return @mail($to, $subject, $body, $headers);
}

/** Minimal SMTP send with TLS and AUTH LOGIN */
function sendMailSmtp($to, $subject, $body, $from, $host, $port, $secure, $username, $password) {
    $errno = 0;
    $errstr = '';
    $ctx = stream_context_create(['ssl' => ['verify_peer' => false, 'verify_peer_name' => false]]);
    $sock = @stream_socket_client(
        ($secure === 'tls' ? 'tcp' : 'ssl') . '://' . $host . ':' . $port,
        $errno, $errstr, 15, STREAM_CLIENT_CONNECT, $ctx
    );
    if (!$sock) return false;

    $read = function () use ($sock) {
        $line = @fgets($sock, 512);
        return $line !== false ? trim($line) : '';
    };
    $write = function ($msg) use ($sock) {
        return @fwrite($sock, $msg . "\r\n") !== false;
    };

    if ($read() === '') { @fclose($sock); return false; }
    $write('EHLO ' . ($_SERVER['SERVER_NAME'] ?? 'localhost'));
    while ($line = $read()) { if (strpos($line, ' ') === 3) break; }

    if ($secure === 'tls' && $port == 587) {
        $write('STARTTLS');
        if (strpos($read(), '220') !== 0) { @fclose($sock); return false; }
        $params = ['ssl' => ['verify_peer' => false, 'verify_peer_name' => false]];
        if (!@stream_socket_enable_crypto($sock, true, STREAM_CRYPTO_METHOD_TLS_CLIENT)) { @fclose($sock); return false; }
        $write('EHLO ' . ($_SERVER['SERVER_NAME'] ?? 'localhost'));
        while ($line = $read()) { if (strpos($line, ' ') === 3) break; }
    }

    $write('AUTH LOGIN');
    if (strpos($read(), '334') !== 0) { @fclose($sock); return false; }
    $write(base64_encode($username));
    if (strpos($read(), '334') !== 0) { @fclose($sock); return false; }
    $write(base64_encode($password));
    if (strpos($read(), '235') !== 0) { @fclose($sock); return false; }

    $write('MAIL FROM:<' . $from . '>');
    if (strpos($read(), '250') !== 0) { @fclose($sock); return false; }
    $write('RCPT TO:<' . $to . '>');
    if (strpos($read(), '250') !== 0) { @fclose($sock); return false; }
    $write('DATA');
    if (strpos($read(), '354') !== 0) { @fclose($sock); return false; }

    $data = "From: " . $from . "\r\nTo: " . $to . "\r\nSubject: " . $subject . "\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\n" . $body . "\r\n.";
    if (!$write($data)) { @fclose($sock); return false; }
    if (strpos($read(), '250') !== 0) { @fclose($sock); return false; }
    $write('QUIT');
    @fclose($sock);
    return true;
}
