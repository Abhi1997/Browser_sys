<?php
/**
 * Whitelist CRUD handlers
 */

function whitelist_list() {
    requireAuth();
    $pdo = db();
    try {
        $rows = $pdo->query("
            SELECT id, domain as url, description, added_by as addedBy,
                   created_at as addedAt, is_active as isActive
            FROM WhitelistDomains
            ORDER BY created_at DESC
        ")->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}

function whitelist_add() {
    $user = requireAuth();
    $data = getJsonBody();
    $userId = $user['userId'] ?? $user['user_id'] ?? null;
    $url = $data['url'] ?? '';
    $domain = preg_replace('#^https?://#', '', $url);
    $domain = explode('/', $domain)[0];
    $domain = explode('?', $domain)[0];

    $pdo = db();
    $st = $pdo->prepare("
        INSERT INTO WhitelistDomains (domain, mode, description, added_by, created_at, is_active)
        VALUES (?, ?, ?, ?, NOW(), 1)
    ");
    $st->execute([
        $domain,
        $data['mode'] ?? 'free',
        $data['description'] ?? null,
        $userId,
    ]);
    $id = $pdo->lastInsertId();
    $row = $pdo->query("SELECT * FROM WhitelistDomains WHERE id = " . (int)$id)->fetch(PDO::FETCH_ASSOC);
    jsonResp(['success' => true, 'data' => $row]);
}

function whitelist_update($id) {
    requireAuth();
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
        db()->prepare("UPDATE WhitelistDomains SET " . implode(', ', $up) . " WHERE id = ?")->execute($vals);
    }
    $row = db()->query("SELECT * FROM WhitelistDomains WHERE id = " . (int)$id)->fetch(PDO::FETCH_ASSOC);
    jsonResp(['success' => true, 'data' => $row]);
}

function whitelist_delete($id) {
    requireAuth();
    db()->prepare("DELETE FROM WhitelistDomains WHERE id = ?")->execute([$id]);
    jsonResp(['success' => true, 'message' => 'Entry removed from whitelist']);
}
