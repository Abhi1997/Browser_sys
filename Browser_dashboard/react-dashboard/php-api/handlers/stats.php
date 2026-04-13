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
    
    // Teacher sees only their assigned students
    if ($role === 'teacher') {
        $teacherId = $user['userId'] ?? $user['user_id'] ?? null;
        $totalStudents = 0;
        $wl = 0;
        $bl = 0;
        
        try {
            $stmt = $pdo->prepare("SELECT COUNT(*) FROM Students WHERE teacher_id = ?");
            $stmt->execute([$teacherId]);
            $totalStudents = (int)$stmt->fetchColumn();
        } catch (Throwable $e) {}
        
        try {
            $wl = (int)$pdo->query("SELECT COUNT(*) FROM WhitelistDomains WHERE is_active = 1")->fetchColumn();
        } catch (Throwable $e) {}
        
        try {
            $bl = (int)$pdo->query("SELECT COUNT(*) FROM BlacklistDomains WHERE is_active = 1")->fetchColumn();
        } catch (Throwable $e) {}
        
        jsonResp([
            'success' => true,
            'data' => [
                'totalUsers' => $totalStudents + 1,
                'totalStudents' => $totalStudents,
                'activeUsers' => 0,
                'activeSessions' => 0,
                'roleDistribution' => [
                    'admin' => 0,
                    'teacher' => 1,
                    'student' => $totalStudents,
                ],
                'whitelistSize' => $wl,
                'blacklistSize' => $bl,
                'recentLogins' => 0,
                'recentChanges' => 0,
            ],
        ]);
        return;
    }
    
    // Superuser and Superadmin see global stats unless specifically targeting an admin
    if ((isSuperuser($user) || isSuperAdmin($user)) && empty($_GET['admin_id'])) {
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
    
    // Admin sees stats for their own data only (or Superadmin filtering by admin)
    $adminId = getRequestedAdminId($user);
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
    $params = $adminParams;

    try {
        $st = $pdo->prepare("
            SELECT s.id, s.user_id as userId, s.device_id as deviceId, s.created_at as sessionStart,
                   s.last_activity_at as lastActivityAt, s.expires_at as expiresAt, s.is_active as isActive,
                   u.username, s.admin_id
            FROM Sessions s
            LEFT JOIN Users u ON s.user_id = u.id
            WHERE 1=1 $adminClause
            ORDER BY s.last_activity_at DESC, s.created_at DESC
            LIMIT {$limit}
        ");
        $st->execute($params);
        $rows = $st->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}

/**
 * Log dashboard open (who opened dashboard, when). Call from web dashboard on load.
 * Qt app logs via Python auth.log_dashboard_open(); web logs via this endpoint.
 */
function log_dashboard_open() {
    $user = requireAuth();
    $userId = $user['userId'] ?? $user['user_id'] ?? null;
    if (!$userId) {
        jsonResp(['success' => false, 'error' => 'Invalid user'], 401);
    }
    $role = strtolower($user['role'] ?? '');
    // Normalize to DB ENUM: teacher, admin, superadmin, superuser
    $roleEnum = 'teacher';
    if ($role === 'superuser') {
        $roleEnum = 'superuser';
    } elseif (in_array($role, ['superadmin', 'super-admin'], true)) {
        $roleEnum = 'superadmin';
    } elseif ($role === 'admin') {
        $roleEnum = 'admin';
    } elseif ($role === 'teacher') {
        $roleEnum = 'teacher';
    }
    $ip = $_SERVER['REMOTE_ADDR'] ?? $_SERVER['HTTP_X_FORWARDED_FOR'] ?? null;
    if (is_string($ip) && strpos($ip, ',') !== false) {
        $ip = trim(explode(',', $ip)[0]);
    }
    $deviceId = $_SERVER['HTTP_X_DEVICE_ID'] ?? null;
    $pdo = db();
    try {
        $st = $pdo->prepare("
            INSERT INTO DashboardLogs (user_id, role, action, endpoint, ip_address, device_id, created_at)
            VALUES (?, ?, 'dashboard_open', ?, ?, ?, NOW())
        ");
        $st->execute([$userId, $roleEnum, null, $ip, $deviceId]);
    } catch (Throwable $e) {
        jsonResp(['success' => false, 'error' => 'Failed to log dashboard open'], 500);
    }
    jsonResp(['success' => true, 'message' => 'Logged']);
}

function dashboard_logs() {
    $user = requireAuth();
    $role = strtolower($user['role'] ?? '');
    $filterRole = strtolower($_GET['role'] ?? '');
    
    if (!in_array($role, ['admin', 'super-admin', 'superadmin', 'superuser'], true)) {
        // Allow teachers ONLY if they are explicitly fetching student logs
        if ($role !== 'teacher' || $filterRole !== 'student') {
            jsonResp(['success' => false, 'error' => 'Forbidden'], 403);
        }
    }
    
    $limit = min(max((int)($_GET['limit'] ?? 100), 1), 500);
    
    $pdo = db();
    try {
        if ($filterRole === 'student') {
            $joinTeacher = '';
            $whereTeacher = '';
            $params = [];
            
            if ($role === 'teacher') {
                $teacherId = getUserTeacherId($user);
                $joinTeacher = 'JOIN Students st ON u.id = st.user_id';
                $whereTeacher = 'AND st.teacher_id = :tid';
            }
            
            $st = $pdo->prepare("
                SELECT s.id, s.user_id as userId, u.role, 'Logged in to browser' as action, NULL as endpoint, NULL as ipAddress, s.device_id as deviceId, s.created_at as createdAt,
                       u.username
                FROM Sessions s
                JOIN Users u ON s.user_id = u.id
                $joinTeacher
                WHERE u.role = 'student' $whereTeacher
                ORDER BY s.created_at DESC
                LIMIT :mylimit
            ");
            
            if ($role === 'teacher') {
                $st->bindValue(':tid', $teacherId, PDO::PARAM_INT);
            }
            $st->bindValue(':mylimit', (int)$limit, PDO::PARAM_INT);
            $st->execute();
            $rows = $st->fetchAll(PDO::FETCH_ASSOC);
        } else {
            $st = $pdo->prepare("
                SELECT d.id, d.user_id as userId, d.role, d.action, d.endpoint, d.ip_address as ipAddress, d.device_id as deviceId, d.created_at as createdAt,
                       u.username
                FROM DashboardLogs d
                LEFT JOIN Users u ON d.user_id = u.id
                ORDER BY d.created_at DESC
                LIMIT :mylimit
            ");
            $st->bindValue(':mylimit', (int)$limit, PDO::PARAM_INT);
            $st->execute();
            $rows = $st->fetchAll(PDO::FETCH_ASSOC);
        }
    } catch (Throwable $e) {
        $rows = [];
        jsonResp(['success' => false, 'error' => $e->getMessage()]);
    }
    jsonResp(['success' => true, 'data' => $rows]);
}

function change_logs() {
    $user = requireAuth();
    $limit = min(max((int)($_GET['limit'] ?? 100), 1), 500);
    $pdo = db();
    
    list($adminClause, $adminParams) = adminIdFilter($user, 'm');
    $params = $adminParams;
    
    try {
        $sql = "
            SELECT m.id, m.student_id as studentId, m.old_mode as oldMode, m.new_mode as newMode,
                   m.changed_by as changedBy, m.changed_at as changedAt, m.admin_id,
                   u.username as changedByName
            FROM ModeHistory m
            LEFT JOIN Users u ON m.changed_by = u.id
            WHERE 1=1 $adminClause
            ORDER BY m.changed_at DESC
            LIMIT {$limit}
        ";
        $stmt = $pdo->prepare($sql);
        $stmt->execute($params);
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}

function top_sites() {
    $user = requireAuth();
    $pdo = db();
    
    try {
        $st = $pdo->prepare("
            SELECT 
                SUBSTRING_INDEX(REPLACE(REPLACE(url, 'https://', ''), 'http://', ''), '/', 1) as domain,
                COUNT(*) as visits
            FROM BrowsingHistory
            WHERE url NOT LIKE '%google.com%' AND url != '' AND url IS NOT NULL
            GROUP BY domain
            ORDER BY visits DESC
            LIMIT 15
        ");
        $st->execute();
        $rows = $st->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}

function active_users() {
    $user = requireAuth();
    $pdo = db();
    
    try {
        $st = $pdo->prepare("
            SELECT u.username, COUNT(bh.id) as activityCount
            FROM BrowsingHistory bh
            JOIN Users u ON bh.user_id = u.id
            GROUP BY bh.user_id, u.username
            ORDER BY activityCount DESC
            LIMIT 10
        ");
        $st->execute();
        $rows = $st->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}
