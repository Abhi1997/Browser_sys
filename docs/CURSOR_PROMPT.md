# 🎯 Complete Project Generation Prompt for Cursor

Copy and paste this entire prompt into Cursor to generate the complete Secure Academic Desktop Browser System:

---

## PROJECT: Secure Academic Desktop Browser System with Role-Based Dashboard

Build a complete PyQt6-based secure academic browser system with role-based access control, Gmail OAuth authentication, strict mode enforcement, device-level tracking, activity monitoring, and a React-based dashboard. The system should use a multi-database architecture with Docker support.

### 🏗️ ARCHITECTURE

**Desktop-First Design:**
- PyQt6 desktop application is the authority and system of record
- Authenticates users, sets browser modes, controls dashboard access
- Logs all activity, verifies device identity, issues dashboard tokens
- Dashboard is a controlled visualization interface, NOT authoritative
- Dashboard runs at http://localhost:3000, opens only when authorized by desktop app
- Dashboard must NOT be directly accessible (only through PyQt6 app)

**Multi-Database Architecture:**
1. **edubrowser** (single database with all tables):
   - Users, Roles, Devices, Sessions, DashboardTokens
   - Students, TimeWindows, ModeHistory
   - WhitelistDomains, BlacklistDomains
   - ActivityLogs, Violations, TeacherActions, AdminActions
   - WarningTriggers, DashboardLogs

**Services:**
- MySQL Database (Docker, port 3307)
- Flask API Server (Docker, port 5000)
- React Dashboard (Docker, port 3000)
- PyQt6 Desktop Application (runs locally, connects to Docker MySQL)

### 🔐 AUTHENTICATION SYSTEM

**Gmail OAuth Login:**
- Students: Gmail login only
- Teachers: Gmail login + Admin approval workflow (status: PENDING → APPROVED)
- Admins: Pre-registered + verification
- Super Admin: Hard-authorized

**Teacher Approval Workflow:**
- Teacher login → status = PENDING
- Admin approves → access granted
- All actions logged

**Login Methods:**
1. Username/Password (traditional)
2. Gmail OAuth (requires GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)
- Environment variables: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
- Redirect URI: http://localhost:8080/callback

**Default Admin User:**
- Username: `admin`
- Password: `admin123!`
- Role: `admin` (no approval required)
- teacher_approval_status: NULL (only teachers need approval)

### 👥 USER ROLES & PERMISSIONS

**Student:**
- Browser access with mode restrictions
- View assigned mode
- Cannot change settings
- No dashboard access
- Mode assigned by Teacher/Admin

**Teacher:**
- Browser access
- Dashboard access (localhost only, authorized by desktop app)
- View student activity
- Change student modes (limited)
- View violations
- Manage whitelist (limited)
- Cannot change user roles or modify admin data

**Admin:**
- Browser access
- Full dashboard access
- View all users and students
- Change any student mode
- View all violations
- Manage whitelist/blacklist
- View all activity logs
- User management
- Approve teachers
- Change roles
- Disable users
- Revoke dashboard access

**Super Admin:**
- All Admin capabilities
- Absolute control
- Emergency overrides

### 🌐 BROWSER MODES

**Four Modes with Strict Enforcement:**
1. **Exam Mode** - Highly restricted, only whitelisted educational domains
2. **Study Mode** - Educational domains + limited additional sites
3. **Restricted Mode** - Moderate restrictions
4. **Free Mode** - Minimal restrictions

**Mode Features:**
- Mode always visible (buttons + colors)
- Mode is NOT user-changeable (set by Teacher/Admin only)
- Attempted bypass → warning popup (serious, security-themed)
- Log event immediately
- Escalate on repeated violations
- Real-time URL filtering at browser engine level

### 🗄️ DATABASE SCHEMA

**Users Table:**
- id, username (UNIQUE), gmail (UNIQUE), password_hash
- role ENUM('student', 'teacher', 'admin', 'superadmin')
- teacher_approval_status ENUM('PENDING', 'APPROVED', 'REJECTED') DEFAULT NULL
- approved_by, approved_at, is_active, created_at, last_login

**Students Table:**
- id, student_id (UNIQUE), user_id (FK), gmail
- assigned_mode ENUM('exam', 'study', 'restricted', 'free')
- violation_count, device_id, ip_address, mac_address
- created_at, updated_at, is_active

**Devices Table:**
- id, device_id (UNIQUE), user_id (FK)
- ip_address, mac_address, device_fingerprint
- registered_at, last_seen, is_active

**WhitelistDomains & BlacklistDomains Tables:**
- id, domain, mode, description/reason
- added_by (FK), is_active, created_at

**ActivityLogs Table:**
- id, student_id, user_id, url, domain
- mode, visit_duration, visit_start, visit_end
- device_id, ip_address, mac_address, is_allowed, created_at

**Violations Table:**
- id, student_id, user_id, violation_type
- description, attempted_url, current_mode
- device_id, ip_address, mac_address, severity
- created_at

**DashboardTokens Table:**
- id, user_id, device_id, token, expires_at, is_active

**Other Tables:**
- Sessions, TimeWindows, ModeHistory, TeacherActions, AdminActions, WarningTriggers, DashboardLogs

### 🖥️ DESKTOP APPLICATION (PyQt6)

**Main Components:**
1. **LoginWindow (GmailLoginWindow)**:
   - Gmail OAuth button
   - Username/Password fields
   - Login button
   - Handles both authentication methods

2. **MainWindow**:
   - Browser tabs with QWebEngineView
   - Navigation toolbar (Back, Forward, Reload, Home, URL bar)
   - Dashboard button (for admin/teacher/superadmin)
   - Mode indicators (for students)
   - Security status bar
   - Loading screen after login
   - Professional styling with icons and colors

3. **BrowserTab**:
   - Web view with mode enforcement
   - URL change detection
   - Activity logging
   - Bypass warning popups

4. **DashboardWindow**:
   - QWebEngineView displaying React dashboard
   - Opens with token and deviceId in URL
   - URL format: `http://localhost:3000/#/dashboard/admin?token={token}&deviceId={deviceId}`

**Key Features:**
- Tab-based browsing
- URL bar with navigation
- Mode enforcement engine (ModeEnforcement class)
- Real-time URL filtering
- Activity logging
- Device tracking (IP, MAC, device fingerprint)
- Animated transitions
- Loading screens
- Security-themed UI (lock icons, warning colors)

### 📊 REACT DASHBOARD

**Framework:**
- React with TypeScript
- React Router (HashRouter)
- React Query for data fetching
- Tailwind CSS + shadcn/ui components
- Vite build tool

**Pages:**
1. **Index** - Landing/redirect page
2. **AdminDashboard** - Full admin interface
3. **TeacherDashboard** - Teacher interface
4. **SuperAdminDashboard** - Super admin interface
5. **Unauthorized** - Access denied page
6. **Loading** - Loading state
7. **NotFound** - 404 page

**Admin Dashboard Features:**
- Statistics cards (Total Users, Active Users, Students by Mode, Violations)
- User management table
- Student management table
- Violations table
- Whitelist/Blacklist management
- Charts:
  - Role distribution (pie chart)
  - Login activity (area chart)
  - Activity timeline
- Real-time data from Flask API

**Teacher Dashboard Features:**
- Class statistics
- Student list with mode management
- Activity monitoring
- Violations view
- Charts for class activity

**API Integration:**
- All data fetched from Flask API at http://localhost:5000
- Token-based authentication
- Device ID validation
- Protected routes based on role

### 🔧 API SERVER (Flask)

**Endpoints:**
- GET `/health` - Health check
- POST `/api/auth/verify-token` - Verify JWT token and device ID
- GET `/api/users` - Get all users
- GET `/api/stats` - Get statistics overview
- GET `/api/students` - Get all students
- PUT `/api/students/{id}/mode` - Update student mode
- GET `/api/violations` - Get violations
- GET `/api/whitelist` - Get whitelist entries
- POST `/api/whitelist` - Add whitelist entry
- DELETE `/api/whitelist/{id}` - Remove whitelist entry
- GET `/api/blacklist` - Get blacklist entries
- POST `/api/blacklist` - Add blacklist entry
- DELETE `/api/blacklist/{id}` - Remove blacklist entry
- GET `/api/activity` - Get activity logs
- GET `/api/teachers/{id}/classes` - Get teacher classes
- GET `/api/classes/{id}/activity` - Get class activity

**Features:**
- CORS enabled for React dashboard
- JWT token validation
- Device ID verification
- Error handling
- JSON responses

### 🐳 DOCKER SETUP

**docker-compose.yml:**
```yaml
services:
  db:
    image: mysql:9.1.0
    ports:
      - "3307:3306"  # Use 3307 to avoid conflict with local MySQL
    environment:
      MYSQL_ROOT_PASSWORD: Innovation
      MYSQL_DATABASE: edubrowser
    volumes:
      - db_data:/var/lib/mysql
      - ./init_single_db.sql:/docker-entrypoint-initdb.d/init_single_db.sql
    healthcheck: ...

  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      DB_HOST: db
      DB_USER: root
      DB_PASSWORD: Innovation
      DB_NAME: edubrowser
    depends_on:
      db:
        condition: service_healthy

  dashboard:
    build: ./react-dashboard
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:5000
    depends_on:
      - db
```

**Dockerfile (Python API):**
- Python 3.13-slim base
- Install requirements.txt
- Copy application files
- CMD: python api_server.py

**React Dashboard Dockerfile:**
- Node base image
- Install dependencies
- Build application
- Serve with Vite

### 📁 FILE STRUCTURE

```
Browser_sys/
├── main.py                    # Entry point
├── browser.py                 # PyQt6 browser UI (MainWindow, BrowserTab, LoginWindow)
├── authentication.py          # Authentication & user management
├── gmail_oauth.py             # Gmail OAuth integration
├── mode_enforcement.py        # Mode enforcement engine
├── api_server.py              # Flask API server
├── setup_databases.py         # Database initialization script
├── populate_sample_data.py    # Sample data population
├── create_admin_quick.py      # Create admin user script
├── requirements.txt           # Python dependencies
├── init_single_db.sql         # Database schema
├── docker-compose.yml         # Docker orchestration
├── Dockerfile                 # Python API Dockerfile
├── .env.example               # Environment variables template
├── react-dashboard/           # React dashboard frontend
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── contexts/
│   ├── Dockerfile
│   └── package.json
└── Documentation files...
```

### 📦 PYTHON DEPENDENCIES

```
mysql-connector-python==9.5.0
PyJWT==2.10.1
PyQt6==6.10.0
PyQt6-WebEngine==6.10.0
python-dotenv==1.2.1
Flask==3.0.0
Flask-CORS==4.0.0
requests==2.31.0
```

### 🎨 UI/UX REQUIREMENTS

**Desktop Application:**
- Professional PyQt6 styling
- Mode buttons with icons and colors:
  - Exam: Red/Lock icon
  - Study: Blue/Book icon
  - Restricted: Orange/Shield icon
  - Free: Green/Globe icon
- Tooltips on all buttons
- Loading screen after login (1.5s animation)
- Security status indicator in status bar
- Animated transitions
- Warning popups (serious, security-themed, red/orange colors)

**Dashboard:**
- Modern React UI with shadcn/ui components
- Dark/light theme support
- Responsive design
- Charts using recharts or similar
- Data tables with sorting/filtering
- Real-time updates where possible
- Professional color scheme

### 🔒 SECURITY FEATURES

- JWT token-based authentication
- Device fingerprinting (IP, MAC, device ID)
- Device registration required for dashboard
- Token expiration (24h for login, 1h for dashboard)
- Password hashing (SHA256)
- Role-based access control (RBAC)
- Mode enforcement at browser level
- Activity logging (all URLs, time spent, violations)
- Violation tracking and escalation
- Audit logs for admin/teacher actions

### 📝 SAMPLE DATA

Create scripts to populate:
- 10 students with different modes
- 3 teachers (approved)
- 1 admin user
- Activity logs (100-200 entries)
- Violations (10-30 entries)
- Whitelist/Blacklist entries
- Device registrations
- Mode history

**Default Credentials:**
- Admin: `admin` / `admin123!`
- Students: `student1`-`student10` / `student123`
- Teachers: `teacher1`-`teacher3` / `teacher123`

### ⚙️ ENVIRONMENT VARIABLES

```env
# Database
DB_HOST=localhost        # or 'db' for Docker
DB_PORT=3307            # Docker MySQL port
DB_USER=root
DB_PASSWORD=Innovation
DB_NAME=edubrowser

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# API
API_PORT=5000
VITE_API_URL=http://localhost:5000

# Dashboard
DASHBOARD_PORT=3000

# JWT
JWT_SECRET=your-secret-key-change-this
```

### 🚀 IMPLEMENTATION REQUIREMENTS

1. **Auto-detect environment**: Scripts should detect if running on host or in Docker
2. **Error handling**: Comprehensive error handling with user-friendly messages
3. **Logging**: Log all important events (logins, violations, mode changes)
4. **Windows compatibility**: Fix encoding issues for Windows console (emojis)
5. **Database port handling**: Support different ports for local vs Docker MySQL
6. **Helper scripts**: Create scripts for common tasks (setup, populate, run with Docker)

### 📚 DOCUMENTATION

Create comprehensive documentation:
- Setup guide
- Docker run guide
- Login guide
- Dashboard guide
- Troubleshooting guide
- Google OAuth setup guide
- API documentation

### ✅ TESTING & VERIFICATION

Ensure:
- Admin can login and access dashboard
- Dashboard displays real data from database
- Mode enforcement works correctly
- Violations are logged
- Device tracking works
- Token validation works
- All roles have correct permissions
- Docker services start correctly
- Database initializes properly

### 🎯 SUCCESS CRITERIA

The system is complete when:
1. ✅ PyQt6 application runs and login works
2. ✅ Admin can login with username/password
3. ✅ Dashboard opens when clicking Dashboard button
4. ✅ Dashboard shows real data (users, students, violations, charts)
5. ✅ Docker services all run successfully
6. ✅ Mode enforcement works (blocked URLs show warnings)
7. ✅ Activity logging works
8. ✅ Sample data populates correctly
9. ✅ All roles can login with appropriate permissions
10. ✅ Documentation is complete

---

## GENERATION INSTRUCTIONS

Generate the complete project with:
1. All Python files with complete implementations
2. Database schema SQL file
3. React dashboard with all components
4. Docker configuration files
5. Setup and population scripts
6. Helper scripts (run with Docker, create admin user, etc.)
7. Comprehensive documentation
8. Sample data population scripts
9. Error handling and logging
10. Windows compatibility fixes

Make sure all code is production-ready, well-commented, and follows best practices.

---

**END OF PROMPT**

