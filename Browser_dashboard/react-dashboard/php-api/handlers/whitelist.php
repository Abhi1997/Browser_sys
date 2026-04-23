<?php
/**
 * Whitelist CRUD handlers - with admin_id data isolation
 */

function whitelist_list() {
    $user = requireAuth();
    $pdo = db();
    
    $pdo = db();
    
    list($adminClause, $adminParams) = adminIdFilter($user, '', true);
    
    try {
        $sql = "
            SELECT id, domain as url, description, added_by as addedBy, admin_id,
                   created_at as addedAt, is_active as isActive, mode
            FROM WhitelistDomains
            WHERE 1=1 $adminClause
            ORDER BY created_at DESC
        ";
        $stmt = $pdo->prepare($sql);
        $stmt->execute($adminParams);
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}

function whitelist_add() {
    $user = requireAuth();
    enforceSuperAdminReadOnly($user, 'add to whitelist');
    
    $data = getJsonBody();
    $userId = $user['userId'] ?? $user['user_id'] ?? null;
    $adminId = getUserAdminId($user);
    $url = $data['url'] ?? '';
    // Strip only HTTP protocols, preserving paths securely for the new substring logic
    $domain = preg_replace('#^https?://#', '', $url);

    $mode = $data['mode'] ?? 'free';
    
    $pdo = db();
    // (Exam Mode 1-to-1 constraint removed to support login redirects)

    $st = $pdo->prepare("
        INSERT INTO WhitelistDomains (domain, mode, description, added_by, admin_id, created_at, is_active)
        VALUES (?, ?, ?, ?, ?, NOW(), 1)
    ");
    $st->execute([
        $domain,
        $data['mode'] ?? 'free',
        $data['description'] ?? null,
        $userId,
        $adminId,
    ]);
    $id = $pdo->lastInsertId();
    $row = $pdo->query("SELECT * FROM WhitelistDomains WHERE id = " . (int)$id)->fetch(PDO::FETCH_ASSOC);
    jsonResp(['success' => true, 'data' => $row]);
}

function whitelist_update($id) {
    $user = requireAuth();
    enforceSuperAdminReadOnly($user, 'update whitelist');
    
    $pdo = db();
    list($adminClause, $adminParams) = adminIdFilter($user, '', true);
    
    // Verify permission: Normal Admins can only edit entries they "own" (where admin_id matches)
    // they can SEE global ones (if $includeGlobal was true) but 403 when trying to UPDATE them.
    $checkParams = array_merge([$id], $adminParams);
    $stmt = $pdo->prepare("SELECT id, admin_id FROM WhitelistDomains WHERE id = ? $adminClause");
    $stmt->execute($checkParams);
    $row = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!$row) {
        jsonResp(['success' => false, 'error' => 'Entry not found or access denied'], 404);
    }
    
    // Double check: if it's a global entry (admin_id IS NULL) and user is NOT a superuser/superadmin, deny update
    if ($row['admin_id'] === null && !isSuperuser($user) && !isSuperAdmin($user)) {
        jsonResp(['success' => false, 'error' => 'Only super-admins can modify global system entries'], 403);
    }
    
    $data = getJsonBody();
    $up = [];
    $vals = [];
    if (array_key_exists('url', $data) || array_key_exists('domain', $data)) {
        $url = $data['url'] ?? $data['domain'] ?? '';
        $domain = preg_replace('#^https?://#', '', $url);
        $up[] = 'domain = ?';
        $vals[] = $domain;
    }
    if (array_key_exists('description', $data)) {
        $up[] = 'description = ?';
        $vals[] = $data['description'];
    }
    if (array_key_exists('mode', $data)) {
        $up[] = 'mode = ?';
        $vals[] = $data['mode'];
    }
    if (array_key_exists('isActive', $data)) {
        $up[] = 'is_active = ?';
        $vals[] = (int)(bool)$data['isActive'];
    }
    if (!empty($up)) {
        // (Exam Mode 1-to-1 constraint removed)

        $vals[] = $id;
        $pdo->prepare("UPDATE WhitelistDomains SET " . implode(', ', $up) . " WHERE id = ?")->execute($vals);
    }
    $row = $pdo->query("SELECT * FROM WhitelistDomains WHERE id = " . (int)$id)->fetch(PDO::FETCH_ASSOC);
    jsonResp(['success' => true, 'data' => $row]);
}

function whitelist_delete($id) {
    $user = requireAuth();
    enforceSuperAdminReadOnly($user, 'delete from whitelist');
    
    $pdo = db();
    list($adminClause, $adminParams) = adminIdFilter($user);
    
    // Verify permission
    $checkParams = array_merge([$id], $adminParams);
    $stmt = $pdo->prepare("SELECT id FROM WhitelistDomains WHERE id = ? $adminClause");
    $stmt->execute($checkParams);
    if (!$stmt->fetch()) {
        jsonResp(['success' => false, 'error' => 'Entry not found or access denied'], 404);
    }
    
    $pdo->prepare("DELETE FROM WhitelistDomains WHERE id = ?")->execute([$id]);
    jsonResp(['success' => true, 'message' => 'Entry removed from whitelist']);
}
