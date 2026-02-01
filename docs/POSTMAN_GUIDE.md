# Postman Guide – Testing the DCES Dashboard API

This guide explains how to test the DCES Dashboard PHP API (and Python backend) using Postman. A ready-to-import collection is provided.

---

## 1. What You Need

- **Postman** installed ([postman.com/downloads](https://www.postman.com/downloads))
- **API base URL:**
  - **Production (PHP on Hostinger):** `https://api.abhinavpaudel.com`
  - **Local PHP:** e.g. `http://localhost` or `http://localhost:8080` (depending on how you run PHP)
  - **Local Python backend:** `http://localhost:5000`
- **Valid credentials** for an admin/superadmin user (username and password from your `Users` table)

---

## 2. Import the Collection

1. Open **Postman**.
2. Click **Import** (top left) or **File → Import**.
3. Choose **Upload Files** and select:
   ```
   react-dashboard/php-api/postman/DCES-API.postman_collection.json
   ```
   Or drag and drop that file into the Import window.
4. Click **Import**.

You should see a collection named **DCES Dashboard API** in the left sidebar.

---

## 3. Set Collection Variables

The collection uses variables so you can switch between local and production without editing every request.

1. Click the **DCES Dashboard API** collection.
2. Open the **Variables** tab.
3. Set (or keep) these **Current Value**s:

| Variable     | Example / Description |
|-------------|------------------------|
| **base_url** | `https://api.abhinavpaudel.com` for production, or `http://localhost:5000` for local Python, or your local PHP URL |
| **token**    | Leave empty – it is set automatically after **Login** |
| **device_id**| `postman-test-device-001` (or any stable string per “device”) |
| **user_id**  | Optional – set to a real user ID when testing Update/Toggle/Delete User |
| **whitelist_id** | Optional – set after Get Whitelist when testing update/delete |
| **blacklist_id** | Optional – set after Get Blacklist when testing update/delete |
| **student_id**   | Optional – set after Get Students when testing Set Student Mode or filtered activity/violations |

4. Click **Save** (or **Update** if you changed the collection).

---

## 4. Recommended Testing Order

### Step 1: Health (no auth)

- Run **Health → Health Check**.
- **Expected:** Status `200`, body like:
  ```json
  { "status": "ok", "message": "Backend API is running" }
  ```
- If this fails, check `base_url` and that the API is reachable (server running, correct URL, no firewall blocking).

### Step 2: Login

- Open **Auth → Login**.
- In the **Body** tab, set real values:
  - `username`: e.g. `admin`
  - `password`: your user’s password
  - `deviceId`: can stay `{{device_id}}` (uses the collection variable).
- Click **Send**.
- **Expected:** Status `200`, body like:
  ```json
  {
    "success": true,
    "data": {
      "token": "eyJ...",
      "user": { "id": "1", "username": "admin", "role": "super-admin", ... }
    }
  }
  ```
- The collection **Tests** script on Login saves `data.token` into the **token** variable. After a successful login, all other requests that use `{{token}}` will use this value.

### Step 3: Verify token (optional)

- Run **Auth → Verify Token**.
- **Expected:** Status `200`, `"success": true`, `"data": { "valid": true, "user": { ... } }`.
- Confirms that the token and `X-Device-ID` are accepted.

### Step 4: Auth-required endpoints

Run any of these; they use `Authorization: Bearer {{token}}` and `X-Device-ID: {{device_id}}` from the collection:

- **Stats → Get Stats** – overview (users, roles, whitelist/blacklist, logins).
- **Stats → Get Admin Stats / Get Login Activity / Get All Admin Stats** – additional stats (some may return empty depending on backend).
- **Users → Get Users** – list users. Optional: pick an id and set **user_id** in Variables for Update/Toggle/Delete.
- **Users → Create User** – create a test user (adjust body as needed).
- **Users → Update User / Toggle User Status / Delete User** – set **user_id** first.
- **Students → Get Students** – list students. Optional: set **student_id** for mode/activity/violations.
- **Students → Set Student Mode** – set **student_id** and body `mode`, `changedBy`.
- **Activity → Get Activity** – all activity or use `?studentId={{student_id}}&limit=50`.
- **Violations → Get Violations** – all violations or by student.
- **Whitelist / Blacklist** – Get, Add, Update (use **whitelist_id** / **blacklist_id**), Delete.
- **Notifications → Get Notifications / Mark Notification Read** – stub behavior on PHP API.
- **Export → Export DB** – PHP API returns 501; use Python backend if you need a real export.

---

## 5. Request Details (Quick Reference)

| Folder     | Request              | Method | Path / example |
|------------|----------------------|--------|-----------------|
| Health     | Health Check         | GET    | `/health` |
| Auth       | Login                | POST   | `/auth/login` |
| Auth       | Verify Token         | POST   | `/api/auth/verify-token` |
| Stats      | Get Stats            | GET    | `/api/stats` |
| Stats      | Get Admin Stats      | GET    | `/stats/admin/1` |
| Stats      | Get Login Activity   | GET    | `/stats/login-activity?days=7` |
| Stats      | Get All Admin Stats  | GET    | `/stats/admins` |
| Users      | Get Users            | GET    | `/api/users` |
| Users      | Create User          | POST   | `/api/users` |
| Users      | Update User          | PATCH  | `/api/users/{{user_id}}` |
| Users      | Toggle User Status   | PATCH  | `/api/users/{{user_id}}/toggle-status` |
| Users      | Delete User          | DELETE | `/api/users/{{user_id}}` |
| Students   | Get Students         | GET    | `/api/students` |
| Students   | Set Student Mode     | POST   | `/api/students/{{student_id}}/mode` |
| Activity   | Get Activity         | GET    | `/api/activity?limit=100` |
| Violations | Get Violations       | GET    | `/api/violations?limit=100` |
| Whitelist  | Get / Add / Update / Delete | GET/POST/PATCH/DELETE | `/api/whitelist`, `/api/whitelist/{{whitelist_id}}` |
| Blacklist  | Get / Add / Update / Delete | GET/POST/PATCH/DELETE | `/api/blacklist`, `/api/blacklist/{{blacklist_id}}` |
| Notifications | Get Notifications | GET  | `/notifications` |
| Notifications | Mark Read         | PATCH  | `/notifications/1/read` |
| Export     | Export DB            | POST   | `/export/db` |

---

## 6. Headers Used by the Collection

- **Content-Type: application/json** – for requests with a JSON body (Login, Create/Update User, Whitelist/Blacklist add/update, Set Student Mode, Verify Token).
- **Authorization: Bearer {{token}}** – added on all requests under Auth (except Login), Stats, Users, Students, Activity, Violations, Whitelist, Blacklist, Notifications, Export. Set by the Login test script.
- **X-Device-ID: {{device_id}}** – sent on every request; must match the device used at login for verify-token and any backend that checks device.

You do not need to set these manually for requests in the collection; they are already configured.

---

## 7. Body Examples

### Login
```json
{
  "username": "admin",
  "password": "your_password",
  "deviceId": "postman-test-device-001"
}
```

### Create User
```json
{
  "username": "newuser",
  "password": "temp123",
  "email": "newuser@example.com",
  "role": "student",
  "isActive": true
}
```

### Add to Whitelist
```json
{
  "url": "https://example.com",
  "description": "Allowed domain",
  "mode": "free"
}
```

### Add to Blacklist
```json
{
  "url": "https://blocked.com",
  "reason": "Blocked domain",
  "mode": "free"
}
```

### Set Student Mode
```json
{
  "mode": "restricted",
  "changedBy": 1
}
```

---

## 8. Typical Errors and Fixes

| Response / behaviour | What to check |
|----------------------|----------------|
| **404 Not Found** | Correct `base_url` (no trailing slash). For PHP, all routes go through `index.php`; ensure your server (e.g. `.htaccess`) routes to it. |
| **401 Missing authentication token** | Run **Login** first. Ensure **Authorization: Bearer {{token}}** is present and **token** is set (see collection Variables after Login). |
| **401 Invalid or expired token** | Token expired or wrong JWT secret. Log in again; if on PHP, ensure `JWT_SECRET` matches the backend that issued the token. |
| **500 / DB or PHP errors** | Check API logs and `config.local.php` (or env): DB host, user, password, database name. |
| **CORS errors** | Usually in browser apps, not in Postman. If you hit CORS from a script, allow your origin in the API. |
| **Login 401 Invalid username or password** | Use credentials that exist in the `Users` table; password must match (e.g. SHA256 hash in DB for PHP). |

---

## 9. Running the Collection (Newman, optional)

To run the collection from the command line (e.g. in CI):

1. Install Newman: `npm install -g newman`
2. Run:
   ```bash
   newman run react-dashboard/php-api/postman/DCES-API.postman_collection.json \
     --env-var "base_url=https://api.abhinavpaudel.com" \
     --env-var "token=YOUR_TOKEN"
   ```
   Or use a Postman **Environment** file and `--environment your-env.json`.

For automated flows, run **Health Check** and **Login** first, then pass the token (e.g. from the Login response) into Newman via `--env-var "token=..."` for subsequent runs.

---

## 10. File Locations

| Item | Path |
|------|------|
| Postman collection | `react-dashboard/php-api/postman/DCES-API.postman_collection.json` |
| This guide | `react-dashboard/docs/POSTMAN_GUIDE.md` |

After importing the collection and setting `base_url` (and optionally **user_id**, **whitelist_id**, **blacklist_id**, **student_id**), start with **Health Check** and **Login**, then use the rest of the requests to test the API.
