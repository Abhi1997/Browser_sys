<?php
/**
 * Browsing history: own (user) and per-student (teacher view)
 */

function history_list()
{
    try {
        $user = requireAuth();
        $userId = $user['userId'] ?? $user['user_id'] ?? null;
        if (!$userId) {
            jsonResp(['success' => false, 'error' => 'Invalid user'], 401);
        }
        $limit = min(max((int)($_GET['limit'] ?? 100), 1), 500);
        $pdo = db();
        $limit_safe = (int)$limit;
        try {
            $st = $pdo->prepare("
                SELECT id, user_id as userId, url, page_title as pageTitle, visited_at as visitedAt, device_id as deviceId
                FROM BrowsingHistory
                WHERE user_id = ?
                ORDER BY visited_at DESC
                LIMIT {$limit_safe}
            ");
            $st->execute([$userId]);
            $rows = $st->fetchAll(PDO::FETCH_ASSOC);
        }
        catch (Throwable $e) {
            $rows = [];
        }
        jsonResp(['success' => true, 'data' => $rows]);
    }
    catch (Throwable $e) {
        jsonResp(['failed' => false, 'error' => $e->getMessage()], 500);
    }
}

function history_list_student($studentIdOrUserId)
{
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
    $limit = min(max((int)($_GET['limit'] ?? 100), 1), 500);
    $limit_safe = (int)$limit;
    try {
        $st = $pdo->prepare("
            SELECT id, user_id as userId, url, page_title as pageTitle, visited_at as visitedAt, device_id as deviceId
            FROM BrowsingHistory
            WHERE user_id = ?
            ORDER BY visited_at DESC
            LIMIT {$limit_safe}
        ");
        $st->execute([$userId]);
        $rows = $st->fetchAll(PDO::FETCH_ASSOC);
    }
    catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}