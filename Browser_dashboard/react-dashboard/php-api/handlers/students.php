<?php
/**
 * Students and student-mode handlers
 * 
 * Data Isolation:
 * - superuser: Can view/modify all students (full access)
 * - superadmin: Can view all students (read-only)
 * - admin: Can view/manage students under their admin_id
 * - teacher: Can only view students assigned to them (teacher_id)
 */

function students_list() {
    $user = requireAuth();
    $pdo = db();
    
    // Build filters based on role
    list($adminClause, $adminParams) = adminIdFilter($user, 's');
    list($teacherClause, $teacherParams) = teacherIdFilter($user, 's');
    
    $params = array_merge($adminParams, $teacherParams);
    
    try {
        $sql = "
            SELECT s.id, s.student_id, s.user_id, s.gmail, s.assigned_mode as mode,
                   s.is_active, s.created_at, s.teacher_id, s.admin_id,
                   u.username, t.username as teacherName,
                   (SELECT device_fingerprint FROM Devices WHERE user_id = s.user_id ORDER BY last_seen DESC LIMIT 1) as deviceToken
            FROM Students s
            LEFT JOIN Users u ON s.user_id = u.id
            LEFT JOIN Users t ON s.teacher_id = t.id
            WHERE 1=1 $adminClause $teacherClause
            ORDER BY s.created_at DESC
        ";
        $stmt = $pdo->prepare($sql);
        $stmt->execute($params);
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        // Fallback if Students table doesn't have new columns yet
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
    $user = requireAuth();
    
    // Superadmin cannot modify
    enforceSuperAdminReadOnly($user, 'change student mode');
    
    $data = getJsonBody();
    $mode = $data['mode'] ?? '';
    $changedBy = $data['changedBy'] ?? null;
    $pdo = db();
    $role = strtolower($user['role'] ?? '');
    $userId = $user['userId'] ?? $user['user_id'] ?? null;
    
    // Verify the user has permission to modify this student
    list($adminClause, $adminParams) = adminIdFilter($user);
    list($teacherClause, $teacherParams) = teacherIdFilter($user);
    
    $checkParams = array_merge([$studentId, $studentId], $adminParams, $teacherParams);
    $checkSql = "SELECT id, assigned_mode, admin_id FROM Students WHERE (student_id = ? OR id = ?) $adminClause $teacherClause";
    $stmt = $pdo->prepare($checkSql);
    $stmt->execute($checkParams);
    $student = $stmt->fetch(PDO::FETCH_ASSOC);
    
    if (!$student) {
        jsonResp(['success' => false, 'error' => 'Student not found or access denied'], 404);
    }
    
    $oldMode = $student['assigned_mode'];
    $studentAdminId = $student['admin_id'];

    try {
        $pdo->prepare("UPDATE Students SET assigned_mode = ? WHERE id = ?")
            ->execute([$mode, $student['id']]);
        
        // Log mode history
        try {
            $pdo->prepare("INSERT INTO ModeHistory (student_id, old_mode, new_mode, changed_by, changed_at, admin_id) VALUES (?, ?, ?, ?, NOW(), ?)")
                ->execute([$studentId, $oldMode, $mode, $changedBy ?? $userId, $studentAdminId]);
            
            if ($role === 'teacher' && $userId) {
                $pdo->prepare("INSERT INTO TeacherActions (teacher_id, action_type, target_student_id, details, created_at) VALUES (?, 'mode_change', ?, ?, NOW())")
                    ->execute([$userId, $studentId, json_encode(['old_mode' => $oldMode, 'new_mode' => $mode])]);
            }
            if ($role === 'admin' && $userId) {
                $pdo->prepare("INSERT INTO AdminActions (admin_id, action_type, target_student_id, details, created_at) VALUES (?, 'mode_change', ?, ?, NOW())")
                    ->execute([$userId, $studentId, json_encode(['old_mode' => $oldMode, 'new_mode' => $mode])]);
            }
        } catch (Throwable $e) {}
    } catch (Throwable $e) {
        jsonResp(['success' => false, 'error' => $e->getMessage()], 500);
    }

    jsonResp(['success' => true, 'data' => ['id' => $studentId, 'mode' => $mode]]);
}

/**
 * Assign a student to a teacher (admin only)
 */
function students_assign_teacher($studentId) {
    $user = requireAuth();
    enforceSuperAdminReadOnly($user, 'assign teacher');
    
    $role = strtolower($user['role'] ?? '');
    if ($role !== 'admin') {
        jsonResp(['success' => false, 'error' => 'Only admins can assign students to teachers'], 403);
    }
    
    $data = getJsonBody();
    $teacherId = $data['teacherId'] ?? $data['teacher_id'] ?? null;
    $adminId = getUserAdminId($user);
    $pdo = db();
    
    // Verify the teacher belongs to this admin
    if ($teacherId) {
        $stmt = $pdo->prepare("SELECT id FROM Users WHERE id = ? AND role = 'teacher' AND admin_id = ?");
        $stmt->execute([$teacherId, $adminId]);
        if (!$stmt->fetch()) {
            jsonResp(['success' => false, 'error' => 'Teacher not found or does not belong to your group'], 404);
        }
    }
    
    // Verify student belongs to this admin
    $stmt = $pdo->prepare("SELECT id FROM Students WHERE (student_id = ? OR id = ?) AND admin_id = ?");
    $stmt->execute([$studentId, $studentId, $adminId]);
    if (!$stmt->fetch()) {
        jsonResp(['success' => false, 'error' => 'Student not found or access denied'], 404);
    }
    
    $pdo->prepare("UPDATE Students SET teacher_id = ? WHERE student_id = ? OR id = ?")
        ->execute([$teacherId, $studentId, $studentId]);
    
    jsonResp(['success' => true, 'data' => ['studentId' => $studentId, 'teacherId' => $teacherId]]);
}
