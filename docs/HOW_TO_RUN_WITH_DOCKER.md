# 🐳 How to Run with Docker

Complete guide to run the Secure Academic Browser System using Docker.

## 📋 Prerequisites

1. **Docker Desktop** installed and running
   - Download: https://www.docker.com/products/docker-desktop
   - Make sure Docker Desktop is running before proceeding

2. **Docker Compose** (included with Docker Desktop)

## 🚀 Quick Start

### Step 1: Start Docker Services

Open PowerShell or Command Prompt in the project directory and run:

```powershell
docker-compose up -d
```

This will start:
- ✅ **MySQL Database** (port 3307)
- ✅ **Flask API Server** (port 5000)
- ✅ **React Dashboard** (port 3000)

**Note:** First time startup may take 1-2 minutes as it downloads images and builds containers.

### Step 2: Wait for Services to Be Ready

Check service status:

```powershell
docker-compose ps
```

Wait until all services show `Up` status. MySQL may take 30-60 seconds to become `healthy`.

### Step 3: Initialize Database (First Time Only)

The database needs to be set up the first time. Run these commands:

```powershell
# Setup database schema
python docker_setup_database.py

# Populate with sample data
$env:DB_HOST="localhost"; $env:DB_PORT="3307"; python populate_sample_data.py
```

### Step 4: Verify Services

**Check API:**
```powershell
curl http://localhost:5000/health
```
Should return: `{"status":"healthy"}`

**Check Dashboard:**
Open your browser: http://localhost:3000

**Check Database:**
```powershell
docker-compose exec db mysql -uroot -pInnovation -e "SHOW DATABASES;"
```

## 📍 Access Points

Once services are running:

- **Dashboard:** http://localhost:3000
- **API Server:** http://localhost:5000
- **API Health Check:** http://localhost:5000/health
- **Database:** localhost:3307 (user: root, password: Innovation)

## 🖥️ Running the PyQt6 Desktop Application

The PyQt6 application runs **locally** (not in Docker) but can connect to Docker MySQL:

### Option 1: Use Docker MySQL (Recommended)

**PowerShell:**
```powershell
$env:DB_HOST="localhost"; $env:DB_PORT="3307"; python main.py
```

**Or use helper script:**
```powershell
.\run_with_docker.ps1
```

**Command Prompt:**
```cmd
run_with_docker.bat
```

### Option 2: Use Local MySQL

If you have local MySQL running on port 3306:

```powershell
# Use default settings (localhost:3306)
python main.py
```

## 🛠️ Common Docker Commands

### View Service Status
```powershell
docker-compose ps
```

### View Logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f db      # Database
docker-compose logs -f app     # API server
docker-compose logs -f dashboard  # Dashboard
```

### Stop Services
```powershell
docker-compose down
```

### Stop Services (Keep Data)
```powershell
docker-compose stop
```

### Start Services
```powershell
docker-compose up -d
```

### Restart a Service
```powershell
docker-compose restart app
docker-compose restart dashboard
docker-compose restart db
```

### Rebuild Containers (After Code Changes)
```powershell
docker-compose up -d --build
```

## 🔄 Complete Workflow

### First Time Setup

1. **Start Docker Desktop**

2. **Start services:**
   ```powershell
   docker-compose up -d
   ```

3. **Wait 30-60 seconds for MySQL to be ready**

4. **Initialize database:**
   ```powershell
   python docker_setup_database.py
   $env:DB_HOST="localhost"; $env:DB_PORT="3307"; python populate_sample_data.py
   ```

5. **Run PyQt6 application:**
   ```powershell
   $env:DB_HOST="localhost"; $env:DB_PORT="3307"; python main.py
   ```

### Daily Use

1. **Start Docker Desktop** (if not running)

2. **Start services:**
   ```powershell
   docker-compose up -d
   ```

3. **Run your application:**
   ```powershell
   $env:DB_HOST="localhost"; $env:DB_PORT="3307"; python main.py
   ```

4. **Stop services when done:**
   ```powershell
   docker-compose down
   ```

## 🔍 Troubleshooting

### Services Won't Start

**Check Docker is running:**
```powershell
docker --version
docker ps
```

**Check port conflicts:**
```powershell
netstat -ano | findstr :3307
netstat -ano | findstr :5000
netstat -ano | findstr :3000
```

### Database Connection Issues

**Check MySQL is healthy:**
```powershell
docker-compose ps
```
Should show `(healthy)` for MySQL container.

**Check MySQL logs:**
```powershell
docker-compose logs db
```

**Test database connection:**
```powershell
docker-compose exec db mysql -uroot -pInnovation -e "SELECT 1"
```

### API Not Responding

**Check API logs:**
```powershell
docker-compose logs app
```

**Test API:**
```powershell
curl http://localhost:5000/health
```

### Dashboard Not Loading

**Check dashboard logs:**
```powershell
docker-compose logs dashboard
```

**Rebuild dashboard:**
```powershell
docker-compose up -d --build dashboard
```

### Reset Everything

If you need to start fresh:

```powershell
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Remove images (optional)
docker-compose down --rmi all

# Start fresh
docker-compose up -d

# Reinitialize database
python docker_setup_database.py
$env:DB_HOST="localhost"; $env:DB_PORT="3307"; python populate_sample_data.py
```

## 📊 Port Configuration

| Service | Container Port | Host Port | Access URL |
|---------|---------------|-----------|------------|
| MySQL | 3306 | 3307 | localhost:3307 |
| API Server | 5000 | 5000 | http://localhost:5000 |
| Dashboard | 3000 | 3000 | http://localhost:3000 |

**Note:** MySQL uses port 3307 on host to avoid conflict with local MySQL (if installed).

## 🔐 Default Credentials

- **Database:**
  - User: `root`
  - Password: `Innovation`
  - Database: `edubrowser`

- **Application Users:**
  - Students: `student1`, `student2`, etc. (password: `student123`)
  - Teachers: `teacher1`, `teacher2`, etc. (password: `teacher123`)
  - Admins: `admin1` (password: `admin123`)

## 📝 Environment Variables

Create a `.env` file (optional) to customize:

```env
# Database
DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=Innovation
DB_NAME=edubrowser

# API
API_PORT=5000

# Dashboard
DASHBOARD_PORT=3000
VITE_API_URL=http://localhost:5000
```

## 🎯 Quick Reference Card

```powershell
# Start everything
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop everything
docker-compose down

# Run PyQt6 app with Docker MySQL
$env:DB_HOST="localhost"; $env:DB_PORT="3307"; python main.py

# Access dashboard
start http://localhost:3000

# Test API
curl http://localhost:5000/health
```

## ✅ Verification Checklist

After starting Docker services, verify:

- [ ] `docker-compose ps` shows all services as `Up`
- [ ] MySQL shows `(healthy)` status
- [ ] `curl http://localhost:5000/health` returns success
- [ ] Dashboard loads at http://localhost:3000
- [ ] Database is accessible: `docker-compose exec db mysql -uroot -pInnovation edubrowser`

## 🆘 Need Help?

- View logs: `docker-compose logs -f [service_name]`
- Check status: `docker-compose ps`
- Restart service: `docker-compose restart [service_name]`
- Rebuild: `docker-compose up -d --build`

---

**You're all set!** 🎉 Docker is the easiest way to run the entire system.

