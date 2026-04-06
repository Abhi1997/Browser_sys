<?php
/**
 * Violations handler
 *
 * Data isolation:
 * - teacher: only sees violations for their assigned students
 * - admin: only sees violations for students under their admin_id
 * - superuser/superadmin: sees all (or filtered by ?admin_id)
 */

function violations_list() {
    $user = requireAuth();
    $role = strtolower($user['role'] ?? '');
    $userId = $user['userId'] ?? $user['user_id'] ?? null;
    $studentId = $_GET['studentId'] ?? '';
    $limit = (int)($_GET['limit'] ?? 100);
    $limit = min(max($limit, 1), 500);

    $pdo = db();

    // Build role-based filtering
    $joinClause = '';
    $whereClauses = [];
    $params = [];

    if ($role === 'teacher') {
        $joinClause = 'JOIN Students s ON v.student_id = s.student_id';
        $whereClauses[] = 's.teacher_id = ?';
        $params[] = $userId;
    } elseif ($role === 'admin') {
        $joinClause = 'JOIN Students s ON v.student_id = s.student_id';
        $whereClauses[] = 's.admin_id = ?';
        $params[] = $userId;
    } elseif (in_array($role, ['superadmin', 'super-admin', 'superuser'], true) && !empty($_GET['admin_id'])) {
        $joinClause = 'JOIN Students s ON v.student_id = s.student_id';
        $whereClauses[] = 's.admin_id = ?';
        $params[] = (int)$_GET['admin_id'];
    }

    if ($studentId !== '') {
        $whereClauses[] = 'v.student_id = ?';
        $params[] = $studentId;
    }

    $whereSql = '';
    if ($whereClauses) {
        $whereSql = 'WHERE ' . implode(' AND ', $whereClauses);
    }

    $params[] = $limit;

    try {
        $st = $pdo->prepare("
            SELECT v.id, v.student_id as studentId, v.user_id, v.attempted_url as url,
                   v.violation_type, v.description as reason, v.created_at as timestamp,
                   v.created_at as createdAt, v.severity, v.current_mode
            FROM Violations v
            $joinClause
            $whereSql
            ORDER BY v.created_at DESC
            LIMIT ?
        ");
        $st->execute($params);
        $rows = $st->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}
