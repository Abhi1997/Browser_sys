Perfect — here is a **fully rewritten, polished, production-ready `README.md`**, with clean structure, dashboard integration, setup instructions, architecture, and future plans.

You can copy and paste this directly into your repository.

---

# **Browser_sys**

A secure, role-based educational web browser built with **PyQt6**, **MySQL**, and an integrated **React dashboard** for administrative and teacher management tools.

Browser_sys provides a desktop environment for controlled web browsing with URL filtering, user authentication, role-based permissions, and system monitoring via a React-powered dashboard.

---

# 🚀 **Features**

## ✅ **1. Authentication & User Management**

* Login system with MySQL-backed credentials
* Secure password hashing
* User roles:

  * `super-admin` — full system access
  * `admin` — manages users and filters
  * `teacher` — classroom tools
  * `student` — restricted browsing
* Records last login timestamp
* Inactive user support

## ✅ **2. Role-Based Browser Access**

* Different UI controls depending on the user role
* Dashboard button shown only for:
  **super-admin**, **admin**, **teacher**

## ✅ **3. PyQt6 Browser**

* Built using `QWebEngineView`
* Multi-tab browsing
* Navigation (Back / Forward / Reload / Home)
* Search & URL bar
* Zoom controls (50%–200%)
* Status bar & title updating

## ✅ **4. URL Filtering**

* Whitelist & blacklist support
* MySQL-backed URL storage
* (Upcoming) live filtering during browsing

## ✅ **5. Admin / Teacher Dashboard**

A separate PyQt6 window embeds a **React-based dashboard** for:

* User management
* Whitelist/blacklist management
* System metrics
* Classroom tools for teachers
* Activity visualization (planned)

Dashboard loads via:

```
http://localhost:3000/?role=<role>&user=<username>
```

or from a production build:

```
file:///path/to/react-dashboard/dist/index.html?role=<role>&user=<username>
```

---

# 📁 **Project Structure**

```
Browser_sys/
├── browser.py               # UI: BrowserTab, LoginWindow, MainWindow, DashboardWindow
├── main.py                  # Application entry point
├── authentication.py        # User auth & MySQL operations
├── initial_setup.py         # Script to create first admin user
├── react-dashboard/         # React dashboard (Vite + React)
├── requirements.txt         # Python dependencies
├── .venv/                   # Virtual environment
└── README.md
```

---

# 🗄️ **Database Schema (MySQL 9.x)**

### **Users**

```sql
CREATE TABLE Users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    permissions TEXT,
    role ENUM('teacher','admin','student','super-admin') NOT NULL,
    last_login DATETIME,
    group_code VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

### **Whitelist**

```sql
CREATE TABLE Whitelist (
    id INT PRIMARY KEY AUTO_INCREMENT,
    url TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    added_by INT,
    FOREIGN KEY (added_by) REFERENCES Users(id)
);
```

### **Blacklist**

```sql
CREATE TABLE Blacklist (
    id INT PRIMARY KEY AUTO_INCREMENT,
    url TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    added_by INT,
    FOREIGN KEY (added_by) REFERENCES Users(id)
);
```

---

# 🛠️ **Installation & Setup**

## 1. Clone the repository

```bash
git clone <repository-url>
cd Browser_sys
```

## 2. Create virtual environment

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure MySQL

Create the database:

```sql
CREATE DATABASE edubrowser;
```

Grant privileges:

```sql
GRANT ALL PRIVILEGES ON edubrowser.* TO 'root'@'localhost' IDENTIFIED BY 'Innovation';
FLUSH PRIVILEGES;
```

Create tables (schema above).

## 5. Initialize admin user

```bash
python initial_setup.py
```

Default credentials (change in production!):

* Username: **admin**
* Password: **admin123**
* Role: **super-admin**

---

# 📊 **Dashboard (React)**

The dashboard is built using **Vite + React**, located inside:

```
react-dashboard/
```

### Install & Run (Development)

```bash
cd react-dashboard
npm install
npm run dev
```

Runs at:

```
http://localhost:3000
```

### Build for Production

```bash
npm run build
```

The built files appear in:

```
react-dashboard/dist/
```

### Dashboard Loading in Python

```python
url = f"http://localhost:3000/?role={role}&user={username}"
# or production build:
# url = f"file:///absolute/path/to/dist/index.html?role={role}&user={username}"
```

### Who Can Access the Dashboard?

| Role        | Dashboard Access |
| ----------- | ---------------- |
| super-admin | ✅ Full Access    |
| admin       | ✅ Admin Tools    |
| teacher     | ✅ Teacher Tools  |
| student     | ❌ No Access      |

---

# ▶️ **Running the Application**

Start the dashboard (optional):

```bash
cd react-dashboard
npm run dev
```

Run Browser_sys:

```bash
source venv/bin/activate
python main.py
```

---

# 🧰 **Troubleshooting**

### MySQL Errors

* *Access denied*: check credentials in `authentication.py`
* *Field 'id' doesn't have default*: ensure `AUTO_INCREMENT`
* *Invalid role inserted*: confirm ENUM matches role names

### PyQt6 Issues

Install WebEngine:

```bash
pip install PyQt6 PyQt6-WebEngine
```

### macOS WebEngine crashes

Set environment flags:

```bash
export QTWEBENGINE_DISABLE_SANDBOX=1
export QTWEBENGINE_CHROMIUM_FLAGS="--disable-gpu --no-sandbox"
```

---

# 📘 **API & Class Summary**

## `Authentication` (authentication.py)

* `register_user(username, password, role, permissions, group_code)`
* `validate_user(username, password)`
* MySQL connection & queries

## `BrowserTab` (browser.py)

* Handles tab browsing, loading, navigation, zoom, title updates

## `LoginWindow` (browser.py)

* Login UI
* Sends results to MainWindow

## `MainWindow` (browser.py)

* Hosts tab manager
* Toolbar & actions
* Dashboard button (role-based)

## `DashboardWindow` (browser.py)

* Loads and displays React dashboard

---

# 📅 **Roadmap**

* 🔒 Enforce whitelist/blacklist filtering
* 🧑‍🏫 Classroom monitoring tools
* 🧾 Activity logging (per student)
* 📚 Multi-language support
* 🏫 School-wide admin controls
* 🔐 Session timeout + logout
* 🧩 Extension-style plugin support

---

# 👤 **Maintainer**

**Abhinav Paudel**
*Last Updated: 2025-12-07
