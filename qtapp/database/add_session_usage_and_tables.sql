-- Session usage: add last_activity_at to Sessions for per-session browser usage (ML-ready)
-- Run once on existing DBs. If you get "duplicate column" error, the column already exists; skip.

-- MySQL 8.0+: run the line below. If column exists, run: ALTER TABLE Sessions DROP COLUMN last_activity_at; then re-run this once.
ALTER TABLE Sessions ADD COLUMN last_activity_at DATETIME DEFAULT NULL AFTER expires_at;
