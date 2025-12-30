# Docker Quick Reference Card

## 🚀 Quick Start

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📋 Essential Commands

### Start/Stop
```bash
docker-compose up -d          # Start in background
docker-compose down            # Stop services
docker-compose restart         # Restart all
docker-compose ps              # Check status
```

### Logs
```bash
docker-compose logs -f                    # All services
docker-compose logs -f db                 # Database only
docker-compose logs -f app                # API only
docker-compose logs -f dashboard          # Dashboard only
```

### Database
```bash
# Connect to MySQL
docker-compose exec db mysql -uroot -pInnovation

# Check databases
docker-compose exec db mysql -uroot -pInnovation -e "SHOW DATABASES;"

# Backup
docker-compose exec db mysqldump -uroot -pInnovation --all-databases > backup.sql
```

### Rebuild
```bash
docker-compose build           # Rebuild all
docker-compose build app       # Rebuild API
docker-compose build dashboard # Rebuild dashboard
docker-compose up -d --build   # Rebuild and start
```

## 🌐 Access Points

- **Dashboard**: http://localhost:3000
- **API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health
- **Database**: localhost:3306
  - User: `root`
  - Password: `Innovation`

## 🔧 Setup Steps

1. **Start Docker services:**
   ```bash
   docker-compose up -d
   ```

2. **Wait for database (30-60 seconds)**

3. **Initialize databases (on host):**
   ```bash
   python setup_databases.py
   ```

4. **Populate sample data (on host):**
   ```bash
   python populate_sample_data.py
   ```

5. **Run PyQt6 app (on host):**
   ```bash
   python main.py
   ```

## 🐛 Troubleshooting

**Ports in use?**
- Check: `netstat -ano | findstr :3306` (Windows)
- Change ports in `docker-compose.yml`

**Services won't start?**
- Check Docker is running: `docker info`
- Check logs: `docker-compose logs`

**Database not accessible?**
- Wait 30-60 seconds after starting
- Check: `docker-compose ps`
- Test: `docker-compose exec db mysqladmin ping -h localhost -pInnovation`

**API not responding?**
- Check: `curl http://localhost:5000/health`
- View logs: `docker-compose logs app`

## 📝 Important Notes

- **PyQt6 app** runs on host, NOT in Docker
- Database password: **Innovation**
- Uses 3 databases: `edubrowser_auth`, `edubrowser_students`, `edubrowser_activity`
- Data persists in Docker volumes

