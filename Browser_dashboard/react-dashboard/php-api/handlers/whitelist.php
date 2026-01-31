<?php
/**
 * Whitelist CRUD handlers - with admin_id data isolation
 */

function whitelist_list() {
    $user = requireAuth();
    $pdo = db();
    
    list($adminClause, $adminParams) = adminIdFilter($user);
    
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
    $domain = preg_replace('#^https?://#', '', $url);
    $domain = explode('/', $domain)[0];
    $domain = explode('?', $domain)[0];

    $pdo = db();
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
    list($adminClause, $adminParams) = adminIdFilter($user);
    
    // Verify permission
    $checkParams = array_merge([$id], $adminParams);
    $stmt = $pdo->prepare("SELECT id FROM WhitelistDomains WHERE id = ? $adminClause");
    $stmt->execute($checkParams);
    if (!$stmt->fetch()) {
        jsonResp(['success' => false, 'error' => 'Entry not found or access denied'], 404);
    }
    
    $data = getJsonBody();
    $up = [];
    $vals = [];
    if (array_key_exists('url', $data) || array_key_exists('domain', $data)) {
        $url = $data['url'] ?? $data['domain'] ?? '';
        $domain = preg_replace('#^https?://#', '', $url);
        $domain = explode('/', $domain)[0];
        $domain = explode('?', $domain)[0];
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
