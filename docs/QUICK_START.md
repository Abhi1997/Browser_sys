# Quick Start Guide - Sample Data

## Step 1: Setup Databases

```bash
python setup_databases.py
```

This creates all three databases with proper schemas.

## Step 2: Populate Sample Data

```bash
python populate_sample_data.py
```

This will populate:
- ✅ 10 Students with different modes
- ✅ 3 Teachers (approved)
- ✅ 1 Admin
- ✅ Activity logs (100-200 entries)
- ✅ Violations (10-30 entries)
- ✅ Whitelist/Blacklist entries
- ✅ Device registrations
- ✅ Mode history
- ✅ Teacher actions

## Step 3: Start Services

**Terminal 1 - API Server:**
```bash
python api_server.py
```

**Terminal 2 - React Dashboard:**
```bash
cd react-dashboard
npm run dev
```

## Step 4: View Dashboard

1. Run the PyQt6 application:
   ```bash
   python main.py
   ```

2. Login with:
   - Username: `admin`
   - Password: `admin1234`
   - Or use any sample user (see credentials below)

3. Click the **Dashboard** button

4. You should see:
   - Real-time statistics
   - User tables with sample data
   - Student management
   - Activity logs
   - Violations
   - Charts with real data

## Sample Credentials

| Role | Username | Password |
|------|----------|----------|
| Super Admin | admin | admin1234 |
| Admin | admin1 | admin123 |
| Teacher | teacher1 | teacher123 |
| Student | student1 | student123 |

## What You'll See

### Admin Dashboard
- **Statistics Cards**: Total users, active users, students by mode, violations
- **Charts**: Role distribution, login activity
- **Tables**: Users, Students, Violations, Whitelist/Blacklist

### Teacher Dashboard
- **Statistics**: Total students, active students, recent activity, violations
- **Student Management**: View and change student modes
- **Activity Monitoring**: See student browsing activity
- **Violations**: View security violations

### Data Highlights
- Students distributed across 4 modes (Exam, Study, Restricted, Free)
- Realistic activity logs with timestamps
- Security violations with different severity levels
- Mode change history
- Teacher action logs

## Troubleshooting

**No data showing?**
- Make sure `populate_sample_data.py` ran successfully
- Check that API server is running on port 5000
- Verify database connections in `.env`

**Script errors?**
- Install dependencies: `pip install mysql-connector-python python-dotenv`
- Make sure MySQL is running
- Run `setup_databases.py` first

**Dashboard not loading?**
- Check browser console for errors
- Verify API server is accessible at `http://localhost:5000`
- Make sure React dashboard is on port 3000

## Next Steps

- Customize sample data in `populate_sample_data.py`
- Add more students, teachers, or domains
- Modify activity patterns
- Test different violation scenarios

