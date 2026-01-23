# Dashboard Setup Guide

## Overview

The dashboard is a web-based interface hosted at `api.abhinavpaudel.com` that requires JWT token authentication. This guide explains how to configure the browser application to connect to and authenticate with the dashboard.

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
- Browser application (`.env` file)
- Dashboard backend (server configuration)

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
1. Browser `.env` file
2. Dashboard backend configuration (server-side)

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

## Step 3: Dashboard Backend Configuration

### 3.1: JWT Secret Configuration

Ensure your dashboard backend uses the **same** `JWT_SECRET` as the browser application.

**For Node.js/Express:**
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

### Issue: Dashboard shows "Token verification failed"

**Cause:** JWT_SECRET mismatch between browser and dashboard

**Solution:**
1. Verify `JWT_SECRET` in browser `.env` matches dashboard backend
2. Restart both browser app and dashboard server after changing secret
3. Generate new token (logout and login again)

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
| `DASHBOARD_URL` | Base URL for dashboard | `https://api.abhinavpaudel.com` |
| `JWT_SECRET` | Secret key for JWT signing | `Xk9mP2qR7vT4wY8zA1bC3dE5fG6hI9jK0lM` |

### Optional Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | `123456789.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | `GOCSPX-abc123...` |

---

## Quick Setup Checklist

- [ ] `.env` file created in project root
- [ ] `DASHBOARD_URL` set to your dashboard domain
- [ ] `JWT_SECRET` generated and set (same in browser and dashboard)
- [ ] Dashboard backend configured to use same `JWT_SECRET`
- [ ] Dashboard backend validates JWT tokens correctly
- [ ] Tested login as admin/teacher/superadmin
- [ ] Dashboard opens successfully with authentication
- [ ] Token and deviceId appear in dashboard URL
- [ ] Dashboard displays user information correctly

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
