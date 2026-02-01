# EduBrowser Setup Guide

## Overview

EduBrowser is a secure educational browser application with role-based access control (RBAC) and URL filtering. The browser connects to a MySQL database on Hostinger for authentication, whitelist/blacklist management, and activity logging.

## Architecture

```
┌─────────────────┐
│  PyQt6 Browser  │ (Local installation)
│   (Desktop App)  │
└────────┬────────┘
         │ Database Connection
         │
         ▼
┌─────────────────┐
│  MySQL Database  │ (Hostinger: u976383844_dces)
│  (Remote Access) │
└─────────────────┘
```

---

## Part 1: Database Setup on Hostinger

### Step 1.1: Access Hostinger Database

1. Log in to Hostinger hPanel
2. Go to **Databases** → **MySQL Databases**
3. Your database credentials:
   - **Database Name**: `u976383844_dces`
   - **Username**: `u976383844_abhi097`
   - **Password**: `!nN0v@tion113`
   - **Host**: `localhost` (for Hostinger basic hosting)

### Step 1.2: Enable Remote Access (Important)

1. In hPanel, go to **Databases** → **Remote MySQL**
2. Add your IP address or use `%` to allow all IPs (less secure but easier)
3. Note: Some Hostinger plans may not support remote access. Check with support if needed.

### Step 1.3: Initialize Database Schema

**Option A: Via phpMyAdmin (Recommended)**

1. Go to **Databases** → **phpMyAdmin**
2. Select database: `u976383844_dces`
3. Click **Import** tab
4. Upload `database/init_single_db.sql`
5. Click **Go**

**Option B: Via Local Script (Connects to Remote DB)**

1. Create `.env` file in project root:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=u976383844_abhi097
   DB_PASSWORD=!nN0v@tion113
   DB_NAME=u976383844_dces
   ```

2. Run setup scripts:
   ```bash
   python database/setup_databases.py
   python database/populate_sample_data.py
   python database/create_admin_quick.py
   ```

### Step 1.4: Verify Database Connection

Test from your local machine:
```bash
python database/testmysql.py
```

Or test with Python:
```python
from authentication import Authentication
auth = Authentication()
print("Connected successfully!")
```

---

## Part 2: Browser App Setup (Local Installation)

### Step 2.1: Install Dependencies

1. **Create virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```

### Step 2.2: Configure Environment

Create `.env` file in project root:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=u976383844_abhi097
DB_PASSWORD=!nN0v@tion113
DB_NAME=u976383844_dces
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
```

**Generate JWT Secret**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and use it for `JWT_SECRET`.

### Step 2.3: Run Browser App

```bash
python main.py
```

The app will:
1. Show login screen (Gmail OAuth or username/password)
2. Authenticate user against Hostinger database
3. Open browser with role-based access
4. Enforce whitelist/blacklist filtering based on user role and mode

---

## Part 3: User Roles and Features

### Roles

- **Super Admin**: Full system access, can manage all users and settings
- **Admin**: Institution-level access, can manage users and whitelist/blacklist
- **Teacher**: Can view student activity and manage class settings
- **Student**: Restricted browsing based on assigned mode

### Browser Modes (for Students)

- **Exam Mode**: Only whitelisted educational sites allowed
- **Study Mode**: Educational and research sites allowed
- **Restricted Mode**: Limited browsing with content filtering
- **Free Mode**: Unrestricted browsing (monitored)

### Features

- **Role-Based Login**: Authentication via database
- **Whitelist/Blacklist Filtering**: URL filtering based on database rules
- **Activity Logging**: All browsing activity logged to database
- **Violation Tracking**: Blocked access attempts are logged
- **Mode Enforcement**: Students can only access URLs allowed in their current mode

---

## Part 4: Configuration Summary

### Environment Variables (.env)

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=u976383844_abhi097
DB_PASSWORD=!nN0v@tion113
DB_NAME=u976383844_dces
JWT_SECRET=your-secret-key-here
```

### Database Connection

The browser connects directly to the Hostinger MySQL database using:
- Host: `localhost` (or the hostname provided by Hostinger)
- Port: `3306` (default MySQL port)
- User: `u976383844_abhi097`
- Database: `u976383844_dces`

---

## Part 5: Testing & Verification

### Test Database Connection

```bash
python -c "from authentication import Authentication; auth = Authentication(); print('Connected!')"
```

### Test Login

1. Run browser: `python main.py`
2. Login with test credentials (see `docs/test_users_credentials.txt`)
3. Verify role-based access works
4. Test URL filtering (for students)

### Test URL Filtering

1. Login as student
2. Try accessing blocked URLs
3. Verify whitelist/blacklist rules are enforced
4. Check violation logs in database

---

## Part 6: Troubleshooting

### Database Connection Failed

- **Check credentials**: Verify DB_USER, DB_PASSWORD, DB_NAME in `.env`
- **Check host**: Use `localhost` (not `db.abhinavpaudel.com`) for Hostinger basic hosting
- **Check remote access**: Ensure remote MySQL is enabled in Hostinger hPanel
- **Check firewall**: Some hosts require IP whitelisting
- **Check MySQL 8.0+**: If using MySQL 8.0+, ensure `allow_public_key_retrieval=True` is set (handled automatically)

### Login Fails

- **Check database**: Verify users exist in database
- **Check credentials**: Verify username/password in database
- **Check Gmail OAuth**: If using Gmail login, verify OAuth credentials are configured

### URL Filtering Not Working

- **Check mode**: Verify student mode is set correctly in database
- **Check whitelist/blacklist**: Verify entries exist in database
- **Check mode_enforcement.py**: Verify filtering logic is correct

### Browser Crashes

- **Check PyQt6**: Ensure PyQt6 and QWebEngine are installed correctly
- **Check Python version**: Requires Python 3.8+
- **Check dependencies**: Run `pip install -r requirements.txt` again

---

## Part 7: Production Checklist

- [ ] Database initialized with schema
- [ ] Database remote access enabled
- [ ] `.env` file configured with correct credentials
- [ ] JWT_SECRET generated and set
- [ ] Test users created in database
- [ ] Whitelist/blacklist entries configured
- [ ] Test login flow end-to-end
- [ ] Test URL filtering for students
- [ ] Test activity logging
- [ ] Test violation tracking

---

## Quick Reference Commands

### Setup Database
```bash
python database/setup_databases.py
python database/populate_sample_data.py
python database/create_admin_quick.py
```

### Test Database Connection
```bash
python database/testmysql.py
```

### Run Browser App
```bash
python main.py
```

### Create Admin User
```bash
python database/create_admin_quick.py
```

---

## Related Documentation

- **docs/PYTHON_APP_SETUP.md** – Configure the Python app to use the hosted API (`https://api.abhinavpaudel.com`), auth (POST /auth/login, Bearer token, X-Device-ID), and same JWT/DB as the PHP API; RBAC.
- **DASHBOARD_SETUP.md** – Configure the Qt app to open the web dashboard and align JWT with the backend.
- **BROWSER_SETUP.md** – Browser, CORS, extension, and API URL setup for the DCES dashboard and PHP API at `https://api.abhinavpaudel.com`.

---

## Support & Notes

- **Database**: Hostinger MySQL supports remote access (check your plan)
- **Browser**: Runs locally, no hosting needed
- **Security**: Keep JWT_SECRET secure, use strong passwords
- **Updates**: After changing database schema, update browser code accordingly

---

**Last Updated**: Browser-only setup with Hostinger database integration.

# Dashboard Setup Guide

## Overview

The dashboard is a web-based interface that talks to the **PHP API** at `https://api.abhinavpaudel.com` (Hostinger). It requires JWT token authentication. This guide explains how to configure the browser application and dashboard to connect to and authenticate with the API.

For browser, CORS, extension, and API URL setup, see **BROWSER_SETUP.md**.

## Prerequisites

- Dashboard is hosted and accessible at your domain
- Dashboard backend is configured to accept JWT tokens
- Browser application is installed and configured

---

## Step 1: Configure Environment Variables

### 1.1: Create or Update `.env` File

Create a `.env` file in the project root directory (or update existing one):

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=u976383844_abhi097
DB_PASSWORD=!nN0v@tion113
DB_NAME=u976383844_dces

# Dashboard Configuration
DASHBOARD_URL=https://api.abhinavpaudel.com

# JWT Secret Key (MUST MATCH DASHBOARD BACKEND!)
# Generate a secure key: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production

# Optional: Gmail OAuth (if using Gmail login)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 1.2: Generate JWT Secret Key

**IMPORTANT**: The `JWT_SECRET` must be the same in both:
- Browser application (qtapp `.env` file)
- PHP API backend (Hostinger: `php-api/config.php` or env `JWT_SECRET`)

Generate a secure JWT secret:

```bash
# Windows PowerShell
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Windows CMD
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Linux/Mac
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Example output:**
```
Xk9mP2qR7vT4wY8zA1bC3dE5fG6hI9jK0lM
```

Copy this value and use it for `JWT_SECRET` in:
1. Browser (qtapp) `.env` file
2. PHP API configuration on Hostinger (`php-api/config.php` or env)

---

## Step 2: Dashboard URL Configuration

### 2.1: Set Dashboard Base URL

The dashboard base URL is configured via the `DASHBOARD_URL` environment variable:

```env
DASHBOARD_URL=https://api.abhinavpaudel.com
```

**Supported formats:**
- `https://api.abhinavpaudel.com` (production)
- `http://localhost:8080` (local development)
- `https://dashboard.yourdomain.com` (custom domain)

### 2.2: Dashboard Paths

The browser automatically appends the correct path based on user role:

- **Admin**: `{DASHBOARD_URL}/dashboard-admin`
- **Super Admin**: `{DASHBOARD_URL}/dashboard-superadmin`
- **Teacher**: `{DASHBOARD_URL}/dashboard-teacher`

**Example URLs generated:**
```
https://api.abhinavpaudel.com/dashboard-admin?token=...&deviceId=...
https://api.abhinavpaudel.com/dashboard-superadmin?token=...&deviceId=...
https://api.abhinavpaudel.com/dashboard-teacher?token=...&deviceId=...
```

---

## Step 3: API Backend Configuration (PHP on Hostinger)

This project uses the **hosted PHP API only** at `https://api.abhinavpaudel.com`; no local Python/Flask API is run.

### 3.1: JWT Secret Configuration

Ensure the **PHP API** at `https://api.abhinavpaudel.com` uses the **same** `JWT_SECRET` as the browser application. Configure it in `php-api/config.php` (or via Hostinger env vars). The React dashboard calls this API using `VITE_API_URL=https://api.abhinavpaudel.com` (set at build time; see BROWSER_SETUP.md).

**For PHP (Hostinger API):**
- Set `jwt_secret` in `config.php` or `JWT_SECRET` in the environment so it matches the Qt app `.env`.

**For Node.js/Express (local dev only):**
```javascript
const jwt = require('jsonwebtoken');
const JWT_SECRET = process.env.JWT_SECRET || 'your-super-secret-jwt-key-change-this-in-production';

// Verify token
jwt.verify(token, JWT_SECRET, (err, decoded) => {
  if (err) {
    // Token invalid
  } else {
    // Token valid, use decoded.userId, decoded.username, decoded.role
  }
});
```

**For Python/Flask:**
```python
import jwt
import os

JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-this-in-production")

# Verify token
try:
    decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    user_id = decoded.get("userId") or decoded.get("user_id")
    username = decoded.get("username")
    role = decoded.get("role")
except jwt.ExpiredSignatureError:
    # Token expired
except jwt.InvalidTokenError:
    # Token invalid
```

### 3.2: Token Validation

The dashboard should:

1. **Extract parameters from URL:**
   ```javascript
   const urlParams = new URLSearchParams(window.location.search);
   const token = urlParams.get('token');
   const deviceId = urlParams.get('deviceId');
   ```

2. **Validate token:**
   - Check token format (JWT has 3 parts separated by dots)
   - Verify signature using `JWT_SECRET`
   - Check expiration (`exp` field)
   - Extract user info: `userId`, `username`, `role`

3. **Store in localStorage:**
   ```javascript
   localStorage.setItem('dashboard_token', token);
   localStorage.setItem('device_id', deviceId);
   ```

### 3.3: Expected Token Payload

The browser generates tokens with this structure:

```json
{
  "userId": 123,
  "user_id": 123,
  "username": "john_doe",
  "role": "admin",
  "iat": 1735603200,
  "exp": 1735689600
}
```

**Role values:**
- `"super-admin"` (for superadmin users)
- `"admin"` (for admin users)
- `"teacher"` (for teacher users)
- `"student"` (for student users - cannot access dashboard)

---

## Step 4: Testing the Setup

### 4.1: Test Browser Connection

1. **Start the browser application:**
   ```bash
   python main.py
   ```

2. **Login as admin/teacher/superadmin**

3. **Click the Dashboard button** (visible only for admin/teacher/superadmin)

4. **Check browser console** (if dashboard fails to load):
   - Open browser DevTools (F12)
   - Check Console tab for errors
   - Check Network tab for failed requests

### 4.2: Verify Token Generation

Test token generation manually:

```python
from authentication import Authentication
from datetime import datetime

auth = Authentication()
token = auth.generate_token(
    username="test_admin",
    role="admin",
    user_id=1
)

print(f"Generated token: {token}")
print(f"Token length: {len(token)}")
```

### 4.3: Test Dashboard URL

Construct and test the dashboard URL:

```python
import urllib.parse
from dashboard_window import DashboardWindow

# This will be done automatically when opening dashboard
# But you can test manually:

token = "your-jwt-token-here"
device_id = "test-device-123"
base_url = "https://api.abhinavpaudel.com"
dashboard_path = "dashboard-admin"

url = f"{base_url}/{dashboard_path}?token={urllib.parse.quote(token)}&deviceId={urllib.parse.quote(device_id)}"
print(f"Dashboard URL: {url}")
```

---

## Step 5: Troubleshooting

### Issue: "Missing required user information"

**Cause:** User not logged in or session expired

**Solution:**
1. Log out and log back in
2. Ensure you're logged in as admin, teacher, or superadmin

### Issue: "Failed to generate dashboard URL"

**Cause:** Token generation failed

**Solution:**
1. Check `JWT_SECRET` is set in `.env`
2. Verify `python-dotenv` is installed: `pip install python-dotenv`
3. Check `.env` file is in project root

### Issue: Dashboard shows "Missing authentication credentials"

**Cause:** Token or deviceId not in URL

**Solution:**
1. Check dashboard URL in browser address bar
2. Verify URL contains `?token=...&deviceId=...`
3. Check `DASHBOARD_URL` environment variable is correct

### Issue: Dashboard shows "Session expired"

**Cause:** Token expiration time (`exp`) is in the past

**Solution:**
1. Tokens expire after 24 hours
2. Close and reopen dashboard to generate new token
3. Check system clock is correct

### Issue: "Invalid or expired token" / Backend verification failed / Failed to fetch (students, stats, etc.)

**Cause:** The PHP API at api.abhinavpaudel.com rejects the token. Almost always **JWT_SECRET mismatch**: the Qt app signs the token with `JWT_SECRET` from its `.env`; the PHP API verifies with `jwt_secret` from its config. They must be **identical**.

**Solution:**
1. In qtapp `.env`, set `JWT_SECRET` to the **exact same** value as in the PHP API on Hostinger (`php-api/config.php` or `JWT_SECRET` env).
2. If you don’t have `JWT_SECRET` in `.env`, the Qt app uses a default and the API will reject the token.
3. Restart the Qt app after changing `.env`, then log in again and open the dashboard (new token will be generated).

**Step-by-step:** See **docs/JWT_SECRET_MATCH.md** for how to generate one secret and set it in both the Qt app and the PHP API.

### Issue: Dashboard shows "Token verification failed"

**Cause:** JWT_SECRET mismatch between browser app and API backend

**Solution:**
1. Verify `JWT_SECRET` in qtapp `.env` matches the PHP API (api.abhinavpaudel.com) config exactly
2. Restart the Qt app after changing the secret
3. Generate new token (logout and login again, then open dashboard)

### Issue: Dashboard shows "User: Not loaded, Role: Not set"

**Cause:** Token payload missing required fields

**Solution:**
1. Verify token contains `userId`, `username`, `role`
2. Check token is valid JWT (3 parts separated by dots)
3. Decode token to verify payload structure

### Issue: Wrong dashboard path (e.g., admin sees teacher dashboard)

**Cause:** Role mapping issue

**Solution:**
1. Check user role in database
2. Verify role is one of: `admin`, `superadmin`, `teacher`
3. Role mapping:
   - `superadmin` → `dashboard-superadmin`
   - `admin` → `dashboard-admin`
   - `teacher` → `dashboard-teacher`

---

## Step 6: Security Best Practices

### 6.1: JWT Secret Security

- **Never commit** `JWT_SECRET` to version control
- Use strong, randomly generated secrets (32+ characters)
- Use different secrets for development and production
- Rotate secrets periodically

### 6.2: HTTPS in Production

- Always use HTTPS for dashboard URLs in production
- Never pass tokens over HTTP in production
- Use SSL/TLS certificates for your domain

### 6.3: Token Expiration

- Tokens expire after 24 hours (configurable)
- Implement token refresh mechanism if needed
- Logout users when token expires

### 6.4: Device ID

- Device ID should be persistent per device
- Use UUID format for device IDs
- Store device ID securely (not in plain text)

---

## Step 7: Environment Variables Summary

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DASHBOARD_URL` | Base URL where the React dashboard is served (Qt app opens this) | `https://api.abhinavpaudel.com` or `https://www.abhinavpaudel.com` |
| `VITE_API_URL` | API base URL for React dashboard build (PHP API on Hostinger) | `https://api.abhinavpaudel.com` |
| `JWT_SECRET` | Secret key for JWT signing (must match Qt app and PHP API) | `Xk9mP2qR7vT4wY8zA1bC3dE5fG6hI9jK0lM` |

### Optional Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | `123456789.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | `GOCSPX-abc123...` |

---

## Quick Setup Checklist

- [ ] `.env` file created in project root (see `env.example`)
- [ ] `DASHBOARD_URL` set to where the React dashboard is served
- [ ] `VITE_API_URL=https://api.abhinavpaudel.com` for production dashboard build
- [ ] `JWT_SECRET` generated and set (same in Qt app and PHP API)
- [ ] PHP API on Hostinger configured with same `JWT_SECRET`
- [ ] Tested login as admin/teacher/superadmin
- [ ] Dashboard opens successfully with authentication
- [ ] Token and deviceId appear in dashboard URL
- [ ] Dashboard displays user information correctly
- [ ] For browser/extension/CORS, see **BROWSER_SETUP.md**

---

## Additional Resources

- **JWT.io**: https://jwt.io (for token debugging)
- **Python JWT Library**: https://pyjwt.readthedocs.io/
- **Environment Variables**: See `env.example` for template

---

## Support

If you encounter issues:

1. Check browser console for errors
2. Verify `.env` file is loaded correctly
3. Test token generation manually
4. Verify dashboard backend logs
5. Check network requests in browser DevTools

For more help, refer to the main `SETUP_GUIDE.md`.

# Browser Setup for the DCES Dashboard

This describes how your browser (and any related extensions/apps) must be set up so they work with the dashboard and **https://api.abhinavpaudel.com** (PHP API on Hostinger).

---

## 1. API Base URL

The extension/app that sends data (activity, violations, mode, etc.) must call the Hostinger API, not localhost:

| Environment | API base URL |
|-------------|--------------|
| **Production** | `https://api.abhinavpaudel.com` |

Paths the dashboard and extension typically call:

- `POST /auth/login`
- `POST /api/auth/verify-token`
- `GET /api/students`
- `POST /api/students/{id}/mode`
- `GET /api/activity`
- `GET /api/violations`
- Plus any endpoints used for reporting visits/blocking.

**Browser setup includes:** setting the extension’s/config’s API base URL to `https://api.abhinavpaudel.com` (no trailing slash).

---

## 2. Allowed Origins (CORS)

The PHP API allows requests from:

- The **dashboard origin** (e.g. `https://abhinavpaudel.com`, `https://www.abhinavpaudel.com`, or wherever you host the React app).
- **Local dev:** `http://localhost:5173`, `http://localhost:3000`, etc.

**What you need to do:**

1. If the dashboard is on `https://www.abhinavpaudel.com`, the API’s CORS must allow that origin.
2. The PHP API currently uses `Access-Control-Allow-Origin: *`. For production you should change it to the exact dashboard origin in `php-api/index.php` (and `.htaccess` if used).
3. **Extension:**  
   - If the extension calls the API from a content script or web page, the API must allow that origin.  
   - If the extension uses a background service worker and calls `fetch('https://api.abhinavpaudel.com/...')`, the request is from the extension origin; add `chrome-extension://YOUR_EXTENSION_ID` to the API’s allowed origins, or keep `*` during development and restrict later.

**Browser setup includes:** knowing where the dashboard and extension run, and configuring the API’s CORS so those origins are allowed.

---

## 3. Cookies and Storage (Dashboard Login)

The dashboard stores JWT and `deviceId` in **localStorage** (see `src/lib/auth.ts`).

- This is same-origin to the site that hosts the dashboard (e.g. `https://www.abhinavpaudel.com`).
- Use **HTTPS** for dashboard and API in production so cookies/storage are not blocked as insecure.
- If dashboard and API are on different subdomains (e.g. `www.abhinavpaudel.com` vs `api.abhinavpaudel.com`):
  - Storing the token in localStorage and sending it in the `Authorization` header is fine and does not depend on cookies.
- No special “browser cookie setup” is required for the API as long as you use the `Authorization: Bearer <token>` header.
- Ensure the browser is not in “block all cookies” or “block third‑party cookies” in a way that breaks your dashboard origin (usually not an issue for same-site + API on subdomain).

**Browser setup:** HTTPS everywhere; no need to change cookie settings if you rely on localStorage + Authorization header.

---

## 4. Extension ↔ API (Students, Activity, Violations)

For a browser extension that reports student activity/visits and violations:

| Item | Requirement |
|------|-------------|
| **API URL** | Set its config/build-time “API base URL” to `https://api.abhinavpaudel.com` (no trailing slash). |
| **Authentication** | If the extension calls protected endpoints, send the same auth as the dashboard: `Authorization: Bearer <token>` and optionally `X-Device-ID`. |
| **Manifest** | In `manifest.json`, include: `"host_permissions": ["https://api.abhinavpaudel.com/*"]` (or broader `"https://*/*"` if needed; narrow when possible). |
| **Content Security Policy** | If the extension or dashboard define a CSP, allow `https://api.abhinavpaudel.com` in `connect-src` (and `frame-src`/`form-action` only if used). Example: `connect-src 'self' https://api.abhinavpaudel.com;` |
| **Mixed content** | Serve dashboard and API over HTTPS. Avoid loading the dashboard over HTTPS and calling `http://api...`; browsers will block mixed content. |

---

## 5. Recommended Browser Settings (for Clients)

- **JavaScript:** Enabled (required for the React dashboard and typical extensions).
- **Cookies:** Allowed for your dashboard domain (and API domain if you ever use cookies there).
- **Third-party cookies:** Only relevant if you embed the dashboard in an iframe on another site; for a normal tab, default settings are usually enough.
- **Do Not Track / strict privacy modes:** These do not usually block `fetch` to `api.abhinavpaudel.com` or localStorage on the dashboard origin; if you use a very strict mode, test login and one API call.

---

## 6. Checklist – “Browser Setup to Work With This”

| Item | Action |
|------|--------|
| **Dashboard URL** | Use HTTPS (e.g. `https://www.abhinavpaudel.com` or `https://api.abhinavpaudel.com`). |
| **API URL** | Use `https://api.abhinavpaudel.com` everywhere (dashboard env and extension config). |
| **Dashboard env** | `VITE_API_URL=https://api.abhinavpaudel.com` for production build. |
| **Extension API base** | Set to `https://api.abhinavpaudel.com`. |
| **Extension manifest** | `host_permissions` includes `https://api.abhinavpaudel.com/*`. |
| **CORS on API** | Allow the dashboard origin (and extension origin if it calls the API from a web/extension context). |
| **Auth** | Use `Authorization: Bearer <token>` (and `X-Device-ID` if needed); no special browser cookie config required. |
| **CSP** | If you use CSP, allow `https://api.abhinavpaudel.com` in `connect-src`. |

---

## 7. Quick Test From the Browser

**Dashboard:**

1. Open the dashboard, log in, open DevTools → Network.
2. Confirm requests go to `https://api.abhinavpaudel.com` (e.g. `/auth/login`, `/api/auth/verify-token`, `/api/stats`).

**Extension:**

1. With the extension installed and configured to use `https://api.abhinavpaudel.com`, trigger an action that should hit the API (e.g. sync mode, send activity).
2. In DevTools (background page or options page), check that those requests target `https://api.abhinavpaudel.com` and return 2xx (or the expected error codes).

---

## 8. Where This Is Configured in This Repo

| Component | Location | Variable / Config |
|-----------|----------|-------------------|
| Qt desktop app (opens dashboard) | `qtapp/env.example`, `qtapp/dashboard_window.py` | `DASHBOARD_URL` (default `https://api.abhinavpaudel.com`) |
| Python app calling the API | `qtapp/env.example`, `qtapp/docs/PYTHON_APP_SETUP.md` | `API_BASE_URL=https://api.abhinavpaudel.com` |
| React dashboard build | `Browser_dashboard/react-dashboard/.env.example`, `.env.production` | `VITE_API_URL=https://api.abhinavpaudel.com` |
| PHP API (Hostinger) | `Browser_dashboard/react-dashboard/php-api/` | CORS in `index.php` / `.htaccess`; `config.php` for DB and JWT |
| JWT secret | Qt app `.env` and PHP API `config.php` | `JWT_SECRET` (must match) |

For dashboard deployment and token flow, see **DASHBOARD_SETUP.md**. For Python app and hosted API, see **docs/PYTHON_APP_SETUP.md**.

