"""
Quick script to create admin user with username 'admin' and password 'admin123!'
No approval required for admin users
"""

import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import mysql.connector
import os
from hashlib import sha256

# Database configuration
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT")
db_config = {
    "host": db_host,
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "Innovation"),
    "allow_public_key_retrieval": True,  # Required for MySQL 8.0+
}

# Add port if specified (for Docker MySQL)
if db_port:
    try:
        db_config["port"] = int(db_port)
    except ValueError:
        pass

DATABASE = os.getenv("DB_NAME", "edubrowser")

def hash_password(password):
    """Hash password using SHA256"""
    return sha256(password.encode()).hexdigest()

def create_admin():
    """Create admin user with username 'admin' and password 'admin123!'"""
    
    username = "admin"
    password = "admin123!"
    
    print("Creating admin user...")
    print("=" * 60)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print("=" * 60)
    
    try:
        # Connect to database
        config = db_config.copy()
        config["database"] = DATABASE
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("""
            SELECT id, username, role, teacher_approval_status, is_active 
            FROM Users 
            WHERE username = %s
        """, (username,))
        existing = cursor.fetchone()
        
        if existing:
            user_id, existing_username, role, approval_status, is_active = existing
            print(f"\nUser '{username}' already exists!")
            print(f"  ID: {user_id}")
            print(f"  Role: {role}")
            print(f"  Approval Status: {approval_status}")
            print(f"  Active: {'Yes' if is_active else 'No'}")
            
            # Update user
            cursor.execute("""
                UPDATE Users 
                SET password_hash = %s, 
                    role = 'admin',
                    teacher_approval_status = NULL,
                    is_active = 1
                WHERE username = %s
            """, (hash_password(password), username))
            conn.commit()
            print(f"\n✅ User '{username}' updated successfully!")
        else:
            # Create new user
            cursor.execute("""
                INSERT INTO Users (username, password_hash, role, is_active, teacher_approval_status, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (
                username,
                hash_password(password),
                "admin",
                1,
                None  # NULL = No approval required (Admin, Super Admin, and Students don't need approval - only Teachers do)
            ))
            conn.commit()
            print(f"\n✅ Admin user '{username}' created successfully!")
        
        # Verify
        cursor.execute("""
            SELECT id, username, role, teacher_approval_status, is_active 
            FROM Users 
            WHERE username = %s
        """, (username,))
        user = cursor.fetchone()
        if user:
            print(f"\n📋 User Details:")
            print(f"  ID: {user[0]}")
            print(f"  Username: {user[1]}")
            print(f"  Role: {user[2]}")
            print(f"  Approval Status: {user[3] or 'None (No approval required - Admin users bypass approval)'}")
            print(f"  Active: {'Yes' if user[4] else 'No'}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Done! You can now login with:")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print("=" * 60)
        
        return True
        
    except mysql.connector.Error as e:
        print(f"\n❌ Database Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_admin()

