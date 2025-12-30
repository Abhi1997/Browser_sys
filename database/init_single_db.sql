-- Single Database Schema for Secure Academic Browser
-- All tables in one database: edubrowser

CREATE DATABASE IF NOT EXISTS edubrowser;
USE edubrowser;

-- ============================================
-- AUTHENTICATION & SECURITY TABLES
-- ============================================

-- Users table (authentication and authorization)
CREATE TABLE IF NOT EXISTS Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    gmail VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    role ENUM('student', 'teacher', 'admin', 'superadmin') NOT NULL,
    permissions TEXT,
    group_code VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    is_active TINYINT(1) DEFAULT 1,
    teacher_approval_status ENUM('PENDING', 'APPROVED', 'REJECTED') DEFAULT NULL,
    approved_by INT NULL,
    approved_at DATETIME NULL,
    INDEX idx_username (username),
    INDEX idx_gmail (gmail),
    INDEX idx_role (role),
    INDEX idx_teacher_status (teacher_approval_status)
);

-- Devices table (device tracking and registration)
CREATE TABLE IF NOT EXISTS Devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    user_id INT NOT NULL,
    ip_address VARCHAR(45),
    mac_address VARCHAR(17),
    device_fingerprint TEXT,
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen DATETIME,
    is_active TINYINT(1) DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_device_id (device_id),
    INDEX idx_user_id (user_id),
    INDEX idx_ip (ip_address)
);

-- Sessions table (active sessions and tokens)
CREATE TABLE IF NOT EXISTS Sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    device_id VARCHAR(255) NOT NULL,
    token VARCHAR(500) NOT NULL,
    dashboard_token VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    is_active TINYINT(1) DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_token (token(255)),
    INDEX idx_device_id (device_id)
);

-- Dashboard authorization tokens
CREATE TABLE IF NOT EXISTS DashboardTokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    device_id VARCHAR(255) NOT NULL,
    token VARCHAR(500) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    is_active TINYINT(1) DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_token (token(255)),
    INDEX idx_user_device (user_id, device_id)
);

-- ============================================
-- STUDENT CONTROL TABLES
-- ============================================

-- Student profiles
CREATE TABLE IF NOT EXISTS Students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(100) UNIQUE NOT NULL,
    user_id INT NOT NULL,  -- Reference to Users.id
    gmail VARCHAR(255) NOT NULL,
    assigned_mode ENUM('exam', 'study', 'restricted', 'free') NOT NULL DEFAULT 'restricted',
    violation_count INT DEFAULT 0,
    device_id VARCHAR(255),
    ip_address VARCHAR(45),
    mac_address VARCHAR(17),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active TINYINT(1) DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_student_id (student_id),
    INDEX idx_user_id (user_id),
    INDEX idx_mode (assigned_mode),
    INDEX idx_device_id (device_id)
);

-- Allowed time windows for students
CREATE TABLE IF NOT EXISTS TimeWindows (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(100) NOT NULL,
    day_of_week ENUM('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'all') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_active TINYINT(1) DEFAULT 1,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    INDEX idx_student_id (student_id)
);

-- Mode history (track mode changes)
CREATE TABLE IF NOT EXISTS ModeHistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(100) NOT NULL,
    old_mode ENUM('exam', 'study', 'restricted', 'free'),
    new_mode ENUM('exam', 'study', 'restricted', 'free') NOT NULL,
    changed_by INT NOT NULL,  -- User ID of admin/teacher who made the change
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES Users(id),
    INDEX idx_student_id (student_id),
    INDEX idx_changed_at (changed_at)
);

-- Whitelist domains (allowed URLs per mode)
CREATE TABLE IF NOT EXISTS WhitelistDomains (
    id INT AUTO_INCREMENT PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    mode ENUM('exam', 'study', 'restricted', 'free') NOT NULL,
    description TEXT,
    added_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active TINYINT(1) DEFAULT 1,
    FOREIGN KEY (added_by) REFERENCES Users(id),
    INDEX idx_domain (domain),
    INDEX idx_mode (mode)
);

-- Blacklist domains (blocked URLs)
CREATE TABLE IF NOT EXISTS BlacklistDomains (
    id INT AUTO_INCREMENT PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    mode ENUM('exam', 'study', 'restricted', 'free') NOT NULL,
    reason TEXT,
    added_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active TINYINT(1) DEFAULT 1,
    FOREIGN KEY (added_by) REFERENCES Users(id),
    INDEX idx_domain (domain),
    INDEX idx_mode (mode)
);

-- ============================================
-- ACTIVITY & LOGS TABLES
-- ============================================

-- Student activity logs
CREATE TABLE IF NOT EXISTS ActivityLogs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(100) NOT NULL,
    user_id INT NOT NULL,
    url VARCHAR(2048) NOT NULL,
    domain VARCHAR(255),
    mode ENUM('exam', 'study', 'restricted', 'free') NOT NULL,
    visit_duration INT DEFAULT 0,  -- in seconds
    visit_start DATETIME NOT NULL,
    visit_end DATETIME,
    device_id VARCHAR(255),
    ip_address VARCHAR(45),
    mac_address VARCHAR(17),
    is_allowed TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_student_id (student_id),
    INDEX idx_user_id (user_id),
    INDEX idx_visit_start (visit_start),
    INDEX idx_domain (domain),
    INDEX idx_mode (mode),
    INDEX idx_device_id (device_id)
);

-- Violation logs (bypass attempts, unauthorized access)
CREATE TABLE IF NOT EXISTS Violations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(100) NOT NULL,
    user_id INT NOT NULL,
    violation_type ENUM('url_blocked', 'mode_bypass_attempt', 'time_window_violation', 'unauthorized_action', 'device_mismatch') NOT NULL,
    description TEXT NOT NULL,
    attempted_url VARCHAR(2048),
    current_mode ENUM('exam', 'study', 'restricted', 'free'),
    device_id VARCHAR(255),
    ip_address VARCHAR(45),
    mac_address VARCHAR(17),
    severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_student_id (student_id),
    INDEX idx_user_id (user_id),
    INDEX idx_violation_type (violation_type),
    INDEX idx_created_at (created_at),
    INDEX idx_severity (severity)
);

-- Teacher actions log
CREATE TABLE IF NOT EXISTS TeacherActions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    action_type ENUM('mode_change', 'whitelist_add', 'whitelist_remove', 'view_student', 'view_activity', 'approve_student') NOT NULL,
    target_student_id VARCHAR(100),
    details TEXT,
    ip_address VARCHAR(45),
    device_id VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_teacher_id (teacher_id),
    INDEX idx_action_type (action_type),
    INDEX idx_created_at (created_at)
);

-- Admin actions log
CREATE TABLE IF NOT EXISTS AdminActions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL,
    action_type ENUM('user_create', 'user_update', 'user_delete', 'role_change', 'teacher_approve', 'teacher_reject', 'mode_change', 'whitelist_manage', 'blacklist_manage', 'device_revoke', 'force_logout') NOT NULL,
    target_user_id INT,
    target_student_id VARCHAR(100),
    details TEXT,
    ip_address VARCHAR(45),
    device_id VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_admin_id (admin_id),
    INDEX idx_action_type (action_type),
    INDEX idx_created_at (created_at)
);

-- Warning triggers (escalation tracking)
CREATE TABLE IF NOT EXISTS WarningTriggers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(100) NOT NULL,
    user_id INT NOT NULL,
    warning_type ENUM('first_violation', 'repeated_violation', 'critical_violation', 'pattern_detected') NOT NULL,
    violation_count INT DEFAULT 1,
    last_violation_at DATETIME,
    escalated_to ENUM('teacher', 'admin', 'superadmin') DEFAULT NULL,
    resolved TINYINT(1) DEFAULT 0,
    resolved_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_student_id (student_id),
    INDEX idx_warning_type (warning_type),
    INDEX idx_resolved (resolved)
);

-- Dashboard usage logs
CREATE TABLE IF NOT EXISTS DashboardLogs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    role ENUM('teacher', 'admin', 'superadmin') NOT NULL,
    action VARCHAR(255) NOT NULL,
    endpoint VARCHAR(255),
    ip_address VARCHAR(45),
    device_id VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_role (role),
    INDEX idx_created_at (created_at)
);

-- Create default super admin user (password: admin1234)
-- Hash for 'admin1234' using SHA256
INSERT INTO Users (username, password_hash, role, is_active) 
VALUES (
    'admin', 
    '1c142b2d01aa34e9a36bde480645a57fd69e14155dacfab5a3f9257b77fdc8d8', 
    'superadmin', 
    1
) ON DUPLICATE KEY UPDATE username=username;

