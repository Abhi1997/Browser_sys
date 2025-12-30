# How to View Data in DBeaver

## Quick Fix for Empty Grid View

If you see the table structure but no data in the grid:

### Method 1: View Data (Recommended)

1. **Right-click** on the table name in the left panel (e.g., `Students`)
2. Select **"View Data"** → **"All Rows"** (or press `Ctrl+Shift+Enter`)
3. The data should now load in the central panel

### Method 2: SQL Query

1. Right-click on the database (`edubrowser`) or table
2. Select **"SQL Editor"** → **"New SQL Script"**
3. Type:
   ```sql
   SELECT * FROM Students LIMIT 100;
   ```
4. Press `Ctrl+Enter` to execute
5. View results in the result panel below

### Method 3: Refresh Data View

If you already have a data view open:
1. Click the **Refresh** button (circular arrow icon) in the toolbar
2. Or press `F5`
3. Or right-click in the grid → **"Refresh"**

## Common Issues

### Issue: "No data" but table shows count
**Solution**: The table exists but data view isn't loaded. Use Method 1 above.

### Issue: Grid shows "0 rows"
**Solution**: 
1. Check if you're connected to the correct database (`edubrowser`)
2. Verify the table actually has data:
   ```sql
   SELECT COUNT(*) FROM Students;
   ```
3. If count is 0, run the populate script again

### Issue: Data view is filtered
**Solution**:
1. Look at the filter bar at the top of the grid
2. Clear any SQL expressions
3. Or click the "X" to clear filters

### Issue: Connection timeout
**Solution**:
1. Right-click connection → **"Edit Connection"**
2. Go to **"Connection Settings"**
3. Increase **"Connection timeout"** to 30 seconds
4. Click **"Test Connection"** → **"OK"**

## Quick Test Query

Run this to verify all data exists:

```sql
SELECT 
    'Users' as table_name, COUNT(*) as row_count FROM Users
UNION ALL
SELECT 'Students', COUNT(*) FROM Students
UNION ALL
SELECT 'ActivityLogs', COUNT(*) FROM ActivityLogs
UNION ALL
SELECT 'Violations', COUNT(*) FROM Violations
UNION ALL
SELECT 'Devices', COUNT(*) FROM Devices;
```

Expected results:
- Users: 15
- Students: 10
- ActivityLogs: 492
- Violations: 52
- Devices: 46

## Step-by-Step for First Time

1. **Connect** to `localhost:3307` with credentials
2. **Expand** `edubrowser` database
3. **Expand** `Tables` folder
4. **Right-click** on `Students` table
5. **Select** "View Data" → "All Rows"
6. **Wait** for data to load (may take a few seconds)
7. **Scroll** through the rows

## Keyboard Shortcuts

- `Ctrl+Shift+Enter`: View all data
- `F5`: Refresh current view
- `Ctrl+Enter`: Execute SQL query
- `Ctrl+Space`: Auto-complete in SQL editor

