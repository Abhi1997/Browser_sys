-- Initialize edubrowser database schema

CREATE TABLE IF NOT EXISTS Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'teacher', 'admin', 'superadmin') NOT NULL,
    permissions TEXT,
    group_code VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    is_active TINYINT(1) DEFAULT 1,
    INDEX idx_username (username),
    INDEX idx_role (role)
);

-- Create default admin user (password: admin1234)
INSERT INTO Users (username, password_hash, role, is_active) 
VALUES (
    'admin', 
    '1c142b2d01aa34e9a36bde480645a57fd69e14155dacfab5a3f9257b77fdc8d8', 
    'admin', 
    1
) ON DUPLICATE KEY UPDATE username=username;
