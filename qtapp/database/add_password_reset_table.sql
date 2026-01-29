-- Password reset tokens for forgot-password flow.
-- Run this on your Hostinger database (e.g. via phpMyAdmin) if not already applied.

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS PasswordResetTokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token_hash VARCHAR(64) NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_token_hash (token_hash),
    INDEX idx_expires (expires_at),
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);
