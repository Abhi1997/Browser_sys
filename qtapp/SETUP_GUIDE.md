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
