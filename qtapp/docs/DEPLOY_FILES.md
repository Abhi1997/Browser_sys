# Files to Update / Upload for Deployment

Use this list when deploying EduBrowser (including superuser role and role hierarchy).

---

## 1. Database (run SQL on your MySQL server)

**Run these in order** (only the ones that apply to your current DB state):

| File | When to run |
|------|-------------|
| `qtapp/database/init_single_db.sql` | **New install only** – creates all tables |
| `qtapp/database/migrate_exam_to_cached_and_cached_sites.sql` | Existing DB that still has "exam" mode or no CachedSites table |
| `qtapp/database/migrate_role_hierarchy_and_isolation.sql` | Existing DB that doesn’t have admin_id/teacher_id on tables |
| `qtapp/database/add_superuser_role.sql` | **Always** – adds superuser role and default user |
| `qtapp/database/add_session_usage_and_tables.sql` | If Sessions table doesn’t have last_activity_at |
| `qtapp/database/add_browsing_history_and_dashboard_logs.sql` | If BrowsingHistory or DashboardLogs don’t exist |

After running SQL, set the **superuser** user’s password (update `password_hash` in `Users` or use your password-reset flow).

---

## 2. PHP API (upload to Hostinger / your API server)

Upload these files from **`Browser_dashboard/react-dashboard/php-api/`**:

| File | Notes |
|------|--------|
| `helpers.php` | isSuperuser, canModify, getUserAdminId, enforceSuperAdminReadOnly |
| `index.php` | Routes (teachers, assign-teacher, admins, cached-sites, etc.) |
| `handlers/users.php` | Superuser + role hierarchy (users list/create/update/delete, admins, teachers) |
| `handlers/students.php` | Data isolation, assign-teacher, set mode |
| `handlers/stats.php` | Stats filtered by admin_id; superuser sees all |
| `handlers/cached_sites.php` | Cached sites list/delete, admin_id filter |
| `handlers/whitelist.php` | admin_id filter, superuser can modify all |
| `handlers/blacklist.php` | admin_id filter, superuser can modify all |
| `handlers/auth.php` | (if you changed login/verify for roles) |
| `config.php` | Only if you have local overrides (often use config.local.php on server) |

**Do not upload** `config.local.php` if it contains secrets – create/update it directly on the server with DB and JWT settings.

---

## 3. React Dashboard (build, then upload)

**Build locally:**
```bash
cd Browser_dashboard/react-dashboard
npm ci
npm run build
```

**Upload** the contents of **`Browser_dashboard/react-dashboard/dist/`** to your web root (e.g. abhinavpaudel.com).

**Source files that were changed** (for reference; you deploy `dist/`):

| File | Notes |
|------|--------|
| `src/App.tsx` | Route `/dashboard-superuser`, SuperuserDashboard |
| `src/pages/Index.tsx` | Role-based redirect (superuser → dashboard-superuser) |
| `src/pages/SuperuserDashboard.tsx` | **New** – superuser dashboard |
| `src/lib/types.ts` | UserRole includes `superuser` |

---

## 4. Python Qt app (desktop – if you ship the app)

Update or package these from **`qtapp/`**:

| File | Notes |
|------|--------|
| `authentication.py` | Valid roles include `superuser` |
| `browser.py` | Dashboard + cache button for `superuser` role |
| `.env` | Do **not** ship; use .env.example. User sets API URL, JWT from login. |

---

## 5. Quick checklist

- [ ] Run required SQL scripts on MySQL (see section 1).
- [ ] Set superuser password in DB.
- [ ] Upload PHP API files (section 2) to Hostinger (or your API host).
- [ ] Build React app (`npm run build`), upload `dist/` (section 3).
- [ ] Ensure **JWT_SECRET** and **DB** config match between qtapp `.env` and PHP `config.local.php`.
- [ ] If distributing the desktop app, use updated qtapp files (section 4).
