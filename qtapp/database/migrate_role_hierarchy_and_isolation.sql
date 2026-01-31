-- ==========================================================
-- Migration: Role Hierarchy & Data Isolation
-- ==========================================================
-- Role Hierarchy:
--   superadmin: Read-only view of all admins, can ONLY create new admins
--   admin: Full operational authority for their own data (teachers, students)
--   teacher: Manages only their assigned students
--   student: End user
--
-- Data Isolation:
--   - Each admin has isolated data (teachers, students, whitelists, etc.)
--   - Teachers belong to ONE admin (admin_id)
--   - Students are assigned to ONE teacher by admin (teacher_id)
--   - Admins cannot see other admins' data
--   - Superadmin can view all but NOT modify
-- ==========================================================

SET NAMES utf8mb4;

-- 1) Add admin_id to Users (for teachers: which admin they belong to)
ALTER TABLE Users
  ADD COLUMN admin_id INT DEFAULT NULL AFTER role,
  ADD INDEX idx_admin_id (admin_id),
  ADD FOREIGN KEY fk_users_admin (admin_id) REFERENCES Users(id) ON DELETE SET NULL;

-- 2) Add teacher_id to Students (which teacher the student is assigned to)
ALTER TABLE Students
  ADD COLUMN teacher_id INT DEFAULT NULL AFTER user_id,
  ADD COLUMN admin_id INT DEFAULT NULL AFTER teacher_id,
  ADD INDEX idx_teacher_id (teacher_id),
  ADD INDEX idx_admin_id (admin_id),
  ADD FOREIGN KEY fk_students_teacher (teacher_id) REFERENCES Users(id) ON DELETE SET NULL,
  ADD FOREIGN KEY fk_students_admin (admin_id) REFERENCES Users(id) ON DELETE SET NULL;

-- 3) Add admin_id to WhitelistDomains (data isolation per admin)
ALTER TABLE WhitelistDomains
  ADD COLUMN admin_id INT DEFAULT NULL AFTER added_by,
  ADD INDEX idx_admin_id (admin_id),
  ADD FOREIGN KEY fk_whitelist_admin (admin_id) REFERENCES Users(id) ON DELETE CASCADE;

-- 4) Add admin_id to BlacklistDomains (data isolation per admin)
ALTER TABLE BlacklistDomains
  ADD COLUMN admin_id INT DEFAULT NULL AFTER added_by,
  ADD INDEX idx_admin_id (admin_id),
  ADD FOREIGN KEY fk_blacklist_admin (admin_id) REFERENCES Users(id) ON DELETE CASCADE;

-- 5) Add admin_id to CachedSites (data isolation per admin)
ALTER TABLE CachedSites
  ADD COLUMN admin_id INT DEFAULT NULL AFTER added_by,
  ADD INDEX idx_admin_id (admin_id),
  ADD FOREIGN KEY fk_cached_admin (admin_id) REFERENCES Users(id) ON DELETE CASCADE;

-- 6) Add admin_id to TimeWindows (data isolation per admin)
ALTER TABLE TimeWindows
  ADD COLUMN admin_id INT DEFAULT NULL AFTER is_active,
  ADD INDEX idx_admin_id (admin_id);

-- 7) Add admin_id to ActivityLogs (for filtering by admin)
ALTER TABLE ActivityLogs
  ADD COLUMN admin_id INT DEFAULT NULL AFTER ip_address,
  ADD INDEX idx_admin_id (admin_id);

-- 8) Add admin_id to Violations (for filtering by admin)
ALTER TABLE Violations
  ADD COLUMN admin_id INT DEFAULT NULL AFTER severity,
  ADD INDEX idx_admin_id (admin_id);

-- 9) Add admin_id to WarningTriggers (for filtering by admin)
ALTER TABLE WarningTriggers
  ADD COLUMN admin_id INT DEFAULT NULL AFTER created_at,
  ADD INDEX idx_admin_id (admin_id);

-- 10) Add admin_id to ModeHistory (for filtering by admin)
ALTER TABLE ModeHistory
  ADD COLUMN admin_id INT DEFAULT NULL AFTER reason,
  ADD INDEX idx_admin_id (admin_id);

-- 11) Add admin_id to BrowsingHistory (for filtering by admin)
ALTER TABLE BrowsingHistory
  ADD COLUMN admin_id INT DEFAULT NULL AFTER device_id,
  ADD INDEX idx_admin_id (admin_id);

-- 12) Add admin_id to Sessions (for filtering by admin)
ALTER TABLE Sessions
  ADD COLUMN admin_id INT DEFAULT NULL AFTER is_active,
  ADD INDEX idx_admin_id (admin_id);

-- 13) Add admin_id to DashboardLogs (for filtering by admin)
ALTER TABLE DashboardLogs
  ADD COLUMN admin_id INT DEFAULT NULL AFTER created_at,
  ADD INDEX idx_admin_id (admin_id);

-- ==========================================================
-- Update existing data: assign existing teachers/students to first admin
-- (Run this only if you have existing data that needs migration)
-- ==========================================================

-- Find the first admin user (not superadmin)
SET @first_admin_id = (SELECT id FROM Users WHERE role = 'admin' AND is_active = 1 ORDER BY id LIMIT 1);

-- If no admin exists, use the superadmin as fallback (you should create a proper admin)
SET @first_admin_id = COALESCE(@first_admin_id, (SELECT id FROM Users WHERE role = 'superadmin' ORDER BY id LIMIT 1));

-- Assign existing teachers to first admin
UPDATE Users SET admin_id = @first_admin_id WHERE role = 'teacher' AND admin_id IS NULL;

-- Find first teacher
SET @first_teacher_id = (SELECT id FROM Users WHERE role = 'teacher' AND is_active = 1 ORDER BY id LIMIT 1);

-- Assign existing students to first teacher and first admin
UPDATE Students SET teacher_id = @first_teacher_id, admin_id = @first_admin_id WHERE teacher_id IS NULL;

-- Assign existing whitelist/blacklist/cached to first admin
UPDATE WhitelistDomains SET admin_id = @first_admin_id WHERE admin_id IS NULL;
UPDATE BlacklistDomains SET admin_id = @first_admin_id WHERE admin_id IS NULL;
UPDATE CachedSites SET admin_id = @first_admin_id WHERE admin_id IS NULL;

-- Note: ActivityLogs, Violations, etc. historical data will have NULL admin_id
-- which is fine - they predate this migration

-- ==========================================================
-- DONE
-- ==========================================================
