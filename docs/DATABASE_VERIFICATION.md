# Database Verification Guide

## Quick Check

If you can't see data in DBeaver, follow these steps:

### 1. Verify Connection Settings

Make sure you're connected with these exact settings:

| Setting | Value |
|---------|-------|
| **Host** | `localhost` |
| **Port** | `3307` |
| **Database** | `edubrowser` (IMPORTANT: Select this database) |
| **Username** | `root` |
| **Password** | `Innovation` |

### 2. Select the Correct Database

In DBeaver:
1. After connecting, expand the connection
2. **Double-click on `edubrowser`** to select it (it should be highlighted/bold)
3. Expand `edubrowser` → `Tables`
4. Right-click any table → `View Data` → `All Rows`

### 3. Refresh the Connection

If tables don't appear:
1. Right-click on your connection in DBeaver
2. Select **"Refresh"** or **"Refresh Connection"**
3. Wait for it to reload

### 4. Verify Database Status

Run this command to check database contents:

```powershell
docker-compose exec -T db mysql -uroot -pInnovation edubrowser -e "SELECT 'Users' as table_name, COUNT(*) as row_count FROM Users UNION ALL SELECT 'Students', COUNT(*) FROM Students UNION ALL SELECT 'ActivityLogs', COUNT(*) FROM ActivityLogs;"
```

Expected output:
- Users: ~15 rows
- Students: ~10 rows
- ActivityLogs: ~492 rows

### 5. Common Issues

#### Issue: "Database doesn't exist"
**Solution**: Make sure you're connecting to port **3307** (not 3306)

#### Issue: "Access denied"
**Solution**: Verify password is exactly `Innovation` (case-sensitive)

#### Issue: "No tables shown"
**Solution**: 
1. Make sure you've selected the `edubrowser` database
2. Refresh the connection
3. Check if Docker container is running: `docker-compose ps db`

#### Issue: "Tables exist but are empty"
**Solution**: Run the populate script:
```powershell
$env:DB_HOST="localhost"
$env:DB_PORT="3307"
python database/populate_sample_data.py
```

### 6. Test Query in DBeaver

Once connected, try this SQL query in DBeaver:

```sql
SELECT 
    'Users' as table_name, COUNT(*) as row_count 
FROM Users
UNION ALL
SELECT 'Students', COUNT(*) FROM Students
UNION ALL
SELECT 'ActivityLogs', COUNT(*) FROM ActivityLogs
UNION ALL
SELECT 'Violations', COUNT(*) FROM Violations
UNION ALL
SELECT 'Devices', COUNT(*) FROM Devices;
```

This should show:
- Users: 15
- Students: 10
- ActivityLogs: 492
- Violations: 6-18
- Devices: 15

### 7. View Sample Data

Try these queries to see actual data:

```sql
-- View users
SELECT id, username, role, last_login, is_active 
FROM Users 
LIMIT 10;

-- View students
SELECT student_id, assigned_mode, violation_count, is_active 
FROM Students 
LIMIT 10;

-- View recent activity
SELECT student_id, url, domain, visit_start, visit_duration 
FROM ActivityLogs 
ORDER BY visit_start DESC 
LIMIT 20;
```

## Still Having Issues?

1. **Check Docker Status**:
   ```powershell
   docker-compose ps db
   ```
   Should show: `Up` and `(healthy)`

2. **Restart Database** (if needed):
   ```powershell
   docker-compose restart db
   ```

3. **Recreate Database** (last resort):
   ```powershell
   $env:DB_HOST="localhost"
   $env:DB_PORT="3307"
   python database/setup_databases.py
   python database/populate_sample_data.py
   ```

