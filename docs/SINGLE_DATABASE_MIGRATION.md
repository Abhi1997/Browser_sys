# Single Database Migration

## ✅ Migration Complete

The system has been migrated from **multi-database architecture** to **single database architecture**.

### What Changed

**Before:**
- 3 separate databases: `edubrowser_auth`, `edubrowser_students`, `edubrowser_activity`

**After:**
- 1 database: `edubrowser` with all tables

### Database Structure

All tables are now in the `edubrowser` database:

#### Authentication & Security Tables
- `Users` - User accounts
- `Devices` - Device tracking
- `Sessions` - Active sessions
- `DashboardTokens` - Dashboard authorization

#### Student Control Tables
- `Students` - Student profiles
- `TimeWindows` - Time restrictions
- `ModeHistory` - Mode change history
- `WhitelistDomains` - Allowed domains
- `BlacklistDomains` - Blocked domains

#### Activity & Logs Tables
- `ActivityLogs` - Browsing activity
- `Violations` - Security violations
- `TeacherActions` - Teacher audit log
- `AdminActions` - Admin audit log
- `WarningTriggers` - Escalation tracking
- `DashboardLogs` - Dashboard usage

### Updated Files

1. **Database Schema**
   - `init_single_db.sql` - New consolidated schema
   - Removed: `init_auth_db.sql`, `init_student_db.sql`, `init_activity_db.sql`

2. **Python Code**
   - `authentication.py` - Updated to use single database
   - `mode_enforcement.py` - Updated connection methods
   - `populate_sample_data.py` - Updated to use single database
   - `setup_databases.py` - Updated to create single database
   - `api_server.py` - Updated database connections
   - `browser.py` - Updated Authentication initialization
   - `gmail_oauth.py` - Updated database name

3. **Docker Configuration**
   - `docker-compose.yml` - Updated to use single database init script

4. **Documentation**
   - `DOCKER_RUN_GUIDE.md` - Updated environment variables

### Configuration

**Environment Variables:**
```env
DB_HOST=localhost        # or 'db' for Docker
DB_USER=root
DB_PASSWORD=Innovation
DB_NAME=edubrowser
```

**Python Code:**
```python
auth = Authentication(
    host="localhost",
    user="root",
    password="Innovation",
    database="edubrowser"
)
```

### Migration Steps (If You Have Existing Data)

If you have existing data in the multi-database setup, you'll need to:

1. **Export data from old databases:**
   ```bash
   mysqldump -u root -pInnovation edubrowser_auth > auth_backup.sql
   mysqldump -u root -pInnovation edubrowser_students > students_backup.sql
   mysqldump -u root -pInnovation edubrowser_activity > activity_backup.sql
   ```

2. **Create new single database:**
   ```bash
   python setup_databases.py
   ```

3. **Import data (manually edit SQL files to remove CREATE DATABASE/USE statements):**
   ```bash
   mysql -u root -pInnovation edubrowser < auth_backup.sql
   mysql -u root -pInnovation edubrowser < students_backup.sql
   mysql -u root -pInnovation edubrowser < activity_backup.sql
   ```

### Benefits

✅ **Simpler setup** - One database to manage
✅ **Easier backups** - Single database backup
✅ **Better referential integrity** - Foreign keys work across all tables
✅ **Simpler configuration** - Fewer environment variables
✅ **Easier deployment** - Single database initialization

### Backward Compatibility

The code maintains backward compatibility by:
- Keeping `_get_auth_conn()`, `_get_student_conn()`, `_get_activity_conn()` as aliases to `_get_conn()`
- All three methods now return the same connection to `edubrowser` database

### Setup Instructions

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

All tables are now in the `edubrowser` database! 🎉

