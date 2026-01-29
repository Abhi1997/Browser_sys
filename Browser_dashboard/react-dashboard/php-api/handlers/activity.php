<?php
/**
 * Activity logs handler
 */

function activity_list() {
    requireAuth();
    $studentId = $_GET['studentId'] ?? '';
    $limit = (int)($_GET['limit'] ?? 100);
    $limit = min(max($limit, 1), 500);

    $pdo = db();
    try {
        if ($studentId !== '') {
            $st = $pdo->prepare("
                SELECT id, student_id as studentId, user_id, url, visit_start as visitStart,
                       visit_duration as duration, created_at as createdAt, domain, mode
                FROM ActivityLogs
                WHERE student_id = ?
                ORDER BY visit_start DESC, created_at DESC
                LIMIT ?
            ");
            $st->execute([$studentId, $limit]);
        } else {
            $st = $pdo->query("
                SELECT id, student_id as studentId, user_id, url, visit_start as visitStart,
                       visit_duration as duration, created_at as createdAt, domain, mode
                FROM ActivityLogs
                ORDER BY visit_start DESC, created_at DESC
                LIMIT " . (int)$limit
            );
        }
        $rows = $st->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}
