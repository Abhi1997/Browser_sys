# Forgot Password

Users can request a password reset link to their **registered email** (the `gmail` field in the Users table). The reset link opens the dashboard at **abhinavpaudel.com/reset-password?token=...** where they set a new password.

---

## Flow

1. **Request reset** – User clicks "Forgot password?" on the Qt login screen (or opens **abhinavpaudel.com/forgot-password**), enters their registered email, and submits.
2. **API** – The PHP API at **api.abhinavpaudel.com** looks up the user by email (`gmail`), creates a one-time token (expires in 1 hour), stores it in **PasswordResetTokens**, and sends an email with the reset link.
3. **Reset** – User opens the link in the email, lands on **abhinavpaudel.com/reset-password?token=...**, enters a new password and confirms. The API validates the token, updates the user’s password, and deletes the token.

---

## Database

The API uses a **PasswordResetTokens** table. If your Hostinger database was created from an older schema, add it by running:

**qtapp/database/add_password_reset_table.sql**

(e.g. in phpMyAdmin: Import or run the SQL). The table is also defined in **init_single_db.sql** for new installs.

---

## Email

The PHP API sends the reset email using **mail()** by default, or **SMTP** if you set SMTP options in config.

- **Sender:** Set **MAIL_FROM** (env) or **mail_from** in **config.local.php** to your sender (e.g. `noreply@abhinavpaudel.com`). Use an address that exists in Hostinger **Emails** for better deliverability.
- **SMTP (optional):** If `mail()` doesn’t work on Hostinger, set **smtp_host**, **smtp_port**, **smtp_username**, **smtp_password** (and **smtp_secure**: `tls`) in **config.local.php**; the API will send via SMTP instead.

**Full steps:** See **Browser_dashboard/react-dashboard/php-api/MAIL_SETUP.md** for step-by-step MAIL_FROM and SMTP setup on Hostinger.

The reset link uses **dashboard_base_url** (default `https://abhinavpaudel.com`). Set **DASHBOARD_BASE_URL** or **dashboard_base_url** in config if your dashboard is on a different URL.

---

## Where it’s implemented

| Part | Location |
|------|----------|
| Qt app "Forgot password?" | **gmail_oauth.py** – link and dialog that call the API |
| API endpoints | **php-api/handlers/auth.php** – `auth_forgot_password`, `auth_reset_password` |
| API routes | **php-api/index.php** – `api/auth/forgot-password`, `api/auth/reset-password` |
| Dashboard pages | **react-dashboard/src/pages** – ForgotPassword.tsx, ResetPassword.tsx |
| Dashboard routes | **App.tsx** – `/forgot-password`, `/reset-password` |

Users must have a **registered email** (gmail) in the database; otherwise the API does not send an email but still returns success (to avoid revealing whether the email exists).
