# 📁 Project Structure

## Directory Organization

### Root Directory
Essential application files kept at root level:

```
Browser_sys/
├── main.py                 # Application entry point
├── browser.py              # PyQt6 browser UI components
├── authentication.py       # User authentication & management
├── gmail_oauth.py          # Gmail OAuth integration
├── mode_enforcement.py     # Browser mode enforcement engine
├── api_server.py           # Flask REST API server
├── admin_dashboard.py      # Dashboard window component
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker orchestration configuration
├── Dockerfile              # Python API Docker image
├── README.md               # Main project documentation
└── .gitignore              # Git ignore rules
```

### database/
Database-related files:

```
database/
├── init_single_db.sql           # Complete database schema
├── setup_databases.py           # Database initialization script
├── populate_sample_data.py      # Sample data population script
├── docker_setup_database.py     # Docker MySQL setup script
└── create_admin_quick.py        # Quick admin user creation
```

### scripts/
Helper and utility scripts:

```
scripts/
├── run_with_docker.ps1          # Run app with Docker MySQL (PowerShell)
├── run_with_docker.bat          # Run app with Docker MySQL (CMD)
├── docker-quick-start.bat       # Quick Docker start (Windows)
├── docker-quick-start.sh        # Quick Docker start (Linux/Mac)
├── start.bat                    # Start services script
├── start.sh                     # Start services script (Linux/Mac)
├── start_all.bat                # Start all services
├── start_all.ps1                # Start all services (PowerShell)
├── create_admin_user.py         # Interactive admin user creation
├── add_test_users.py            # Add test users script
└── intial_setup.py              # Initial setup script
```

### docs/
All documentation files:

```
docs/
├── CURSOR_PROMPT.md                  # Complete project generation prompt
├── HOW_TO_RUN_WITH_DOCKER.md         # Comprehensive Docker guide
├── QUICK_START_DOCKER.md             # Quick Docker reference
├── LOGIN_GUIDE.md                    # Login instructions
├── GOOGLE_OAUTH_SETUP.md             # Gmail OAuth setup guide
├── DASHBOARD_TROUBLESHOOTING.md      # Dashboard troubleshooting
├── ADMIN_LOGIN_FIXED.md              # Admin login fix documentation
├── LOGIN_CREDENTIALS.txt             # Credentials reference
├── test_users_credentials.txt        # Test user credentials
└── ...other documentation files
```

### react-dashboard/
React dashboard frontend application:

```
react-dashboard/
├── src/                        # Source code
│   ├── pages/                  # Page components
│   ├── components/             # React components
│   ├── hooks/                  # Custom hooks
│   ├── lib/                    # Utilities and API
│   └── contexts/               # React contexts
├── public/                     # Static assets
├── Dockerfile                  # Dashboard Docker image
├── package.json                # Node.js dependencies
└── vite.config.ts             # Vite configuration
```

## File Naming Conventions

- **Core application files:** snake_case (e.g., `browser.py`, `api_server.py`)
- **Database files:** snake_case with descriptive names (e.g., `setup_databases.py`)
- **Scripts:** snake_case or kebab-case (e.g., `run_with_docker.ps1`)
- **Documentation:** UPPER_CASE with underscores (e.g., `HOW_TO_RUN_WITH_DOCKER.md`)

## Quick Access

**Start application:**
```powershell
.\scripts\run_with_docker.ps1
```

**Setup database:**
```powershell
python database/setup_databases.py
python database/populate_sample_data.py
```

**View documentation:**
```powershell
# Main guide
docs/HOW_TO_RUN_WITH_DOCKER.md

# Login help
docs/LOGIN_GUIDE.md

# Troubleshooting
docs/DASHBOARD_TROUBLESHOOTING.md
```

## Notes

- Core application files remain in root for easy access
- Related files are grouped in logical folders
- Documentation is centralized in `docs/` folder
- Scripts are organized in `scripts/` folder
- Database files are in `database/` folder
- Old/unused files have been removed

