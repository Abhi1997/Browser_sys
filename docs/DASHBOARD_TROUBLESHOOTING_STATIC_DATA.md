# Troubleshooting: Dashboard Showing Static/Mock Data

If your dashboard is showing static/mock data instead of data from the database, follow these steps:

## Symptoms
- User table shows `jsmith`, `mjohnson`, etc. (mock users)
- Data doesn't change when you add/delete items
- Whitelist/blacklist shows mock entries

## Root Cause
The React application is not making API calls, or the browser has cached an old JavaScript bundle.

## Solution Steps

### Step 1: Hard Refresh Browser
1. Press `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)
2. Or `Ctrl + F5` to force reload
3. This clears the browser cache for that page

### Step 2: Clear Browser Cache
1. Press `F12` to open Developer Tools
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"
4. Or go to browser settings → Clear browsing data → Cached images and files

### Step 3: Check Browser Console
1. Press `F12` to open Developer Tools
2. Go to the "Console" tab
3. Look for any red error messages
4. Common errors:
   - `Failed to fetch` → API server not running
   - `CORS error` → API server CORS configuration issue
   - `Network error` → Can't reach API server

### Step 4: Check Network Tab
1. Press `F12` to open Developer Tools
2. Go to the "Network" tab
3. Filter by "Fetch/XHR"
4. Refresh the dashboard page
5. You should see requests to:
   - `http://localhost:5000/api/users`
   - `http://localhost:5000/api/whitelist`
   - `http://localhost:5000/api/blacklist`
   - `http://localhost:5000/api/stats`
6. If you DON'T see these requests, the React app isn't calling the API

### Step 5: Rebuild React Dashboard
If the above steps don't work, rebuild the dashboard container:

```powershell
docker-compose build dashboard
docker-compose restart dashboard
```

### Step 6: Verify API Endpoints
Test if the API endpoints are working:

```powershell
# Test users endpoint
Invoke-WebRequest -Uri "http://localhost:5000/api/users" -Method GET

# Test whitelist endpoint  
Invoke-WebRequest -Uri "http://localhost:5000/api/whitelist" -Method GET
```

### Step 7: Check Docker Logs
Check if API requests are being received:

```powershell
docker-compose logs app --tail=50 | Select-String "GET.*users|GET.*whitelist"
```

You should see log entries like:
```
172.18.0.1 - - [DATE] "GET /api/users HTTP/1.1" 200 -
```

## Verification

After following these steps, you should see:

1. **Network Tab**: API requests being made to `/api/users`, `/api/whitelist`, etc.
2. **Console**: No errors (or only non-critical warnings)
3. **Dashboard**: Real data from your database (e.g., `student1`, `student2`, etc. instead of `jsmith`, `mjohnson`)
4. **Docker Logs**: API request entries in the logs

## Still Not Working?

If you've followed all steps and still see mock data:

1. **Check React Query DevTools** (if installed):
   - Open React Query DevTools in browser
   - Check if queries are being executed
   - Check query status (loading, success, error)

2. **Check API Response Format**:
   - In Network tab, click on a request
   - Check the "Response" tab
   - Verify the response has `{"success": true, "data": [...]}` format

3. **Verify Component Code**:
   - Confirm components are using hooks like `useUsers()`, `useWhitelist()`, etc.
   - NOT using `mockUsers`, `mockWhitelist` directly

4. **Check Environment Variables**:
   ```powershell
   docker-compose exec dashboard env | Select-String "VITE_API_URL"
   ```
   Should show: `VITE_API_URL=http://localhost:5000`

## Quick Test

To quickly test if the API is working, open browser console and run:

```javascript
fetch('http://localhost:5000/api/users')
  .then(r => r.json())
  .then(console.log)
```

You should see your real database users, not mock data.

