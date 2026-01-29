<?php
/**
 * Copy this file to config.local.php and fill in your values.
 * Do not commit config.local.php - add it to .gitignore.
 * On Hostinger you can also set DB_*, JWT_SECRET, MAIL_FROM, DASHBOARD_BASE_URL via environment variables.
 */
return [
    'db' => [
        'host'     => getenv('DB_HOST') ?: 'srv1882.hstgr.io',
        'user'     => getenv('DB_USER') ?: 'u976383844_abhi097',
        'password' => getenv('DB_PASSWORD') ?: '',
        'database' => getenv('DB_NAME') ?: 'u976383844_dces',
        'port'     => (int)(getenv('DB_PORT') ?: 3306),
    ],
    'jwt_secret' => getenv('JWT_SECRET') ?: 'your-super-secret-jwt-key-change-this-in-production',

    // Forgot-password email: sender address (must be valid; use your domain for better deliverability)
    'mail_from' => getenv('MAIL_FROM') ?: 'noreply@abhinavpaudel.com',

    // Base URL for reset link in email (dashboard where user sets new password)
    'dashboard_base_url' => getenv('DASHBOARD_BASE_URL') ?: 'https://abhinavpaudel.com',

    // Optional: SMTP (if PHP mail() doesn't work on Hostinger, set these and use sendMail() helper)
    // 'smtp_host'     => 'smtp.hostinger.com',
    // 'smtp_port'     => 587,
    // 'smtp_secure'   => 'tls',
    // 'smtp_username' => 'your-email@abhinavpaudel.com',
    // 'smtp_password' => 'your-email-password',
];
