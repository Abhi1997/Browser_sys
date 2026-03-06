-- Bookmarks: per-user personal bookmarks
-- Students can only see their own; Teachers/Admins can monitor students' bookmarks.

CREATE TABLE IF NOT EXISTS Bookmarks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    url VARCHAR(2048) NOT NULL,
    title VARCHAR(512) DEFAULT NULL,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_added (user_id, added_at),
    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);
