<?php
/**
 * Bookmarks: own (user) and per-student (teacher view)
 */

function bookmarks_list() {
    $user = requireAuth();
    $userId = $user['userId'] ?? $user['user_id'] ?? null;
    if (!$userId) {
        jsonResp(['success' => false, 'error' => 'Invalid user'], 401);
    }
    $pdo = db();
    try {
        $st = $pdo->prepare("
            SELECT id, user_id as userId, url, title, added_at as addedAt
            FROM Bookmarks
            WHERE user_id = ?
            ORDER BY added_at DESC
        ");
        $st->execute([$userId]);
        $rows = $st->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}

function bookmarks_list_student($studentIdOrUserId) {
    $user = requireAuth();
    $role = $user['role'] ?? '';
    $teacherOrAdmin = in_array(strtolower($role), ['teacher', 'admin', 'super-admin', 'superuser'], true);
    if (!$teacherOrAdmin) {
        jsonResp(['success' => false, 'error' => 'Forbidden'], 403);
    }
    $pdo = db();
    // Resolve student_id to user_id if needed
    $userId = $studentIdOrUserId;
    if (!is_numeric($studentIdOrUserId)) {
        $st = $pdo->prepare("SELECT user_id FROM Students WHERE student_id = ? OR id = ?");
        $st->execute([$studentIdOrUserId, $studentIdOrUserId]);
        $row = $st->fetch(PDO::FETCH_ASSOC);
        $userId = $row['user_id'] ?? null;
    }
    if (!$userId) {
        jsonResp(['success' => false, 'error' => 'Student not found'], 404);
    }
    try {
        $st = $pdo->prepare("
            SELECT id, user_id as userId, url, title as title, added_at as addedAt
            FROM Bookmarks
            WHERE user_id = ?
            ORDER BY added_at DESC
        ");
        $st->execute([$userId]);
        $rows = $st->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}

function bookmarks_add() {
    $user = requireAuth();
    $userId = $user['userId'] ?? $user['user_id'] ?? null;
    if (!$userId) {
        jsonResp(['success' => false, 'error' => 'Invalid user'], 401);
    }
    $input = getJsonInput();
    $url = $input['url'] ?? null;
    $title = $input['title'] ?? $url;
    
    if (!$url) {
        jsonResp(['success' => false, 'error' => 'URL is required'], 400);
    }
    
    $pdo = db();
    try {
        // Check if exists
        $st = $pdo->prepare("SELECT id FROM Bookmarks WHERE user_id = ? AND url = ?");
        $st->execute([$userId, $url]);
        $existing = $st->fetch();
        
        if ($existing) {
            $st = $pdo->prepare("UPDATE Bookmarks SET title = ?, added_at = NOW() WHERE id = ?");
            $st->execute([$title, $existing['id']]);
        } else {
            $st = $pdo->prepare("INSERT INTO Bookmarks (user_id, url, title, added_at) VALUES (?, ?, ?, NOW())");
            $st->execute([$userId, $url, $title]);
        }
        jsonResp(['success' => true]);
    } catch (Throwable $e) {
        jsonResp(['success' => false, 'error' => $e->getMessage()], 500);
    }
}

function bookmarks_remove() {
    $user = requireAuth();
    $userId = $user['userId'] ?? $user['user_id'] ?? null;
    if (!$userId) {
        jsonResp(['success' => false, 'error' => 'Invalid user'], 401);
    }
    $input = getJsonInput();
    $url = $input['url'] ?? null;
    
    if (!$url) {
        jsonResp(['success' => false, 'error' => 'URL is required'], 400);
    }
    
    $pdo = db();
    try {
        $st = $pdo->prepare("DELETE FROM Bookmarks WHERE user_id = ? AND url = ?");
        $st->execute([$userId, $url]);
        jsonResp(['success' => true]);
    } catch (Throwable $e) {
        jsonResp(['success' => false, 'error' => $e->getMessage()], 500);
    }
}
