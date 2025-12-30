# Fix: Unknown MySQL server host 'db'

## Problem

When running `setup_databases.py` or `populate_sample_data.py` on your host machine, you get:
```
❌ Database setup failed: 2005 (HY000): Unknown MySQL server host 'db' (11001)
```

## Cause

The error occurs because your `.env` file (or environment) has `DB_HOST=db`, which is the Docker container name. This hostname only works **inside Docker containers**, not on your host machine.

## Solution

### Option 1: Use localhost explicitly (Recommended for host machine)

When running scripts on your **host machine**, make sure to use `localhost`:

**Create or update `.env` file:**
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=Innovation
AUTH_DB=edubrowser_auth
STUDENT_DB=edubrowser_students
ACTIVITY_DB=edubrowser_activity
```

**Or run without .env file** (scripts default to localhost):
```bash
# Remove or rename .env if it has DB_HOST=db
mv .env .env.docker
python setup_databases.py
```

### Option 2: Use environment variable

Override the host when running:

**Windows PowerShell:**
```powershell
$env:DB_HOST="localhost"; python setup_databases.py
```

**Windows CMD:**
```cmd
set DB_HOST=localhost && python setup_databases.py
```

**Mac/Linux:**
```bash
DB_HOST=localhost python setup_databases.py
```

### Option 3: Updated Scripts (Auto-detect)

The scripts have been updated to automatically detect if you're running on host machine and use `localhost` even if `.env` says `db`.

## Quick Fix Commands

**For setup_databases.py:**
```bash
# Windows
set DB_HOST=localhost && python setup_databases.py

# Mac/Linux
DB_HOST=localhost python setup_databases.py
```

**For populate_sample_data.py:**
```bash
# Windows
set DB_HOST=localhost && python populate_sample_data.py

# Mac/Linux
DB_HOST=localhost python populate_sample_data.py
```

## Understanding the Setup

### Host Machine (Your Computer)
- Use: `localhost` or `127.0.0.1`
- When: Running Python scripts directly
- Examples: `setup_databases.py`, `populate_sample_data.py`, `main.py`

### Docker Containers
- Use: `db` (container name)
- When: Services running inside Docker
- Examples: `api_server.py` in Docker, React dashboard in Docker

## Complete Setup Workflow

**1. Start Docker services:**
```bash
docker-compose up -d
```

**2. Wait for database to be ready (30-60 seconds)**

**3. Run setup scripts on host (use localhost):**
```bash
# Windows
set DB_HOST=localhost && python setup_databases.py
set DB_HOST=localhost && python populate_sample_data.py

# Mac/Linux
DB_HOST=localhost python setup_databases.py
DB_HOST=localhost python populate_sample_data.py
```

**4. Run PyQt6 application on host:**
```bash
python main.py
```

## Verify Connection

Test if you can connect:
```bash
# Windows
mysql -h localhost -u root -pInnovation -e "SHOW DATABASES;"

# Mac/Linux (if mysql client installed)
mysql -h localhost -u root -pInnovation -e "SHOW DATABASES;"
```

Or using Docker:
```bash
docker-compose exec db mysql -uroot -pInnovation -e "SHOW DATABASES;"
```

## Summary

- **Host machine scripts** → Use `localhost`
- **Docker containers** → Use `db`
- **Default** → Scripts default to `localhost` if no `.env` file
- **Auto-detect** → Updated scripts automatically handle this

The scripts now automatically detect if you're on host machine and use `localhost` even if `.env` has `DB_HOST=db`.

