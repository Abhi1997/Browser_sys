# Docker Run Guide - Secure Academic Browser

Complete guide to run the entire system using Docker.

## 📋 Prerequisites

1. **Docker Desktop** installed and running
   - Download from: https://www.docker.com/products/docker-desktop
   - Make sure Docker Desktop is running before proceeding

2. **Docker Compose** (usually included with Docker Desktop)

## 🚀 Quick Start

### Option 1: Using Helper Scripts (Recommended)

**Windows:**
```powershell
.\start.bat
```

**Mac/Linux:**
```bash
chmod +x start.sh
./start.sh
```

### Option 2: Manual Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

## 📁 Step-by-Step Setup

### Step 1: Prepare Environment (Optional)

Create a `.env` file in the project root (optional - defaults are used if not present):

```env
# Database Configuration
DB_HOST=localhost    # Use 'localhost' when running scripts on host machine
                     # Use 'db' when running inside Docker containers
DB_USER=root
DB_PASSWORD=Innovation
DB_NAME=edubrowser

# API Configuration
API_PORT=5000
VITE_API_URL=http://localhost:5000

# Dashboard Configuration
DASHBOARD_PORT=3000

# Docker Configuration
DB_PORT=3306
```

### Step 2: Start Docker Services

```bash
docker-compose up -d
```

This will start:
- ✅ **MySQL Database** (port 3306)
- ✅ **Flask API Server** (port 5000)
- ✅ **React Dashboard** (port 3000)

### Step 3: Wait for Services to Be Ready

Check service status:
```bash
docker-compose ps
```

Wait until all services show `healthy` or `Up` status. Database initialization may take 30-60 seconds.

### Step 4: Initialize Databases

The databases need to be created and populated. Run these commands from your host machine (not inside Docker):

```bash
# Create databases and schemas
python setup_databases.py

# Populate with sample data
python populate_sample_data.py
```

**Note:** Make sure you have Python and required packages installed on your host machine for these scripts.

### Step 5: Run PyQt6 Application (Local)

The PyQt6 desktop application **cannot run inside Docker** - run it locally:

```bash
# Activate virtual environment (if using one)
# Windows:
.venv\Scripts\Activate.ps1

# Mac/Linux:
source venv/bin/activate

# Run the application
python main.py
```

The application will connect to:
- Database: `localhost:3306`
- API: `http://localhost:5000`
- Dashboard: `http://localhost:3000`

## 🐳 Docker Services

### Services Overview

| Service | Container Name | Port | Description |
|---------|---------------|------|-------------|
| **MySQL** | `edubrowser_mysql` | 3306 | Database server |
| **API** | `edubrowser_app` | 5000 | Flask API server |
| **Dashboard** | `edubrowser_dashboard` | 3000 | React dashboard |

### Service Details

#### 1. MySQL Database

```bash
# Connect to MySQL
docker-compose exec db mysql -uroot -pInnovation

# Check databases
docker-compose exec db mysql -uroot -pInnovation -e "SHOW DATABASES;"

# View logs
docker-compose logs -f db
```

#### 2. Flask API Server

```bash
# View logs
docker-compose logs -f app

# Restart service
docker-compose restart app

# Check API health
curl http://localhost:5000/health
```

#### 3. React Dashboard

```bash
# View logs
docker-compose logs -f dashboard

# Restart service
docker-compose restart dashboard

# Access dashboard
# Open browser: http://localhost:3000
```

## 📊 Access Points

Once everything is running:

- **React Dashboard**: http://localhost:3000
- **API Server**: http://localhost:5000
- **API Health Check**: http://localhost:5000/health
- **MySQL Database**: localhost:3306
  - User: `root`
  - Password: `Innovation`

## 🔧 Common Docker Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### Stop and Remove Data (Fresh Start)
```bash
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f db
docker-compose logs -f app
docker-compose logs -f dashboard
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart db
docker-compose restart app
docker-compose restart dashboard
```

### Rebuild Containers
```bash
# Rebuild all
docker-compose build

# Rebuild specific service
docker-compose build app
docker-compose build dashboard

# Rebuild and restart
docker-compose up -d --build
```

### Check Status
```bash
docker-compose ps
```

### Execute Commands in Containers
```bash
# MySQL shell
docker-compose exec db mysql -uroot -pInnovation

# Python shell in API container
docker-compose exec app python

# Node shell in dashboard container
docker-compose exec dashboard sh
```

## 🗄️ Database Management

### Initialize Databases (First Time)

Run on your host machine:
```bash
python setup_databases.py
```

### Populate Sample Data

Run on your host machine:
```bash
python populate_sample_data.py
```

### Backup Database

```bash
# Backup all databases
docker-compose exec db mysqldump -uroot -pInnovation --all-databases > backup.sql

# Backup specific database
docker-compose exec db mysqldump -uroot -pInnovation edubrowser_auth > auth_backup.sql
docker-compose exec db mysqldump -uroot -pInnovation edubrowser_students > students_backup.sql
docker-compose exec db mysqldump -uroot -pInnovation edubrowser_activity > activity_backup.sql
```

### Restore Database

```bash
# Restore all databases
docker-compose exec -T db mysql -uroot -pInnovation < backup.sql

# Restore specific database
docker-compose exec -T db mysql -uroot -pInnovation edubrowser_auth < auth_backup.sql
```

### Access Database Directly

```bash
# MySQL command line
docker-compose exec db mysql -uroot -pInnovation

# Or from host machine (if MySQL client installed)
mysql -h localhost -P 3306 -u root -pInnovation
```

## 🔍 Troubleshooting

### Services Won't Start

**Check Docker is running:**
```bash
docker --version
docker-compose --version
```

**Check for port conflicts:**
```bash
# Windows
netstat -ano | findstr :3306
netstat -ano | findstr :5000
netstat -ano | findstr :3000

# Mac/Linux
lsof -i :3306
lsof -i :5000
lsof -i :3000
```

**If ports are in use, change them in `docker-compose.yml`:**

```yaml
ports:
  - "3307:3306"  # Change host port
```

### Database Connection Issues

**Check if database is healthy:**
```bash
docker-compose ps db
```

**Check database logs:**
```bash
docker-compose logs db
```

**Test connection:**
```bash
docker-compose exec db mysqladmin ping -h localhost -pInnovation
```

### API Server Not Responding

**Check logs:**
```bash
docker-compose logs app
```

**Restart API:**
```bash
docker-compose restart app
```

**Check if API is accessible:**
```bash
curl http://localhost:5000/health
```

### Dashboard Not Loading

**Check logs:**
```bash
docker-compose logs dashboard
```

**Rebuild dashboard:**
```bash
docker-compose build dashboard
docker-compose up -d dashboard
```

**Check if dashboard is accessible:**
```bash
curl http://localhost:3000
```

### Database Not Initialized

If databases don't exist:

1. **Stop services:**
   ```bash
   docker-compose down
   ```

2. **Remove volumes (fresh start):**
   ```bash
   docker-compose down -v
   ```

3. **Start services:**
   ```bash
   docker-compose up -d
   ```

4. **Wait for database to be ready (30-60 seconds)**

5. **Run setup scripts from host:**
   ```bash
   python setup_databases.py
   python populate_sample_data.py
   ```

### PyQt6 Application Can't Connect

**Make sure:**
- Docker services are running: `docker-compose ps`
- API is accessible: `curl http://localhost:5000/health`
- Database is accessible: `docker-compose exec db mysqladmin ping -h localhost -pInnovation`
- Using correct credentials in `.env` or code

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Host Machine                    │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   PyQt6 Desktop Application      │  │
│  │        (main.py)                 │  │
│  │   Run locally, not in Docker     │  │
│  └──────────────┬───────────────────┘  │
│                 │                       │
│                 │ Connects to           │
│                 │                       │
└─────────────────┼───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│         Docker Network                  │
│    (edubrowser_network)                 │
│                                         │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │   MySQL  │  │   API    │  │Dashboard││
│  │  :3306   │  │  :5000   │  │  :3000  ││
│  └────┬─────┘  └────┬─────┘  └────┬───┘│
│       │             │              │    │
│       └─────────────┴──────────────┘    │
│              Internal Network           │
└─────────────────────────────────────────┘
```

## 📝 Notes

1. **PyQt6 GUI**: Must run on host machine, not in Docker
2. **Database Persistence**: Data is stored in Docker volumes
3. **Environment Variables**: Use `.env` file for configuration
4. **Multi-Database**: System uses 3 separate databases (auth, students, activity)
5. **Port Forwarding**: All services expose ports to host machine

## 🔐 Default Credentials

| Service | User | Password |
|---------|------|----------|
| MySQL | root | Innovation |
| Application | admin | admin1234 |

## 🎯 Next Steps

After Docker services are running:

1. ✅ Initialize databases: `python setup_databases.py`
2. ✅ Populate sample data: `python populate_sample_data.py`
3. ✅ Run PyQt6 app: `python main.py`
4. ✅ Login and access dashboard
5. ✅ View data in dashboard at http://localhost:3000

## 📚 Additional Resources

- Docker Compose documentation: https://docs.docker.com/compose/
- MySQL Docker image: https://hub.docker.com/_/mysql
- Node.js Docker image: https://hub.docker.com/_/node

