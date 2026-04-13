<?php
/**
 * Activity logs handler
 *
 * Data isolation:
 * - teacher: only sees activity for their assigned students
 * - admin: only sees activity for students under their admin_id
 * - superuser/superadmin: sees all (or filtered by ?admin_id)
 */

function activity_list() {
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
        $joinClause = 'JOIN Students s ON al.student_id = s.student_id';
        $whereClauses[] = 's.teacher_id = ?';
        $params[] = $userId;
    } elseif ($role === 'admin') {
        $joinClause = 'JOIN Students s ON al.student_id = s.student_id';
        $whereClauses[] = 's.admin_id = ?';
        $params[] = $userId;
    } elseif (in_array($role, ['superadmin', 'super-admin', 'superuser'], true) && !empty($_GET['admin_id'])) {
        $joinClause = 'JOIN Students s ON al.student_id = s.student_id';
        $whereClauses[] = 's.admin_id = ?';
        $params[] = (int)$_GET['admin_id'];
    }

    if ($studentId !== '') {
        $whereClauses[] = 'al.student_id = ?';
        $params[] = $studentId;
    }

    $whereSql = '';
    if ($whereClauses) {
        $whereSql = 'WHERE ' . implode(' AND ', $whereClauses);
    }

    try {
        $st = $pdo->prepare("
            SELECT al.id, al.student_id as studentId, al.user_id, al.url, al.visit_start as visitStart,
                   al.visit_duration as duration, al.created_at as createdAt, al.domain, al.mode
            FROM ActivityLogs al
            $joinClause
            $whereSql
            ORDER BY al.visit_start DESC, al.created_at DESC
            LIMIT {$limit}
        ");
        $st->execute($params);
        $rows = $st->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}
