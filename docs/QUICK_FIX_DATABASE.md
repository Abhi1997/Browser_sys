# Quick Fix: Database Schema Error

## Problem

You're getting this error:
```
Unknown column 'gmail' in 'field list'
```

This means the database exists but has the **old schema** (without `gmail` column).

## Solution

You need to **drop and recreate** the database with the new schema.

### Option 1: Use Reset Script (Recommended)

```bash
python reset_database.py
```

This will:
1. Drop the existing `edubrowser` database
2. Recreate it with the new single-database schema
3. All tables will be created with correct columns

### Option 2: Manual Reset

**Step 1: Drop database**
```sql
DROP DATABASE IF EXISTS edubrowser;
```

**Step 2: Run setup script**
```bash
python setup_databases.py
```

### Option 3: Using Python Script

Create a simple script:

```python
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Innovation"
)
cursor = conn.cursor()

# Drop database
cursor.execute("DROP DATABASE IF EXISTS edubrowser")
print("✅ Database dropped")

# Recreate (run setup script)
conn.commit()
cursor.close()
conn.close()

# Now run setup
import subprocess
subprocess.run(["python", "setup_databases.py"])
```

## After Reset

1. **Populate sample data:**
   ```bash
   python populate_sample_data.py
   ```

2. **Run application:**
   ```bash
   python main.py
   ```

## Why This Happened

The database was created with the old `init_db.sql` schema. The new system uses `init_single_db.sql` which has:
- `gmail` column in Users table
- All tables in single database
- Additional columns for teacher approval, etc.

## Verification

After reset, verify the schema:

```python
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Innovation",
    database="edubrowser"
)
cursor = conn.cursor()

cursor.execute("DESCRIBE Users")
columns = cursor.fetchall()
print("Users table columns:")
for col in columns:
    print(f"  - {col[0]} ({col[1]})")

cursor.close()
conn.close()
```

You should see `gmail` column in the output.

