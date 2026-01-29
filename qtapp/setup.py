#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive setup script for EduBrowser production deployment
"""
import os
import secrets
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def generate_jwt_secret():
    """Generate a secure JWT secret key"""
    return secrets.token_urlsafe(32)

def create_env_file():
    """Create .env file from env.example with user input"""
    env_example = Path("env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("✅ Keeping existing .env file")
            return False
    
    print("\n🔧 Setting up production environment...")
    print("=" * 60)
    
    # Read template
    if not env_example.exists():
        print("❌ env.example not found!")
        return False
    
    template = env_example.read_text()
    
    # Collect configuration
    print("\n📊 Database Configuration:")
    print("-" * 60)
    db_host = input("Database Host [db.abhinavpaudel.com]: ").strip() or "db.abhinavpaudel.com"
    db_port = input("Database Port [3306]: ").strip() or "3306"
    db_user = input("Database User [root]: ").strip() or "root"
    db_password = input("Database Password: ").strip()
    if not db_password:
        print("⚠️  Warning: Empty password!")
    db_name = input("Database Name [edubrowser]: ").strip() or "edubrowser"
    
    print("\n🌐 Domain Configuration:")
    print("-" * 60)
    dashboard_url = input("Dashboard URL [https://api.abhinavpaudel.com]: ").strip() or "https://api.abhinavpaudel.com"
    api_url = input("API URL [https://api.abhinavpaudel.com]: ").strip() or "https://api.abhinavpaudel.com"
    
    print("\n🔐 Security Configuration:")
    print("-" * 60)
    generate_secret = input("Generate new JWT secret? (Y/n): ").strip().lower()
    if generate_secret != 'n':
        jwt_secret = generate_jwt_secret()
        print(f"✅ Generated JWT secret: {jwt_secret[:20]}...")
    else:
        jwt_secret = input("Enter JWT secret (or press Enter to generate): ").strip()
        if not jwt_secret:
            jwt_secret = generate_jwt_secret()
            print(f"✅ Generated JWT secret: {jwt_secret[:20]}...")
    
    # Replace values
    config = template
    config = config.replace("DB_HOST=db.abhinavpaudel.com", f"DB_HOST={db_host}")
    config = config.replace("DB_PORT=3306", f"DB_PORT={db_port}")
    config = config.replace("DB_USER=root", f"DB_USER={db_user}")
    config = config.replace("DB_PASSWORD=your_database_password", f"DB_PASSWORD={db_password}")
    config = config.replace("DB_NAME=edubrowser", f"DB_NAME={db_name}")
    config = config.replace("DASHBOARD_URL=https://api.abhinavpaudel.com", f"DASHBOARD_URL={dashboard_url}")
    config = config.replace("VITE_API_URL=https://api.abhinavpaudel.com", f"VITE_API_URL={api_url}")
    config = config.replace("API_BASE_URL=https://api.abhinavpaudel.com", f"API_BASE_URL={api_url}")
    config = config.replace("JWT_SECRET=your-super-secret-jwt-key-change-this-in-production", f"JWT_SECRET={jwt_secret}")
    
    # Write .env file
    env_file.write_text(config)
    print(f"\n✅ Created .env file!")
    return True

def test_database_connection():
    """Test database connection"""
    print("\n🔌 Testing database connection...")
    try:
        from authentication import Authentication
        auth = Authentication()
        conn = auth._get_conn()
        if conn.is_connected():
            print("✅ Database connection successful!")
            conn.close()
            return True
        else:
            print("❌ Database connection failed!")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print("\n💡 Tips:")
        print("   - Verify DB_HOST, DB_USER, DB_PASSWORD in .env")
        print("   - Ensure MySQL server is running and accessible")
        print("   - Check firewall rules if using remote database")
        return False

def setup_database():
    """Set up database schema"""
    print("\n📦 Setting up database schema...")
    response = input("Initialize database tables? (Y/n): ").strip().lower()
    if response == 'n':
        print("⏭️  Skipping database setup")
        return False
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "database/setup_databases.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Database schema created successfully!")
            
            # Ask about sample data
            add_sample = input("\nAdd sample data? (y/N): ").strip().lower()
            if add_sample == 'y':
                print("📊 Populating sample data...")
                result = subprocess.run([sys.executable, "database/populate_sample_data.py"],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Sample data added!")
                else:
                    print(f"⚠️  Error: {result.stderr}")
            return True
        else:
            print(f"❌ Database setup failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("🚀 EduBrowser Production Setup")
    print("=" * 60)
    
    # Step 1: Create .env file
    if create_env_file():
        print("\n✅ Environment configuration created!")
    else:
        print("\n⚠️  Using existing .env file")
    
    # Step 2: Test database connection
    if test_database_connection():
        # Step 3: Setup database
        setup_database()
    else:
        print("\n⚠️  Please fix database connection before continuing")
        print("   Edit .env file and run this script again")
        return
    
    # Step 4: Create admin user
    print("\n👤 Admin User Setup:")
    print("-" * 60)
    create_admin = input("Create admin user? (Y/n): ").strip().lower()
    if create_admin != 'n':
        try:
            import subprocess
            result = subprocess.run([sys.executable, "database/create_admin_quick.py"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Admin user created!")
            else:
                print(f"⚠️  Error: {result.stderr}")
        except Exception as e:
            print(f"⚠️  Error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print("\n📋 Next Steps:")
    print("   1. Use the hosted PHP API at https://api.abhinavpaudel.com (no local API needed)")
    print("   2. Build dashboard: cd react-dashboard && npm run build")
    print("   3. Deploy to your server")
    print("\n📚 See BROWSER_SETUP.md and docs/PYTHON_APP_SETUP.md for API configuration")
    print("=" * 60)

if __name__ == "__main__":
    main()
