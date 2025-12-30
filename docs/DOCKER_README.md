# Docker Deployment Guide

## Quick Start

### Prerequisites
- Docker Desktop installed
- Docker Compose installed

### Step 1: Environment Configuration

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` if you want to change default passwords or configuration.

### Step 2: Start Services with Docker Compose

Start the database and React dashboard:
```bash
docker-compose up -d
```

This will start:
- **MySQL Database** on port 3306
- **React Dashboard** on port 3000

Wait for services to be healthy:
```bash
docker-compose ps
```

### Step 3: Initialize Database (First Time Only)

The database will be automatically initialized with the schema and default admin user.

Or manually run the setup script:
```bash
# Make sure venv is activated
.venv\Scripts\Activate.ps1   # Windows PowerShell
python add_test_users.py      # Add test users
```

### Step 4: Run the Python Browser Application

**Note:** The PyQt6 GUI application cannot run inside Docker without X11 forwarding. Run it locally:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1
python main.py
```

The application will connect to:
- MySQL database at `localhost:3306`
- React dashboard at `http://localhost:3000`

## Docker Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f db
docker-compose logs -f dashboard
```

### Stop Services
```bash
docker-compose down
```

### Stop and Remove Data
```bash
docker-compose down -v
```

### Rebuild Containers
```bash
docker-compose build
docker-compose up -d
```

## Service URLs

- **React Dashboard:** http://localhost:3000
- **MySQL Database:** localhost:3306
  - User: `root`
  - Password: `Innovation` (or from .env)
  - Database: `edubrowser`

## Default Users

After running `add_test_users.py`:

| Username | Password | Role |
|----------|----------|------|
| admin | admin1234 | admin |
| admin1 | admin123! | admin |
| admin2 | admin456! | admin |
| teacher1 | teach123! | teacher |
| teacher2 | teach456! | teacher |
| teacher3 | teach789! | teacher |
| student1 | student123! | student |
| student2 | student456! | student |
| student3 | student789! | student |
| student4 | student012! | student |

## Troubleshooting

### Database Connection Issues
Check if MySQL is healthy:
```bash
docker-compose ps
```

Test connection:
```bash
docker-compose exec db mysql -uroot -pInnovation -e "SHOW DATABASES;"
```

### React Dashboard Not Loading
Check logs:
```bash
docker-compose logs dashboard
```

Rebuild:
```bash
docker-compose build dashboard
docker-compose up -d dashboard
```

### Port Conflicts
If ports 3000 or 3306 are already in use, edit `docker-compose.yml` to change ports:
```yaml
ports:
  - "3001:3000"  # Change host port
```

## Production Deployment

For production:
1. Change all default passwords in `.env`
2. Update `JWT_SECRET` in `.env`
3. Use production-ready MySQL configuration
4. Build React dashboard for production:
   ```bash
   cd react-dashboard
   npm run build
   ```
5. Serve built files with nginx or similar

## Network Architecture

```
┌─────────────────┐
│  Python Browser │ (Local - PyQt6 GUI)
│    (main.py)    │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│  MySQL Database │  │ React Dashboard │
│  (Docker:3306)  │  │ (Docker:3000)   │
└─────────────────┘  └─────────────────┘
         │
         │
    edubrowser_network
```
