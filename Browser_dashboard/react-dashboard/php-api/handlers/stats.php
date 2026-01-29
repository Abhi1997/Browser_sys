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
    requireAuth();

    $pdo = db();
    $total = (int)$pdo->query("SELECT COUNT(*) FROM Users")->fetchColumn();
    $active = (int)$pdo->query("SELECT COUNT(*) FROM Users WHERE is_active = 1")->fetchColumn();

    $roles = [];
    foreach ($pdo->query("SELECT role, COUNT(*) as c FROM Users GROUP BY role")->fetchAll(PDO::FETCH_ASSOC) as $r) {
        $roles[$r['role']] = (int)$r['c'];
    }

    $wl = 0;
    $bl = 0;
    $recent = 0;
    $totalStudents = $roles['student'] ?? 0;
    try {
        $wl = (int)$pdo->query("SELECT COUNT(*) FROM WhitelistDomains WHERE is_active = 1")->fetchColumn();
    } catch (Throwable $e) {}
    try {
        $bl = (int)$pdo->query("SELECT COUNT(*) FROM BlacklistDomains WHERE is_active = 1")->fetchColumn();
    } catch (Throwable $e) {}
    try {
        $recent = (int)$pdo->query("SELECT COUNT(*) FROM Users WHERE last_login >= DATE_SUB(NOW(), INTERVAL 24 HOUR)")->fetchColumn();
    } catch (Throwable $e) {}
    try {
        $totalStudents = (int)$pdo->query("SELECT COUNT(*) FROM Students")->fetchColumn();
    } catch (Throwable $e) {}

    jsonResp([
        'success' => true,
        'data' => [
            'totalUsers' => $total,
            'totalStudents' => $totalStudents,
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
}

function change_logs() {
    requireAuth();
    $limit = min(max((int)($_GET['limit'] ?? 100), 1), 500);
    $pdo = db();
    try {
        $rows = $pdo->query("
            SELECT m.id, m.student_id as studentId, m.old_mode as oldMode, m.new_mode as newMode,
                   m.changed_by as changedBy, m.changed_at as changedAt,
                   u.username as changedByName
            FROM ModeHistory m
            LEFT JOIN Users u ON m.changed_by = u.id
            ORDER BY m.changed_at DESC
            LIMIT " . $limit
        )->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}
