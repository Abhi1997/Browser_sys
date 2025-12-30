# language: python
# authentication.py
import os
import socket
import platform
import uuid
from dotenv import load_dotenv
import mysql.connector
from hashlib import sha256
from datetime import datetime, timedelta
import jwt
import urllib.parse

load_dotenv()  # load .env if present

class Authentication:
    def __init__(self, host="localhost", user="root", password="", 
                 database="edubrowser"):
        """
        Initialize authentication with single database support
        
        Args:
            host: MySQL host
            user: MySQL user
            password: MySQL password
            database: Database name (default: edubrowser)
        """
        # Auto-detect if we're on host machine or Docker container
        db_host = os.getenv("DB_HOST", host)
        # If DB_HOST is set to 'db' but we're on host machine, use localhost
        if db_host == "db":
            try:
                # Try to resolve 'db' - if it fails, we're on host machine
                socket.gethostbyname('db')
            except socket.gaierror:
                # Can't resolve 'db', we're on host machine, use localhost
                db_host = "localhost"
        
        self.db_base_config = {
            "host": db_host,
            "user": os.getenv("DB_USER", user),
            "password": os.getenv("DB_PASSWORD", password),
        }
        
        # Add port if specified (for Docker MySQL on different port)
        db_port = os.getenv("DB_PORT")
        if db_port:
            try:
                self.db_base_config["port"] = int(db_port)
            except ValueError:
                pass  # Invalid port, ignore
        
        self.database = os.getenv("DB_NAME", os.getenv("DATABASE", database))
        
    def _get_conn(self):
        """Get connection to database"""
        config = self.db_base_config.copy()
        config["database"] = self.database
        return mysql.connector.connect(**config)
    
    # Backward compatibility aliases
    def _get_auth_conn(self):
        """Get connection to database (alias for backward compatibility)"""
        return self._get_conn()
    
    def _get_student_conn(self):
        """Get connection to database (alias for backward compatibility)"""
        return self._get_conn()
    
    def _get_activity_conn(self):
        """Get connection to database (alias for backward compatibility)"""
        return self._get_conn()
    
    def get_device_info(self):
        """
        Collect device information (IP, MAC, fingerprint)
        Returns: dict with device_id, ip_address, mac_address, device_fingerprint
        """
        try:
            # Get IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('8.8.8.8', 80))
                ip_address = s.getsockname()[0]
            except Exception:
                ip_address = '127.0.0.1'
            finally:
                s.close()
            
            # Get MAC address (platform-specific)
            mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                                   for elements in range(0, 2*6, 2)][::-1])
            
            # Generate device fingerprint
            device_fingerprint = f"{platform.system()}_{platform.machine()}_{platform.processor()}_{mac_address}"
            
            # Generate or retrieve device ID
            device_id = str(uuid.uuid4())
            
            return {
                "device_id": device_id,
                "ip_address": ip_address,
                "mac_address": mac_address,
                "device_fingerprint": device_fingerprint
            }
        except Exception as e:
            # Fallback values
            return {
                "device_id": str(uuid.uuid4()),
                "ip_address": "127.0.0.1",
                "mac_address": "00:00:00:00:00:00",
                "device_fingerprint": "unknown"
            }
    
    def register_device(self, user_id, device_info):
        """
        Register or update device information
        
        Args:
            user_id: User ID
            device_info: Dict with device_id, ip_address, mac_address, device_fingerprint
        """
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            # Check if device exists
            cursor.execute("""
                SELECT id FROM Devices WHERE device_id=%s AND user_id=%s
            """, (device_info["device_id"], user_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing device
                cursor.execute("""
                    UPDATE Devices 
                    SET ip_address=%s, mac_address=%s, device_fingerprint=%s, 
                        last_seen=%s, is_active=1
                    WHERE device_id=%s AND user_id=%s
                """, (device_info["ip_address"], device_info["mac_address"], 
                      device_info["device_fingerprint"], datetime.now(),
                      device_info["device_id"], user_id))
            else:
                # Insert new device
                cursor.execute("""
                    INSERT INTO Devices (device_id, user_id, ip_address, mac_address, 
                                      device_fingerprint, registered_at, last_seen, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
                """, (device_info["device_id"], user_id, device_info["ip_address"],
                      device_info["mac_address"], device_info["device_fingerprint"],
                      datetime.now(), datetime.now()))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error registering device: {e}")
            return False
    
    def register_user(self, username, password=None, gmail=None, role="student", 
                     permissions=None, group_code=None):
        """
        Register a new user
        
        Args:
            username: Username
            password: Password (optional if using Gmail OAuth)
            gmail: Gmail address (optional)
            role: User role
            permissions: JSON permissions string
            group_code: Group/class code
        """
        if role not in ("teacher", "admin", "student", "superadmin"):
            raise ValueError("Invalid role")
        
        if not password and not gmail:
            raise ValueError("Either password or gmail must be provided")
        
        hashed_password = sha256(password.encode()).hexdigest() if password else None
        created_at = datetime.now()
        
        # Set teacher approval status
        # Only teachers require approval - admin, superadmin, and students don't need approval
        teacher_approval_status = None
        if role == "teacher":
            teacher_approval_status = "PENDING"  # Teachers need admin approval before login
        # All other roles (admin, superadmin, student) have teacher_approval_status = NULL (no approval needed)
        
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Users (username, gmail, password_hash, role, permissions, 
                                 group_code, created_at, is_active, teacher_approval_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (username, gmail, hashed_password, role, permissions, group_code, 
                  created_at, 1, teacher_approval_status))
            conn.commit()
            user_id = cursor.lastrowid
            cursor.close()
            conn.close()
            
            # If student, create student profile
            if role == "student":
                self._create_student_profile(user_id, username, gmail)
            
            return user_id
        except mysql.connector.Error as e:
            print(f"Error registering user: {e}")
            return None
    
    def _create_student_profile(self, user_id, username, gmail):
        """Create student profile"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Students (student_id, user_id, gmail, assigned_mode, 
                                    violation_count, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, user_id, gmail, "restricted", 0, 1))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating student profile: {e}")
            return False
    
    def validate_user(self, username, password):
        """Validate user credentials (legacy method)"""
        hashed_password = sha256(password.encode()).hexdigest()
        conn = self._get_auth_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, role FROM Users 
            WHERE username=%s AND password_hash=%s AND is_active=1
        """, (username, hashed_password))
        user = cursor.fetchone()
        if user:
            user_id, role = user
            cursor.execute("UPDATE Users SET last_login=%s WHERE id=%s", 
                         (datetime.now(), user_id))
            conn.commit()
            cursor.close()
            conn.close()
            return role
        cursor.close()
        conn.close()
        return None
    
    def validate_user_with_id(self, username, password):
        """Validate user and return both role and user_id"""
        hashed_password = sha256(password.encode()).hexdigest()
        conn = self._get_auth_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, role, teacher_approval_status FROM Users 
            WHERE username=%s AND password_hash=%s AND is_active=1
        """, (username, hashed_password))
        user = cursor.fetchone()
        if user:
            user_id, role, approval_status = user
            
            # Check teacher approval (admin, superadmin, and students don't require approval)
            # Only teachers need approval before they can login
            if role == "teacher" and approval_status != "APPROVED":
                cursor.close()
                conn.close()
                return None  # Teacher not approved
            
            # Admin, superadmin, and students can login without approval
            
            cursor.execute("UPDATE Users SET last_login=%s WHERE id=%s", 
                         (datetime.now(), user_id))
            conn.commit()
            cursor.close()
            conn.close()
            return (role, user_id)
        cursor.close()
        conn.close()
        return None
    
    def authenticate_user(self, username, password, device_id):
        """
        Authenticate user and generate dashboard token
        
        Args:
            username: Username
            password: Password
            device_id: Device ID for token
            
        Returns: dict with success, token, and user info or None
        """
        result = self.validate_user_with_id(username, password)
        
        if not result:
            return {"success": False, "error": "Invalid credentials"}
        
        role, user_id = result
        
        try:
            # Get full user info
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, gmail, role, is_active 
                FROM Users 
                WHERE id=%s
            """, (user_id,))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not user_data:
                return {"success": False, "error": "User not found"}
            
            # Generate token
            token = self.generate_token(username, role, user_id)
            
            # Register/update device
            device_info = {
                "device_id": device_id,
                "ip_address": "127.0.0.1",
                "mac_address": "00:00:00:00:00:00",
                "device_fingerprint": "web-dashboard"
            }
            self.register_device(user_id, device_info)
            
            return {
                "success": True,
                "token": token,
                "user": {
                    "id": user_data[0],
                    "username": user_data[1],
                    "gmail": user_data[2],
                    "role": user_data[3],
                    "is_active": bool(user_data[4])
                }
            }
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return {"success": False, "error": str(e)}
    
    def validate_gmail_user(self, gmail):
        """
        Validate user by Gmail (for OAuth)
        Returns: (role, user_id) or None
        """
        conn = self._get_auth_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, role, teacher_approval_status FROM Users 
            WHERE gmail=%s AND is_active=1
        """, (gmail,))
        user = cursor.fetchone()
        if user:
            user_id, role, approval_status = user
            
            # Check teacher approval (admin, superadmin, and students don't require approval)
            # Only teachers need approval before they can login
            if role == "teacher" and approval_status != "APPROVED":
                cursor.close()
                conn.close()
                return None  # Teacher not approved
            
            # Admin, superadmin, and students can login without approval
            
            cursor.execute("UPDATE Users SET last_login=%s WHERE id=%s", 
                         (datetime.now(), user_id))
            conn.commit()
            cursor.close()
            conn.close()
            return (role, user_id)
        cursor.close()
        conn.close()
        return None
    
    def approve_teacher(self, teacher_id, admin_id):
        """Approve a pending teacher"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Users 
                SET teacher_approval_status='APPROVED', 
                    approved_by=%s, 
                    approved_at=%s
                WHERE id=%s AND role='teacher'
            """, (admin_id, datetime.now(), teacher_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            # Log admin action
            self._log_admin_action(admin_id, "teacher_approve", teacher_id, 
                                  f"Approved teacher ID {teacher_id}")
            return True
        except Exception as e:
            print(f"Error approving teacher: {e}")
            return False
    
    def _log_admin_action(self, admin_id, action_type, target_user_id, details):
        """Log admin action"""
        try:
            device_info = self.get_device_info()
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO AdminActions (admin_id, action_type, target_user_id, 
                                       details, ip_address, device_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (admin_id, action_type, target_user_id, details, 
                  device_info["ip_address"], device_info["device_id"], datetime.now()))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error logging admin action: {e}")
    
    def generate_token(self, username, role, user_id):
        """Generate JWT token for dashboard authentication"""
        secret_key = os.getenv("JWT_SECRET", "your-secret-key-change-this")
        # Normalize role format for consistency (superadmin -> super-admin)
        normalized_role = "super-admin" if role == "superadmin" else role
        payload = {
            "user_id": user_id,  # Keep snake_case for Python compatibility
            "userId": user_id,    # Also include camelCase for React compatibility
            "username": username,
            "role": normalized_role,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, secret_key, algorithm="HS256")
    
    def validate_token(self, token, device_id):
        """
        Validate JWT token and device ID
        Checks both DashboardTokens table and Devices table
        
        Returns: dict with user info or None
        """
        try:
            secret_key = os.getenv("JWT_SECRET", "your-secret-key-change-this")
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            
            user_id = payload.get("user_id")
            if not user_id:
                return None
            
            conn = self._get_conn()
            cursor = conn.cursor()
            
            # First check DashboardTokens table (for dashboard access)
            cursor.execute("""
                SELECT u.id, u.username, u.role, u.is_active
                FROM DashboardTokens dt
                JOIN Users u ON dt.user_id = u.id
                WHERE dt.token=%s AND dt.device_id=%s AND dt.user_id=%s 
                  AND dt.is_active=1 AND dt.expires_at > UTC_TIMESTAMP()
                  AND u.is_active=1
            """, (token, device_id, user_id))
            
            result = cursor.fetchone()
            
            # If not found in DashboardTokens, check Devices table (for general access)
            if not result:
                cursor.execute("""
                    SELECT u.id, u.username, u.role, u.is_active
                    FROM Devices d
                    JOIN Users u ON d.user_id = u.id
                    WHERE d.device_id=%s AND d.user_id=%s AND d.is_active=1 AND u.is_active=1
                """, (device_id, user_id))
                result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if result:
                # Both queries return the same format: (u.id, u.username, u.role, u.is_active)
                return {
                    "id": result[0],
                    "username": result[1],
                    "role": result[2],
                    "is_active": bool(result[3])
                }
            return None
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            print(f"Error validating token: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_device_id(self):
        """Generate a unique device ID"""
        return str(uuid.uuid4())
    
    def create_dashboard_token(self, user_id, device_id):
        """
        Create dashboard authorization token
        
        Returns: dashboard token string
        """
        try:
            token = self.generate_token("dashboard", "dashboard", user_id)
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO DashboardTokens (user_id, device_id, token, expires_at, is_active)
                VALUES (%s, %s, %s, %s, 1)
            """, (user_id, device_id, token, expires_at))
            conn.commit()
            cursor.close()
            conn.close()
            
            return token
        except Exception as e:
            print(f"Error creating dashboard token: {e}")
            return None
    
    def get_student_mode(self, user_id):
        """Get assigned mode for a student"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT assigned_mode FROM Students 
                WHERE user_id=%s AND is_active=1
            """, (user_id,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                return result[0]
            return "restricted"  # Default mode
        except Exception as e:
            print(f"Error getting student mode: {e}")
            return "restricted"
    
    def set_student_mode(self, student_id, new_mode, changed_by):
        """Set student mode (admin/teacher only)"""
        if new_mode not in ("exam", "study", "restricted", "free"):
            raise ValueError("Invalid mode")
        
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            # Get current mode
            cursor.execute("""
                SELECT assigned_mode FROM Students WHERE student_id=%s
            """, (student_id,))
            current = cursor.fetchone()
            old_mode = current[0] if current else None
            
            # Update mode
            cursor.execute("""
                UPDATE Students SET assigned_mode=%s, updated_at=%s 
                WHERE student_id=%s
            """, (new_mode, datetime.now(), student_id))
            
            # Log mode change
            if old_mode:
                cursor.execute("""
                    INSERT INTO ModeHistory (student_id, old_mode, new_mode, 
                                           changed_by, changed_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (student_id, old_mode, new_mode, changed_by, datetime.now()))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error setting student mode: {e}")
            return False
    
    @property
    def db_config(self):
        """Legacy property for backward compatibility"""
        config = self.db_base_config.copy()
        config["database"] = self.database
        return config
