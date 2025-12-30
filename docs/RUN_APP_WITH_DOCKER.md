# 🚀 Run Application with Docker MySQL

Simple guide to run your PyQt6 application connecting to Docker MySQL.

## ✅ Quick Method

### Windows PowerShell

```powershell
$env:DB_HOST="localhost"; $env:DB_PORT="3307"; python main.py
```

Or use the helper script:
```powershell
.\run_with_docker.ps1
```

### Windows Command Prompt

```cmd
set DB_HOST=localhost && set DB_PORT=3307 && python main.py
```

Or use the batch file:
```cmd
run_with_docker.bat
```

## 📝 Step-by-Step

1. **Make sure Docker services are running:**
   ```powershell
   docker-compose ps
   ```
   All services should show `Up` or `healthy`.

2. **Set environment variables:**
   ```powershell
   $env:DB_HOST="localhost"
   $env:DB_PORT="3307"
   ```

3. **Run the application:**
   ```powershell
   python main.py
   ```

## 🔍 Troubleshooting

### Still Getting "Unknown host 'db'" Error?

The application is still trying to connect to host 'db'. Make sure:

1. **Set environment variables before running:**
   ```powershell
   $env:DB_HOST="localhost"
   $env:DB_PORT="3307"
   ```

2. **Check if Docker MySQL is running:**
   ```powershell
   docker-compose ps
   ```
   MySQL should show `(healthy)`

3. **Test connection manually:**
   ```powershell
   docker-compose exec db mysql -uroot -pInnovation -e "SELECT 1"
   ```

### Connection Refused?

- Make sure Docker MySQL is running on port 3307
- Check port: `netstat -ano | findstr :3307`
- Verify Docker container: `docker-compose ps`

## 📊 Port Configuration

- **Docker MySQL:** `localhost:3307` (use this when running app locally)
- **Local MySQL:** `localhost:3306` (if you have local MySQL installed)

## 💡 Alternative: Use Helper Scripts

### PowerShell Script
```powershell
.\run_with_docker.ps1
```

### Batch File
```cmd
run_with_docker.bat
```

These scripts automatically set the correct environment variables.

## ✅ Verification

After running, you should see:
- Application window opens
- No database connection errors
- Login screen appears
- Can connect to database successfully

---

**That's it!** Your application will now connect to Docker MySQL on port 3307.

