<?php
/**
 * Students and student-mode handlers
 */

function students_list() {
    requireAuth();
    $pdo = db();
    try {
        $rows = $pdo->query("
            SELECT s.id, s.student_id, s.user_id, s.gmail, s.assigned_mode as mode,
                   s.is_active, s.created_at, u.username
            FROM Students s
            LEFT JOIN Users u ON s.user_id = u.id
            ORDER BY s.created_at DESC
        ")->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = $pdo->query("
            SELECT id, id as student_id, username, gmail as email, is_active,
                   'restricted' as mode, created_at
            FROM Users
            WHERE role = 'student'
            ORDER BY created_at DESC
        ")->fetchAll(PDO::FETCH_ASSOC);
    }
    jsonResp(['success' => true, 'data' => $rows]);
}

function students_set_mode($studentId) {
    requireAuth();
    $data = getJsonBody();
    $mode = $data['mode'] ?? '';
    $changedBy = $data['changedBy'] ?? null;
    $pdo = db();

    try {
        $pdo->prepare("UPDATE Students SET assigned_mode = ? WHERE student_id = ? OR id = ?")
            ->execute([$mode, $studentId, $studentId]);
        try {
            $old = $pdo->prepare("SELECT assigned_mode FROM Students WHERE student_id = ? OR id = ?");
            $old->execute([$studentId, $studentId]);
            $oldMode = $old->fetchColumn();
            $pdo->prepare("INSERT INTO ModeHistory (student_id, old_mode, new_mode, changed_by, changed_at) VALUES (?, ?, ?, ?, NOW())")
                ->execute([$studentId, $oldMode, $mode, $changedBy]);
        } catch (Throwable $e) {}
    } catch (Throwable $e) {
        // no-op if table/columns missing
    }

    jsonResp(['success' => true, 'data' => ['id' => $studentId, 'mode' => $mode]]);
}
