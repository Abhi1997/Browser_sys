"""
Populate databases with sample data for dashboard visualization

Usage:
    python populate_sample_data.py

Make sure you have:
    1. MySQL server running
    2. Databases created (run setup_databases.py first)
    3. Required Python packages installed (mysql-connector-python)
"""

import sys
import io

# Fix encoding for Windows console to handle emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import mysql.connector
except ImportError:
    print("❌ Error: mysql-connector-python is not installed.")
    print("   Please install it using: pip install mysql-connector-python")
    exit(1)

from datetime import datetime, timedelta
import random
import os

# Try to load .env file if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, use defaults

# Database configuration
# Note: When running on host machine, use 'localhost'
# When running inside Docker, use 'db' (container name)
db_host = os.getenv("DB_HOST", "localhost")

# If DB_HOST is set to 'db' but we're running on host, use localhost
if db_host == "db":
    import socket
    try:
        # Try to resolve 'db' - if it fails, we're on host machine
        socket.gethostbyname('db')
    except socket.gaierror:
        # Can't resolve 'db', we're on host machine, use localhost
        db_host = "localhost"
        print("ℹ️  Running on host machine - using 'localhost' instead of 'db'")

DB_CONFIG = {
    "host": db_host,
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "Innovation"),
}

# Add port if specified (for Docker MySQL on different port)
db_port = os.getenv("DB_PORT")
if db_port:
    try:
        DB_CONFIG["port"] = int(db_port)
    except ValueError:
        pass  # Invalid port, ignore

DATABASE = os.getenv("DB_NAME", os.getenv("DATABASE", "edubrowser"))

# Sample data
SAMPLE_STUDENTS = [
    {"username": "student1", "gmail": "student1@example.com", "mode": "exam"},
    {"username": "student2", "gmail": "student2@example.com", "mode": "study"},
    {"username": "student3", "gmail": "student3@example.com", "mode": "restricted"},
    {"username": "student4", "gmail": "student4@example.com", "mode": "free"},
    {"username": "student5", "gmail": "student5@example.com", "mode": "exam"},
    {"username": "student6", "gmail": "student6@example.com", "mode": "study"},
    {"username": "student7", "gmail": "student7@example.com", "mode": "restricted"},
    {"username": "student8", "gmail": "student8@example.com", "mode": "free"},
    {"username": "student9", "gmail": "student9@example.com", "mode": "exam"},
    {"username": "student10", "gmail": "student10@example.com", "mode": "study"},
]

SAMPLE_TEACHERS = [
    {"username": "teacher1", "gmail": "teacher1@example.com"},
    {"username": "teacher2", "gmail": "teacher2@example.com"},
    {"username": "teacher3", "gmail": "teacher3@example.com"},
]

SAMPLE_ADMINS = [
    {"username": "admin1", "gmail": "admin1@example.com"},
]

EDUCATIONAL_DOMAINS = [
    "wikipedia.org",
    "khanacademy.org",
    "coursera.org",
    "edx.org",
    "stackoverflow.com",
    "github.com",
    "google.com",
    "youtube.com",
    "scholar.google.com",
    "pubmed.ncbi.nlm.nih.gov",
    "ieee.org",
    "acm.org",
    "arxiv.org",
    "jstor.org",
]

BLOCKED_DOMAINS = [
    "facebook.com",
    "twitter.com",
    "instagram.com",
    "tiktok.com",
    "reddit.com",
    "9gag.com",
    "4chan.org",
]

def get_conn():
    """Get database connection"""
    config = DB_CONFIG.copy()
    config["database"] = DATABASE
    return mysql.connector.connect(**config)

def hash_password(password):
    """Hash password using SHA256"""
    from hashlib import sha256
    return sha256(password.encode()).hexdigest()

def populate_users():
    """Populate users"""
    print("📝 Populating users...")
    conn = get_conn()
    cursor = conn.cursor()
    
    # Add students
    for student in SAMPLE_STUDENTS:
        created_at = datetime.now() - timedelta(days=random.randint(1, 90))
        last_login = datetime.now() - timedelta(
            hours=random.randint(0, 72)  # Last login within last 3 days
        ) if random.random() > 0.1 else None  # 10% chance of never logged in
        
        try:
            cursor.execute("""
                INSERT INTO Users (username, gmail, password_hash, role, is_active, created_at, last_login)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                student["username"],
                student["gmail"],
                hash_password("student123"),
                "student",
                1,
                created_at,
                last_login
            ))
        except mysql.connector.IntegrityError:
            # Update existing user with last_login
            cursor.execute("""
                UPDATE Users 
                SET last_login=%s 
                WHERE username=%s AND last_login IS NULL
            """, (
                datetime.now() - timedelta(hours=random.randint(0, 72)),
                student["username"]
            ))
            print(f"  ⚠️  User {student['username']} already exists, updating last_login...")
    
    # Add teachers
    for teacher in SAMPLE_TEACHERS:
        created_at = datetime.now() - timedelta(days=random.randint(1, 60))
        last_login = datetime.now() - timedelta(
            hours=random.randint(0, 48)  # Last login within last 2 days
        ) if random.random() > 0.05 else None  # 5% chance of never logged in
        
        try:
            cursor.execute("""
                INSERT INTO Users (username, gmail, password_hash, role, is_active, 
                                 teacher_approval_status, created_at, last_login)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                teacher["username"],
                teacher["gmail"],
                hash_password("teacher123"),
                "teacher",
                1,
                "APPROVED",
                created_at,
                last_login
            ))
        except mysql.connector.IntegrityError:
            # Update existing user with last_login
            cursor.execute("""
                UPDATE Users 
                SET last_login=%s 
                WHERE username=%s AND last_login IS NULL
            """, (
                datetime.now() - timedelta(hours=random.randint(0, 48)),
                teacher["username"]
            ))
            print(f"  ⚠️  User {teacher['username']} already exists, updating last_login...")
    
    # Add admins
    for admin in SAMPLE_ADMINS:
        created_at = datetime.now() - timedelta(days=random.randint(1, 120))
        last_login = datetime.now() - timedelta(
            hours=random.randint(0, 24)  # Admin logged in recently
        )
        
        try:
            cursor.execute("""
                INSERT INTO Users (username, gmail, password_hash, role, is_active, created_at, last_login)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                admin["username"],
                admin["gmail"],
                hash_password("admin123"),
                "admin",
                1,
                created_at,
                last_login
            ))
        except mysql.connector.IntegrityError:
            # Update existing user with last_login
            cursor.execute("""
                UPDATE Users 
                SET last_login=%s 
                WHERE username=%s AND last_login IS NULL
            """, (
                datetime.now() - timedelta(hours=random.randint(0, 24)),
                admin["username"]
            ))
            print(f"  ⚠️  User {admin['username']} already exists, updating last_login...")
    
    # Also update existing admin user (admin/admin123!) with last_login if missing
    cursor.execute("""
        UPDATE Users 
        SET last_login=%s 
        WHERE username='admin' AND (last_login IS NULL OR last_login < %s)
    """, (
        datetime.now() - timedelta(hours=random.randint(0, 12)),
        datetime.now() - timedelta(days=1)
    ))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("  ✅ Users populated with last_login dates")

def populate_students():
    """Populate student profiles"""
    print("📚 Populating student profiles...")
    conn = get_conn()
    cursor = conn.cursor()
    
    # Get student user IDs
    cursor.execute("SELECT id, username, gmail FROM Users WHERE role='student'")
    students = cursor.fetchall()
    
    for user_id, username, gmail in students:
        # Find matching mode
        mode = "restricted"
        for s in SAMPLE_STUDENTS:
            if s["username"] == username:
                mode = s["mode"]
                break
        
        try:
            cursor.execute("""
                INSERT INTO Students (student_id, user_id, gmail, assigned_mode, 
                                   violation_count, device_id, ip_address, mac_address, 
                                   is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                username,
                user_id,
                gmail,
                mode,
                random.randint(0, 5),
                f"device-{user_id}",
                f"192.168.1.{random.randint(10, 254)}",
                f"{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}",
                1,
                datetime.now() - timedelta(days=random.randint(1, 90)),
                datetime.now() - timedelta(days=random.randint(0, 7))
            ))
        except mysql.connector.IntegrityError:
            print(f"  ⚠️  Student {username} already exists, updating...")
            cursor.execute("""
                UPDATE Students 
                SET assigned_mode=%s, violation_count=%s, updated_at=%s
                WHERE student_id=%s
            """, (mode, random.randint(0, 5), datetime.now(), username))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("  ✅ Student profiles populated")

def populate_whitelist_blacklist():
    """Populate whitelist and blacklist"""
    print("🔗 Populating whitelist and blacklist...")
    conn = get_conn()
    cursor = conn.cursor()
    
    # Get admin user ID
    cursor.execute("SELECT id FROM Users WHERE role='admin' LIMIT 1")
    admin_result = cursor.fetchone()
    admin_id = admin_result[0] if admin_result else 1
    
    # Add whitelist entries
    modes = ["exam", "study", "restricted", "free"]
    for domain in EDUCATIONAL_DOMAINS:
        for mode in modes:
            try:
                cursor.execute("""
                    INSERT INTO WhitelistDomains (domain, mode, description, added_by, is_active, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    domain,
                    mode,
                    f"Educational resource for {mode} mode",
                    admin_id,
                    1,
                    datetime.now() - timedelta(days=random.randint(1, 30))
                ))
            except mysql.connector.IntegrityError:
                pass  # Already exists
    
    # Add blacklist entries
    for domain in BLOCKED_DOMAINS:
        for mode in ["exam", "study", "restricted"]:
            try:
                cursor.execute("""
                    INSERT INTO BlacklistDomains (domain, mode, reason, added_by, is_active, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    domain,
                    mode,
                    f"Social media/entertainment blocked in {mode} mode",
                    admin_id,
                    1,
                    datetime.now() - timedelta(days=random.randint(1, 30))
                ))
            except mysql.connector.IntegrityError:
                pass  # Already exists
    
    conn.commit()
    cursor.close()
    conn.close()
    print("  ✅ Whitelist and blacklist populated")

def populate_devices():
    """Populate device registrations"""
    print("💻 Populating devices...")
    conn = get_conn()
    cursor = conn.cursor()
    
    # Get all users
    cursor.execute("SELECT id FROM Users")
    users = cursor.fetchall()
    
    for (user_id,) in users:
        try:
            cursor.execute("""
                INSERT INTO Devices (device_id, user_id, ip_address, mac_address, 
                                   device_fingerprint, registered_at, last_seen, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                f"device-{user_id}",
                user_id,
                f"192.168.1.{random.randint(10, 254)}",
                f"{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}",
                f"Windows_{random.randint(10,11)}_x64",
                datetime.now() - timedelta(days=random.randint(1, 30)),
                datetime.now() - timedelta(hours=random.randint(0, 24)),
                1
            ))
        except mysql.connector.IntegrityError:
            pass  # Already exists
    
    conn.commit()
    cursor.close()
    conn.close()
    print("  ✅ Devices populated")

def populate_activity_logs():
    """Populate activity logs with more diverse data"""
    print("📊 Populating activity logs...")
    conn = get_conn()
    cursor = conn.cursor()
    
    # Get all students
    cursor.execute("SELECT student_id, user_id, assigned_mode FROM Students")
    students = cursor.fetchall()
    
    # Generate activity for last 14 days (more data for better charts)
    for student_id, user_id, mode in students:
        # Generate 10-30 activity entries per student
        num_entries = random.randint(10, 30)
        for _ in range(num_entries):
            # Random time in last 14 days
            visit_start = datetime.now() - timedelta(
                days=random.randint(0, 14),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            visit_duration = random.randint(30, 3600)  # 30 seconds to 1 hour
            visit_end = visit_start + timedelta(seconds=visit_duration)
            
            # Choose domain based on mode
            if mode == "free":
                domain = random.choice(EDUCATIONAL_DOMAINS + BLOCKED_DOMAINS)
                is_allowed = 1
            elif mode in ["exam", "study"]:
                domain = random.choice(EDUCATIONAL_DOMAINS)
                is_allowed = 1
            else:  # restricted
                domain = random.choice(EDUCATIONAL_DOMAINS[:5])  # Limited selection
                is_allowed = 1
            
            url = f"https://{domain}/page{random.randint(1, 100)}"
            
            cursor.execute("""
                INSERT INTO ActivityLogs (student_id, user_id, url, domain, mode,
                                        visit_duration, visit_start, visit_end,
                                        device_id, ip_address, mac_address, is_allowed, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                student_id,
                user_id,
                url,
                domain,
                mode,
                visit_duration,
                visit_start,
                visit_end,
                f"device-{user_id}",
                f"192.168.1.{random.randint(10, 254)}",
                f"{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}",
                is_allowed,
                visit_start
            ))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("  ✅ Activity logs populated (last 14 days)")

def populate_violations():
    """Populate violation logs with more diverse data"""
    print("⚠️  Populating violations...")
    conn = get_conn()
    cursor = conn.cursor()
    
    # Get all students (we'll create violations for some of them)
    cursor.execute("SELECT student_id, user_id, assigned_mode FROM Students")
    all_students = cursor.fetchall()
    
    # Select 60% of students to have violations
    students_with_violations = random.sample(all_students, max(1, int(len(all_students) * 0.6)))
    students = students_with_violations
    
    violation_types = ["url_blocked", "mode_bypass_attempt", "time_window_violation", "unauthorized_action"]
    severities = ["low", "medium", "high", "critical"]
    
    for student_id, user_id, mode in students:
        # Generate 1-3 violations per student
        num_violations = random.randint(1, 3)
        for i in range(num_violations):
            violation_type = random.choice(violation_types)
            severity = random.choice(severities)
            
            # Higher severity for exam mode violations
            if mode == "exam" and severity == "low":
                severity = random.choice(["medium", "high"])
            
            attempted_url = f"https://{random.choice(BLOCKED_DOMAINS)}/page{random.randint(1, 100)}"
            
            created_at = datetime.now() - timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23)
            )
            
            descriptions = {
                "url_blocked": f"Attempted to access blocked domain: {attempted_url.split('/')[2]}",
                "mode_bypass_attempt": f"Attempted to bypass {mode} mode restrictions",
                "time_window_violation": "Access attempted outside allowed time window",
                "unauthorized_action": "Unauthorized action detected"
            }
            
            cursor.execute("""
                INSERT INTO Violations (student_id, user_id, violation_type, description,
                                      attempted_url, current_mode, device_id, ip_address,
                                      mac_address, severity, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                student_id,
                user_id,
                violation_type,
                descriptions.get(violation_type, "Security violation detected"),
                attempted_url,
                mode,
                f"device-{user_id}",
                f"192.168.1.{random.randint(10, 254)}",
                f"{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}",
                severity,
                created_at
            ))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("  ✅ Violations populated")

def populate_mode_history():
    """Populate mode change history"""
    print("📜 Populating mode history...")
    conn = get_conn()
    cursor = conn.cursor()
    
    # Get admin user ID
    cursor.execute("SELECT id FROM Users WHERE role='admin' LIMIT 1")
    admin_result = cursor.fetchone()
    admin_id = admin_result[0] if admin_result else 1
    
    # Get students
    cursor.execute("SELECT student_id, assigned_mode FROM Students")
    students = cursor.fetchall()
    
    modes = ["exam", "study", "restricted", "free"]
    
    for student_id, current_mode in students:
        # Generate 1-2 mode changes per student
        num_changes = random.randint(1, 2)
        old_mode = None
        
        for i in range(num_changes):
            if old_mode is None:
                old_mode = random.choice([m for m in modes if m != current_mode])
            
            new_mode = random.choice([m for m in modes if m != old_mode])
            
            changed_at = datetime.now() - timedelta(
                days=random.randint(1, 30),
                hours=random.randint(0, 23)
            )
            
            reasons = [
                "Exam period started",
                "Study period assigned",
                "Restrictions applied",
                "Free browsing enabled",
                "Mode updated by admin"
            ]
            
            cursor.execute("""
                INSERT INTO ModeHistory (student_id, old_mode, new_mode, changed_by, changed_at, reason)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                student_id,
                old_mode,
                new_mode,
                admin_id,
                changed_at,
                random.choice(reasons)
            ))
            
            old_mode = new_mode
    
    conn.commit()
    cursor.close()
    conn.close()
    print("  ✅ Mode history populated")

def populate_teacher_actions():
    """Populate teacher action logs"""
    print("👨‍🏫 Populating teacher actions...")
    conn = get_conn()
    cursor = conn.cursor()
    
    # Get teachers
    cursor.execute("SELECT id FROM Users WHERE role='teacher'")
    teachers = cursor.fetchall()
    
    # Get students
    cursor.execute("SELECT student_id FROM Students LIMIT 10")
    students = cursor.fetchall()
    
    action_types = ["mode_change", "view_student", "view_activity", "whitelist_add"]
    
    for (teacher_id,) in teachers:
        # Generate 5-10 actions per teacher
        num_actions = random.randint(5, 10)
        for _ in range(num_actions):
            action_type = random.choice(action_types)
            target_student = random.choice(students)[0] if students else None
            
            details = {
                "mode_change": f"Changed mode for student {target_student}",
                "view_student": f"Viewed profile of student {target_student}",
                "view_activity": f"Viewed activity logs for student {target_student}",
                "whitelist_add": "Added domain to whitelist"
            }
            
            created_at = datetime.now() - timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23)
            )
            
            cursor.execute("""
                INSERT INTO TeacherActions (teacher_id, action_type, target_student_id, details,
                                          ip_address, device_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                teacher_id,
                action_type,
                target_student,
                details.get(action_type, "Action performed"),
                f"192.168.1.{random.randint(10, 254)}",
                f"device-{teacher_id}",
                created_at
            ))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("  ✅ Teacher actions populated")

def main():
    """Main function to populate all databases"""
    print("=" * 60)
    print("🚀 Populating Databases with Sample Data")
    print("=" * 60)
    print()
    
    try:
        populate_users()
        populate_students()
        populate_devices()
        populate_whitelist_blacklist()
        populate_activity_logs()
        populate_violations()
        populate_mode_history()
        populate_teacher_actions()
        
        print()
        print("=" * 60)
        print("✅ Sample data population completed!")
        print("=" * 60)
        print()
        print("📋 Summary:")
        print(f"  - Users: {len(SAMPLE_STUDENTS) + len(SAMPLE_TEACHERS) + len(SAMPLE_ADMINS)}")
        print(f"  - Students: {len(SAMPLE_STUDENTS)}")
        print(f"  - Teachers: {len(SAMPLE_TEACHERS)}")
        print(f"  - Admins: {len(SAMPLE_ADMINS)}")
        print(f"  - Whitelist domains: {len(EDUCATIONAL_DOMAINS)}")
        print(f"  - Blacklist domains: {len(BLOCKED_DOMAINS)}")
        print()
        print("🔑 Default Passwords:")
        print("  - Students: student123")
        print("  - Teachers: teacher123")
        print("  - Admins: admin123")
        print()
        print("💡 You can now view the data in the dashboard!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

