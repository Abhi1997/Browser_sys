<?php
/**
 * Notifications handlers - stub for dashboard compatibility.
 * Frontend calls GET /notifications and PATCH /notifications/:id/read.
 */

function notifications_list() {
    requireAuth();
    jsonResp(['success' => true, 'data' => []]);
}

function notifications_read($id) {
    requireAuth();
    jsonResp(['success' => true]);
}
