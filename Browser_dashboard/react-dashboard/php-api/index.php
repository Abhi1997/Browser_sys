<?php
/**
 * DCES Dashboard API - PHP entrypoint for Hostinger (api.abhinavpaudel.com)
 * Routes all requests to handler functions.
 */

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PATCH, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Device-ID');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

require __DIR__ . '/helpers.php';

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$path = trim($path, '/');
// Some hosts strip a base path; normalize so "auth/..." and bare "stats"/"students"/"violations" match
$pathAliases = [
    'auth/forgot-password' => 'api/auth/forgot-password',
    'auth/reset-password' => 'api/auth/reset-password',
    'auth/verify-token' => 'api/auth/verify-token',
    'auth/login' => 'auth/login',
    'stats' => 'api/stats',
    'students' => 'api/students',
    'violations' => 'api/violations',
    'history' => 'api/history',
    'dashboard-logs' => 'api/dashboard-logs',
    'sessions' => 'api/sessions',
    'warning-triggers' => 'api/warning-triggers',
    'users' => 'api/users',
    'whitelist' => 'api/whitelist',
    'blacklist' => 'api/blacklist',
    'cached-sites' => 'api/cached-sites',
    'teachers' => 'api/teachers',
    'admins' => 'api/admins',
];
if (isset($pathAliases[$path])) {
    $path = $pathAliases[$path];
}
if ($path === 'api/auth/forgot-password' || $path === 'auth/forgot-password') {
    $path = 'api/auth/forgot-password';
}
if ($path === 'api/auth/reset-password' || $path === 'auth/reset-password') {
    $path = 'api/auth/reset-password';
}
$method = $_SERVER['REQUEST_METHOD'];

$routes = [
    'POST' => [
        'auth/login' => ['auth_login', 'auth'],
        'api/auth/verify-token' => ['auth_verify', 'auth'],
        'api/auth/forgot-password' => ['auth_forgot_password', 'auth'],
        'api/auth/reset-password' => ['auth_reset_password', 'auth'],
        'api/users' => ['users_create', 'users'],
        'api/whitelist' => ['whitelist_add', 'whitelist'],
        'api/blacklist' => ['blacklist_add', 'blacklist'],
        'export/db' => ['export_db', 'export'],
    ],
    'GET' => [
        'api/stats' => ['stats', 'stats'],
        'stats/login-activity' => ['stats_login_activity', 'stats'],
        'stats/admins' => ['stats_admins', 'stats'],
        'api/users' => ['users_list', 'users'],
        'api/whitelist' => ['whitelist_list', 'whitelist'],
        'api/blacklist' => ['blacklist_list', 'blacklist'],
        'api/students' => ['students_list', 'students'],
        'api/activity' => ['activity_list', 'activity'],
        'api/violations' => ['violations_list', 'violations'],
        'api/change-logs' => ['change_logs', 'stats'],
        'api/dashboard-logs' => ['dashboard_logs', 'stats'],
        'api/sessions' => ['sessions_list', 'stats'],
        'api/warning-triggers' => ['warnings_list', 'warnings'],
        'api/cached-sites' => ['cached_sites_list', 'cached_sites'],
        'api/history' => ['history_list', 'history'],
        'api/admins' => ['admins_list', 'users'],
        'api/teachers' => ['teachers_list', 'users'],
        'notifications' => ['notifications_list', 'notifications'],
        'health' => ['health', 'stats'],
        'api/debug' => ['debug', 'stats'],
        'debug' => ['debug', 'stats'],
    ],
    'PATCH' => [],
    'DELETE' => [],
];

// Parametrized routes (method + path with id)
$paramRoutes = [
    'GET' => [
        'stats/admin/([^/]+)' => ['stats_admin', 'stats'],
        'api/students/([^/]+)/history' => ['history_list_student', 'history'],
    ],
    'POST' => [
        'api/students/([^/]+)/mode' => ['students_set_mode', 'students'],
        'api/students/([^/]+)/assign-teacher' => ['students_assign_teacher', 'students'],
    ],
    'PATCH' => [
        'api/users/([^/]+)' => ['users_update', 'users'],
        'api/users/([^/]+)/toggle-status' => ['users_toggle', 'users'],
        'api/whitelist/([^/]+)' => ['whitelist_update', 'whitelist'],
        'api/blacklist/([^/]+)' => ['blacklist_update', 'blacklist'],
        'notifications/([^/]+)/read' => ['notifications_read', 'notifications'],
    ],
    'DELETE' => [
        'api/users/([^/]+)' => ['users_delete', 'users'],
        'api/whitelist/([^/]+)' => ['whitelist_delete', 'whitelist'],
        'api/blacklist/([^/]+)' => ['blacklist_delete', 'blacklist'],
        'api/cached-sites/([^/]+)' => ['cached_sites_delete', 'cached_sites'],
    ],
];

$handlerFunc = null;
$handlerFile = null;
$params = [];

foreach ($routes[$method] ?? [] as $pattern => list($func, $file)) {
    if ($path === $pattern) {
        $handlerFunc = $func;
        $handlerFile = $file;
        break;
    }
}

if (!$handlerFunc && isset($paramRoutes[$method])) {
    foreach ($paramRoutes[$method] as $pattern => list($func, $file)) {
        $re = '@^' . $pattern . '$@';
        if (preg_match($re, $path, $m)) {
            array_shift($m);
            $params = $m;
            $handlerFunc = $func;
            $handlerFile = $file;
            break;
        }
    }
}

if (!$handlerFunc || !$handlerFile) {
    jsonResp(['success' => false, 'error' => 'Not found'], 404);
}

$handlerPath = __DIR__ . '/handlers/' . $handlerFile . '.php';
if (!is_file($handlerPath)) {
    jsonResp(['success' => false, 'error' => 'Handler file not found'], 500);
}

require $handlerPath;

if (!function_exists($handlerFunc)) {
    jsonResp(['success' => false, 'error' => 'Handler not implemented'], 500);
}

try {
    $handlerFunc(...$params);
} catch (Throwable $e) {
    error_log('API handler error: ' . $e->getMessage() . ' in ' . $e->getFile() . ':' . $e->getLine());
    jsonResp([
        'success' => false,
        'error' => 'Server error. Please check API logs.',
        'message' => $e->getMessage(),
    ], 500);
}
