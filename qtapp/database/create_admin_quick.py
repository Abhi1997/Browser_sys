"""
Quick script to create admin user with username 'admin' and password 'admin123!'
No approval required for admin users
"""

import sys
import io
import os
from hashlib import sha256

# Fix encoding for Windows console (Windows only)
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Import MySQL connector
try:
    import mysql.connector
except ImportError:
    print("❌ mysql-connector-python is not installed.")
    print("   Install it with: pip install mysql-connector-python")
    exit(1)

# ----------------------------
# Database Configuration
# ----------------------------
DB_HOST = os.getenv("DB_HOST", "srv1882.hstgr.io")
DB_USER = os.getenv("DB_USER", "u976383844_abhi097")
DB_PASSWORD = os.getenv("DB_PASSWORD", "!nN0v@tion113")
DB_NAME = os.getenv("DB_NAME", "u976383844_dces")
DB_PORT = int(os.getenv("DB_PORT", 3306))

DB_CONFIG = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "port": DB_PORT,
    "database": DB_NAME
}

# ----------------------------
# Utility functions
# ----------------------------
def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return sha256(password.encode()).hexdigest()

# ----------------------------
# Main function to create admin
# ----------------------------
def create_admin():
    username = "admin"
    password = "admin123!"

    print("Creating admin user...")
    print("=" * 60)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print("=" * 60)

    try:
        # Connect to the database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Check if the admin already exists
        cursor.execute("""
            SELECT id, username, role, teacher_approval_status, is_active
            FROM Users
            WHERE username = %s
        """, (username,))
        existing = cursor.fetchone()

        if existing:
            user_id, _, role, approval_status, is_active = existing
            print(f"\nUser '{username}' already exists!")
            print(f"  ID: {user_id}")
            print(f"  Role: {role}")
            print(f"  Approval Status: {approval_status}")
            print(f"  Active: {'Yes' if is_active else 'No'}")

            # Update existing user
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
            # Create new admin user
            cursor.execute("""
                INSERT INTO Users (username, password_hash, role, is_active, teacher_approval_status, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (
                username,
                hash_password(password),
                "admin",
                1,
                None  # Admin does not require approval
            ))
            conn.commit()
            print(f"\n✅ Admin user '{username}' created successfully!")

        # Verify creation
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
            print(f"  Approval Status: {user[3] or 'None (Admin users bypass approval)'}")
            print(f"  Active: {'Yes' if user[4] else 'No'}")

        # Close connection
        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("✅ Done! You can now login with:")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print("=" * 60)

    except mysql.connector.Error as e:
        print(f"\n❌ Database Error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

# ----------------------------
# Run script
# ----------------------------
if __name__ == "__main__":
    create_admin()
