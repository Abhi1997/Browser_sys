<?php
/**
 * User CRUD handlers
 * 
 * Role Hierarchy & Data Isolation:
 * - superadmin: Can view all users (read-only), can ONLY create new admins
 * - admin: Can view/manage users under their admin_id (teachers + students)
 * - teacher: Can view their assigned students only
 */

function users_list() {
    $user = requireAuth();
    $pdo = db();
    $role = strtolower($user['role'] ?? '');
    
    // Superuser and Superadmin see all users unless filtering by a specific admin
    if ((isSuperuser($user) || isSuperAdmin($user)) && empty($_GET['admin_id'])) {
        $rows = $pdo->query("
            SELECT id, username, gmail, role, admin_id, is_active, created_at, last_login 
            FROM Users 
            ORDER BY role, created_at DESC
        ")->fetchAll(PDO::FETCH_ASSOC);
        jsonResp(['success' => true, 'data' => $rows]);
        return;
    }
    
    // Admin sees users under them (or Superadmin filtering by a specific admin)
    if ($role === 'admin' || ((isSuperuser($user) || isSuperAdmin($user)) && !empty($_GET['admin_id']))) {
        $adminId = getRequestedAdminId($user);
        $stmt = $pdo->prepare("
            SELECT u.id, u.username, u.gmail, u.role, u.admin_id, u.is_active, u.created_at, u.last_login 
            FROM Users u
            WHERE u.role = 'teacher' AND u.admin_id = ?
            UNION
            SELECT u.id, u.username, u.gmail, u.role, s.admin_id, u.is_active, u.created_at, u.last_login
            FROM Users u
            JOIN Students s ON u.id = s.user_id
            WHERE s.admin_id = ?
            ORDER BY role, created_at DESC
        ");
        $stmt->execute([$adminId, $adminId]);
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
        jsonResp(['success' => true, 'data' => $rows]);
        return;
    }
    
    // Teacher sees only students assigned to them
    if ($role === 'teacher') {
        $teacherId = getUserTeacherId($user);
        $stmt = $pdo->prepare("
            SELECT u.id, u.username, u.gmail, u.role, u.is_active, u.created_at, u.last_login 
            FROM Users u
            JOIN Students s ON u.id = s.user_id
            WHERE s.teacher_id = ?
            ORDER BY u.created_at DESC
        ");
        $stmt->execute([$teacherId]);
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
        jsonResp(['success' => true, 'data' => $rows]);
        return;
    }
    
    // Students see nothing
    jsonResp(['success' => true, 'data' => []]);
}

function users_create() {
    $user = requireAuth();
    $data = getJsonBody();
    $pdo = db();
    $callerRole = strtolower($user['role'] ?? '');
    $newRole = strtolower($data['role'] ?? 'student');
    
    // Superuser can create any user type
    if (isSuperuser($user)) {
        $pass = isset($data['password']) && $data['password'] !== '' ? hashPassword($data['password']) : '';
        $adminId = $data['adminId'] ?? $data['admin_id'] ?? null;
        
        $st = $pdo->prepare("INSERT INTO Users (username, password_hash, gmail, role, admin_id, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?, NOW())");
        $st->execute([
            $data['username'] ?? '',
            $pass,
            $data['email'] ?? $data['gmail'] ?? '',
            $newRole,
            $adminId,
            isset($data['isActive']) ? (int)(bool)$data['isActive'] : 1,
        ]);
        $id = $pdo->lastInsertId();
        
        // If creating a student, also create Students record
        if ($newRole === 'student') {
            $teacherId = $data['teacherId'] ?? $data['teacher_id'] ?? null;
            $studentId = $data['studentId'] ?? $data['student_id'] ?? $data['username'] ?? 'S' . $id;
            $pdo->prepare("INSERT INTO Students (student_id, user_id, teacher_id, admin_id, gmail, assigned_mode, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?, 1, NOW())")
                ->execute([$studentId, $id, $teacherId, $adminId, $data['email'] ?? $data['gmail'] ?? '', $data['mode'] ?? 'restricted']);
        }
        
        $row = $pdo->query("SELECT * FROM Users WHERE id = " . (int)$id)->fetch(PDO::FETCH_ASSOC);
        jsonResp(['success' => true, 'data' => $row, 'message' => ucfirst($newRole) . ' created successfully']);
        return;
    }
    
    // Superadmin can ONLY create admins
    if (isSuperAdmin($user)) {
        if ($newRole !== 'admin') {
            jsonResp([
                'success' => false, 
                'error' => 'Super admins can only create new admins. To create teachers or students, log in as an admin.'
            ], 403);
        }
        // Create admin (no admin_id - they are independent)
        $pass = isset($data['password']) && $data['password'] !== '' ? hashPassword($data['password']) : '';
        $st = $pdo->prepare("INSERT INTO Users (username, password_hash, gmail, role, is_active, created_at) VALUES (?, ?, ?, 'admin', ?, NOW())");
        $st->execute([
            $data['username'] ?? '',
            $pass,
            $data['email'] ?? $data['gmail'] ?? '',
            isset($data['isActive']) ? (int)(bool)$data['isActive'] : 1,
        ]);
        $id = $pdo->lastInsertId();
        $row = $pdo->query("SELECT * FROM Users WHERE id = " . (int)$id)->fetch(PDO::FETCH_ASSOC);
        jsonResp(['success' => true, 'data' => $row, 'message' => 'Admin created successfully']);
        return;
    }
    
    // Admin can create teachers and students under them
    if ($callerRole === 'admin') {
        $adminId = getUserAdminId($user);
        $pass = isset($data['password']) && $data['password'] !== '' ? hashPassword($data['password']) : '';
        
        if ($newRole === 'teacher') {
            // Create teacher under this admin
            $st = $pdo->prepare("INSERT INTO Users (username, password_hash, gmail, role, admin_id, is_active, created_at) VALUES (?, ?, ?, 'teacher', ?, ?, NOW())");
            $st->execute([
                $data['username'] ?? '',
                $pass,
                $data['email'] ?? $data['gmail'] ?? '',
                $adminId,
                isset($data['isActive']) ? (int)(bool)$data['isActive'] : 1,
            ]);
            $id = $pdo->lastInsertId();
            $row = $pdo->query("SELECT * FROM Users WHERE id = " . (int)$id)->fetch(PDO::FETCH_ASSOC);
            jsonResp(['success' => true, 'data' => $row, 'message' => 'Teacher created successfully']);
            return;
        }
        
        if ($newRole === 'student') {
            // Create student user and Students record
            $teacherId = $data['teacherId'] ?? $data['teacher_id'] ?? null;
            
            // Verify teacher belongs to this admin
            if ($teacherId) {
                $stmt = $pdo->prepare("SELECT id FROM Users WHERE id = ? AND role = 'teacher' AND admin_id = ?");
                $stmt->execute([$teacherId, $adminId]);
                if (!$stmt->fetch()) {
                    jsonResp(['success' => false, 'error' => 'Teacher not found or does not belong to your group'], 404);
                }
            }
            
            $st = $pdo->prepare("INSERT INTO Users (username, password_hash, gmail, role, is_active, created_at) VALUES (?, ?, ?, 'student', ?, NOW())");
            $st->execute([
                $data['username'] ?? '',
                $pass,
                $data['email'] ?? $data['gmail'] ?? '',
                isset($data['isActive']) ? (int)(bool)$data['isActive'] : 1,
            ]);
            $userId = $pdo->lastInsertId();
            
            // Create Students record
            $studentId = $data['studentId'] ?? $data['student_id'] ?? $data['username'] ?? 'S' . $userId;
            $st2 = $pdo->prepare("INSERT INTO Students (student_id, user_id, teacher_id, admin_id, gmail, assigned_mode, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?, 1, NOW())");
            $st2->execute([
                $studentId,
                $userId,
                $teacherId,
                $adminId,
                $data['email'] ?? $data['gmail'] ?? '',
                $data['mode'] ?? 'restricted',
            ]);
            
            $row = $pdo->query("SELECT * FROM Users WHERE id = " . (int)$userId)->fetch(PDO::FETCH_ASSOC);
            jsonResp(['success' => true, 'data' => $row, 'message' => 'Student created successfully']);
            return;
        }
        
        // Admin cannot create other admins or superadmins
        jsonResp(['success' => false, 'error' => 'Admins can only create teachers and students'], 403);
        return;
    }
    
    // Teachers cannot create users
    jsonResp(['success' => false, 'error' => 'You do not have permission to create users'], 403);
}

function users_update($id) {
    $user = requireAuth();
    enforceSuperAdminReadOnly($user, 'update users');
    
    $data = getJsonBody();
    $pdo = db();
    $callerRole = strtolower($user['role'] ?? '');
    
    // Superuser can update any user
    if (isSuperuser($user)) {
        $up = [];
        $vals = [];
        if (array_key_exists('username', $data)) {
            $up[] = 'username = ?';
            $vals[] = $data['username'];
        }
        if (array_key_exists('email', $data) || array_key_exists('gmail', $data)) {
            $up[] = 'gmail = ?';
            $vals[] = $data['email'] ?? $data['gmail'] ?? '';
        }
        if (array_key_exists('role', $data)) {
            $up[] = 'role = ?';
            $vals[] = $data['role'];
        }
        if (array_key_exists('admin_id', $data) || array_key_exists('adminId', $data)) {
            $up[] = 'admin_id = ?';
            $vals[] = $data['admin_id'] ?? $data['adminId'];
        }
        if (array_key_exists('isActive', $data)) {
            $up[] = 'is_active = ?';
            $vals[] = (int)(bool)$data['isActive'];
        }
        if (empty($up)) {
            jsonResp(['success' => false, 'error' => 'No fields to update'], 400);
        }
        $vals[] = $id;
        $pdo->prepare("UPDATE Users SET " . implode(', ', $up) . " WHERE id = ?")->execute($vals);
        $row = $pdo->query("SELECT * FROM Users WHERE id = " . (int)$id)->fetch(PDO::FETCH_ASSOC);
        jsonResp(['success' => true, 'data' => $row]);
        return;
    }
    
    // Verify the user has permission to update this user
    $adminId = getUserAdminId($user);
    
    if ($callerRole === 'admin') {
        // Admin can only update teachers/students under them
        $stmt = $pdo->prepare("
            SELECT u.id FROM Users u WHERE u.id = ? AND (
                (u.role = 'teacher' AND u.admin_id = ?) OR
                EXISTS (SELECT 1 FROM Students s WHERE s.user_id = u.id AND s.admin_id = ?)
            )
        ");
        $stmt->execute([$id, $adminId, $adminId]);
        if (!$stmt->fetch()) {
            jsonResp(['success' => false, 'error' => 'User not found or access denied'], 404);
        }
    } elseif ($callerRole === 'teacher') {
        // Teachers can only update their assigned students
        $teacherId = getUserTeacherId($user);
        $stmt = $pdo->prepare("
            SELECT u.id FROM Users u 
            JOIN Students s ON u.id = s.user_id
            WHERE u.id = ? AND s.teacher_id = ?
        ");
        $stmt->execute([$id, $teacherId]);
        if (!$stmt->fetch()) {
            jsonResp(['success' => false, 'error' => 'User not found or access denied'], 404);
        }
    }
    
    $up = [];
    $vals = [];
    if (array_key_exists('username', $data)) {
        $up[] = 'username = ?';
        $vals[] = $data['username'];
    }
    if (array_key_exists('email', $data) || array_key_exists('gmail', $data)) {
        $up[] = 'gmail = ?';
        $vals[] = $data['email'] ?? $data['gmail'] ?? '';
    }
    // Only admin can change roles (and not to admin/superadmin)
    if ($callerRole === 'admin' && array_key_exists('role', $data)) {
        $newRole = strtolower($data['role']);
        if (!in_array($newRole, ['student', 'teacher'], true)) {
            jsonResp(['success' => false, 'error' => 'Can only set role to student or teacher'], 400);
        }
        $up[] = 'role = ?';
        $vals[] = $newRole;
    }
    if (array_key_exists('isActive', $data)) {
        $up[] = 'is_active = ?';
        $vals[] = (int)(bool)$data['isActive'];
    }
    if (empty($up)) {
        jsonResp(['success' => false, 'error' => 'No fields to update'], 400);
    }
    $vals[] = $id;
    $pdo->prepare("UPDATE Users SET " . implode(', ', $up) . " WHERE id = ?")->execute($vals);
    $row = $pdo->query("SELECT * FROM Users WHERE id = " . (int)$id)->fetch(PDO::FETCH_ASSOC);
    jsonResp(['success' => true, 'data' => $row]);
}

function users_delete($id) {
    $user = requireAuth();
    enforceSuperAdminReadOnly($user, 'delete users');
    
    $pdo = db();
    $callerRole = strtolower($user['role'] ?? '');
    $adminId = getUserAdminId($user);
    
    // Superuser can delete any user
    if (isSuperuser($user)) {
        $pdo->prepare("DELETE FROM Users WHERE id = ?")->execute([$id]);
        jsonResp(['success' => true, 'message' => 'User deleted successfully']);
        return;
    }
    
    // Verify permission
    if ($callerRole === 'admin') {
        $stmt = $pdo->prepare("
            SELECT u.id FROM Users u WHERE u.id = ? AND (
                (u.role = 'teacher' AND u.admin_id = ?) OR
                EXISTS (SELECT 1 FROM Students s WHERE s.user_id = u.id AND s.admin_id = ?)
            )
        ");
        $stmt->execute([$id, $adminId, $adminId]);
        if (!$stmt->fetch()) {
            jsonResp(['success' => false, 'error' => 'User not found or access denied'], 404);
        }
    } else {
        jsonResp(['success' => false, 'error' => 'Only admins can delete users'], 403);
    }
    
    $pdo->prepare("DELETE FROM Users WHERE id = ?")->execute([$id]);
    jsonResp(['success' => true, 'message' => 'User deleted successfully']);
}

function users_toggle($id) {
    $user = requireAuth();
    enforceSuperAdminReadOnly($user, 'toggle user status');
    
    $pdo = db();
    $callerRole = strtolower($user['role'] ?? '');
    $adminId = getUserAdminId($user);
    
    // Superuser can toggle any user
    if (isSuperuser($user)) {
        $cur = $pdo->query("SELECT is_active FROM Users WHERE id = " . (int)$id)->fetch(PDO::FETCH_ASSOC);
        if (!$cur) {
            jsonResp(['success' => false, 'error' => 'User not found'], 404);
        }
        $new = !((int)$cur['is_active']);
        $pdo->prepare("UPDATE Users SET is_active = ? WHERE id = ?")->execute([$new ? 1 : 0, $id]);
        $row = $pdo->query("SELECT * FROM Users WHERE id = " . (int)$id)->fetch(PDO::FETCH_ASSOC);
        jsonResp(['success' => true, 'data' => $row]);
        return;
    }
    
    // Verify permission (same as update)
    if ($callerRole === 'admin') {
        $stmt = $pdo->prepare("
            SELECT u.id, u.is_active FROM Users u WHERE u.id = ? AND (
                (u.role = 'teacher' AND u.admin_id = ?) OR
                EXISTS (SELECT 1 FROM Students s WHERE s.user_id = u.id AND s.admin_id = ?)
            )
        ");
        $stmt->execute([$id, $adminId, $adminId]);
        $cur = $stmt->fetch(PDO::FETCH_ASSOC);
    } else {
        jsonResp(['success' => false, 'error' => 'Only admins can toggle user status'], 403);
    }
    
    if (!$cur) {
        jsonResp(['success' => false, 'error' => 'User not found or access denied'], 404);
    }
    $new = !((int)$cur['is_active']);
    $pdo->prepare("UPDATE Users SET is_active = ? WHERE id = ?")->execute([$new ? 1 : 0, $id]);
    $row = $pdo->query("SELECT * FROM Users WHERE id = " . (int)$id)->fetch(PDO::FETCH_ASSOC);
    jsonResp(['success' => true, 'data' => $row]);
}

function admins_list() {
    $user = requireAuth();
    $pdo = db();
    
    // Only superuser and superadmin can see the list of all admins
    if (!isSuperuser($user) && !isSuperAdmin($user)) {
        jsonResp(['success' => false, 'error' => 'Only superusers and super admins can view the admin list'], 403);
    }
    
    $rows = $pdo->query("SELECT id, username, gmail, role, is_active, created_at, last_login FROM Users WHERE role = 'admin' ORDER BY username")->fetchAll(PDO::FETCH_ASSOC);
    jsonResp(['success' => true, 'data' => $rows]);
}

/**
 * Get teachers for the current admin (for assignment dropdown)
 */
function teachers_list() {
    $user = requireAuth();
    $role = strtolower($user['role'] ?? '');
    
    if ($role === 'teacher') {
        jsonResp(['success' => true, 'data' => []]);
        return;
    }
    
    if ($role !== 'admin' && !isSuperAdmin($user) && !isSuperuser($user)) {
        jsonResp(['success' => false, 'error' => 'Only admins can list teachers'], 403);
    }
    
    $pdo = db();
    
    if ((isSuperuser($user) || isSuperAdmin($user)) && empty($_GET['admin_id'])) {
        // Superuser and Superadmin see all teachers
        $rows = $pdo->query("SELECT id, username, gmail, admin_id, is_active, created_at FROM Users WHERE role = 'teacher' ORDER BY username")->fetchAll(PDO::FETCH_ASSOC);
    } else {
        // Admin sees only their teachers (or Superadmin filtering by admin)
        $adminId = getRequestedAdminId($user);
        $stmt = $pdo->prepare("SELECT id, username, gmail, admin_id, is_active, created_at FROM Users WHERE role = 'teacher' AND admin_id = ? ORDER BY username");
        $stmt->execute([$adminId]);
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
    
    jsonResp(['success' => true, 'data' => $rows]);
}
