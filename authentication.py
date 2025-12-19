# language: python
# authentication.py
import os
from dotenv import load_dotenv
import mysql.connector
from hashlib import sha256
from datetime import datetime

load_dotenv()  # load .env if present

class Authentication:
    def __init__(self, host="localhost", user="root", password="", database="edubrowser"):
        self.db_config = {
            "host": os.getenv("DB_HOST", host),
            "user": os.getenv("DB_USER", user),
            "password": os.getenv("DB_PASSWORD", password),
            "database": os.getenv("DB_NAME", database)
        }

    def register_user(self, username, password, role, permissions=None, group_code=None):
        if role not in ("teacher", "admin", "student", "super-admin"):
            raise ValueError("Invalid role")
        hashed_password = sha256(password.encode()).hexdigest()
        created_at = datetime.now()
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Users (username, password_hash, role, permissions, group_code, created_at, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (username, hashed_password, role, permissions, group_code, created_at, 1))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except mysql.connector.Error:
            return False

    def validate_user(self, username, password):
        hashed_password = sha256(password.encode()).hexdigest()
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, role FROM Users WHERE username=%s AND password_hash=%s AND is_active=1
        """, (username, hashed_password))
        user = cursor.fetchone()
        if user:
            user_id, role = user
            cursor.execute("UPDATE Users SET last_login=%s WHERE id=%s", (datetime.now(), user_id))
            conn.commit()
            cursor.close()
            conn.close()
            return role
        cursor.close()
        conn.close()
        return None