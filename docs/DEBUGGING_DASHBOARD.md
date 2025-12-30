# Debugging Dashboard Issues

Since the PyQt6 browser doesn't have a console, here are ways to debug dashboard authentication issues:

## 1. Check API Server Logs

View the Flask API server logs to see authentication errors:

```powershell
docker-compose logs app --tail 100
```

Look for:
- `validate_token` errors
- `Invalid token` messages
- `Missing token or deviceId` errors
- Database connection errors

## 2. Check Error Display

If authentication fails, the dashboard will now show an error message on screen with:
- The error message
- Debug information (user, role, loading state)
- Instructions to retry

## 3. Verify Admin User

Make sure the admin user exists and is configured correctly:

```powershell
python database/create_admin_quick.py
```

This should show:
- User ID
- Username: admin
- Role: admin
- Approval Status: None (no approval required)
- Active: Yes

## 4. Check Token Generation

When you open the dashboard from PyQt6, it:
1. Gets device info
2. Registers the device
3. Generates a dashboard token
4. Opens the dashboard with token and deviceId in URL

## 5. Common Issues

### "Missing authentication credentials"
- Token or deviceId not in URL
- Solution: Close and reopen dashboard from PyQt6 app

### "Session expired"
- Token has expired (older than 24 hours)
- Solution: Close and reopen dashboard

### "Invalid token"
- Token doesn't match what's in database
- Token and deviceId don't match
- Solution: Close and reopen dashboard to get fresh token

### "Access Denied" / Redirected to /unauthorized
- Token validation failed
- Role doesn't match required role
- User not authenticated
- Solution: Check API logs, verify user role in database

## 6. Database Verification

Check if the admin user and device are registered:

```sql
-- Check admin user
SELECT id, username, role, teacher_approval_status, is_active 
FROM Users 
WHERE username = 'admin';

-- Check dashboard tokens (for your device)
SELECT * FROM DashboardTokens 
WHERE user_id = 1 
ORDER BY created_at DESC 
LIMIT 5;

-- Check devices
SELECT * FROM Devices 
WHERE user_id = 1 
ORDER BY registered_at DESC 
LIMIT 5;
```

## 7. Rebuild Containers

If changes were made to authentication code:

```powershell
docker-compose up -d --build app
```

## 8. Test API Endpoint Directly

You can test the verify endpoint (if you have a token):

```powershell
# Replace TOKEN and DEVICE_ID with actual values from URL
curl -X POST http://localhost:5000/api/auth/verify-token `
  -H "Content-Type: application/json" `
  -d '{\"token\":\"TOKEN\",\"deviceId\":\"DEVICE_ID\"}'
```

## 9. Python Console Output

The PyQt6 application prints errors to the Python console. Check the terminal where you ran `python main.py` or the script output for:
- "Failed to create dashboard token"
- "Failed to open dashboard"
- Database connection errors
- Authentication errors

## Next Steps

If you're still having issues:
1. Check the error message displayed on screen (if any)
2. Check API server logs: `docker-compose logs app --tail 100`
3. Verify admin user: `python database/create_admin_quick.py`
4. Close and reopen the dashboard to get a fresh token
5. Check that the React dashboard is running on port 3000

