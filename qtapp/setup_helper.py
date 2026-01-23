#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple setup helper - checks configuration and guides through setup
"""
import os
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass  # If already wrapped, ignore

def check_env_file():
    """Check if .env exists and is configured"""
    env_file = Path(".env")
    if not env_file.exists():
        print("[ERROR] .env file not found!")
        print("   Creating from env.example...")
        env_example = Path("env.example")
        if env_example.exists():
            env_file.write_text(env_example.read_text())
            print("   [OK] Created .env file")
            print("   [WARN] Please edit .env with your database credentials")
            return False
        else:
            print("   [ERROR] env.example not found!")
            return False
    
    # Check if contains placeholder values
    content = env_file.read_text()
    if "your_database_password" in content or "your-super-secret" in content:
        print("[WARN] .env file contains placeholder values")
        print("   Please update:")
        print("   - DB_PASSWORD")
        print("   - JWT_SECRET (generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\")")
        return False
    
    print("[OK] .env file configured")
    return True

def test_database():
    """Test database connection"""
    print("\n🔌 Testing database connection...")
    try:
        from authentication import Authentication
        auth = Authentication()
        conn = auth._get_conn()
        if conn.is_connected():
            print("[OK] Database connection successful!")
            conn.close()
            return True
        else:
            print("[ERROR] Database connection failed!")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        print("\n💡 Check:")
        print("   - DB_HOST, DB_USER, DB_PASSWORD in .env")
        print("   - MySQL server is running")
        print("   - Firewall allows connection")
        return False

def check_database_schema():
    """Check if database tables exist"""
    print("\n📊 Checking database schema...")
    try:
        from authentication import Authentication
        auth = Authentication()
        conn = auth._get_conn()
        cursor = conn.cursor()
        
        # Check for Users table
        cursor.execute("SHOW TABLES LIKE 'Users'")
        if cursor.fetchone():
            print("[OK] Database tables exist")
            cursor.close()
            conn.close()
            return True
        else:
            print("[WARN] Database tables not found")
            print("   Run: python database/setup_databases.py")
            cursor.close()
            conn.close()
            return False
    except Exception as e:
        print(f"❌ Error checking schema: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("EduBrowser Setup Helper")
    print("=" * 60)
    
    # Step 1: Check .env
    print("\n[1/4] Checking .env file...")
    env_ok = check_env_file()
    
    if not env_ok:
        print("\n⚠️  Please configure .env file first!")
        print("   See QUICK_SETUP.md for instructions")
        return
    
    # Step 2: Test database
    print("\n[2/4] Testing database connection...")
    db_ok = test_database()
    
    if not db_ok:
        print("\n⚠️  Please fix database connection!")
        return
    
    # Step 3: Check schema
    print("\n[3/4] Checking database schema...")
    schema_ok = check_database_schema()
    
    if not schema_ok:
        print("\n💡 To create database tables:")
        print("   python database/setup_databases.py")
        response = input("\n   Create tables now? (y/N): ").strip().lower()
        if response == 'y':
            import subprocess
            result = subprocess.run([sys.executable, "database/setup_databases.py"])
            if result.returncode == 0:
                print("   ✅ Database tables created!")
                schema_ok = True
            else:
                print("   ❌ Failed to create tables")
                return
    
    # Step 4: Check admin user
    print("\n[4/4] Checking admin user...")
    try:
        from authentication import Authentication
        auth = Authentication()
        conn = auth._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Users WHERE role='admin'")
        admin_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        if admin_count > 0:
            print(f"[OK] Found {admin_count} admin user(s)")
        else:
            print("[WARN] No admin users found")
            print("   Run: python database/create_admin_quick.py")
            response = input("\n   Create admin user now? (y/N): ").strip().lower()
            if response == 'y':
                import subprocess
                result = subprocess.run([sys.executable, "database/create_admin_quick.py"])
                if result.returncode == 0:
                    print("   [OK] Admin user created!")
                else:
                    print("   [ERROR] Failed to create admin user")
    except Exception as e:
        print(f"[WARN] Could not check admin users: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Setup Status")
    print("=" * 60)
    print(f"Environment: {'[OK]' if env_ok else '[ERROR]'}")
    print(f"Database: {'[OK]' if db_ok else '[ERROR]'}")
    print(f"Schema: {'[OK]' if schema_ok else '[ERROR]'}")
    
    if env_ok and db_ok and schema_ok:
        print("\n[OK] Setup complete! You can now:")
        print("   1. Test API: python api_server.py")
        print("   2. Build dashboard: cd react-dashboard && npm run build")
        print("   3. Deploy to your server")
    else:
        print("\n[WARN] Please complete the setup steps above")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
