# Python App Setup (EduBrowser with RBAC)

This doc describes how to configure the Python “browser” application (EduBrowser) so it works with the **hosted** PHP API at `https://api.abhinavpaudel.com` in production, and how RBAC and auth stay in sync with the dashboard.

---

## 1. Call the Hosted API in Production

Your Python application (the “browser” with RBAC) must use the hosted API in production:

| Setting | Value |
|--------|--------|
| **API base URL** | `https://api.abhinavpaudel.com` (no trailing slash) |

### 1.1 Where the API URL is used

- **Opening the dashboard**  
  The Qt app opens the web dashboard at `DASHBOARD_URL`. That URL is where users see the React app; the React app itself calls the API using `VITE_API_URL` (set at build time). For production, set:
  - `DASHBOARD_URL` to where the dashboard is served (e.g. `https://www.abhinavpaudel.com` or `https://api.abhinavpaudel.com`).

- **Python code calling the API**  
  If the Python app makes HTTP requests to the API (e.g. login, sync, reporting), use the same base URL. Set `API_BASE_URL=https://api.abhinavpaudel.com` in `.env` and use it as the base for all API calls. The app currently uses the **same MySQL database** as the PHP API for auth and RBAC; tokens are generated locally with the same `JWT_SECRET`. If you add or move flows to “call the hosted API,” use `API_BASE_URL` and the auth below.

---

## 2. Auth When Calling the Hosted API

Use the same auth as the dashboard:

1. **Login**  
   `POST /auth/login` with JSON body:
   - `username`
   - `password`
   - `deviceId`

2. **Other requests**  
   Send:
   - Header: `Authorization: Bearer <token>`
   - Header: `X-Device-ID: <deviceId>` (optional but recommended)

Example (conceptual):

```python
import os
import requests

API_BASE = os.getenv("API_BASE_URL", "https://api.abhinavpaudel.com").rstrip("/")

# Login
r = requests.post(f"{API_BASE}/auth/login", json={
    "username": "admin",
    "password": "secret",
    "deviceId": "your-device-uuid",
})
data = r.json()
token = data.get("token")
device_id = data.get("deviceId") or "your-device-uuid"

# Later request
headers = {
    "Authorization": f"Bearer {token}",
    "X-Device-ID": device_id,
    "Content-Type": "application/json",
}
r2 = requests.get(f"{API_BASE}/api/students", headers=headers)
```

---

## 3. JWT Secret and DB in Sync With the PHP API

For tokens and users to match across the Python app, dashboard, and PHP API:

| Item | Requirement |
|------|-------------|
| **JWT secret** | Same value in Qt app `.env` (`JWT_SECRET`) and PHP API (`php-api/config.php` or env `JWT_SECRET`). |
| **Database** | Python app and PHP API use the same MySQL DB (same host, user, password, database). Configure via `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` in Qt app `.env` and in the PHP API config. |

Generate a strong secret and keep it only in env/config (never in code):

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Use that value for `JWT_SECRET` in both the Qt app and the PHP API.

---

## 4. Environment Variables (Qt app)

In the Qt app project root, use a `.env` file (see `env.example`). For production with the hosted API:

| Variable | Description | Production example |
|----------|-------------|--------------------|
| `DB_HOST` | MySQL host (same as PHP API) | Hostinger host, e.g. `srv1882.hstgr.io` or `localhost` |
| `DB_PORT` | MySQL port | `3306` |
| `DB_USER` | MySQL user | e.g. `u976383844_abhi097` |
| `DB_PASSWORD` | MySQL password | (same as PHP API) |
| `DB_NAME` | Database name | e.g. `u976383844_dces` |
| `DASHBOARD_URL` | Where the React dashboard is served | `https://www.abhinavpaudel.com` or `https://api.abhinavpaudel.com` |
| `API_BASE_URL` | Base URL when Python code calls the API | `https://api.abhinavpaudel.com` |
| `JWT_SECRET` | Secret for signing/verifying JWTs (must match PHP API) | long random string |
| `VITE_API_URL` | Used when *building* the React dashboard; not by the Python runtime | `https://api.abhinavpaudel.com` |

---

## 5. RBAC and Roles

The Python app enforces RBAC using the same DB and roles as the PHP API:

- **super-admin** – full access
- **admin** – admin dashboard and management
- **teacher** – teacher dashboard and class-level data
- **student** – browser use only; no dashboard access

User and role data live in the shared MySQL database. Keeping `JWT_SECRET` and DB config identical in the Qt app and PHP API keeps roles and tokens in sync.

---

## 6. Quick Checklist

- [ ] `DASHBOARD_URL` set to the real dashboard origin (e.g. `https://www.abhinavpaudel.com` or `https://api.abhinavpaudel.com`).
- [ ] `API_BASE_URL=https://api.abhinavpaudel.com` if the Python app calls the API.
- [ ] `JWT_SECRET` in Qt app `.env` matches PHP API config.
- [ ] DB host, user, password, and name match between Qt app and PHP API.
- [ ] Auth to the API uses `POST /auth/login` and then `Authorization: Bearer <token>` and `X-Device-ID` on other requests.

---

## 7. Related Docs

- **BROWSER_SETUP.md** – Browser, CORS, extension, and API URL for the DCES dashboard and PHP API.
- **DASHBOARD_SETUP.md** – Dashboard URL, token, and backend alignment.
- **SETUP_GUIDE.md** – Database and overall EduBrowser setup.
