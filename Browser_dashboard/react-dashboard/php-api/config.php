<?php
/**
 * API config - loads from config.local.php if present, else uses env/defaults.
 */
$defaults = [
    'db' => [
        'host'     => 'srv1882.hstgr.io',
        'user'     => 'u976383844_abhi097',
        'password' => '',
        'database' => 'u976383844_dces',
        'port'     => 3306,
    ],
    'jwt_secret' => 'your-super-secret-jwt-key-change-this-in-production',
    'dashboard_base_url' => 'https://abhinavpaudel.com',
    'mail_from' => 'noreply@abhinavpaudel.com',
];

if (is_file(__DIR__ . '/config.local.php')) {
    $local = require __DIR__ . '/config.local.php';
    $config = array_replace_recursive($defaults, $local);
} else {
    $config = $defaults;
    if (($v = getenv('DB_HOST')) !== false) $config['db']['host'] = $v;
    if (($v = getenv('DB_USER')) !== false) $config['db']['user'] = $v;
    if (($v = getenv('DB_PASSWORD')) !== false) $config['db']['password'] = $v;
    if (($v = getenv('DB_NAME')) !== false) $config['db']['database'] = $v;
    if (($v = getenv('DB_PORT')) !== false) $config['db']['port'] = (int)$v;
    if (($v = getenv('JWT_SECRET')) !== false) $config['jwt_secret'] = $v;
    if (($v = getenv('DASHBOARD_BASE_URL')) !== false) $config['dashboard_base_url'] = $v;
    if (($v = getenv('MAIL_FROM')) !== false) $config['mail_from'] = $v;
}

return $config;
