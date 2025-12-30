# API Connectivity Issue - Fetch Hanging

## Problem
When running `fetch('http://localhost:5000/api/users')` in browser console, the request hangs (Promise stays pending).

## Cause
The API endpoint might be:
1. Taking too long to respond (database query timeout)
2. Not handling the request properly
3. Missing CORS headers (though CORS is configured)

## Solution

### Step 1: Check API Response Format
The API should return JSON in this format:
```json
{
  "success": true,
  "data": [...]
}
```

### Step 2: Test with Error Handling
Instead of the simple fetch, use this in browser console:

```javascript
fetch('http://localhost:5000/api/users')
  .then(r => {
    console.log('Status:', r.status);
    return r.json();
  })
  .then(d => console.log('Success:', d))
  .catch(e => console.error('Error:', e))
```

### Step 3: Check Browser Network Tab
1. Press F12 → Network tab
2. Filter by "Fetch/XHR"
3. Try the fetch again
4. Click on the request to see:
   - Request headers
   - Response headers
   - Response preview
   - Timing information

### Step 4: Check if Request Completes
Look for:
- Status code (200, 404, 500, etc.)
- Response time
- Any error messages

### Step 5: Verify API Server Logs
Check Docker logs for the request:
```powershell
docker-compose logs app --tail=20 | Select-String "users"
```

You should see:
```
172.18.0.1 - - [DATE] "GET /api/users HTTP/1.1" 200 -
```

If you see `500` or other error codes, there's a server-side issue.

### Step 6: Test API Directly
Test if the API works from the host machine:

```powershell
# PowerShell
Invoke-WebRequest -Uri "http://localhost:5000/api/users" -Method GET | Select-Object -ExpandProperty Content
```

### Step 7: Check CORS Headers
In browser Network tab, check the response headers for:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type, Authorization, X-Device-ID`

## Common Issues

### Issue 1: Database Connection Timeout
If the database query is slow, the API will hang.

**Fix**: Check database connection:
```powershell
docker-compose exec db mysql -uroot -pInnovation -e "SELECT 1"
```

### Issue 2: Missing CORS Headers
If CORS headers are missing, the browser will block the response.

**Fix**: Already configured in `api_server.py`, but verify:
```python
CORS(app, 
     resources={r"/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization", "X-Device-ID"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
```

### Issue 3: Browser Blocking Mixed Content
If the dashboard is served over HTTPS but API is HTTP, browser blocks it.

**Fix**: Not applicable (both are HTTP on localhost)

### Issue 4: Network Connectivity
Browser can't reach `localhost:5000`.

**Fix**: 
1. Verify port is accessible: `Test-NetConnection -ComputerName localhost -Port 5000`
2. Check if firewall is blocking
3. Try `127.0.0.1:5000` instead of `localhost:5000`

## Quick Debug Script

Run this in browser console to diagnose:

```javascript
(async () => {
  try {
    console.log('Testing API connectivity...');
    const start = Date.now();
    const response = await fetch('http://localhost:5000/api/users');
    const duration = Date.now() - start;
    console.log(`Response time: ${duration}ms`);
    console.log('Status:', response.status);
    console.log('Headers:', [...response.headers.entries()]);
    const data = await response.json();
    console.log('Data:', data);
  } catch (error) {
    console.error('Error:', error);
  }
})();
```

This will show:
- How long the request takes
- The status code
- Response headers
- The actual data (or error)

## Expected Result

You should see:
- Status: 200
- Response time: < 1000ms (usually < 100ms)
- Data: `{ success: true, data: [...] }` with your database users

If the request takes > 5 seconds or hangs indefinitely, there's a problem with the API server or database connection.

