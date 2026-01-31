<?php
/**
 * Cached sites: list and delete (teachers/admins). Add is done from Qt app "Cache this page".
 * With admin_id data isolation.
 */

function cached_sites_list() {
    $user = requireAuth();
    $role = strtolower($user['role'] ?? '');
    if (!in_array($role, ['teacher', 'admin', 'super-admin', 'superadmin', 'superuser'], true)) {
        jsonResp(['success' => false, 'error' => 'Forbidden'], 403);
    }
    
    $pdo = db();
    list($adminClause, $adminParams) = adminIdFilter($user, 'c');
    
    try {
        $sql = "
            SELECT c.id, c.url, c.title, c.file_path as filePath, c.added_by as addedBy,
                   c.created_at as createdAt, c.updated_at as updatedAt, c.is_active as isActive,
                   c.admin_id, u.username as addedByName
            FROM CachedSites c
            LEFT JOIN Users u ON c.added_by = u.id
            WHERE c.is_active = 1 $adminClause
            ORDER BY c.created_at DESC
        ";
        $stmt = $pdo->prepare($sql);
        $stmt->execute($adminParams);
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}

function cached_sites_delete($id) {
    $user = requireAuth();
    enforceSuperAdminReadOnly($user, 'delete cached sites');
    
    $role = strtolower($user['role'] ?? '');
    if (!in_array($role, ['teacher', 'admin', 'superuser'], true)) {
        jsonResp(['success' => false, 'error' => 'Forbidden'], 403);
    }
    
    $pdo = db();
    list($adminClause, $adminParams) = adminIdFilter($user);
    
    // Verify permission
    $checkParams = array_merge([$id], $adminParams);
    $stmt = $pdo->prepare("SELECT id FROM CachedSites WHERE id = ? $adminClause");
    $stmt->execute($checkParams);
    if (!$stmt->fetch()) {
        jsonResp(['success' => false, 'error' => 'Cached site not found or access denied'], 404);
    }
    
    try {
        $pdo->prepare("UPDATE CachedSites SET is_active = 0 WHERE id = ?")->execute([$id]);
    } catch (Throwable $e) {
        jsonResp(['success' => false, 'error' => $e->getMessage()], 500);
    }
    jsonResp(['success' => true, 'data' => ['id' => $id]]);
}
