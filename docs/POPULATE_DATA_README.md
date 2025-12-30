# Populate Sample Data

This script populates all three databases with sample data for dashboard visualization.

## Prerequisites

1. **MySQL Server Running**
   - Make sure MySQL is running on your system

2. **Databases Created**
   - Run `python setup_databases.py` first to create the databases

3. **Python Dependencies**
   ```bash
   pip install mysql-connector-python python-dotenv
   ```

## Usage

```bash
python populate_sample_data.py
```

## What Gets Populated

### 1. Users (Auth Database)
- **10 Students**: student1 through student10
  - Password: `student123`
  - Gmail: student1@example.com, etc.
  
- **3 Teachers**: teacher1, teacher2, teacher3
  - Password: `teacher123`
  - Status: APPROVED
  
- **1 Admin**: admin1
  - Password: `admin123`

### 2. Student Profiles (Student Database)
- All students with assigned modes:
  - Exam Mode: student1, student5, student9
  - Study Mode: student2, student6, student10
  - Restricted Mode: student3, student7
  - Free Mode: student4, student8
- Violation counts (0-5 per student)
- Device IDs, IP addresses, MAC addresses

### 3. Whitelist & Blacklist (Student Database)
- **14 Educational Domains** whitelisted for all modes:
  - wikipedia.org, khanacademy.org, coursera.org, etc.
  
- **7 Blocked Domains** for exam/study/restricted modes:
  - facebook.com, twitter.com, instagram.com, etc.

### 4. Activity Logs (Activity Database)
- **5-20 activity entries per student**
- Last 7 days of browsing activity
- URLs, domains, visit duration, timestamps
- Device information

### 5. Violations (Activity Database)
- **1-3 violations per student** (for students with violation_count > 0)
- Different violation types:
  - url_blocked
  - mode_bypass_attempt
  - time_window_violation
  - unauthorized_action
- Severity levels: low, medium, high, critical

### 6. Mode History (Student Database)
- **1-2 mode changes per student**
- Historical mode transitions
- Admin who made the change
- Reasons for changes

### 7. Teacher Actions (Activity Database)
- **5-10 actions per teacher**
- Action types: mode_change, view_student, view_activity, whitelist_add
- Timestamps and details

### 8. Devices (Auth Database)
- Device registrations for all users
- IP addresses, MAC addresses
- Device fingerprints

## Sample Data Summary

- **Total Users**: 14 (10 students + 3 teachers + 1 admin)
- **Activity Logs**: ~100-200 entries
- **Violations**: ~10-30 entries
- **Whitelist Entries**: ~56 (14 domains × 4 modes)
- **Blacklist Entries**: ~21 (7 domains × 3 modes)
- **Mode History**: ~10-20 entries
- **Teacher Actions**: ~15-30 entries

## Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Student | student1, student2, ... | student123 |
| Teacher | teacher1, teacher2, teacher3 | teacher123 |
| Admin | admin1 | admin123 |
| Super Admin | admin | admin1234 |

## Viewing the Data

After running the script:

1. **Start the API server:**
   ```bash
   python api_server.py
   ```

2. **Start the React dashboard:**
   ```bash
   cd react-dashboard
   npm run dev
   ```

3. **Open the dashboard from PyQt6:**
   - Login as admin/teacher
   - Click Dashboard button
   - You should see all the sample data!

## Re-running the Script

The script is idempotent - you can run it multiple times:
- Existing users won't be duplicated
- Existing students will be updated
- New activity logs and violations will be added

## Customization

You can modify the sample data in `populate_sample_data.py`:
- `SAMPLE_STUDENTS` - Add more students
- `SAMPLE_TEACHERS` - Add more teachers
- `EDUCATIONAL_DOMAINS` - Add more whitelisted domains
- `BLOCKED_DOMAINS` - Add more blocked domains

## Troubleshooting

**Error: ModuleNotFoundError: No module named 'mysql'**
```bash
pip install mysql-connector-python
```

**Error: Access denied**
- Check your MySQL credentials in `.env` or update them in the script

**Error: Database doesn't exist**
- Run `python setup_databases.py` first

**No data showing in dashboard**
- Make sure API server is running on port 5000
- Check browser console for errors
- Verify database connections

