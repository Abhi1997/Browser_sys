# 🔧 Dashboard Troubleshooting Guide

If the dashboard is not opening, follow these steps:

## ✅ Quick Checks

### 1. Check Dashboard Service is Running

```powershell
docker-compose ps dashboard
```

Should show: `Up` status

### 2. Check Dashboard is Accessible

Open in browser: http://localhost:3000

Should load the React dashboard.

### 3. Check Dashboard Logs

```powershell
docker-compose logs dashboard
```

Look for any errors.

## 🐛 Common Issues

### Issue: Dashboard Window Opens But Shows Blank/Error

**Possible Causes:**
1. Dashboard service not running
2. Incorrect URL format
3. Token generation failed
4. Device registration failed

**Solutions:**
1. **Start dashboard service:**
   ```powershell
   docker-compose up -d dashboard
   ```

2. **Check if dashboard is accessible:**
   ```powershell
   curl http://localhost:3000
   ```

3. **Check browser console** (if dashboard window opens):
   - Right-click in dashboard window
   - Select "Inspect" or "Developer Tools"
   - Check Console tab for errors

### Issue: Dashboard Doesn't Open at All

**Check:**
1. User role is correct (`admin`, `superadmin`, or `teacher`)
2. No error messages in application console
3. Dashboard service is running

**Solution:**
1. Make sure you're logged in as admin/teacher:
   - Username: `admin`
   - Password: `admin123!`

2. Check application console for errors when clicking Dashboard button

3. Verify dashboard service:
   ```powershell
   docker-compose ps
   docker-compose logs dashboard --tail 50
   ```

### Issue: "Failed to create dashboard token"

**Cause:** Database connection issue or token creation failed

**Solution:**
1. Check database connection:
   ```powershell
   docker-compose exec db mysql -uroot -pInnovation -e "SELECT 1"
   ```

2. Check if DashboardTokens table exists:
   ```powershell
   docker-compose exec db mysql -uroot -pInnovation edubrowser -e "SHOW TABLES LIKE 'DashboardTokens'"
   ```

3. Restart services:
   ```powershell
   docker-compose restart app dashboard
   ```

### Issue: Dashboard Opens But Shows "Unauthorized"

**Cause:** Token validation failed or role mismatch

**Solution:**
1. Check user role in database:
   ```sql
   SELECT id, username, role FROM Users WHERE username='admin';
   ```
   Should show: `role = 'admin'`

2. Verify token is being generated correctly

3. Check API server is running:
   ```powershell
   docker-compose ps app
   curl http://localhost:5000/health
   ```

## 🔍 Debugging Steps

### Step 1: Verify Services

```powershell
docker-compose ps
```

All services should be `Up`:
- ✅ `edubrowser_mysql` - Up (healthy)
- ✅ `edubrowser_app` - Up
- ✅ `edubrowser_dashboard` - Up

### Step 2: Check Logs

```powershell
# Dashboard logs
docker-compose logs dashboard --tail 50

# API logs
docker-compose logs app --tail 50

# Application console (when running python main.py)
# Look for error messages
```

### Step 3: Test Dashboard Directly

1. Open browser
2. Go to: http://localhost:3000
3. Should see the React dashboard interface

### Step 4: Test API

```powershell
curl http://localhost:5000/health
```

Should return: `{"status":"healthy"}`

### Step 5: Check Database

```powershell
docker-compose exec db mysql -uroot -pInnovation edubrowser -e "SELECT id, username, role FROM Users WHERE username='admin'"
```

Should show admin user exists with role='admin'.

## ✅ Expected Behavior

When clicking the Dashboard button:

1. ✅ Dashboard window opens (new window/dialog)
2. ✅ Shows React dashboard interface
3. ✅ Displays admin dashboard content
4. ✅ Shows user data and statistics

## 🛠️ Reset Dashboard

If dashboard is completely broken:

```powershell
# Stop dashboard
docker-compose stop dashboard

# Remove dashboard container
docker-compose rm -f dashboard

# Rebuild and start
docker-compose up -d --build dashboard

# Check logs
docker-compose logs dashboard -f
```

## 📝 Additional Checks

### Check Port 3000 is Available

```powershell
netstat -ano | findstr :3000
```

Should show the dashboard service listening.

### Check Browser WebEngine

The dashboard uses PyQt6 WebEngine. If it fails:
- Check PyQt6-WebEngine is installed: `pip show PyQt6-WebEngine`
- Check for WebEngine errors in console
- Try opening dashboard URL directly in regular browser

## 🆘 Still Not Working?

1. **Check all logs:**
   ```powershell
   docker-compose logs --tail 100
   ```

2. **Restart all services:**
   ```powershell
   docker-compose restart
   ```

3. **Verify user credentials:**
   - Make sure you're logged in as admin
   - Check user exists in database

4. **Check for Python errors:**
   - Run application with verbose output
   - Look for exceptions in console

---

**Fixed in latest update:**
- ✅ DashboardWindow now correctly handles URL with token and deviceId
- ✅ Added error handling for token generation failures
- ✅ Added user feedback for errors

