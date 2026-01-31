-- 1) Replace "exam" mode with "cached" mode (offline-only, no network)
-- 2) Add CachedSites table (teachers/admins manage; students only view cached in cached mode)

-- Update existing rows: exam -> cached
UPDATE Students SET assigned_mode = 'cached' WHERE assigned_mode = 'exam';
UPDATE ModeHistory SET old_mode = 'cached' WHERE old_mode = 'exam';
UPDATE ModeHistory SET new_mode = 'cached' WHERE new_mode = 'exam';
UPDATE WhitelistDomains SET mode = 'cached' WHERE mode = 'exam';
UPDATE BlacklistDomains SET mode = 'cached' WHERE mode = 'exam';
UPDATE ActivityLogs SET mode = 'cached' WHERE mode = 'exam';
UPDATE Violations SET current_mode = 'cached' WHERE current_mode = 'exam';

-- Change ENUMs: exam -> cached (MySQL: modify column to new ENUM)
ALTER TABLE Students MODIFY assigned_mode ENUM('cached', 'study', 'restricted', 'free') DEFAULT 'restricted';
ALTER TABLE ModeHistory MODIFY old_mode ENUM('cached', 'study', 'restricted', 'free');
ALTER TABLE ModeHistory MODIFY new_mode ENUM('cached', 'study', 'restricted', 'free') NOT NULL;
ALTER TABLE WhitelistDomains MODIFY mode ENUM('cached', 'study', 'restricted', 'free') NOT NULL;
ALTER TABLE BlacklistDomains MODIFY mode ENUM('cached', 'study', 'restricted', 'free') NOT NULL;
ALTER TABLE ActivityLogs MODIFY mode ENUM('cached', 'study', 'restricted', 'free') NOT NULL;
ALTER TABLE Violations MODIFY current_mode ENUM('cached', 'study', 'restricted', 'free');

-- CachedSites: URLs that are cached offline; only these load in cached mode (teachers/admins add/edit)
CREATE TABLE IF NOT EXISTS CachedSites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(2048) NOT NULL,
    title VARCHAR(512) DEFAULT NULL,
    file_path VARCHAR(1024) NOT NULL COMMENT 'Relative path to cached file under cache base dir',
    added_by INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active TINYINT(1) DEFAULT 1,
    FOREIGN KEY (added_by) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_url (url(255)),
    INDEX idx_added_by (added_by)
);
