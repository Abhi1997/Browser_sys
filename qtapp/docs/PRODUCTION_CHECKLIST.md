# Production Checklist — Market-Ready EduBrowser

Use this checklist before going live.

---

## 1. Database

- [ ] Run **migrate_exam_to_cached_and_cached_sites.sql** on existing DB (exam → cached, CachedSites table).
- [ ] Run **migrate_role_hierarchy_and_isolation.sql** to add admin_id/teacher_id columns for data isolation.
- [ ] Run **add_superuser_role.sql** to add the superuser role (ultimate superuser).
- [ ] Run **add_session_usage_and_tables.sql** if **Sessions** does not have **last_activity_at**.
- [ ] Run **add_browsing_history_and_dashboard_logs.sql** if **BrowsingHistory** does not exist.
- [ ] **JWT_SECRET** in **qtapp/.env** matches PHP API (Hostinger) exactly.
- [ ] **DB** credentials in **qtapp/.env** and **php-api/config.local.php** are correct and restricted to this app.

---

## 2. Cached Mode (Offline Only)

- [ ] Teachers/admins use **"Cache this page"** (toolbar) to add sites for offline use.
- [ ] Cached files are stored under **EduBrowser/cache** (see Authentication.get_cache_base_dir()).
- [ ] In **cached** mode, students only open cached sites; no network (interceptor blocks http/https).
- [ ] Dashboard: **Cached sites** list/delete available to teachers/admins (Admin tab + Teacher section; API: GET/DELETE **api/cached-sites**).

---

## 3. Security & Config

- [ ] **GOOGLE_SAFEBROWSING_API_KEY** set in **.env** for free-mode URL checking.
- [ ] **.env** is not committed (in .gitignore); use **env.example** as template.
- [ ] PHP **config.local.php** on Hostinger has correct DB, **jwt_secret**, and no syntax errors (e.g. comma before `mail_from`).
- [ ] Debug endpoint: **api/debug** returns config/DB status; restrict or disable in production if desired.

---

## 4. Hostinger / API

- [ ] **api.abhinavpaudel.com** serves the latest **php-api** (index.php, handlers, config; path alias **cached-sites** → api/cached-sites included).
- [ ] **abhinavpaudel.com** serves the latest React dashboard **dist/** (npm run build).
- [ ] PHP error logging enabled; check **.logs** for 500s (see HOSTINGER_API_LOGS.md).

---

## 5. Qt App

- [ ] **python main.py** (or packaged executable) runs without errors after login.
- [ ] Mode visible at launch (loading screen + window title).
- [ ] Session usage logged (Sessions.last_activity_at); dashboard shows **Session usage** for admins.
- [ ] Violations and **Warning triggers** recorded; dashboard shows **Warning triggers** for teachers/admins.

---

## 6. Modes Summary

| Mode     | Behavior |
|----------|----------|
| **Cached**   | Offline only. Only pre-cached sites (teachers/admins add via "Cache this page"). No network. |
| **Study**    | Whitelist + blacklist. |
| **Restricted** | Whitelist + blacklist. |
| **Free**     | Safe Browsing check + whitelist/blacklist. |

---

## 7. Loose Ends Addressed

- **Cached sites** list/delete in dashboard: Admin tab **Cached sites**, Teacher section **Cached sites** (API GET/DELETE api/cached-sites).
- User mode visible at application launch (loading screen + window title).
- Violations and warning triggers recorded and shown in dashboard.
- Session usage (start/activity/end) logged for ML; admin **Session usage** tab.
- TimeWindows enforced; outside window = violation.
- TeacherActions / AdminActions logged on mode change from dashboard.
- Browsing history per user; My History + teacher view per student.
- Dashboard open logged (DashboardLogs); admin **Dashboard logs** tab.
- Cached mode: no network; only cached sites; cache managed by teachers/admins.

---

## 8. Optional Hardening

- Rate limit or restrict **api/debug** in production (e.g. by IP or env flag).
- HTTPS only for dashboard and API in production.
- Regular DB backups (Hostinger / your provider).
- Keep dependencies updated (**pip**, **npm**).
