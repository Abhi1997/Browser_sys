# Python Application (Browser) Setup – RBAC and API

The “browser” in this project is a **Python application with RBAC** that runs on client machines and talks to the same backend as the React dashboard.

---

## 1. API base URL

Configure the Python app to use the **hosted API** in production:

```text
API_BASE_URL = "https://api.abhinavpaudel.com"
```

Use this for all HTTP calls (login, verify-token, students, activity, violations, etc.). No trailing slash.

---

## 2. Authentication

- **Login:** `POST {API_BASE_URL}/auth/login`  
  Body: `{"username": "...", "password": "...", "deviceId": "..."}`  
  Store the returned `token` and reuse the same `deviceId` for that machine.

- **Protected calls:**  
  - Header: `Authorization: Bearer <token>`  
  - Header: `X-Device-ID: <deviceId>`  
  - Body (when applicable): JSON.

- **Token refresh:** Call `POST {API_BASE_URL}/api/auth/verify-token` with `{"token": "...", "deviceId": "..."}`. If it fails, redirect to login.

---

## 3. RBAC and roles

Roles come from the `Users` table and are returned in login/verify responses as `user["role"]`. The Python app must enforce them:

| Role        | Typical permissions                                                |
|------------|---------------------------------------------------------------------|
| **superadmin** | Full access: users, whitelist, blacklist, students, export, etc.   |
| **admin**      | Scoped management (e.g. their students, their lists).               |
| **teacher**    | View students/activity/violations; optionally change student mode. |
| **student**    | Own session only; app may report activity/violations, no admin APIs. |

The app should:

1. After login/verify, read `user["role"]` (and `user["id"]` if needed).
2. Restrict UI and API calls by role (e.g. hide admin menus for students; don’t call `/api/users` for students).
3. Send the same JWT and `X-Device-ID` so the API can validate the user and device.

---

## 4. Network and deployment

- The Python app needs **outbound HTTPS** to `https://api.abhinavpaudel.com`.
- If the app is packaged (e.g. PyInstaller) or runs in a locked-down environment, ensure firewall/proxy allow this.
- No browser-style “permissions” are required; normal HTTP from a desktop app is enough.

---

## 5. Environment and secrets

- **Production:** set `API_BASE_URL=https://api.abhinavpaudel.com` via config or environment variable.
- **Development:** use `http://localhost:5000` (or your local API URL) and switch to the hosted URL for staging/production.
- **Secrets:** do not commit passwords. Use env vars, keyring, or a one-time admin login that stores a token.

---

## 6. Checklist – Python app (“browser”) setup

| Item              | Action                                                                 |
|-------------------|------------------------------------------------------------------------|
| API base URL      | Set to `https://api.abhinavpaudel.com` for production.                 |
| Login             | Call `POST /auth/login` with `username`, `password`, `deviceId`; store `token`. |
| Auth on requests  | Send `Authorization: Bearer <token>` and `X-Device-ID: <deviceId>`.    |
| RBAC              | Use `user["role"]` from login/verify to restrict features and API calls. |
| Roles             | Align with dashboard: superadmin, admin, teacher, student.              |
| Network           | Allow outbound HTTPS to `api.abhinavpaudel.com`.                        |
