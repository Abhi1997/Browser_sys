<?php
/**
 * Violations handler
 */

function violations_list() {
    requireAuth();
    $studentId = $_GET['studentId'] ?? '';
    $limit = (int)($_GET['limit'] ?? 100);
    $limit = min(max($limit, 1), 500);

    $pdo = db();
    try {
        if ($studentId !== '') {
            $st = $pdo->prepare("
                SELECT id, student_id as studentId, user_id, attempted_url as url,
                       violation_type, description as reason, created_at as timestamp,
                       created_at as createdAt, severity, current_mode
                FROM Violations
                WHERE student_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ");
            $st->execute([$studentId, $limit]);
        } else {
            $st = $pdo->query("
                SELECT id, student_id as studentId, user_id, attempted_url as url,
                       violation_type, description as reason, created_at as timestamp,
                       created_at as createdAt, severity, current_mode
                FROM Violations
                ORDER BY created_at DESC
                LIMIT " . (int)$limit
            );
        }
        $rows = $st->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}
