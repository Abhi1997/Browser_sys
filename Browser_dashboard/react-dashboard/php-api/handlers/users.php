<?php
/**
 * User CRUD handlers
 */

function users_list() {
    requireAuth();
    $pdo = db();
    $rows = $pdo->query("SELECT id, username, gmail, role, is_active, created_at, last_login FROM Users ORDER BY created_at DESC")->fetchAll(PDO::FETCH_ASSOC);
    jsonResp(['success' => true, 'data' => $rows]);
}

function users_create() {
    requireAuth();
    $data = getJsonBody();
    $pdo = db();
    $pass = isset($data['password']) && $data['password'] !== '' ? hashPassword($data['password']) : '';
    $st = $pdo->prepare("INSERT INTO Users (username, password_hash, gmail, role, is_active, created_at) VALUES (?, ?, ?, ?, ?, NOW())");
    $st->execute([
        $data['username'] ?? '',
        $pass,
        $data['email'] ?? $data['gmail'] ?? '',
        $data['role'] ?? 'student',
        isset($data['isActive']) ? (int)(bool)$data['isActive'] : 1,
    ]);
    $id = $pdo->lastInsertId();
    $row = $pdo->query("SELECT * FROM Users WHERE id = " . (int)$id)->fetch(PDO::FETCH_ASSOC);
    jsonResp(['success' => true, 'data' => $row, 'message' => 'User created successfully']);
}

function users_update($id) {
    requireAuth();
    $data = getJsonBody();
    $up = [];
    $vals = [];
    if (array_key_exists('username', $data)) {
        $up[] = 'username = ?';
        $vals[] = $data['username'];
    }
    if (array_key_exists('email', $data) || array_key_exists('gmail', $data)) {
        $up[] = 'gmail = ?';
        $vals[] = $data['email'] ?? $data['gmail'] ?? '';
    }
    if (array_key_exists('role', $data)) {
        $up[] = 'role = ?';
        $vals[] = $data['role'];
    }
    if (array_key_exists('isActive', $data)) {
        $up[] = 'is_active = ?';
        $vals[] = (int)(bool)$data['isActive'];
    }
    if (empty($up)) {
        jsonResp(['success' => false, 'error' => 'No fields to update'], 400);
    }
    $vals[] = $id;
    db()->prepare("UPDATE Users SET " . implode(', ', $up) . " WHERE id = ?")->execute($vals);
    $row = db()->query("SELECT * FROM Users WHERE id = " . (int)$id)->fetch(PDO::FETCH_ASSOC);
    jsonResp(['success' => true, 'data' => $row]);
}

function users_delete($id) {
    requireAuth();
    db()->prepare("DELETE FROM Users WHERE id = ?")->execute([$id]);
    jsonResp(['success' => true, 'message' => 'User deleted successfully']);
}

function users_toggle($id) {
    requireAuth();
    $pdo = db();
    $cur = $pdo->query("SELECT is_active FROM Users WHERE id = " . (int)$id)->fetch(PDO::FETCH_ASSOC);
    if (!$cur) {
        jsonResp(['success' => false, 'error' => 'User not found'], 404);
    }
    $new = !((int)$cur['is_active']);
    $pdo->prepare("UPDATE Users SET is_active = ? WHERE id = ?")->execute([$new ? 1 : 0, $id]);
    $row = $pdo->query("SELECT * FROM Users WHERE id = " . (int)$id)->fetch(PDO::FETCH_ASSOC);
    jsonResp(['success' => true, 'data' => $row]);
}

function admins_list() {
    requireAuth();
    $pdo = db();
    $rows = $pdo->query("SELECT id, username, gmail, role, is_active, created_at, last_login FROM Users WHERE role = 'admin' ORDER BY username")->fetchAll(PDO::FETCH_ASSOC);
    jsonResp(['success' => true, 'data' => $rows]);
}
