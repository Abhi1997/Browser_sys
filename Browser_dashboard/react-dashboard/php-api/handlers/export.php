<?php
/**
 * Export handler - stub for dashboard compatibility.
 * Frontend calls POST /export/db and expects a blob. Returns 501 or minimal placeholder.
 */

function export_db() {
    requireAuth();
    jsonResp([
        'success' => false,
        'error' => 'Export not implemented on PHP API. Use Python backend for DB export.',
    ], 501);
}
