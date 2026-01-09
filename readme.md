# Secure Academic Desktop Browser System

A comprehensive PyQt6-based secure academic browser system with role-based access control, Gmail OAuth authentication, strict mode enforcement, device-level tracking, and a React-based dashboard.

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Start services:**
   ```powershell
   docker-compose up -d
   ```

2. **Initialize database:**
   ```powershell
   python database/setup_databases.py
   $env:DB_HOST="localhost"; $env:DB_PORT="3307"; python database/populate_sample_data.py
   ```

3. **Run application:**
   ```powershell
   .\scripts\run_with_docker.ps1
   ```

4. **Login:**
   - Username: `admin`
   - Password: `admin123!`
   - **Note:** Admin users do NOT require approval - they can login immediately.

### Local Setup

1. **Setup database:**
   ```powershell
   python database/setup_databases.py
   python database/populate_sample_data.py
   ```

2. **Run application:**
   ```powershell
   python main.py
   ```

## 📁 Project Structure

```
Browser_sys/
├── main.py                 # Application entry point
├── browser.py              # PyQt6 browser UI
├── authentication.py       # User authentication & management
├── gmail_oauth.py          # Gmail OAuth integration
├── mode_enforcement.py     # Browser mode enforcement
├── api_server.py           # Flask API server
├── admin_dashboard.py      # Dashboard window component
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker orchestration
├── Dockerfile              # Python API Dockerfile
│
├── database/               # Database files
│   ├── init_single_db.sql        # Database schema
│   ├── setup_databases.py        # Database setup script
│   ├── populate_sample_data.py   # Sample data population
│   ├── docker_setup_database.py  # Docker DB setup
│   └── create_admin_quick.py     # Create admin user
│
├── scripts/                # Helper scripts
│   ├── run_with_docker.ps1       # Run app with Docker MySQL
│   ├── run_with_docker.bat       # Windows batch version
│   └── ...other helper scripts
│
├── docs/                   # Documentation
│   ├── CURSOR_PROMPT.md          # Complete project generation prompt
│   ├── HOW_TO_RUN_WITH_DOCKER.md # Docker setup guide
│   ├── LOGIN_GUIDE.md            # Login instructions
│   ├── ADMIN_APPROVAL_POLICY.md  # Approval policy documentation
│   └── ...other documentation
│
└── react-dashboard/        # React dashboard frontend
    ├── src/
    ├── Dockerfile
    └── package.json
```

## 🔑 Default Credentials

- **Admin:** `admin` / `admin123!` ⚠️ **No approval required**
- **Teachers:** `teacher1`-`teacher3` / `teacher123` ⚠️ **Require admin approval**
- **Students:** `student1`-`student10` / `student123` ⚠️ **No approval required**

## 👥 User Roles & Approval

| Role | Approval Required | Notes |
|------|-------------------|-------|
| **Admin** | ❌ NO | Can login immediately, full access |
| **Super Admin** | ❌ NO | Can login immediately, absolute control |
| **Student** | ❌ NO | Can login immediately, browser access only |
| **Teacher** | ✅ YES | Must be approved by admin before login |

**Important:** Only Teachers require approval. Admin, Super Admin, and Student users can login immediately without any approval workflow.

See `docs/ADMIN_APPROVAL_POLICY.md` for detailed information.

## 📚 Documentation

See the `docs/` folder for comprehensive documentation:
- **HOW_TO_RUN_WITH_DOCKER.md** - Complete Docker setup guide
- **LOGIN_GUIDE.md** - Login instructions and credentials
- **GOOGLE_OAUTH_SETUP.md** - Gmail OAuth configuration
- **DASHBOARD_TROUBLESHOOTING.md** - Troubleshooting guide
- **ADMIN_APPROVAL_POLICY.md** - Approval policy details
- **CURSOR_PROMPT.md** - Complete project generation prompt

## 🐳 Docker Services

- **MySQL Database:** Port 3307
- **Flask API:** Port 5000
- **React Dashboard:** Port 3000

## 🛠️ Key Features

- ✅ Role-based access control (Student, Teacher, Admin, Super Admin)
- ✅ Gmail OAuth authentication
- ✅ Browser mode enforcement (Exam, Study, Restricted, Free)
- ✅ Device tracking and activity monitoring
- ✅ Real-time dashboard with charts and statistics
- ✅ Violation tracking and logging
- ✅ Multi-database architecture
- ✅ Docker support
- ✅ Admin users don't require approval

## 📝 Requirements

- Python 3.13+
- MySQL 9.1+
- Docker Desktop (for Docker setup)
- Node.js (for React dashboard development)

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:
- Database credentials
- Google OAuth credentials (optional)
- JWT secret

## 📖 More Information

See `docs/` folder for detailed documentation on setup, deployment, and usage.

---

**Built with:** PyQt6, Flask, React, TypeScript, MySQL, Docker
