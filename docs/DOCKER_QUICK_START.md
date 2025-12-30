# 🚀 Docker Quick Start

Get up and running in 3 simple steps!

## Step 1: Start Services

```powershell
docker-compose up -d
```

## Step 2: Initialize Database (First Time Only)

```powershell
python docker_setup_database.py
$env:DB_HOST="localhost"; $env:DB_PORT="3307"; python populate_sample_data.py
```

## Step 3: Run Application

```powershell
$env:DB_HOST="localhost"; $env:DB_PORT="3307"; python main.py
```

## ✅ That's It!

- **Dashboard:** http://localhost:3000
- **API:** http://localhost:5000
- **Database:** localhost:3307

## 🛑 Stop Services

```powershell
docker-compose down
```

## 🔍 Check Status

```powershell
docker-compose ps
docker-compose logs -f
```

---

For detailed instructions, see [HOW_TO_RUN_WITH_DOCKER.md](HOW_TO_RUN_WITH_DOCKER.md)

