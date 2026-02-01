# Where to Check Hostinger API Logs

When the dashboard shows "Request failed: 500" or data is static/empty, the PHP API on **api.abhinavpaudel.com** is returning errors. Use the steps below to find the cause.

---

## 1. Use the debug endpoint (easiest)

After deploying the updated PHP API, open in your browser:

- **https://api.abhinavpaudel.com/api/debug**  
  or  
- **https://api.abhinavpaudel.com/debug**

You’ll get a JSON response like:

- `config_loaded: true`, `db_connected: true` → API and DB are OK; 500 may be from auth or another handler.
- `error: "db: ..."` → Database connection failed (wrong host/user/password/database in config).
- `error: "config: ..."` → Config file or env problem.

Fix whatever the `error` field says (e.g. wrong DB credentials in `config.local.php` or Hostinger env).

---

## 2. Where Hostinger stores error logs

1. Log in to **hPanel** (Hostinger).
2. Open **File Manager**.
3. Enable **“Access all files of your web hosting”** (or similar) so you can see hidden folders.
4. Go to the **`.logs`** folder (often at the root of your hosting account).
5. Open the file named **`error_log_`** + your **subdomain** (e.g. `error_log_api.abhinavpaudel.com` or `error_log_api`).

That file contains PHP errors (warnings, notices, fatals). When a request returns 500, the corresponding PHP error is usually logged there.

---

## 3. Enable PHP error logging (if the log is empty)

1. In hPanel go to **Advanced** → **PHP Configuration** (or **PHP Info**).
2. Ensure **error logging** is enabled (e.g. `log_errors = On`).
3. Optional: set **display_errors = Off** in production so errors go only to the log, not to the browser.

After enabling, trigger the 500 again (e.g. open the teacher dashboard); then refresh the `error_log_*` file to see the new entry.

---

## 4. "syntax error, unexpected identifier \"mail_from\", expecting \"]\""

This is a **PHP parse error** in **config.local.php** (or the main config) on Hostinger. It means a **missing comma** before the `'mail_from'` line.

**Fix:** On Hostinger, open **php-api/config.local.php** and ensure **every array entry has a comma** at the end (except the last). For example:

```php
return [
    'db' => [ ... ],
    'jwt_secret' => '...',
    'dashboard_base_url' => 'https://abhinavpaudel.com',   // ← comma required
    'mail_from' => 'noreply@abhinavpaudel.com',
];
```

Add the missing comma on the line **above** `'mail_from'` (e.g. after `'jwt_secret'` or `'dashboard_base_url'`), save, and try the API again.

---

## 5. Quick checklist for 500 on api.abhinavpaudel.com

- [ ] Open **https://api.abhinavpaudel.com/api/debug** (or **/debug**) and read the `error` field.
- [ ] In **.logs**, check **error_log_*** for the API subdomain after a 500 request.
- [ ] If error says **"syntax error... mail_from"**: add missing comma in **config.local.php** (see section 4 above).
- [ ] In **config.local.php** (or Hostinger env), confirm **DB** host, user, password, database name.
- [ ] Confirm **JWT_SECRET** matches the Qt app `.env` (if it doesn’t, you usually get **401**, not 500).
- [ ] Redeploy **index.php**, **helpers.php**, and **handlers/stats.php** so the debug endpoint and error handling are live.
- [ ] If you see **"syntax error... mail_from"** in the dashboard/API: fix **config.local.php** on Hostinger (add missing comma before `'mail_from'`).

---

## Links

- [Hostinger: Where to find your website’s error logs](https://support.hostinger.com/en/articles/1583298-where-to-find-your-website-s-error-logs)
- [Hostinger: How to enable PHP error messages](https://support.hostinger.com/support/4259219-how-to-turn-on-php-error-messages-in-hpanel)
