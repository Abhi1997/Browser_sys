# 📁 Project Folder Structure

## Clean Organization

The project has been organized into logical folders:

### Root Directory (`/`)
**Core application files** - Keep essential files at root for easy access:
- `main.py` - Application entry point
- `browser.py` - PyQt6 browser UI
- `authentication.py` - User authentication
- `gmail_oauth.py` - Gmail OAuth
- `mode_enforcement.py` - Mode enforcement
- `api_server.py` - Flask API
- `admin_dashboard.py` - Dashboard component
- `requirements.txt` - Dependencies
- `docker-compose.yml` - Docker config
- `Dockerfile` - Python API Dockerfile
- `README.md` - Main documentation

### `/database/`
**Database-related files:**
- `init_single_db.sql` - Database schema
- `setup_databases.py` - Setup script
- `populate_sample_data.py` - Sample data
- `docker_setup_database.py` - Docker DB setup
- `create_admin_quick.py` - Create admin user

**Usage:**
```powershell
python database/setup_databases.py
python database/populate_sample_data.py
```

### `/scripts/`
**Helper and utility scripts:**
- `run_with_docker.ps1` / `.bat` - Run app with Docker MySQL
- `docker-quick-start.bat` / `.sh` - Quick Docker start
- `start.bat` / `.sh` - Start services
- `create_admin_user.py` - Interactive admin creation
- `add_test_users.py` - Add test users
- Other utility scripts

**Usage:**
```powershell
.\scripts\run_with_docker.ps1
```

### `/docs/`
**All documentation:**
- `HOW_TO_RUN_WITH_DOCKER.md` - Docker guide
- `LOGIN_GUIDE.md` - Login instructions
- `GOOGLE_OAUTH_SETUP.md` - OAuth setup
- `DASHBOARD_TROUBLESHOOTING.md` - Troubleshooting
- `CURSOR_PROMPT.md` - Project generation prompt
- All other documentation files

### `/react-dashboard/`
**React dashboard frontend:**
- React + TypeScript application
- Source code in `src/`
- Dockerfile for containerization
- Package configuration

## File Paths

When running scripts from root directory:

**Database scripts:**
- `python database/setup_databases.py`
- `python database/populate_sample_data.py`

**Helper scripts:**
- `.\scripts\run_with_docker.ps1`
- `.\scripts\docker-quick-start.bat`

**Documentation:**
- `docs/HOW_TO_RUN_WITH_DOCKER.md`
- `docs/LOGIN_GUIDE.md`

## Removed Files

The following old/unused files were removed:
- `init_auth_db.sql` (replaced by init_single_db.sql)
- `init_student_db.sql` (replaced by init_single_db.sql)
- `init_activity_db.sql` (replaced by init_single_db.sql)
- `init_db.sql` (replaced by init_single_db.sql)
- `react-dashboard.zip` (unnecessary archive)

## Benefits

✅ **Clean root directory** - Only essential files
✅ **Logical organization** - Related files grouped together
✅ **Easy navigation** - Find files quickly
✅ **Better maintainability** - Clear structure
✅ **Professional appearance** - Organized project structure

