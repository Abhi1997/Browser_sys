-- ==========================================================
-- Secure Academic Browser (EduBrowser)
-- Single Database Schema (Hostinger Shared Hosting Compatible)
-- Database must already exist (NO CREATE DATABASE)
-- MySQL 8 / utf8mb4
-- ==========================================================

SET NAMES utf8mb4;
SET time_zone = '+00:00';

-- ==========================================================
-- AUTHENTICATION & SECURITY
-- ==========================================================

CREATE TABLE IF NOT EXISTS Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    gmail VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
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
    INDEX idx_teacher_status (teacher_approval_status),
    FOREIGN KEY (approved_by) REFERENCES Users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS Devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(255) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    ip_address VARCHAR(45),
    mac_address VARCHAR(17),
    device_fingerprint TEXT,
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen DATETIME,
    is_active TINYINT(1) DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_ip (ip_address)
);

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

-- ==========================================================
-- STUDENTS & CONTROLS
-- ==========================================================

CREATE TABLE IF NOT EXISTS Students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(100) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    gmail VARCHAR(255) NOT NULL,
    assigned_mode ENUM('exam', 'study', 'restricted', 'free') DEFAULT 'restricted',
    violation_count INT DEFAULT 0,
    device_id VARCHAR(255),
    ip_address VARCHAR(45),
    mac_address VARCHAR(17),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active TINYINT(1) DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_mode (assigned_mode),
    INDEX idx_device_id (device_id)
);

CREATE TABLE IF NOT EXISTS TimeWindows (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(100) NOT NULL,
    day_of_week ENUM('monday','tuesday','wednesday','thursday','friday','saturday','sunday','all') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_active TINYINT(1) DEFAULT 1,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    INDEX idx_student_id (student_id)
);

CREATE TABLE IF NOT EXISTS ModeHistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(100) NOT NULL,
    old_mode ENUM('exam', 'study', 'restricted', 'free'),
    new_mode ENUM('exam', 'study', 'restricted', 'free') NOT NULL,
    changed_by INT NOT NULL,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES Users(id),
    INDEX idx_student_id (student_id),
    INDEX idx_changed_at (changed_at)
);

CREATE TABLE IF NOT EXISTS WhitelistDomains (
    id INT AUTO_INCREMENT PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    mode ENUM('exam', 'study', 'restricted', 'free') NOT NULL,
    description TEXT,
    added_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active TINYINT(1) DEFAULT 1,
    FOREIGN KEY (added_by) REFERENCES Users(id) ON DELETE SET NULL,
    INDEX idx_domain (domain),
    INDEX idx_mode (mode)
);

CREATE TABLE IF NOT EXISTS BlacklistDomains (
    id INT AUTO_INCREMENT PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    mode ENUM('exam', 'study', 'restricted', 'free') NOT NULL,
    reason TEXT,
    added_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active TINYINT(1) DEFAULT 1,
    FOREIGN KEY (added_by) REFERENCES Users(id) ON DELETE SET NULL,
    INDEX idx_domain (domain),
    INDEX idx_mode (mode)
);

-- ==========================================================
-- ACTIVITY, VIOLATIONS & AUDIT LOGS
-- ==========================================================

CREATE TABLE IF NOT EXISTS ActivityLogs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(100) NOT NULL,
    user_id INT NOT NULL,
    url VARCHAR(2048) NOT NULL,
    domain VARCHAR(255),
    mode ENUM('exam', 'study', 'restricted', 'free') NOT NULL,
    visit_duration INT DEFAULT 0,
    visit_start DATETIME NOT NULL,
    visit_end DATETIME,
    device_id VARCHAR(255),
    ip_address VARCHAR(45),
    mac_address VARCHAR(17),
    is_allowed TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_student_mode_time (student_id, mode, visit_start),
    INDEX idx_domain (domain)
);

CREATE TABLE IF NOT EXISTS Violations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(100) NOT NULL,
    user_id INT NOT NULL,
    violation_type ENUM(
        'url_blocked',
        'mode_bypass_attempt',
        'time_window_violation',
        'unauthorized_action',
        'device_mismatch'
    ) NOT NULL,
    description TEXT NOT NULL,
    attempted_url VARCHAR(2048),
    current_mode ENUM('exam', 'study', 'restricted', 'free'),
    device_id VARCHAR(255),
    ip_address VARCHAR(45),
    mac_address VARCHAR(17),
    severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_student_severity_time (student_id, severity, created_at),
    INDEX idx_violation_type (violation_type)
);

CREATE TABLE IF NOT EXISTS TeacherActions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    action_type ENUM(
        'mode_change',
        'whitelist_add',
        'whitelist_remove',
        'view_student',
        'view_activity',
        'approve_student'
    ) NOT NULL,
    target_student_id VARCHAR(100),
    details TEXT,
    ip_address VARCHAR(45),
    device_id VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_teacher_id (teacher_id),
    INDEX idx_action_type (action_type)
);

CREATE TABLE IF NOT EXISTS AdminActions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL,
    action_type ENUM(
        'user_create',
        'user_update',
        'user_delete',
        'role_change',
        'teacher_approve',
        'teacher_reject',
        'mode_change',
        'whitelist_manage',
        'blacklist_manage',
        'device_revoke',
        'force_logout'
    ) NOT NULL,
    target_user_id INT,
    target_student_id VARCHAR(100),
    details TEXT,
    ip_address VARCHAR(45),
    device_id VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_admin_id (admin_id),
    INDEX idx_action_type (action_type)
);

CREATE TABLE IF NOT EXISTS WarningTriggers (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(100) NOT NULL,
    user_id INT NOT NULL,
    warning_type ENUM(
        'first_violation',
        'repeated_violation',
        'critical_violation',
        'pattern_detected'
    ) NOT NULL,
    violation_count INT DEFAULT 1,
    last_violation_at DATETIME,
    escalated_to ENUM('teacher', 'admin', 'superadmin'),
    resolved TINYINT(1) DEFAULT 0,
    resolved_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_student_warning (student_id, warning_type, resolved)
);

CREATE TABLE IF NOT EXISTS DashboardLogs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    role ENUM('teacher', 'admin', 'superadmin') NOT NULL,
    action VARCHAR(255) NOT NULL,
    endpoint VARCHAR(255),
    ip_address VARCHAR(45),
    device_id VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_user_role_time (user_id, role, created_at)
);

-- ==========================================================
-- DEFAULT SUPERADMIN (NO PASSWORD SET HERE)
-- Password must be created/reset via backend using bcrypt
-- ==========================================================

INSERT INTO Users (username, password_hash, role, is_active)
VALUES ('admin', 'RESET_REQUIRED', 'superadmin', 1)
ON DUPLICATE KEY UPDATE username = username;
