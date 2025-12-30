# Docker Start Guide

## 🚨 Port Conflict Issue

If you see an error:
```
ports are not available: exposing port TCP 0.0.0.0:3306 -> 127.0.0.1:0: listen tcp 0.0.0.0:3306: bind: Only one usage of each socket address
```

This means you have a **local MySQL server** running on port 3306.

## ✅ Solution Options

### Option 1: Use Local MySQL (Recommended for Development)

Since you already have MySQL running locally, you can use it directly:

1. **Keep Docker for API and Dashboard only:**
   - Modify `docker-compose.yml` to use a different port for MySQL, OR
   - Don't run the MySQL container, just use your local MySQL

2. **Stop Docker MySQL service** and use local MySQL:
   ```bash
   # Edit docker-compose.yml - comment out or remove the 'db' service
   # Or change the port mapping to use a different port
   ```

3. **Use local MySQL with Docker services:**
   - Your local MySQL is at `localhost:3306`
   - Docker services can connect to `host.docker.internal:3306` (if on Windows/Mac)
   - Or use `localhost:3306` if services are not in Docker

### Option 2: Stop Local MySQL and Use Docker MySQL

**Windows:**
```powershell
# Stop MySQL service
net stop MySQL80
# or
net stop MySQL
# or check services:
services.msc
# Find MySQL service and stop it
```

**Then start Docker:**
```bash
docker-compose up -d
```

### Option 3: Change Docker MySQL Port

Edit `docker-compose.yml` and change the port mapping:

```yaml
services:
  db:
    ports:
      - "${DB_PORT:-3307}:3306"  # Use 3307 instead of 3306
```

Then update your `.env` or connection strings to use port 3307.

## 🎯 Recommended Setup for Development

Since you're developing with Docker but have local MySQL:

1. **Use local MySQL** (port 3306) - already running ✅
2. **Run API server in Docker** (or locally, both work)
3. **Run Dashboard in Docker** (or locally)

### Modified docker-compose.yml (MySQL on different port)

If you want to run MySQL in Docker on a different port:

```yaml
services:
  db:
    ports:
      - "3307:3306"  # Changed from 3306 to 3307
```

Then connect using:
- Host: `localhost`
- Port: `3307`

### Or Remove MySQL from Docker

Comment out the `db` service in `docker-compose.yml` and use only:
- API server container (connects to localhost MySQL)
- Dashboard container

## 🚀 Quick Start (Using Local MySQL)

1. **Ensure MySQL is running locally:**
   ```bash
   # Check if MySQL is running
   mysql -u root -pInnovation -e "SELECT 1"
   ```

2. **Start only API and Dashboard in Docker:**
   ```bash
   # Edit docker-compose.yml to remove/comment db service
   # Or just start specific services:
   docker-compose up -d app dashboard
   ```

3. **Or use local MySQL with Docker MySQL on different port:**
   ```bash
   # Edit docker-compose.yml port mapping to 3307
   docker-compose up -d
   ```

## 📝 Current Status

Your setup:
- ✅ Local MySQL running on port 3306
- ✅ Docker containers created but not started (due to port conflict)
- ✅ Application configured to use localhost (will work with local MySQL)

## ✅ Recommended Action

**Keep using local MySQL** - it's already working! Just make sure:
1. Local MySQL is running
2. Database `edubrowser` exists (you already created it)
3. Sample data is populated (you already did this)

Then run:
```bash
python main.py
```

If you want Docker services (API/Dashboard), either:
- Use different ports, OR
- Stop local MySQL and use Docker MySQL

