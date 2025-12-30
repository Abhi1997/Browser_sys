# ⚡ Quick Start with Docker

## 1️⃣ Start Docker Services

```powershell
docker-compose up -d
```

Wait 30 seconds, then check:
```powershell
docker-compose ps
```

## 2️⃣ Run Your Application

```powershell
$env:DB_HOST="localhost"; $env:DB_PORT="3307"; python main.py
```

**Or use the helper script:**
```powershell
.\run_with_docker.ps1
```

## 3️⃣ Access Services

- **Application:** Running in window
- **Dashboard:** http://localhost:3000
- **API:** http://localhost:5000

## 🛑 Stop Everything

```powershell
docker-compose down
```

---

**That's all!** 🎉

For more details, see [HOW_TO_RUN_WITH_DOCKER.md](HOW_TO_RUN_WITH_DOCKER.md)

