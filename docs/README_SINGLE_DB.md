# Single Database Configuration

## ✅ Migration Complete

The system now uses a **single database** (`edubrowser`) with all tables instead of multiple databases.

## Database Structure

**Database Name:** `edubrowser`

**All Tables:**
- `Users` - Authentication & user accounts
- `Devices` - Device tracking
- `Sessions` - Active sessions
- `DashboardTokens` - Dashboard authorization
- `Students` - Student profiles
- `TimeWindows` - Time restrictions
- `ModeHistory` - Mode change history
- `WhitelistDomains` - Allowed domains
- `BlacklistDomains` - Blocked domains
- `ActivityLogs` - Browsing activity
- `Violations` - Security violations
- `TeacherActions` - Teacher audit log
- `AdminActions` - Admin audit log
- `WarningTriggers` - Escalation tracking
- `DashboardLogs` - Dashboard usage

## Configuration

### Environment Variables

```env
DB_HOST=localhost        # or 'db' for Docker
DB_USER=root
DB_PASSWORD=Innovation
DB_NAME=edubrowser
```

### Python Code

```python
from authentication import Authentication

auth = Authentication(
    host="localhost",    # or "db" in Docker
    user="root",
    password="Innovation",
    database="edubrowser"
)
```

## Setup

1. **Create database:**
   ```bash
   python setup_databases.py
   ```

2. **Populate sample data:**
   ```bash
   python populate_sample_data.py
   ```

3. **Run application:**
   ```bash
   python main.py
   ```

## Docker Configuration

The `docker-compose.yml` is already configured for single database. Just make sure:

```env
DB_NAME=edubrowser
```

All services will use the same database with different tables.

