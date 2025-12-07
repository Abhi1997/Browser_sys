# Browser_sys

A PyQt6-based web browser with user authentication, role-based access control, and URL filtering (whitelist/blacklist).

## Current Progress (as of 2025-12-05)

### Project Structure

- `browser.py` — Contains UI classes: `BrowserTab`, `LoginWindow`, and `MainWindow`.
- `main.py` — Application entry point that creates the `QApplication` and runs the `LoginWindow` and `MainWindow`.
- `authentication.py` — Handles user authentication and database operations.
- `intial_setup.py` — Script to initialize the database with an admin user.
- `.venv/` — Virtual environment containing all project dependencies.
- `requirements.txt` — Pinned dependency list.

### Key Features

- **User Authentication**: Login system with username and password validation.
- **Role-Based Access Control**: Supports four user roles:
  - `super-admin` — Full system access.
  - `admin` — Administrative features.
  - `teacher` — Teacher-specific features.
  - `student` — Student-specific features.
- **MySQL Database Integration**: Stores user credentials, whitelist, and blacklist.
- **Web Browsing**: Basic web browsing functionality with tabs, navigation, and zoom controls.

### Database Schema

The project uses a MySQL 9.1.0 database with the following tables.

#### Users Table
```sql
CREATE TABLE Users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    permissions TEXT,
    role ENUM('teacher', 'admin', 'student', 'super-admin') NOT NULL,
    last_login DATETIME,
    group_code VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

#### Whitelist Table
```sql
CREATE TABLE Whitelist (
    id INT PRIMARY KEY AUTO_INCREMENT,
    url TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    added_by INT,
    FOREIGN KEY (added_by) REFERENCES Users (id)
);
```

#### Blacklist Table
```sql
CREATE TABLE Blacklist (
    id INT PRIMARY KEY AUTO_INCREMENT,
    url TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    added_by INT,
    FOREIGN KEY (added_by) REFERENCES Users (id)
);
```

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- MySQL 9.1.0 or higher
- pip (Python package manager)

### Steps

1. **Clone the repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd Browser_sys
   ```

2. **Create and activate the virtual environment**:

   **macOS/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   **Windows (PowerShell):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the MySQL database**:
   - Create the `edubrowser` database:
     ```sql
     CREATE DATABASE edubrowser;
     ```
   - Create the required tables using the schema provided above.
   - Ensure the MySQL user has appropriate permissions (example using `root`):
     ```sql
     GRANT ALL PRIVILEGES ON edubrowser.* TO 'root'@'localhost' IDENTIFIED BY 'Innovation';
     FLUSH PRIVILEGES;
     ```

5. **Initialize the database with an admin user**:
   ```bash
   python intial_setup.py
   ```

   This will create an `admin` user with the following credentials (change in production):
   - Username: `admin`
   - Password: `admin123`
   - Role: `super-admin`

6. **Run the application**:
   ```bash
   python main.py
   ```

## How to Run

### macOS/Linux

1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Run the application:
   ```bash
   python main.py
   ```

### Windows (PowerShell)

1. Set execution policy (if needed):
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
   ```

2. Activate the virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. Run the application:
   ```powershell
   python main.py
   ```

### Windows (Command Prompt)

1. Activate the virtual environment:
   ```cmd
   venv\Scripts\activate
   ```

2. Run the application:
   ```cmd
   python main.py
   ```

## Troubleshooting

### MySQL Connection Error

**Error**: `Access denied for user 'root'@'localhost' (using password: YES)`

**Solution**:
1. Verify MySQL credentials in 

authentication.py

 or when instantiating `Authentication`:
   ```python
   auth = Authentication(host="localhost", user="root", password="Innovation", database="edubrowser")
   ```
2. Ensure the `edubrowser` database exists and the user has privileges.
3. Create a dedicated DB user if necessary:
   ```sql
   CREATE USER 'browser_user'@'localhost' IDENTIFIED BY 'secure_password';
   GRANT ALL PRIVILEGES ON edubrowser.* TO 'browser_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

### Role / Enum or Constraint Errors

If you get errors inserting a role (e.g., "Data truncated for column 'role'"), confirm the role column allows the value (`super-admin`) or adjust the column definition to use ENUM or VARCHAR and validate in application code.

### `id` Column Errors

If MySQL complains "Field 'id' doesn't have a default value", ensure `id` is defined with `AUTO_INCREMENT`:
```sql
ALTER TABLE Users MODIFY id INT NOT NULL AUTO_INCREMENT;
```

### PyQt6 Import Errors

Ensure `PyQt6` and `PyQt6-WebEngine` are installed:
```bash
pip install PyQt6==6.10.0 PyQt6-WebEngine==6.10.0
```

### Python Interpreter Issues (VS Code)

1. Open Command Palette: `Cmd+Shift+P`.
2. Select `Python: Select Interpreter`.
3. Choose the interpreter from the `.venv/` directory.

## Requirements

All dependencies are listed in 

requirements.txt

:

```
PyQt6==6.10.0
PyQt6-WebEngine==6.10.0
PyQt6-sip==13.8.0
mysql-connector-python==9.0.0
```

To install all requirements:
```bash
pip install -r requirements.txt
```

## Features & Functionalities

### Browser Features
- **Tab Management**: Open multiple tabs with `Ctrl+T`, close tabs with `Ctrl+W`.
- **Navigation**: Back, Forward, Reload, and Home buttons.
- **URL Bar**: Enter URLs and search queries.
- **Zoom Controls**: Adjust zoom level from 50% to 200%.
- **Status Bar**: Display page loading status.

### Authentication Features
- **Login Window**: Secure login with username and password.
- **User Validation**: Checks user credentials against the database.
- **Last Login Tracking**: Records the last login time for each user.
- **Role-Based Access**: Different permissions for different user roles.

### Database Features
- **User Management**: Store user credentials with hashed passwords.
- **URL Filtering**: Whitelist and blacklist URLs for content control.
- **Audit Trail**: Track user login history and URL access.

## Future Enhancements

- URL filtering using the Whitelist and Blacklist tables.
- Role-based access to browser features.
- User management dashboard for admins.
- Session management and logout functionality.
- Student monitoring and activity logging.
- Advanced content filtering and parental controls.
- Multi-language support.

## Project Structure

```
Browser_sys/
├── .venv/                    # Virtual environment
├── .vscode/
│   └── settings.json         # VS Code settings
├── browser.py               # UI classes (BrowserTab, LoginWindow, MainWindow)
├── main.py                  # Application entry point
├── authentication.py        # Authentication and database operations
├── intial_setup.py          # Database initialization script
├── requirements.txt         # Project dependencies
└── README.md               # This file
```

## API & Class Documentation

### Authentication Class

**File**: 

authentication.py



**Methods**:
- `__init__(host, user, password, database)` — Initialize database connection.
- `register_user(username, password, role, permissions, group_code)` — Register a new user.
- `validate_user(username, password)` — Validate user credentials and return role.

### BrowserTab Class

**File**: 

browser.py



**Methods**:
- `__init__(parent)` — Initialize browser tab with web engine view.
- `on_url_changed(qurl)` — Handle URL changes.
- `on_title_changed(title)` — Handle page title changes.
- `on_load_finished(ok)` — Handle page load completion.

### LoginWindow Class

**File**: 

browser.py



**Methods**:
- `__init__()` — Initialize login dialog.
- `handle_login()` — Process login form submission.

### MainWindow Class

**File**: 

browser.py



**Methods**:
- `__init__()` — Initialize main browser window.
- `setup_toolbar()` — Set up navigation toolbar.
- `setup_menu()` — Set up menu bar.
- `add_tab()` — Open a new browser tab.
- `close_tab(index)` — Close a browser tab.
- `navigate_to_url()` — Navigate to URL from address bar.
- `navigate_home()` — Navigate to home page (Google).
- `on_zoom_changed(text)` — Handle zoom level changes.

## Usage Examples

### Creating a New User (Admin)
```python
from authentication import Authentication

auth = Authentication(host="localhost", user="root", password="Innovation", database="edubrowser")
auth.register_user("teacher_user", "password123", "teacher", permissions="basic", group_code="CLASS_A")
```

### Validating User Login
```python
role = auth.validate_user("admin", "admin123")
if role:
    print(f"Login successful! Role: {role}")
else:
    print("Login failed!")
```

## Contributions

Abhinav Paudel


## License

This project is licensed under Abhinav Paudel.

## Contact & Support

For issues, questions, or suggestions, please open an issue on the project repository.

---

**Last Updated**: 2025-12-07  
**Maintainer**: Abhinav Paudel  
**Status**: Under Development