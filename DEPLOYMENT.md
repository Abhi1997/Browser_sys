# 🚀 EduBrowser Docker Deployment Guide

Deploy EduBrowser anywhere with Docker Compose. This guide covers local development and production deployment.

## Prerequisites

- **Docker** (v20.10+) - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (v2.0+) - Usually included with Docker Desktop
- **Git** (optional) - For cloning the repository

Verify installation:
```bash
docker --version
docker-compose --version
```

## Quick Start (5 minutes)

### 1. Clone or Download the Project
```bash
git clone <repository-url> edubrowser
cd edubrowser
```

### 2. Configure Environment (Optional)
Edit `.env` file to customize settings:
```bash
# Database
DB_PASSWORD=Innovation          # Change this in production!
DB_NAME=edubrowser

# API Server
API_PORT=5000

# Dashboard
DASHBOARD_PORT=3000
VITE_API_URL=http://localhost:5000
```

### 3. Start Services
```bash
docker-compose up -d
```

Wait for all services to be healthy (30-60 seconds):
```bash
docker-compose ps
```

### 4. Access the Application

| Component | URL |
|-----------|-----|
| **React Dashboard** | http://localhost:3000 |
| **API Server** | http://localhost:5000 |
| **Database** | localhost:3306 |

## Default Credentials

After first run, test users are automatically created:

| Username | Password | Role |
|----------|----------|------|
| superadmin1 | super123! | superadmin |
| admin1 | admin123! | admin |
| teacher1 | teach123! | teacher |
| student1 | student123! | student |

See `test_users_credentials.txt` for all test users.

## Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app      # API Server
docker-compose logs -f dashboard # React Dashboard
docker-compose logs -f db       # Database
```

### Stop Services
```bash
# Pause without removing data
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove all data (clean start)
docker-compose down -v
```

### Restart Services
```bash
docker-compose restart

# Rebuild and restart
docker-compose up -d --build
```

### Check Service Status
```bash
docker-compose ps
docker-compose exec app curl http://localhost:5000/health
```

## Production Deployment

### 1. Server Requirements
- Minimum: 2GB RAM, 10GB disk
- Recommended: 4GB RAM, 20GB disk
- OS: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2

### 2. Security Checklist
```bash
# Change all default passwords in .env
DB_PASSWORD=<strong-password>

# Set proper environment
NODE_ENV=production

# Use HTTPS in production
# Update VITE_API_URL to use https://
```

### 3. Deploy on Cloud

#### AWS EC2
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone project
git clone <repository-url>
cd edubrowser

# Start services
docker-compose up -d
```

#### DigitalOcean Droplet
```bash
# Create droplet with Docker pre-installed
# Then SSH and follow AWS EC2 steps above
```

#### Docker Compose on VPS
```bash
# Install Docker and Docker Compose
sudo apt-get update
sudo apt-get install docker.io docker-compose -y

# Add user to docker group
sudo usermod -aG docker $USER

# Deploy
git clone <repository-url>
cd edubrowser
docker-compose up -d
```

### 4. Persistence & Backups
```bash
# Database is stored in named volume
# Backup MySQL data
docker-compose exec db mysqldump -u root -p$DB_PASSWORD $DB_NAME > backup.sql

# Restore from backup
docker-compose exec -T db mysql -u root -p$DB_PASSWORD $DB_NAME < backup.sql
```

### 5. Monitoring & Maintenance

#### Check System Health
```bash
docker system df                    # Disk usage
docker stats                        # CPU/Memory usage
docker-compose logs --tail=50 app   # Last 50 logs
```

#### Auto-restart Containers
Already enabled with `restart: unless-stopped` in docker-compose.yml

#### Update Services
```bash
# Pull latest images
docker-compose pull

# Rebuild and restart
docker-compose up -d --build
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :3000          # Linux/macOS
netstat -ano | findstr :3000  # Windows

# Change port in .env
DASHBOARD_PORT=3001
API_PORT=5001
```

### Database Connection Failed
```bash
# Check database logs
docker-compose logs db

# Verify MySQL is healthy
docker-compose exec db mysqladmin ping -u root -p$DB_PASSWORD

# Restart database
docker-compose restart db
```

### Containers Won't Start
```bash
# Check logs
docker-compose logs

# Remove containers and restart
docker-compose down
docker-compose up -d --build
```

### Out of Disk Space
```bash
# Clean up unused Docker data
docker system prune -a --volumes

# Remove specific volumes
docker volume prune
```

## Architecture

```
┌─────────────────────────────────────────────┐
│        Docker Compose Network               │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐   ┌──────────────┐      │
│  │   MySQL DB   │   │ React Dashboard   │      │
│  │   :3306      │   │   :3000      │      │
│  └──────────────┘   └──────────────┘      │
│       ▲                    │                │
│       │                    │                │
│  ┌────┴────────────────────┴──────┐       │
│  │     API Server (Flask)         │       │
│  │        :5000                   │       │
│  └────────────────────────────────┘       │
│                                             │
└─────────────────────────────────────────────┘
```

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | db | Database hostname |
| `DB_USER` | root | Database user |
| `DB_PASSWORD` | Innovation | Database password |
| `DB_NAME` | edubrowser | Database name |
| `DB_PORT` | 3306 | Database port |
| `API_PORT` | 5000 | API Server port |
| `DASHBOARD_PORT` | 3000 | Dashboard port |
| `VITE_API_URL` | http://localhost:5000 | API endpoint for React |
| `NODE_ENV` | development | Node environment |

## Support & Documentation

- **GitHub Issues**: Report bugs and feature requests
- **Local Development**: Run `docker-compose up` with `restart: no` for development
- **API Docs**: Available at `/api/docs` once server is running

## License

See LICENSE file in the repository.
