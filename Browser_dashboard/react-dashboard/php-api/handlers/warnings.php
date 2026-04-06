<?php
/**
 * Warning triggers: violations recorded with escalation (for dashboard)
 *
 * Data isolation:
 * - teacher: only sees warnings for their assigned students
 * - admin: only sees warnings for students under their admin_id
 * - superuser/superadmin: sees all (or filtered by ?admin_id)
 */

function warnings_list() {
    $user = requireAuth();
    $role = strtolower($user['role'] ?? '');
    if (!in_array($role, ['teacher', 'admin', 'super-admin', 'superadmin', 'superuser'], true)) {
        jsonResp(['success' => false, 'error' => 'Forbidden'], 403);
    }
    $userId = $user['userId'] ?? $user['user_id'] ?? null;
    $limit = min(max((int)($_GET['limit'] ?? 100), 1), 500);
    $studentId = $_GET['studentId'] ?? '';
    $pdo = db();

    // Build role-based filtering
    $joinClause = '';
    $whereClauses = ['1=1'];
    $params = [];

    if ($role === 'teacher') {
        $joinClause = 'JOIN Students s ON w.student_id = s.student_id';
        $whereClauses[] = 's.teacher_id = ?';
        $params[] = $userId;
    } elseif ($role === 'admin') {
        $joinClause = 'JOIN Students s ON w.student_id = s.student_id';
        $whereClauses[] = 's.admin_id = ?';
        $params[] = $userId;
    } elseif (in_array($role, ['superadmin', 'super-admin', 'superuser'], true) && !empty($_GET['admin_id'])) {
        $joinClause = 'JOIN Students s ON w.student_id = s.student_id';
        $whereClauses[] = 's.admin_id = ?';
        $params[] = (int)$_GET['admin_id'];
    }

    if ($studentId !== '') {
        $whereClauses[] = 'w.student_id = ?';
        $params[] = $studentId;
    }

    $whereSql = 'WHERE ' . implode(' AND ', $whereClauses);

    try {
        $sql = "
            SELECT w.id, w.student_id as studentId, w.user_id as userId, w.warning_type as warningType,
                   w.violation_count as violationCount, w.last_violation_at as lastViolationAt,
                   w.escalated_to as escalatedTo, w.resolved, w.resolved_at as resolvedAt, w.created_at as createdAt,
                   u.username
            FROM WarningTriggers w
            LEFT JOIN Users u ON w.user_id = u.id
            $joinClause
            $whereSql
            ORDER BY w.created_at DESC LIMIT " . (int)$limit;
        $st = $pdo->prepare($sql);
        $st->execute($params);
        $rows = $st->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}
