# Database Configuration

## Current Setup

The system uses a **multi-database architecture** with the following databases:

1. **edubrowser_auth** - Authentication & Security Database
   - Users, roles, sessions
   - Devices, dashboard tokens

2. **edubrowser_students** - Student Control Database
   - Student profiles and modes
   - Whitelist/Blacklist
   - Mode history

3. **edubrowser_activity** - Activity & Logs Database
   - Activity logs
   - Violations
   - Teacher/Admin actions

## Database Credentials

- **Host**: localhost
- **User**: root
- **Password**: Innovation
- **Port**: 3306 (default)

## Configuration Files

All scripts use these defaults:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Innovation",
}
```

## Environment Variables

You can override defaults using `.env` file:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=Innovation
AUTH_DB=edubrowser_auth
STUDENT_DB=edubrowser_students
ACTIVITY_DB=edubrowser_activity
```

## Setup Instructions

1. **Create databases:**
   ```bash
   python setup_databases.py
   ```
   This creates all three databases with proper schemas.

2. **Populate sample data:**
   ```bash
   python populate_sample_data.py
   ```

## Verification

To verify the databases exist and password is correct:

```bash
mysql -u root -pInnovation -e "SHOW DATABASES LIKE 'edubrowser%';"
```

You should see:
- edubrowser_auth
- edubrowser_students
- edubrowser_activity

## Notes

- All scripts default to password: **Innovation**
- Multi-database architecture is required for the system to function properly
- Each database has specific tables and purposes (see individual init_*.sql files)

