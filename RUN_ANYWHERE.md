# 🚀 Run EduBrowser Anywhere with Docker

Your EduBrowser application is now fully containerized and portable!

## Quick Start

### Windows Users
```powershell
# Double-click: start.bat
# Or from terminal:
.\start.bat
```

### Mac/Linux Users
```bash
# Make script executable (first time only)
chmod +x start.sh

# Run:
./start.sh
```

Both scripts will automatically:
- ✅ Check Docker is installed
- ✅ Create `.env` file if missing
- ✅ Start all services
- ✅ Display access URLs

## What's Included

Your Docker setup includes:

| Service | Port | Purpose |
|---------|------|---------|
| **API Server** | 5000 | Python Flask API backend |
| **React Dashboard** | 3000 | Web-based dashboard interface |
| **MySQL Database** | 3306 | Data storage |

## Running Anywhere

### 1. **Your Local Machine** ✅
```bash
./start.sh   # Mac/Linux
start.bat    # Windows
```

### 2. **Cloud Server (AWS, DigitalOcean, etc.)**
```bash
# SSH into server
ssh user@your-server.com

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (Linux)
sudo usermod -aG docker $USER

# Clone or upload project
git clone <your-repo>
cd edubrowser

# Start services
docker-compose up -d

# Access at: http://your-server-ip:3000
```

### 3. **Docker Compose on Hosting Platform**
Platforms like:
- **Render** - https://render.com (free tier available)
- **Railway.app** - https://railway.app
- **Heroku** - https://www.heroku.com
- **Fly.io** - https://fly.io

These platforms support `docker-compose` natively.

### 4. **Kubernetes / Docker Swarm**
For production at scale:
```bash
docker-compose config > kube-manifest.yaml
# Convert and deploy to Kubernetes
```

## Configuration

### Edit Environment Variables
```bash
# Edit .env file
# Change database password, ports, URLs, etc.
nano .env    # Linux/Mac
notepad .env # Windows

# Restart services
docker-compose down
docker-compose up -d
```

### Available Options in `.env`
```env
# Database
DB_PASSWORD=Innovation          # CHANGE THIS IN PRODUCTION!
DB_NAME=edubrowser

# Ports
API_PORT=5000
DASHBOARD_PORT=3000
DB_PORT=3306

# API URL (for dashboard to reach API)
VITE_API_URL=http://localhost:5000
```

## Common Commands

### Using Helper Scripts
```bash
./start.sh up        # Start services
./start.sh down      # Stop services
./start.sh restart   # Restart services
./start.sh logs app  # View API logs
./start.sh health    # Check health
./start.sh help      # Show all commands
```

### Using Docker Compose Directly
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f app

# Restart specific service
docker-compose restart app

# Scale services (replicas)
docker-compose up -d --scale app=3

# View status
docker-compose ps
```

## Accessing Your Application

### From Same Network
```
Dashboard: http://localhost:3000
API:       http://localhost:5000
Database:  localhost:3306
```

### From Different Machine
```
Dashboard: http://<machine-ip>:3000
API:       http://<machine-ip>:5000
Database:  <machine-ip>:3306
```

### From Cloud Server
```
Dashboard: http://<server-ip>:3000
API:       http://<server-ip>:5000
```

## Security for Production

⚠️ **Important**: Don't use default credentials in production!

### Security Checklist
```bash
# 1. Change database password
DB_PASSWORD=YourSecurePassword123!

# 2. Use HTTPS
VITE_API_URL=https://api.yourdomain.com

# 3. Add firewall rules
# - Only expose port 3000 to trusted IPs
# - Keep ports 5000, 3306 internal only

# 4. Use reverse proxy (Nginx, Caddy)
# - Handles SSL certificates
# - Better performance
# - Request routing

# 5. Regular backups
docker-compose exec db mysqldump -u root -p$DB_PASSWORD $DB_NAME > backup.sql
```

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :3000           # Mac/Linux
netstat -ano | findstr 3000  # Windows

# Change port in .env and restart
DASHBOARD_PORT=8080
docker-compose restart
```

### Services Won't Start
```bash
# View detailed logs
docker-compose logs

# Check Docker daemon is running
docker ps

# Rebuild containers
docker-compose down
docker-compose up -d --build
```

### Database Connection Failed
```bash
# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db

# Verify password is correct in .env
```

### Out of Disk Space
```bash
# Clean up unused Docker resources
docker system prune -a

# Check disk usage
docker system df
```

## Performance Tips

### For Local Development
```bash
# Use development mode
NODE_ENV=development
```

### For Production
```bash
# Use production mode
NODE_ENV=production

# Limit CPU/Memory
docker-compose.yml:
  services:
    app:
      deploy:
        resources:
          limits:
            cpus: '0.5'
            memory: 512M
```

### Scaling
```bash
# Run multiple API instances
docker-compose up -d --scale app=3

# Add load balancer (Nginx)
# Distribute traffic across instances
```

## File Structure

```
edubrowser/
├── docker-compose.yml      # Container orchestration
├── .env                    # Environment variables (create from .env.example)
├── .env.example            # Template for environment variables
├── .dockerignore           # Files to exclude from builds
├── Dockerfile              # API server image definition
├── start.sh               # Linux/Mac startup script
├── start.bat              # Windows startup script
├── DEPLOYMENT.md          # Detailed deployment guide
│
├── api_server.py          # Flask API server
├── authentication.py      # Auth logic
├── requirements.txt       # Python dependencies
│
└── react-dashboard/       # React frontend
    ├── Dockerfile
    ├── package.json
    └── src/
```

## Support

- **Issues**: Check `docker-compose logs` for error messages
- **Configuration**: Edit `.env` file
- **Documentation**: See `DEPLOYMENT.md` for advanced setup
- **API Docs**: Visit http://localhost:5000 after starting

## Next Steps

1. ✅ **Test Locally**: Run `start.sh` or `start.bat`
2. 📝 **Customize**: Edit `.env` with your settings
3. 🚀 **Deploy**: Push to cloud provider
4. 🔒 **Secure**: Update passwords and enable HTTPS
5. 📊 **Monitor**: Check logs regularly

---

**Your application is now truly portable and production-ready!** 🎉
