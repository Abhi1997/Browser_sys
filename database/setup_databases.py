"""
Database Setup Script
Creates single database with all tables
"""

import sys
import io

# Fix encoding for Windows console to handle emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import mysql.connector
import os

# Try to load .env file if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, use defaults

def setup_databases():
    """Create and initialize single database with all tables"""
    
    # Database configuration
    # Note: When running on host machine, use 'localhost'
    # When running inside Docker, use 'db' (container name)
    db_host = os.getenv("DB_HOST", "localhost")
    
    # If DB_HOST is set to 'db' but we're running on host, use localhost
    # This handles the case where .env has DB_HOST=db for Docker containers
    if db_host == "db":
        import socket
        try:
            # Try to resolve 'db' - if it fails, we're on host machine
            socket.gethostbyname('db')
        except socket.gaierror:
            # Can't resolve 'db', we're on host machine, use localhost
            db_host = "localhost"
            print("ℹ️  Running on host machine - using 'localhost' instead of 'db'")
    
    db_config = {
        "host": db_host,
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "Innovation"),
        "allow_public_key_retrieval": True,  # Required for MySQL 8.0+
    }
    
    print("🔧 Setting up Secure Academic Browser Database...")
    print("=" * 60)
    
    try:
        # Connect without database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Drop existing database if it exists (to ensure clean schema)
        print("\n🗑️  Dropping existing database (if exists)...")
        cursor.execute("DROP DATABASE IF EXISTS edubrowser")
        conn.commit()
        print("  ✅ Old database dropped")
        
        # First create the database explicitly
        print("\n📊 Creating database...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS edubrowser")
        conn.commit()
        print("  ✅ Database created")
        
        # Now switch to the database
        cursor.execute("USE edubrowser")
        print("  ✅ Using database edubrowser")
        
        # Read and execute single database script (skip CREATE DATABASE and USE statements)
        print("\n📋 Creating tables...")
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sql_file = os.path.join(script_dir, "init_single_db.sql")
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_script = f.read()
            
            # Execute the entire script using multi_statements mode
            # First, let's remove CREATE DATABASE and USE statements and execute the rest
            lines = sql_script.split('\n')
            filtered_lines = []
            skip_next_use = False
            for line in lines:
                line_stripped = line.strip().upper()
                # Skip CREATE DATABASE line
                if "CREATE DATABASE" in line_stripped:
                    continue
                # Skip USE line
                if line_stripped.startswith("USE "):
                    continue
                # Skip comment-only lines
                if line_stripped.startswith("--"):
                    continue
                filtered_lines.append(line)
            
            # Join and split by semicolon
            filtered_script = '\n'.join(filtered_lines)
            statements = [s.strip() for s in filtered_script.split(";") if s.strip()]
            
            table_count = 0
            for statement in statements:
                # Skip CREATE DATABASE and USE statements
                stmt_upper = statement.upper().strip()
                if "CREATE DATABASE" in stmt_upper or stmt_upper.startswith("USE "):
                    continue
                
                try:
                    cursor.execute(statement)
                    if "CREATE TABLE" in stmt_upper:
                        table_count += 1
                except mysql.connector.Error as e:
                    # Ignore "already exists" and "Duplicate" errors
                    error_str = str(e).lower()
                    if "already exists" not in error_str and "duplicate" not in error_str and "unknown database" not in error_str:
                        print(f"  ⚠️  Warning: {e}")
        
        conn.commit()
        print(f"  ✅ Created {table_count} tables successfully")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Database setup completed!")
        print("\n📋 Database: edubrowser")
        print("   Tables: Users, Devices, Students, ActivityLogs, Violations, etc.")
        print("\n📋 Next steps:")
        print("  1. Populate sample data: python populate_sample_data.py")
        print("  2. Run the application: python main.py")
        print("  3. Default admin credentials:")
        print("     Username: admin")
        print("     Password: admin1234")
        
    except mysql.connector.Error as e:
        print(f"\n❌ Database setup failed: {e}")
        print("\nPlease ensure:")
        print("  - MySQL server is running")
        print("  - Database credentials are correct")
        print("  - User has CREATE DATABASE privileges")
        return False
    
    return True

if __name__ == "__main__":
    setup_databases()

