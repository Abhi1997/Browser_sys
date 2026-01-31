-- ==========================================================
-- Add Superuser Role - Ultimate Superuser
-- ==========================================================
-- Superuser: Can view AND modify everything across all admins
-- Sits above Super Admin in the hierarchy
-- ==========================================================

SET NAMES utf8mb4;

-- 1) Add 'superuser' to Users role ENUM (if you had 'developer', it stays until step 2)
ALTER TABLE Users 
MODIFY COLUMN role ENUM('student', 'teacher', 'admin', 'superadmin', 'superuser', 'developer') NOT NULL;

-- 2) Migrate any existing developer role to superuser (if add_developer_role.sql was run before)
UPDATE Users SET role = 'superuser' WHERE role = 'developer';
UPDATE DashboardLogs SET role = 'superuser' WHERE role = 'developer';

-- 3) Final Users enum: only superuser (no developer)
ALTER TABLE Users 
MODIFY COLUMN role ENUM('student', 'teacher', 'admin', 'superadmin', 'superuser') NOT NULL;

-- 4) DashboardLogs enum
ALTER TABLE DashboardLogs 
MODIFY COLUMN role ENUM('teacher', 'admin', 'superadmin', 'superuser') NOT NULL;

-- 5) Create default superuser user (password must be set via backend)
INSERT INTO Users (username, password_hash, role, is_active, created_at)
VALUES ('superuser', 'RESET_REQUIRED', 'superuser', 1, NOW())
ON DUPLICATE KEY UPDATE role = 'superuser';

-- ==========================================================
-- Role Hierarchy (updated):
--   superuser:   View + modify ALL data across ALL admins (god mode)
--   superadmin:  View all data, can ONLY create new admins
--   admin:       Full authority for their own isolated group
--   teacher:     Manages only their assigned students
--   student:     End user
-- ==========================================================
