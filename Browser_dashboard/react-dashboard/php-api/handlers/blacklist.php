<?php
/**
 * Blacklist CRUD handlers
 */

function blacklist_list() {
    requireAuth();
    $pdo = db();
    try {
        $rows = $pdo->query("
            SELECT id, domain as url, reason, added_by as addedBy,
                   created_at as addedAt, is_active as isActive, mode
            FROM BlacklistDomains
            ORDER BY created_at DESC
        ")->fetchAll(PDO::FETCH_ASSOC);
    } catch (Throwable $e) {
        $rows = [];
    }
    jsonResp(['success' => true, 'data' => $rows]);
}

function blacklist_add() {
    $user = requireAuth();
    $data = getJsonBody();
    $userId = $user['userId'] ?? $user['user_id'] ?? null;
    $url = $data['url'] ?? '';
    $domain = preg_replace('#^https?://#', '', $url);
    $domain = explode('/', $domain)[0];
    $domain = explode('?', $domain)[0];

    $pdo = db();
    $st = $pdo->prepare("
        INSERT INTO BlacklistDomains (domain, mode, reason, added_by, created_at, is_active)
        VALUES (?, ?, ?, ?, NOW(), 1)
    ");
    $st->execute([
        $domain,
        $data['mode'] ?? 'free',
        $data['reason'] ?? null,
        $userId,
    ]);
    $id = $pdo->lastInsertId();
    $row = $pdo->query("SELECT * FROM BlacklistDomains WHERE id = " . (int)$id)->fetch(PDO::FETCH_ASSOC);
    jsonResp(['success' => true, 'data' => $row]);
}

function blacklist_update($id) {
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
    if (array_key_exists('reason', $data)) {
        $up[] = 'reason = ?';
        $vals[] = $data['reason'];
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
        db()->prepare("UPDATE BlacklistDomains SET " . implode(', ', $up) . " WHERE id = ?")->execute($vals);
    }
    $row = db()->query("SELECT * FROM BlacklistDomains WHERE id = " . (int)$id)->fetch(PDO::FETCH_ASSOC);
    jsonResp(['success' => true, 'data' => $row]);
}

function blacklist_delete($id) {
    requireAuth();
    db()->prepare("DELETE FROM BlacklistDomains WHERE id = ?")->execute([$id]);
    jsonResp(['success' => true, 'message' => 'Entry removed from blacklist']);
}
