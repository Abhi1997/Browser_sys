# PHP config syntax – "mail_from" error

If the API returns **500** and the error message says:

**syntax error, unexpected identifier "mail_from", expecting "]"**

then **config.local.php** (on Hostinger or locally) has a **missing comma** in the `return [ ... ];` array.

## Fix

Open **config.local.php** and ensure **every array entry ends with a comma** (except the last one). Example:

```php
return [
    'db' => [ ... ],
    'jwt_secret' => '...',
    'dashboard_base_url' => 'https://abhinavpaudel.com',   // ← comma required
    'mail_from' => 'noreply@abhinavpaudel.com',
];
```

Add the missing comma on the line **above** `'mail_from'`, save the file, and try the API again.

See **qtapp/docs/HOSTINGER_API_LOGS.md** for more troubleshooting.
