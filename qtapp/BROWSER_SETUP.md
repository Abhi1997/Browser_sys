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
