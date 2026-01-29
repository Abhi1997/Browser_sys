# DCES Dashboard – Hostinger Deployment Guide

This guide covers deploying the React dashboard and PHP API on Hostinger using the **api.abhinavpaudel.com** subdomain for the API.

---

## 1. Overview

| Component | Where it runs | URL |
|-----------|----------------|-----|
| **Dashboard** (React) | Main domain or www | e.g. `https://www.abhinavpaudel.com` or `https://abhinavpaudel.com` |
| **API** (PHP) | Subdomain | `https://api.abhinavpaudel.com` |

The dashboard is a static build; the API is PHP that connects to your existing MySQL database.

---

## 2. Deploy the PHP API (api.abhinavpaudel.com)

### 2.1 Subdomain and document root

1. In **Hostinger hPanel**: **Domains** → **api.abhinavpaudel.com** (or **Subdomains**).
2. Ensure the subdomain points to your hosting and note its **document root** (e.g. `domains/api.abhinavpaudel.com/public_html` or `public_html/api`).

### 2.2 Upload PHP API files

Upload the contents of the `php-api/` folder into that document root so you have:

```
<document_root>/
├── .htaccess
├── index.php
├── config.php
├── config.example.php
├── helpers.php
└── handlers/
    ├── auth.php
    ├── stats.php
    ├── users.php
    ├── students.php
    ├── activity.php
    ├── violations.php
    ├── whitelist.php
    ├── blacklist.php
    ├── notifications.php
    └── export.php
```

**Do not** put the React app inside the API document root.

### 2.3 Configure database and JWT

**Option A – `config.local.php` (recommended on shared hosting)**

1. Copy `config.example.php` to `config.local.php` in the same folder.
2. Edit `config.local.php` and set:
   - `db.password` – your MySQL password
   - `jwt_secret` – same secret you use in the Python backend (must match for tokens to work)

**Option B – Environment variables**

If your Hostinger plan supports env vars for this domain, set:

- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`
- `JWT_SECRET`

Use the same values as in your Python backend so the PHP API talks to the same DB and accepts the same JWTs.

### 2.4 PHP version

In hPanel, set PHP to **8.0** or **8.1** for this (sub)domain and ensure **pdo_mysql**, **json**, and **mbstring** are enabled.

### 2.5 Test the API

- Open: `https://api.abhinavpaudel.com/health`  
- Expected: `{"status":"ok","message":"Backend API is running"}`

If you see that, the API is live.

---

## 3. Deploy the Dashboard (React)

### 3.1 Production build

From the project root:

```bash
cd react-dashboard
npm install
npm run build
```

This uses `.env.production`, which sets `VITE_API_URL=https://api.abhinavpaudel.com`, so the built app will call your API subdomain. For custom builds, copy `.env.example` to `.env` and set `VITE_API_URL` to your API base URL (no trailing slash).

### 3.2 Upload the build

1. In Hostinger, open the **document root** of the site where the dashboard should run (e.g. main domain or www).
2. Upload the **contents** of `react-dashboard/dist/` into that root, e.g.:
   - `index.html`
   - `assets/` (folder)
   - `favicon.ico`, `robots.txt`, etc.

So the dashboard is served from the same domain (or www), and the API from `https://api.abhinavpaudel.com`.

### 3.3 SPA routing (optional)

If your dashboard uses client-side routing (e.g. React Router), copy `react-dashboard/public/.htaccess` into the dashboard document root so that non-file requests are redirected to `index.html`. Your existing `public/.htaccess` already does this.

---

## 4. Python “browser” app (your application with RBAC)

Your Python application (the “browser” with RBAC) must call the **hosted** API in production:

- Set **API base URL** to: `https://api.abhinavpaudel.com`
- Use the same auth as the dashboard: `POST /auth/login` with `username`, `password`, `deviceId`; then send `Authorization: Bearer <token>` and `X-Device-ID` on all other requests.
- Use the same JWT secret and DB as the PHP API so tokens and users stay in sync.

See the Python app’s **docs/PYTHON_APP_SETUP.md** (in the qtapp repository) for RBAC and Python app configuration, or **BROWSER_SETUP.md** in qtapp for browser/API setup.

---

## 5. Testing the API with Postman

A Postman collection and guide are provided for testing all API endpoints:

- **Collection:** `php-api/postman/DCES-API.postman_collection.json`
- **Guide:** [docs/POSTMAN_GUIDE.md](docs/POSTMAN_GUIDE.md)

Import the collection, set `base_url` to `https://api.abhinavpaudel.com`, run **Auth → Login** with your credentials, then use the other requests. The guide explains variables, headers, body examples, and common errors.

---

## 6. Checklist

| Step | Action |
|------|--------|
| 1 | Create/point subdomain **api.abhinavpaudel.com** to your Hostinger account |
| 2 | Upload **php-api/** contents into that subdomain’s document root |
| 3 | Add **config.local.php** (or env vars) with DB password and JWT secret |
| 4 | Set PHP 8.0/8.1 and test **https://api.abhinavpaudel.com/health** |
| 5 | Run **npm run build** in `react-dashboard` (uses `.env.production`) |
| 6 | Upload **dist/** contents into the dashboard document root |
| 7 | Point the Python app at **https://api.abhinavpaudel.com** and same JWT secret |

---

## 7. Troubleshooting

- **404 on API routes**  
  Ensure `.htaccess` is uploaded and `mod_rewrite` is on. The rule sends all requests to `index.php`.

- **CORS errors**  
  The PHP API sends `Access-Control-Allow-Origin: *`. If you later restrict this, add your dashboard origin (e.g. `https://www.abhinavpaudel.com`).

- **“Invalid or expired token”**  
  `JWT_SECRET` in PHP must match the one used to create the token (e.g. in your Python backend or when logging in via the dashboard).

- **DB connection errors**  
  Check `config.local.php` or env vars: host, user, password, database name. Hostinger typically uses a host like `srvXXXX.hstgr.io` for MySQL.

- **Export not available**  
  The PHP API returns 501 for `POST /export/db`. Use the Python backend if you need DB export from the dashboard.
