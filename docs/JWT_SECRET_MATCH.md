# How to Match JWT_SECRET (Qt App ↔ PHP API)

The Qt app and the PHP API at **api.abhinavpaudel.com** must use the **exact same** JWT secret. If they don’t, the dashboard gets "Invalid or expired token" and API calls fail.

---

## Option A: Set the same new secret in both places (recommended)

Use one secret everywhere.

### Step 1: Generate a secret (once)

In a terminal, from the **qtapp** folder:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Example output: `Xk9mP2qR7vT4wY8zA1bC3dE5fG6hI9jK0lM`

Copy that value (your output will be different).

### Step 2: Put it in the Qt app

1. Open **qtapp/.env**.
2. Set:
   ```env
   JWT_SECRET=<paste the value from Step 1>
   ```
   Example:
   ```env
   JWT_SECRET=Xk9mP2qR7vT4wY8zA1bC3dE5fG6hI9jK0lM
   ```
3. Save the file.

### Step 3: Put the same value in the PHP API on Hostinger

**If you use config.local.php on the server:**

1. On Hostinger, open the file that overrides config (e.g. **php-api/config.local.php**).
2. Set:
   ```php
   'jwt_secret' => 'Xk9mP2qR7vT4wY8zA1bC3dE5fG6hI9jK0lM',
   ```
   (Use the **exact same** string you put in qtapp/.env.)
3. Save and upload if you edit locally.

**If Hostinger lets you set environment variables:**

1. In hPanel (or your hosting env vars), add:
   - Name: `JWT_SECRET`
   - Value: the same string as in qtapp/.env
2. Save. The PHP API will use this (see php-api/config.php).

**If you only have the default config.php:**

1. Edit **php-api/config.php** on the server.
2. In the `$defaults` array, set:
   ```php
   'jwt_secret' => 'Xk9mP2qR7vT4wY8zA1bC3dE5fG6hI9jK0lM',
   ```
   (Same value as in qtapp/.env.)
3. Save.

### Step 4: Restart and test

1. Restart the Qt app (so it reloads .env).
2. Log in again and open the dashboard (a new token is generated).
3. The dashboard should load and API calls should work.

---

## Option B: Copy from PHP API → Qt app

If the PHP API **already** has a secret and you want the Qt app to match:

1. On Hostinger, open **php-api/config.php** or **config.local.php** (or check the **JWT_SECRET** env var).
2. Copy the **exact** `jwt_secret` value (the string in quotes).
3. In **qtapp/.env**, set:
   ```env
   JWT_SECRET=<that exact value>
   ```
4. Save .env, restart the Qt app, then log in again and open the dashboard.

---

## Option C: Copy from Qt app → PHP API

If **qtapp/.env** already has the correct `JWT_SECRET` and you want the PHP API to match:

1. Open **qtapp/.env** and copy the value of `JWT_SECRET` (no spaces, one line).
2. On Hostinger, set that same value in the PHP API:
   - In **config.local.php**: `'jwt_secret' => 'paste-here',`
   - Or in the **JWT_SECRET** environment variable.
3. Save. Restart the Qt app, log in again, and open the dashboard.

---

## Checklist

- [ ] Same string in **qtapp/.env** (`JWT_SECRET=...`) and in **PHP API** (`jwt_secret` or `JWT_SECRET`).
- [ ] No extra spaces or quotes in .env (e.g. `JWT_SECRET=abc123` not `JWT_SECRET = "abc123"`).
- [ ] **Only the raw secret string** in .env—no PHP code (e.g. not `'jwt_secret' => getenv(...)`). The Qt app will try to recover from a pasted PHP line, but for reliability use just the secret.
- [ ] Qt app restarted after changing .env.
- [ ] New token: log in again and open the dashboard after changing the secret.

---

## Quick test

After matching:

1. Run the Qt app, log in, open the dashboard.
2. If you still see "Invalid or expired token", the two secrets still differ—double-check the string in both places (no typos, same encoding).
