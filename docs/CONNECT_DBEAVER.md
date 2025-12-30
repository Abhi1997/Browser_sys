# Connecting to Docker MySQL Database with DBeaver

This guide explains how to connect to the MySQL database running in Docker using DBeaver on your local machine.

## Connection Details

When the database is running in Docker, use these connection settings:

| Setting | Value |
|---------|-------|
| **Host** | `localhost` |
| **Port** | `3307` |
| **Database** | `edubrowser` |
| **Username** | `root` |
| **Password** | `Innovation` |

## Steps to Connect

### 1. Make Sure Docker is Running

First, ensure the database container is running:

```powershell
docker-compose ps db
```

If it's not running, start it:

```powershell
docker-compose up -d db
```

### 2. Open DBeaver

1. Launch DBeaver on your local machine
2. Click **New Database Connection** (or press `Ctrl+Shift+N`)

### 3. Select MySQL

1. In the connection wizard, select **MySQL**
2. Click **Next**

### 4. Enter Connection Details

Fill in the connection settings:

- **Server Host**: `localhost`
- **Port**: `3307`
- **Database**: `edubrowser`
- **Username**: `root`
- **Password**: `Innovation`

### 5. Test Connection

1. Click **Test Connection** button
2. If you see "MySQL driver not found", DBeaver will prompt you to download it - click **Download**
3. Wait for the download and installation
4. Click **Test Connection** again
5. You should see a success message: "Connected"

### 6. Finish Setup

1. Click **Finish**
2. The database connection will appear in the Database Navigator
3. Expand the connection to see the `edubrowser` database
4. Expand `edubrowser` to see all tables

## Available Tables

Once connected, you'll see these tables in the `edubrowser` database:

- **Users** - User accounts and authentication
- **Students** - Student profiles and modes
- **Devices** - Device registrations
- **DashboardTokens** - Dashboard access tokens
- **ActivityLogs** - Browser activity logs
- **Violations** - Security violations
- **AdminActions** - Admin action logs
- **WhitelistDomains** - Allowed domains
- **BlacklistDomains** - Blocked domains
- **ModeHistory** - Mode change history
- **Sessions** - Active sessions
- **TimeWindows** - Student time windows

## Viewing Data

To view table contents:

1. Expand the `edubrowser` database
2. Expand **Tables**
3. Right-click on any table
4. Select **View Data** → **All Rows** (or press `F4`)

## Running Queries

To run SQL queries:

1. Right-click on the `edubrowser` database
2. Select **SQL Editor** → **New SQL Script**
3. Type your SQL query
4. Press `Ctrl+Enter` to execute

### Example Queries

**View all users:**
```sql
SELECT * FROM Users;
```

**View admin users:**
```sql
SELECT id, username, role, is_active, teacher_approval_status 
FROM Users 
WHERE role = 'admin';
```

**View students:**
```sql
SELECT * FROM Students;
```

**View recent activity:**
```sql
SELECT * FROM ActivityLogs 
ORDER BY visit_start DESC 
LIMIT 50;
```

**View violations:**
```sql
SELECT * FROM Violations 
ORDER BY created_at DESC 
LIMIT 50;
```

## Troubleshooting

### Connection Refused

If you get "Connection refused":

1. Check if the database container is running:
   ```powershell
   docker-compose ps db
   ```

2. Check the port mapping:
   ```powershell
   docker-compose ps db
   ```
   Should show: `0.0.0.0:3307->3306/tcp`

3. Try restarting the container:
   ```powershell
   docker-compose restart db
   ```

### Access Denied

If you get "Access denied":

1. Verify the password is exactly: `Innovation` (case-sensitive)
2. Verify the username is: `root`

### Database Not Found

If you get "Database doesn't exist":

1. Make sure the database was initialized:
   ```powershell
   python database/setup_databases.py
   ```

2. Check if the database exists:
   ```powershell
   docker-compose exec db mysql -uroot -pInnovation -e "SHOW DATABASES;"
   ```

### Port Already in Use

If port 3307 is already in use:

1. Check what's using the port:
   ```powershell
   netstat -ano | findstr :3307
   ```

2. Either stop the conflicting service or change the port in `docker-compose.yml`

## Quick Connection String

For advanced users, here's the JDBC connection string:

```
jdbc:mysql://localhost:3307/edubrowser?useSSL=false
```

## Notes

- The database runs on port **3307** (not the default 3306) to avoid conflicts with local MySQL
- All credentials are stored in `docker-compose.yml`
- The database persists data in a Docker volume
- You can modify data directly, but be careful with production data!

