"""
Setup database in Docker MySQL
Connects to Docker MySQL on port 3307
"""

import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import mysql.connector

def setup_docker_database():
    """Setup database in Docker MySQL (port 3307)"""
    
    print("Setting up Docker MySQL database...")
    print("=" * 60)
    
    try:
        # Connect to Docker MySQL on port 3307
        conn = mysql.connector.connect(
            host="localhost",
            port=3307,
            user="root",
            password="Innovation",
            allow_public_key_retrieval=True  # Required for MySQL 8.0+
        )
        cursor = conn.cursor()
        
        # Drop existing database if it exists
        print("\nDropping existing database (if exists)...")
        cursor.execute("DROP DATABASE IF EXISTS edubrowser")
        conn.commit()
        print("  Database dropped")
        
        # Create database
        print("\nCreating database...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS edubrowser")
        conn.commit()
        print("  Database created")
        
        # Use database
        cursor.execute("USE edubrowser")
        print("  Using database edubrowser")
        
        # Read and execute schema
        print("\nCreating tables...")
        with open("init_single_db.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()
            
            lines = sql_script.split('\n')
            filtered_lines = []
            for line in lines:
                line_stripped = line.strip().upper()
                # Skip CREATE DATABASE and USE statements
                if "CREATE DATABASE" in line_stripped or line_stripped.startswith("USE "):
                    continue
                # Skip comment-only lines
                if line_stripped.startswith("--"):
                    continue
                filtered_lines.append(line)
            
            filtered_script = '\n'.join(filtered_lines)
            statements = [s.strip() for s in filtered_script.split(";") if s.strip()]
            
            table_count = 0
            for statement in statements:
                stmt_upper = statement.upper().strip()
                if "CREATE DATABASE" in stmt_upper or stmt_upper.startswith("USE "):
                    continue
                
                try:
                    cursor.execute(statement)
                    if "CREATE TABLE" in stmt_upper:
                        table_count += 1
                except mysql.connector.Error as e:
                    error_str = str(e).lower()
                    if "already exists" not in error_str and "duplicate" not in error_str:
                        print(f"  Warning: {e}")
        
        conn.commit()
        print(f"  Created {table_count} tables successfully")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("Docker database setup completed!")
        print("\nNext steps:")
        print("  python docker_populate_data.py")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    setup_docker_database()

