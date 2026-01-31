<?php
/**
 * Stats and health handlers
 */

function health() {
    jsonResp(['status' => 'ok', 'message' => 'Backend API is running']);
}

/**
 * Debug endpoint: test config and DB (no auth). Use to see why API returns 500.
 * GET https://api.abhinavpaudel.com/api/debug or /debug
 */
function debug() {
    $path = trim(parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH), '/');
    $out = [
        'api' => 'ok',
        'path_received' => $path,
        'config_loaded' => false,
        'db_connected' => false,
        'error' => null,
    ];
    try {
        $cfg = getConfig();
        $out['config_loaded'] = true;
        $out['db_host'] = $cfg['db']['host'] ?? '(not set)';
        $out['db_name'] = $cfg['db']['database'] ?? '(not set)';
        $out['jwt_secret_set'] = !empty($cfg['jwt_secret']) && is_string($cfg['jwt_secret']);
    } catch (Throwable $e) {
        $out['error'] = 'config: ' . $e->getMessage();
        jsonResp($out, 200);
        return;
    }
    try {
        $pdo = db();
        $pdo->query('SELECT 1');
        $out['db_connected'] = true;
    } catch (Throwable $e) {
        $out['error'] = 'db: ' . $e->getMessage();
    }
    jsonResp($out, 200);
}

function stats_admin($id) {
    requireAuth();
    jsonResp(['success' => true, 'data' => (object)[]]);
}

function stats_login_activity() {
    requireAuth();
    jsonResp(['success' => true, 'data' => []]);
}

function stats_admins() {
    requireAuth();
    jsonResp(['success' => true, 'data' => []]);
}

function stats() {
    $user = requireAuth();
    $pdo = db();
    $role = strtolower($user['role'] ?? '');
    
    // Superuser and Superadmin see global stats
    if (isSuperuser($user) || isSuperAdmin($user)) {
        $total = (int)$pdo->query("SELECT COUNT(*) FROM Users")->fetchColumn();
        $active = (int)$pdo->query("SELECT COUNT(*) FROM Users WHERE is_active = 1")->fetchColumn();
        $roles = [];
        foreach ($pdo->query("SELECT role, COUNT(*) as c FROM Users GROUP BY role")->fetchAll(PDO::FETCH_ASSOC) as $r) {
            $roles[$r['role']] = (int)$r['c'];
        }
        $wl = (int)$pdo->query("SELECT COUNT(*) FROM WhitelistDomains WHERE is_active = 1")->fetchColumn();
        $bl = (int)$pdo->query("SELECT COUNT(*) FROM BlacklistDomains WHERE is_active = 1")->fetchColumn();
        $recent = (int)$pdo->query("SELECT COUNT(*) FROM Users WHERE last_login >= DATE_SUB(NOW(), INTERVAL 24 HOUR)")->fetchColumn();
        $totalStudents = (int)$pdo->query("SELECT COUNT(*) FROM Students")->fetchColumn();
        $totalAdmins = (int)$pdo->query("SELECT COUNT(*) FROM Users WHERE role = 'admin'")->fetchColumn();
        
        jsonResp([
            'success' => true,
            'data' => [
                'totalUsers' => $total,
                'totalStudents' => $totalStudents,
                'totalAdmins' => $totalAdmins,
                'activeUsers' => $active,
                'activeSessions' => 0,
                'roleDistribution' => [
                    'admin' => $roles['admin'] ?? 0,
                    'teacher' => $roles['teacher'] ?? 0,
                    'student' => $roles['student'] ?? 0,
                ],
                'whitelistSize' => $wl,
                'blacklistSize' => $bl,
                'recentLogins' => $recent,
                'recentChanges' => 0,
            ],
        ]);
        return;
    }
    
    // Admin sees stats for their own data only
    $adminId = getUserAdminId($user);
    list($adminClause, $adminParams) = adminIdFilter($user);
    
    $totalTeachers = 0;
    $totalStudents = 0;
    $wl = 0;
    $bl = 0;
    
    try {
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM Users WHERE role = 'teacher' AND admin_id = ?");
        $stmt->execute([$adminId]);
        $totalTeachers = (int)$stmt->fetchColumn();
    } catch (Throwable $e) {}
    
    try {
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM Students WHERE admin_id = ?");
        $stmt->execute([$adminId]);
        $totalStudents = (int)$stmt->fetchColumn();
    } catch (Throwable $e) {}
    
    try {
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM WhitelistDomains WHERE is_active = 1 AND admin_id = ?");
        $stmt->execute([$adminId]);
        $wl = (int)$stmt->fetchColumn();
    } catch (Throwable $e) {}
    
    try {
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM BlacklistDomains WHERE is_active = 1 AND admin_id = ?");
        $stmt->execute([$adminId]);
        $bl = (int)$stmt->fetchColumn();
    } catch (Throwable $e) {}

    jsonResp([
        'success' => true,
        'data' => [
            'totalUsers' => $totalTeachers + $totalStudents + 1, // +1 for admin
            'totalStudents' => $totalStudents,
            'totalTeachers' => $totalTeachers,
            'activeUsers' => 0,
            'activeSessions' => 0,
            'roleDistribution' => [
                'admin' => 1,
                'teacher' => $totalTeachers,
                'student' => $totalStudents,
            ],
            'whitelistSize' => $wl,
            'blacklistSize' => $bl,
            'recentLogins' => 0,
            'recentChanges' => 0,
        ],
    ]);
}

function sessions_list() {
    $user = requireAuth();
    $role = strtolower($user['role'] ?? '');
    if (!in_array($role, ['admin', 'super-admin', 'superadmin', 'superuser'], true)) {
        jsonResp(['success' => false, 'error' => 'Forbidden'], 403);
    }
    $limit = min(max((int)($_GET['limit'] ?? 100), 1), 500);
    $pdo = db();
    
    list($adminClause, $adminParams) = adminIdFilter($user, 's');
    $params = array_merge($adminParams, [$limit]);
    
    try {
        $st = $pdo->prepare("
            SELECT s.id, s.user_id as userId, s.device_id as deviceId, s.created_at as sessionStart,
                   s.last_activity_at as lastActivityAt, s.expires_at as expiresAt, s.is_active as isActive,
                   u.username, s.admin_id
            FROM Sessions s
            LEFT JOIN Users u ON s.user_id = u.id
            WHERE 1=1 $adminClause
            ORDER BY s.last_activity_at DESC, s.created_at DESC
            LIMIT ?
        ");
        $st->execute($params);
        $rows = $st->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}

function dashboard_logs() {
    $user = requireAuth();
    $role = $user['role'] ?? '';
    if (!in_array(strtolower($role), ['admin', 'super-admin', 'superuser'], true)) {
        jsonResp(['success' => false, 'error' => 'Forbidden'], 403);
    }
    $limit = min(max((int)($_GET['limit'] ?? 100), 1), 500);
    $pdo = db();
    try {
        $st = $pdo->prepare("
            SELECT d.id, d.user_id as userId, d.role, d.action, d.endpoint, d.ip_address as ipAddress, d.device_id as deviceId, d.created_at as createdAt,
                   u.username
            FROM DashboardLogs d
            LEFT JOIN Users u ON d.user_id = u.id
            ORDER BY d.created_at DESC
            LIMIT ?
        ");
        $st->execute([$limit]);
        $rows = $st->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}

function change_logs() {
    $user = requireAuth();
    $limit = min(max((int)($_GET['limit'] ?? 100), 1), 500);
    $pdo = db();
    
    list($adminClause, $adminParams) = adminIdFilter($user, 'm');
    $params = array_merge($adminParams, [$limit]);
    
    try {
        $sql = "
            SELECT m.id, m.student_id as studentId, m.old_mode as oldMode, m.new_mode as newMode,
                   m.changed_by as changedBy, m.changed_at as changedAt, m.admin_id,
                   u.username as changedByName
            FROM ModeHistory m
            LEFT JOIN Users u ON m.changed_by = u.id
            WHERE 1=1 $adminClause
            ORDER BY m.changed_at DESC
            LIMIT ?
        ";
        $stmt = $pdo->prepare($sql);
        $stmt->execute($params);
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}
