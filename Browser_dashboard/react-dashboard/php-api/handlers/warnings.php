<?php
/**
 * Warning triggers: violations recorded with escalation (for dashboard)
 */

function warnings_list() {
    $user = requireAuth();
    $role = strtolower($user['role'] ?? '');
    if (!in_array($role, ['teacher', 'admin', 'super-admin', 'superuser'], true)) {
        jsonResp(['success' => false, 'error' => 'Forbidden'], 403);
    }
    $limit = min(max((int)($_GET['limit'] ?? 100), 1), 500);
    $studentId = $_GET['studentId'] ?? '';
    $pdo = db();
    try {
        $sql = "
            SELECT w.id, w.student_id as studentId, w.user_id as userId, w.warning_type as warningType,
                   w.violation_count as violationCount, w.last_violation_at as lastViolationAt,
                   w.escalated_to as escalatedTo, w.resolved, w.resolved_at as resolvedAt, w.created_at as createdAt,
                   u.username
            FROM WarningTriggers w
            LEFT JOIN Users u ON w.user_id = u.id
            WHERE 1=1
        ";
        $params = [];
        if ($studentId !== '') {
            $sql .= " AND w.student_id = ?";
            $params[] = $studentId;
        }
        $sql .= " ORDER BY w.created_at DESC LIMIT " . (int)$limit;
        $st = $pdo->prepare($sql);
        $st->execute($params);
        $rows = $st->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}
