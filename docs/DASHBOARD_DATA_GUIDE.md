# Dashboard Data Guide

This guide explains the sample data that populates the database for dynamic dashboard visualization.

## 📊 Data Population

The `database/populate_sample_data.py` script populates the database with comprehensive sample data for all dashboard components.

### Enhanced Features

1. **User Login Activity**
   - All users now have `last_login` dates populated
   - Students: Last login within last 3 days (90% chance)
   - Teachers: Last login within last 2 days (95% chance)
   - Admins: Last login within last 24 hours
   - Admin user (`admin`/`admin123!`) always has recent login

2. **Activity Logs**
   - **10-30 entries per student** (previously 5-20)
   - **Last 14 days** of activity (previously 7 days)
   - Diverse domains based on student mode
   - Realistic visit durations (30 seconds to 1 hour)
   - Proper timestamps for chart visualization

3. **Violations**
   - **60% of students** have violations (improved distribution)
   - Various violation types: `url_blocked`, `mode_bypass_attempt`, `time_window_violation`, `unauthorized_action`
   - Different severity levels: `low`, `medium`, `high`, `critical`
   - Realistic timestamps (last 7 days)

4. **Complete Data Sets**
   - Users: 14 total (10 students, 3 teachers, 1 admin)
   - Student profiles with assigned modes
   - Device registrations for all users
   - Whitelist/Blacklist domains
   - Mode history records
   - Teacher action logs

## 🎯 Dashboard Components Using This Data

### Admin Dashboard

- **Stats Cards**: Total users, active users, active students, mode distribution
- **Login Activity Chart**: Uses `ActivityLogs` data grouped by date
- **Role Distribution Chart**: Uses `Users` table counts by role
- **User Table**: Displays all users with `last_login` dates
- **Student Table**: Shows students with assigned modes and violation counts
- **Violations Table**: Lists all security violations
- **Whitelist/Blacklist Tables**: Shows domain management

### Teacher Dashboard

- **Class Stats**: Student counts and activity metrics
- **Activity Timeline**: Uses `ActivityLogs` data
- **Student List**: All students with their modes

### Super Admin Dashboard

- **Global Stats**: Overall system statistics
- **Admin Stats**: Admin-specific metrics
- **Comparison Charts**: Role-based comparisons

## 🔄 Running the Data Population Script

### With Docker MySQL

```powershell
$env:DB_HOST="localhost"
$env:DB_PORT="3307"
python database/populate_sample_data.py
```

### With Local MySQL

```powershell
python database/populate_sample_data.py
```

The script will:
- ✅ Create/update users with `last_login` dates
- ✅ Populate student profiles
- ✅ Register devices
- ✅ Add whitelist/blacklist domains
- ✅ Generate activity logs (14 days)
- ✅ Create violations
- ✅ Add mode history
- ✅ Log teacher actions

## 📝 Sample Users

| Username | Password | Role | Notes |
|----------|----------|------|-------|
| `admin` | `admin123!` | admin | Main admin user |
| `student1` to `student10` | `student123` | student | 10 sample students |
| `teacher1` to `teacher3` | `teacher123` | teacher | 3 sample teachers |
| `admin1` | `admin123` | admin | Additional admin |

## 📈 Data Statistics

After running the script, you should see:

- **~14 Users** (10 students, 3 teachers, 1+ admins)
- **~10 Student Profiles** (with assigned modes)
- **~150-300 Activity Logs** (10-30 per student, last 14 days)
- **~6-18 Violations** (60% of students have 1-3 violations each)
- **~20-40 Mode History Records** (1-2 per student)
- **~15-30 Teacher Actions** (5-10 per teacher)
- **~56 Whitelist Entries** (14 domains × 4 modes)
- **~21 Blacklist Entries** (7 domains × 3 modes)

## 🔍 Viewing Data in DBeaver

Connect to the database using:
- **Host**: `localhost`
- **Port**: `3307`
- **Database**: `edubrowser`
- **Username**: `root`
- **Password**: `Innovation`

See `docs/CONNECT_DBEAVER.md` for detailed connection instructions.

## 🎨 Chart Data Details

### Login Activity Chart
- Groups `ActivityLogs` by date
- Shows total logins and unique users per day
- Displays last 7 days of data
- Uses `visit_start` or `created_at` timestamps

### Role Distribution Chart
- Counts users by role from `Users` table
- Shows Admin, Teacher, Student distribution
- Updates in real-time

### Activity Timeline
- Shows individual activity entries
- Filters by student (if applicable)
- Displays URL, domain, duration, timestamp

## 🔄 Refreshing Dashboard Data

The dashboard automatically refreshes:
- **Stats**: Every 30 seconds
- **Activity**: Every 10 seconds
- **Other data**: On manual refresh or navigation

To refresh all data:
1. Close and reopen the dashboard window
2. Or wait for automatic refresh intervals

## ⚠️ Important Notes

1. **Data Persistence**: Data persists in the Docker volume `db_data`
2. **Re-running Script**: Safe to run multiple times (updates existing records)
3. **Real Data**: The dashboard uses **real database data**, not mock data
4. **Performance**: With ~300 activity logs, queries are fast (<100ms)

## 🚀 Next Steps

1. ✅ Run the populate script (already done)
2. ✅ Open the dashboard from the PyQt6 browser
3. ✅ View all charts and tables with dynamic data
4. ✅ Verify login activity charts show data
5. ✅ Check user table shows last_login dates

All dashboard elements should now display dynamic data from the database! 🎉

