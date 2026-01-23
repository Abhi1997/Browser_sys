"""
Database Setup Script for EduBrowser
Creates single database with all tables on Hostinger MySQL
"""

import sys
import io
import os

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import mysql.connector
except ImportError:
    print("❌ mysql-connector-python is not installed.")
    print("Install it via: pip install mysql-connector-python")
    sys.exit(1)

# Try to load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def setup_databases():
    """Create and initialize the EduBrowser database and tables"""
    
    # --- Database credentials (Hostinger) ---
    db_host = os.getenv("DB_HOST", "srv1882.hstgr.io")        # Replace with your MySQL host
    db_user = os.getenv("DB_USER", "u976383844_abhi097")      # Your MySQL username
    db_password = os.getenv("DB_PASSWORD", "!nN0v@tion113")   # Your MySQL password
    db_name = os.getenv("DB_NAME", "u976383844_dces")              # Database name
    db_port = int(os.getenv("DB_PORT", 3306))                 # Default MySQL port

    db_config_no_db = {
        "host": db_host,
        "user": db_user,
        "password": db_password,
        "port": db_port
    }

    print("🔧 Setting up EduBrowser Database...")
    print("=" * 60)

    try:
        # Connect to MySQL server (without database)
        conn = mysql.connector.connect(**db_config_no_db)
        cursor = conn.cursor()

        # Drop existing database if exists
        print("\n🗑️  Dropping existing database (if exists)...")
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
        conn.commit()
        print("  ✅ Old database dropped")

        # Create database
        print("\n📊 Creating database...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        print(f"  ✅ Database '{db_name}' created")

        # Switch to database
        cursor.execute(f"USE {db_name}")
        print(f"  ✅ Using database '{db_name}'")

        # Read SQL file with all table definitions
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sql_file = os.path.join(script_dir, "init_single_db.sql")

        if not os.path.exists(sql_file):
            print(f"❌ SQL file not found: {sql_file}")
            return False

        with open(sql_file, "r", encoding="utf-8") as f:
            sql_script = f.read()

        # Remove CREATE DATABASE and USE statements
        lines = sql_script.split('\n')
        filtered_lines = []
        for line in lines:
            line_upper = line.strip().upper()
            if "CREATE DATABASE" in line_upper or line_upper.startswith("USE "):
                continue
            if line_upper.startswith("--"):
                continue
            filtered_lines.append(line)

        filtered_script = '\n'.join(filtered_lines)
        statements = [stmt.strip() for stmt in filtered_script.split(";") if stmt.strip()]

        table_count = 0
        for stmt in statements:
            try:
                cursor.execute(stmt)
                if "CREATE TABLE" in stmt.upper():
                    table_count += 1
            except mysql.connector.Error as e:
                error_str = str(e).lower()
                if "already exists" not in error_str:
                    print(f"  ⚠️  Warning: {e}")

        conn.commit()
        print(f"\n  ✅ Created {table_count} tables successfully")

        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("✅ Database setup completed!")
        print(f"📋 Database: {db_name}")
        print("   Tables: Users, Devices, Students, ActivityLogs, Violations, etc.")
        print("\n📋 Next steps:")
        print("  1. Populate sample data: python populate_sample_data.py")
        print("  2. Run the application: python main.py")
        print("  3. Default admin credentials:")
        print("     Username: admin")
        print("     Password: admin1234")
        return True

    except mysql.connector.Error as e:
        print(f"\n❌ Database setup failed: {e}")
        print("\nPlease ensure:")
        print("  - MySQL server is running")
        print("  - Database credentials are correct")
        print("  - User has CREATE DATABASE privileges")
        return False

if __name__ == "__main__":
    setup_databases()
