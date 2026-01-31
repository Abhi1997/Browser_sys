-- BrowsingHistory: per-user visit history (user can view own; teachers see students')
-- DashboardLogs already exists in init_single_db.sql - use it for dashboard open logging

CREATE TABLE IF NOT EXISTS BrowsingHistory (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    url VARCHAR(2048) NOT NULL,
    page_title VARCHAR(512) DEFAULT NULL,
    visited_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    device_id VARCHAR(255) DEFAULT NULL,
    INDEX idx_user_visited (user_id, visited_at),
    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- Ensure DashboardLogs has an 'action' value we use for opens (already has action VARCHAR(255))
-- No schema change needed; use action = 'dashboard_open'.
