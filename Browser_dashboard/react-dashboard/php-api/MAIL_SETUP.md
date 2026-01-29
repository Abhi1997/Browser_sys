# Email setup for forgot-password (Hostinger)

The API sends password-reset emails using PHP. You can use **PHP mail()** (default) or **SMTP**. Set **MAIL_FROM** (or **mail_from** in config) to your desired sender address.

---

## 1. Set the sender address (MAIL_FROM)

The “From” address in reset emails is controlled by **mail_from** in config or the **MAIL_FROM** environment variable.

### Option A: config.local.php (recommended on Hostinger)

1. On the server, in the **php-api** folder, create or edit **config.local.php** (copy from **config.example.php** if needed).
2. Set **mail_from** to an address on your domain (better deliverability):

   ```php
   return [
       // ... other keys (db, jwt_secret, etc.) ...
       'mail_from' => 'noreply@abhinavpaudel.com',
       'dashboard_base_url' => 'https://abhinavpaudel.com',
   ];
   ```

3. Use an address that exists on your hosting (e.g. create **noreply@abhinavpaudel.com** in Hostinger **Emails** so the server can send as that address).

### Option B: Environment variable (if your plan supports it)

1. In **Hostinger hPanel** → **Advanced** → **Environment variables** (or the equivalent for your plan).
2. Add:
   - **Name:** `MAIL_FROM`
   - **Value:** `noreply@abhinavpaudel.com` (or your chosen sender)
3. Save. The API will use this (see **config.php**).

---

## 2. Use PHP mail() (default)

The code uses PHP’s **mail()** with the headers:

- **From:** value of **mail_from** / **MAIL_FROM**
- **Reply-To:** same as From
- **Content-Type:** text/plain; charset=UTF-8

On Hostinger, **mail()** usually works if:

- You use a **From** address that is a real mailbox or alias on your domain (e.g. **noreply@abhinavpaudel.com**).
- You created that address in hPanel → **Emails** (or it’s the main account email).

If reset emails are not received:

1. Check **Spam/Junk**.
2. In hPanel → **Emails**, ensure the sender address exists and is active.
3. Try sending a test email from Hostinger’s “Email” or “File Manager” test feature to confirm **mail()** works.

---

## 3. Optional: use SMTP (if mail() doesn’t work)

If **mail()** fails or emails don’t arrive, use Hostinger’s SMTP.

### Step 1: Get SMTP details from Hostinger

1. In **hPanel** → **Emails** → choose your domain.
2. Create or select a mailbox (e.g. **noreply@abhinavpaudel.com**).
3. Note:
   - **SMTP server:** e.g. `smtp.hostinger.com`
   - **Port:** 587 (TLS) or 465 (SSL)
   - **Username:** full email (e.g. `noreply@abhinavpaudel.com`)
   - **Password:** the mailbox password

### Step 2: Add SMTP config (config.local.php)

In **config.local.php** add (with your real values):

```php
'smtp_host'     => 'smtp.hostinger.com',
'smtp_port'     => 587,
'smtp_secure'   => 'tls',
'smtp_username' => 'noreply@abhinavpaudel.com',
'smtp_password' => 'your-mailbox-password',
```

### Step 3: Use the SMTP mail helper

The API can use a small SMTP helper when these keys are set. If you have a **sendMail** helper that uses **smtp_*** from config, the forgot-password handler will use it instead of **mail()** once you add the helper (see below).

---

## 4. Quick checklist

- [ ] **mail_from** or **MAIL_FROM** set to your sender (e.g. `noreply@abhinavpaudel.com`).
- [ ] Sender address exists in Hostinger **Emails** (or is the account email).
- [ ] **dashboard_base_url** is correct (used for the reset link in the email).
- [ ] If using SMTP: **smtp_*** keys set in **config.local.php** and **sendMail()** implemented/used.

---

## 5. Test

1. Trigger “Forgot password” from the Qt app or dashboard with a user whose **gmail** (registered email) is set.
2. Check inbox and spam for the reset email.
3. Open the link and set a new password to confirm the full flow.

If nothing arrives, check Hostinger’s mail logs (if available) and that **mail_from** / **MAIL_FROM** matches a valid sender on your domain.
