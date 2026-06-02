# DCES Core System

A secure, centralized, and role-based custom browsing environment designed specifically for educational and localized administration use. The application enforces website restrictions, captures browsing analytics, and offers unified management tools for students, teachers, administrators, and super-administrators.

## System Architecture

The project consists of three tightly integrated components:

### 1. **Qt Desktop Browser Application (`/qtapp`)**
A custom web browser client built with **Python & PyQt6 (QtWebEngine)**. It forces users into specific profiles (Modes) securely logging usage activity natively whilst rendering the dashboard overlays. Supports Gmail OAuth & direct credential auth.

### 2. **React Admin Dashboard (`/Browser_dashboard/react-dashboard`)**
A centralized visual interface built with **React (TypeScript), Vite, Tailwind CSS, & ShadCN/ui**. It retrieves and visualizes all logged activity dynamically while processing administrative actions like database interactions, approval of user roles, & blocking domains.

### 3. **PHP API Backend (`/Browser_dashboard/react-dashboard/php-api`)**
A REST API written in vanilla **PHP 8**. It scales as the bridge mapping all incoming connections from the Desktop Browser logs, and React Admin interface directly securely to the singular **MySQL DB**. Both systems share identical JWT logic & secret keys to unify sessions.

---

## Repository Structure

```text
Browser_sys/
├── qtapp/                            # The Desktop Client (Python)
│   ├── main.py                       # Application Entry Point
│   ├── browser.py                    # Core rendering window (PyQt6 WebEngineView)
│   ├── authentication.py             # User DB sync, JWT parsing, Role assignment
│   ├── dashboard_window.py           # Injects React dashboard inside the client
│   ├── management_window.py          # Native admin control panel for 15 DB Tables
│   ├── requirements.txt              # Pip dependencies 
│   └── tests/                        # Headless wrappers bypassing Browser rendering
│       ├── test_superadmin_dashboard.py
│       ├── test_admin_dashboard.py
│       ├── test_teacher_dashboard.py
│       └── test_student_dashboard.py
├── Browser_dashboard/ 
│   └── react-dashboard/              # The Frontend Dashboard (React/Node)
│       ├── src/                      # TS and React UI Components
│       ├── package.json              # Dashboard NPM dependencies
│       └── php-api/                  # The Backend API Router (PHP)
│           ├── index.php             # Request Router
│           └── handlers/             # Endpoints for Users, Activity, Auth, etc.
├── docs/                             # Additional Documentation
└── database/                         # (Conceptual) DB mapping logic & tables
```

---

## Running The Project

### Option A: Running the Python Desktop Application (DCES)

**Prerequisites:** Python 3.10+, pip
1. Navigate to the `qtapp` directory:
   ```bash
   cd qtapp
   ```
2. Setup the python virtual environment & requirements:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or `.\venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```
3. Set your environment variables:
   Ensure you parse `.env` setting `DB_HOST`, `DB_USER`, `DB_PASSWORD` & `JWT_SECRET` (Must match exact PHP JWT config). 
4. Launch the application:
   ```bash
   python main.py
   ```

### Option B: Running the React Dashboard Locally

**Prerequisites:** Node.js v18+, NPM/Bun
1. Navigate into the front-end tracking dashboard:
   ```bash
   cd Browser_dashboard/react-dashboard
   ```
2. Install NodeJS Dependencies natively:
   ```bash
   npm install
   ```
3. Boot the local React-Vite Dev Server:
   ```bash
   npm run dev
   ```

---

## Built-in Test Users & Roles

The system uses RBAC (Role-Based Access Control). Students are monitored and severely restricted, whereas Teachers/Admins have dashboard access to review usages.

Use the established **Testing Credentials** to safely analyze different levels of visibility:

| Username | Password | Role | Features |
|---|---|---|---|
| `superadmin1` | `superadmin123!` | **Superadmin** | Has access to modify DB tables, change system states. |
| `admin` | `admin123!` | **Superuser** | Unrestricted access across testing environment views. |
| `admintest` | `admintest123!` | **Admin** | Manages students & teachers, reviews logs. |
| `abhinavteacher`| `abhinavteacher123!` | **Teacher** | Overviews class data, assigns domains to whitelists. |
| `userstudent` | `userstudent123!` | **Student** | Monitored access, lacks access to dashboard bypass. |

---

## Bypassing the Desktop Browser for Dashboard Testing

If you are tweaking the UI or API and need to test the Dashboard rendering **without** launching the full Qt browser overhead, standalone python bypass scripts are provided in the qtapp `tests/` directory:

1. Launch your python environment.
2. Run any role directly into its dashboard state:
   ```bash
   python qtapp/tests/test_teacher_dashboard.py
   ```
   *(This immediately executes DB `Authentication`, verifies the JWT securely, generates the Device Session layout natively, and loads the PyQt Dashboard Window wrapper).*

---

## Production PHP & Deployment

For production (e.g. Hostinger integration):
- Build the Dashboard `npm run build` locally, uploading `/dist/` into standard hosting paths.
- Upload `/php-api/` intact into your target API Subdomain (`api.domain.com`). 
- Check the fully detailed API setup located in `Browser_dashboard/react-dashboard/DEPLOYMENT.md` for specific MySQL connection configurations, PHP headers, & CORS enforcement.
