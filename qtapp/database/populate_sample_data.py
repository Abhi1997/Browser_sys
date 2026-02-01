"""
Populate EduBrowser database with sample data for dashboard visualization

Usage:
    python populate_sample_data.py

Requirements:
    - MySQL server running (Hostinger remote database)
    - Databases created (run setup_databases.py first)
    - Python packages: mysql-connector-python
"""

import sys
import io
import os
import random
from datetime import datetime, timedelta
from hashlib import sha256

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import mysql.connector
except ImportError:
    print("❌ mysql-connector-python is not installed.")
    print("   Install it using: pip install mysql-connector-python")
    sys.exit(1)

# Load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- Database Configuration ---
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

# Validate required database credentials
if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
    raise ValueError("DB_HOST, DB_USER, DB_PASSWORD, and DB_NAME must be set in .env file")

DB_CONFIG = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME,
    "port": DB_PORT
}

# --- Sample Data ---
SAMPLE_STUDENTS = [{"username": f"student{i}", "gmail": f"student{i}@example.com", "mode": random.choice(["cached","study","restricted","free"])} for i in range(1,11)]
SAMPLE_TEACHERS = [{"username": f"teacher{i}", "gmail": f"teacher{i}@example.com"} for i in range(1,4)]
SAMPLE_ADMINS = [{"username": "admin", "gmail": "admin@example.com"}]

EDU_DOMAINS = [
    "wikipedia.org","khanacademy.org","coursera.org","edx.org","stackoverflow.com","github.com",
    "google.com","youtube.com","scholar.google.com","pubmed.ncbi.nlm.nih.gov"
]

BLOCKED_DOMAINS = [
    "facebook.com","twitter.com","instagram.com","tiktok.com","reddit.com"
]

# --- Helper Functions ---
def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

def hash_password(password):
    return sha256(password.encode()).hexdigest()

# --- Populate Functions ---
def populate_users():
    print("📝 Populating users...")
    conn = get_conn()
    cursor = conn.cursor()
    # Students
    for s in SAMPLE_STUDENTS:
        try:
            cursor.execute("""
                INSERT INTO Users (username, gmail, password_hash, role, is_active, created_at)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (s["username"], s["gmail"], hash_password("student123"), "student", 1, datetime.now()))
        except mysql.connector.IntegrityError:
            pass
    # Teachers
    for t in SAMPLE_TEACHERS:
        try:
            cursor.execute("""
                INSERT INTO Users (username, gmail, password_hash, role, is_active, teacher_approval_status, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (t["username"], t["gmail"], hash_password("teacher123"), "teacher", 1, "APPROVED", datetime.now()))
        except mysql.connector.IntegrityError:
            pass
    # Admins
    for a in SAMPLE_ADMINS:
        try:
            cursor.execute("""
                INSERT INTO Users (username, gmail, password_hash, role, is_active, created_at)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (a["username"], a["gmail"], hash_password("admin123"), "admin", 1, datetime.now()))
        except mysql.connector.IntegrityError:
            pass
    conn.commit()
    cursor.close()
    conn.close()
    print("  ✅ Users populated.")

def populate_students():
    print("📚 Populating student profiles...")
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, gmail FROM Users WHERE role='student'")
    students = cursor.fetchall()
    for user_id, username, gmail in students:
        mode = next((s["mode"] for s in SAMPLE_STUDENTS if s["username"]==username), "restricted")
        try:
            cursor.execute("""
                INSERT INTO Students (student_id, user_id, gmail, assigned_mode, violation_count, device_id, ip_address, mac_address, is_active, created_at, updated_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                username, user_id, gmail, mode, random.randint(0,5), f"device-{user_id}",
                f"192.168.1.{random.randint(10,254)}",
                f"{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}",
                1, datetime.now()-timedelta(days=random.randint(1,90)), datetime.now()
            ))
        except mysql.connector.IntegrityError:
            cursor.execute("UPDATE Students SET assigned_mode=%s, violation_count=%s, updated_at=%s WHERE student_id=%s",
                           (mode, random.randint(0,5), datetime.now(), username))
    conn.commit()
    cursor.close()
    conn.close()
    print("  ✅ Student profiles populated.")

def populate_whitelist_blacklist():
    print("🔗 Populating whitelist/blacklist...")
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Users WHERE role='admin' LIMIT 1")
    admin_id = cursor.fetchone()[0] if cursor.fetchone() else 1
    modes = ["cached","study","restricted","free"]
    for d in EDU_DOMAINS:
        for m in modes:
            try:
                cursor.execute("INSERT INTO WhitelistDomains (domain, mode, description, added_by, is_active, created_at) VALUES (%s,%s,%s,%s,%s,%s)",
                               (d,m,f"Educational resource for {m}",admin_id,1,datetime.now()))
            except mysql.connector.IntegrityError:
                pass
    for d in BLOCKED_DOMAINS:
        for m in ["cached","study","restricted"]:
            try:
                cursor.execute("INSERT INTO BlacklistDomains (domain, mode, reason, added_by, is_active, created_at) VALUES (%s,%s,%s,%s,%s,%s)",
                               (d,m,f"Blocked in {m}",admin_id,1,datetime.now()))
            except mysql.connector.IntegrityError:
                pass
    conn.commit()
    cursor.close()
    conn.close()
    print("  ✅ Whitelist and blacklist populated.")

def populate_devices():
    print("💻 Populating devices...")
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Users")
    users = cursor.fetchall()
    for (uid,) in users:
        try:
            cursor.execute("""
                INSERT INTO Devices (device_id,user_id,ip_address,mac_address,device_fingerprint,registered_at,last_seen,is_active)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                f"device-{uid}", uid, f"192.168.1.{random.randint(10,254)}",
                f"{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}",
                f"Windows_{random.randint(10,11)}_x64",
                datetime.now()-timedelta(days=random.randint(1,30)),
                datetime.now()-timedelta(hours=random.randint(0,24)),
                1
            ))
        except mysql.connector.IntegrityError:
            pass
    conn.commit()
    cursor.close()
    conn.close()
    print("  ✅ Devices populated.")

def populate_activity_logs():
    print("📊 Populating activity logs...")
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, user_id, assigned_mode FROM Students")
    students = cursor.fetchall()
    for student_id, user_id, mode in students:
        for _ in range(random.randint(10,20)):
            start = datetime.now() - timedelta(days=random.randint(0,14), hours=random.randint(0,23))
            duration = random.randint(30,3600)
            end = start + timedelta(seconds=duration)
            domain = random.choice(EDU_DOMAINS+BLOCKED_DOMAINS) if mode=="free" else random.choice(EDU_DOMAINS)
            url = f"https://{domain}/page{random.randint(1,100)}"
            cursor.execute("""
                INSERT INTO ActivityLogs (student_id,user_id,url,domain,mode,visit_duration,visit_start,visit_end,device_id,ip_address,mac_address,is_allowed,created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                student_id,user_id,url,domain,mode,duration,start,end,f"device-{user_id}",
                f"192.168.1.{random.randint(10,254)}",
                f"{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}",
                1,start
            ))
    conn.commit()
    cursor.close()
    conn.close()
    print("  ✅ Activity logs populated.")

def populate_violations():
    print("⚠️ Populating violations...")
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id,user_id,assigned_mode FROM Students")
    students = cursor.fetchall()
    types = ["url_blocked","mode_bypass","time_violation","unauthorized_action"]
    severities = ["low","medium","high","critical"]
    for student_id,user_id,mode in random.sample(students, max(1,int(len(students)*0.6))):
        for _ in range(random.randint(1,3)):
            vt = random.choice(types)
            sev = random.choice(severities)
            url = f"https://{random.choice(BLOCKED_DOMAINS)}/page{random.randint(1,100)}"
            cursor.execute("""
                INSERT INTO Violations (student_id,user_id,violation_type,description,attempted_url,current_mode,device_id,ip_address,mac_address,severity,created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                student_id,user_id,vt,f"Violation: {vt}",url,mode,f"device-{user_id}",
                f"192.168.1.{random.randint(10,254)}",
                f"{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}",
                sev,datetime.now()-timedelta(days=random.randint(0,7))
            ))
    conn.commit()
    cursor.close()
    conn.close()
    print("  ✅ Violations populated.")

def populate_mode_history():
    print("📜 Populating mode history...")
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, assigned_mode FROM Students")
    students = cursor.fetchall()
    modes = ["cached","study","restricted","free"]
    for student_id, current_mode in students:
        for _ in range(random.randint(1,5)):
            new_mode = random.choice([m for m in modes if m != current_mode])
            cursor.execute("""
                INSERT INTO ModeHistory (student_id, old_mode, new_mode, changed_at)
                VALUES (%s,%s,%s,%s)
            """, (student_id, current_mode, new_mode, datetime.now()-timedelta(days=random.randint(0,14))))
    conn.commit()
    cursor.close()
    conn.close()
    print("  ✅ Mode history populated.")

# --- Main Execution ---
if __name__ == "__main__":
    populate_users()
    populate_students()
    populate_whitelist_blacklist()
    populate_devices()
    populate_activity_logs()
    populate_violations()
    populate_mode_history()
    print("🎉 All sample data populated successfully!")
