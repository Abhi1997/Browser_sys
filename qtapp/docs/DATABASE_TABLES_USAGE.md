# Database Tables Usage

All tables are utilized as follows.

| Table | Purpose |
|-------|--------|
| **Users** | Accounts, roles, auth. Has `admin_id` for teachers (which admin they belong to). |
| **Devices** | Device registration and last_seen (updated on login). |
| **Sessions** | Browser session usage: `created_at` = session start, `last_activity_at` = last activity (updated every 2 min and on navigate). Used for ML/automation. |
| **DashboardTokens** | Dashboard JWT tokens. |
| **DashboardLogs** | Dashboard open events (user_id, role, action, ip_address, created_at). |
| **Students** | Student records, assigned_mode, violation_count. Has `teacher_id` (assigned teacher) and `admin_id` (which admin group). |
| **TimeWindows** | Allowed browsing times per student/day. Enforced in mode_enforcement; outside window = violation. |
| **ModeHistory** | Mode changes (old_mode, new_mode, changed_by, changed_at). Shown in Change logs. |
| **WhitelistDomains** | Allowed domains per mode (cached, study, restricted, free). Has `admin_id` for data isolation per admin group. |
| **BlacklistDomains** | Blocked domains per mode. Has `admin_id` for data isolation per admin group. |
| **ActivityLogs** | Student visit logs (url, domain, mode, visit_start, visit_end, duration). |
| **BrowsingHistory** | Per-user visit history (user_id, url, page_title, visited_at). Own history + teacher view. |
| **Violations** | Blocked attempts (url_blocked, time_window_violation, etc.) with severity. |
| **WarningTriggers** | First violation, repeated violation, escalation (teacher/admin). Shown in dashboard. |
| **TeacherActions** | Teacher actions (e.g. mode_change) when teacher updates student mode from dashboard. |
| **AdminActions** | Admin actions (e.g. mode_change) when admin updates student mode. |
| **PasswordResetTokens** | Forgot-password flow. |

## Session usage (for ML)

- **Start:** When the browser opens after login, `session_start_or_touch` creates/updates a row in **Sessions** with `created_at` and `last_activity_at`.
- **Activity:** Every 2 minutes and on each navigation, `session_touch` updates `last_activity_at`.
- **End:** On window close, `session_end` sets `is_active = 0`.

You can query **Sessions** (e.g. by user_id, session_start, last_activity_at) for ML or reporting.
