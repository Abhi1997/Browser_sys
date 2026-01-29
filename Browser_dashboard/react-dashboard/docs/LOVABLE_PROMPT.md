# Lovable Prompt – DCES Dashboard (copy everything below the line)

Copy **everything** in the section below into Lovable (lovable.dev) as your project prompt. The backend API already exists; you are generating a new React dashboard that connects to it with dynamic data and role-based views.

---

## Copy from here (Lovable prompt)

Build a **DCES Dashboard** – a role-based admin panel for managing users, students, whitelist/blacklist domains, activity logs, and violations.

### CRITICAL: Data must be dynamic from Hostinger database via API

- **All data must be fetched from the live API.** The API runs on Hostinger at `https://api.abhinavpaudel.com` and connects to a **Hostinger MySQL database**. The dashboard must **never** use mock data, static JSON, or hardcoded lists.
- **Every screen must show dynamic data:** stats cards from `GET /api/stats`, user list from `GET /api/users`, students from `GET /api/students`, activity from `GET /api/activity`, violations from `GET /api/violations`, whitelist/blacklist from their GET endpoints. Charts (role distribution, login activity) must use data from the API responses.
- **No placeholder or fake data:** If the API returns empty arrays or zero counts, show that (e.g. “No users yet” or “0”). Do not fill tables or charts with dummy rows or sample data. Use loading states while fetching, then render exactly what the API returns.
- **Refetch after changes:** After create/update/delete/toggle, call the API again (or invalidate React Query) so the UI shows the latest data from the database.

### Backend API

- **Base URL:** Use `import.meta.env.VITE_API_URL` (default `https://api.abhinavpaudel.com`). No trailing slash. This API reads from and writes to the Hostinger database.
- **All responses:** JSON with shape `{ success: boolean, data?: T, error?: string, message?: string }`.
- **Auth:** After login, send on every request: `Authorization: Bearer <token>`, `X-Device-ID: <deviceId>`, `Content-Type: application/json` where applicable.

### Authentication

- **Login:** `POST {{baseUrl}}/auth/login`  
  Body: `{ "username": string, "password": string, "deviceId": string }`.  
  Response: `{ success: true, data: { token: string, user: User } }`.  
  Store `token` and `deviceId` in localStorage (or similar) and send them on all subsequent requests.
- **Verify token:** `POST {{baseUrl}}/api/auth/verify-token`  
  Body: `{ "token": string, "deviceId": string }` + same headers.  
  Response: `{ success: true, data: { valid: true, user: User } }`.  
  Use this on app load to restore session.
- **Logout:** Clear stored token and deviceId and redirect to login.

### User roles and routing

- **Roles:** `super-admin` | `admin` | `teacher` | `student` (from API; API may return `super-admin` or `superadmin` – normalize to `super-admin` in the UI).
- **Routes:**  
  - `/` – Login page (or redirect to role dashboard if already logged in).  
  - `/dashboard-superadmin` – Super admin dashboard (full access).  
  - `/dashboard-admin` – Admin dashboard (scoped management).  
  - `/dashboard-teacher` – Teacher dashboard (students, activity, violations, class metrics).  
  - `/unauthorized` – Shown when user has no access.  
  - `*` – 404.
- After login, redirect by role: super-admin → `/dashboard-superadmin`, admin → `/dashboard-admin`, teacher → `/dashboard-teacher`, student → `/unauthorized` (or a read-only student view if you add one).
- Protect dashboard routes: if not logged in or token invalid, redirect to `/`. If role doesn’t match route, redirect to `/unauthorized`.

### API endpoints (use these exactly)

**Health (no auth)**  
- `GET /health` → `{ status: "ok", message: string }`

**Stats (auth required)**  
- `GET /api/stats` → `data`: `{ totalUsers, activeUsers, activeSessions, roleDistribution: { admin, teacher, student }, whitelistSize, blacklistSize, recentLogins, recentChanges }`  
- `GET /stats/admin/:id` → admin-specific stats (object)  
- `GET /stats/login-activity?days=7` → `data`: array of `{ date, logins, uniqueUsers }`  
- `GET /stats/admins` → `data`: array of admin stats

**Users (auth required)**  
- `GET /api/users` → `data`: array of User  
- `POST /api/users` → body: `{ username?, password?, email?, role?, isActive? }` → created User  
- `PATCH /api/users/:id` → body: `{ username?, email?, role?, isActive? }` → updated User  
- `DELETE /api/users/:id` → success  
- `PATCH /api/users/:id/toggle-status` → updated User  

**User type:** `{ id: string, username: string, email: string (or gmail from API), role: string, isActive: boolean, createdAt: string, lastLogin?: string }`

**Students (auth required)**  
- `GET /api/students` → `data`: array of `{ id, student_id, user_id, gmail, mode, is_active, created_at, username? }`  
- `POST /api/students/:studentId/mode` → body: `{ mode: string, changedBy: number }` → `{ id, mode }`

**Activity (auth required)**  
- `GET /api/activity?limit=100` or `?studentId=...&limit=100` → `data`: array of `{ id, studentId, user_id, url, visitStart, duration, createdAt, domain, mode }`

**Violations (auth required)**  
- `GET /api/violations?limit=100` or `?studentId=...&limit=100` → `data`: array of `{ id, studentId, url, violation_type, reason, timestamp, severity, current_mode }`

**Whitelist (auth required)**  
- `GET /api/whitelist` → `data`: array of `{ id, url (or domain), description, addedBy, addedAt, isActive }`  
- `POST /api/whitelist` → body: `{ url: string, description?, mode? }` → created entry  
- `PATCH /api/whitelist/:id` → body: `{ url?, description?, mode?, isActive? }` → updated entry  
- `DELETE /api/whitelist/:id` → success  

**Blacklist (auth required)**  
- `GET /api/blacklist` → `data`: array of `{ id, url (or domain), reason, addedBy, addedAt, isActive }`  
- `POST /api/blacklist` → body: `{ url: string, reason?, mode? }` → created entry  
- `PATCH /api/blacklist/:id` → body: `{ url?, reason?, mode?, isActive? }` → updated entry  
- `DELETE /api/blacklist/:id` → success  

**Notifications (auth required)**  
- `GET /notifications` → `data`: array of notifications (may be empty)  
- `PATCH /notifications/:id/read` → success  

**Export (auth required)**  
- `POST /export/db` → may return 501 or blob; handle as “export not available” in UI if needed.

### UI requirements

- **Login page:** Username, password, submit. Call login API; on success store token and deviceId, then redirect by role. Show API errors (e.g. “Invalid username or password”).
- **Layout:** Sidebar + main content. Sidebar: nav links by role (e.g. Super Admin: Dashboard, Users, Whitelist, Blacklist, Students, Activity, Violations, Export; Admin: similar scoped; Teacher: Dashboard, Students, Activity, Violations). Header: current user name, logout.
- **Super Admin dashboard:** Stats cards (total users, active users, users by role, whitelist/blacklist size, recent logins). Charts: role distribution (pie/bar), login activity over time (line/bar). Optional: recent activity table or summary.
- **Admin dashboard:** Same idea but scoped to their data if API supports it; otherwise same stats/charts.
- **Teacher dashboard:** Class/student summary cards, list of students, activity and violations tables (filterable by student). Optional: simple chart of activity over time.
- **Users page (super-admin/admin):** Data table with columns: username, email, role, isActive, lastLogin, actions. Actions: Edit (modal or inline), Toggle status, Delete (with confirm). “Add user” button → modal/form: username, password, email, role, isActive. Use GET/POST/PATCH/DELETE and toggle-status endpoints.
- **Students page:** Data table: student id, username/email, mode, status, actions. “Set mode” action → modal or dropdown: select mode (e.g. restricted, free), submit via POST /api/students/:id/mode.
- **Whitelist page:** Table: url/domain, description, addedAt, isActive, actions. Add (modal), Edit, Delete. Use GET/POST/PATCH/DELETE whitelist.
- **Blacklist page:** Same pattern as whitelist (url, reason, addedAt, isActive, Add/Edit/Delete).
- **Activity page:** Table: studentId, url, visitStart, duration, domain, mode. Filters: student (dropdown from GET /api/students), limit. Use GET /api/activity with query params.
- **Violations page:** Table: studentId, url, violation_type, reason, timestamp, severity. Same filtering idea as activity.
- **Notifications:** If API returns data, show list and “mark read”; otherwise show empty state.
- **Export:** Button that calls POST /export/db; if 501 or error, show “Export not available” or message from API.
- **Dynamic behavior:** All tables, stats cards, and charts must be filled **only** from API responses (Hostinger database via API). Use loading and error states. After mutations (create/update/delete/toggle), refetch the relevant list or invalidate queries so the UI always reflects the latest database state. Use React Query (or similar) for fetching and caching. Never use mock or static data.
- **Design:** Modern, clean UI. Prefer a consistent design system (e.g. shadcn/ui or similar). Responsive: sidebar collapses or becomes drawer on small screens. Accessible (labels, focus, errors).

### Tech stack

- **React 18** with **TypeScript**.  
- **Vite** for build.  
- **React Router** for routes above.  
- **Tailwind CSS** for styling.  
- **React Query (TanStack Query)** for API calls, caching, and refetch after mutations.  
- **Environment:** Read API base URL from `import.meta.env.VITE_API_URL` (default `https://api.abhinavpaudel.com`). Generate deviceId once per device (e.g. UUID in localStorage) and reuse for login and all requests.

### Summary

- Single-page app: login → role-based dashboard (super-admin, admin, teacher) with sidebar, stats, charts, and CRUD tables for users, students, whitelist, blacklist, activity, violations.  
- **All data must be fetched from the Hostinger API** (which reads/writes the Hostinger MySQL database). No mock or static data – every list, stat, and chart must come from API calls and show dynamic, live database content.  
- Auth via JWT + deviceId in headers.  
- Dynamic, responsive UI with loading/error states and refetch after mutations so the dashboard always shows up-to-date data from the database.

---

## Copy until here (end of Lovable prompt)

---

## After Lovable generates the app

1. **Replace the frontend:** Export or copy the generated app from Lovable and replace the contents of `src/` (and adjust `index.html` / `vite.config` if needed) in this repo. Keep `php-api/`, `backend/`, `public/.htaccess`, and config files.
2. **Environment:** Set `VITE_API_URL=https://api.abhinavpaudel.com` in `.env.production` (or in Lovable’s env) for production builds.
3. **Device ID:** Ensure the generated app creates/stores a stable `deviceId` (e.g. UUID in localStorage) and sends it with login and every request.

If you want to **remove the current dashboard UI** before generating with Lovable (so you can drop in the new app cleanly), delete or replace the contents of `src/` except keep a minimal `main.tsx` and `index.html` entry point until Lovable’s app is pasted in.
