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


def _get_jwt_secret():
    """
    Read and normalize JWT_SECRET from environment.
    Use this everywhere we sign/verify tokens so the value always matches the PHP API.
    - Strips whitespace.
    - If the value was accidentally pasted from PHP (e.g. 'jwt_secret' => getenv(...) ?: 'SECRET',),
      extracts only the actual secret string so token verification still works.
    """
    import re
    raw = os.getenv("JWT_SECRET", "your-secret-key-change-this").strip()
    # If it looks like PHP/corrupted (contains => or quotes or getenv), extract the secret
    if not raw or "=>" in raw or "getenv" in raw or ("'" in raw and len(raw) > 60):
        # Try: last quoted substring (e.g. 'ZnLQFGG8...')
        quoted = re.findall(r"'([^']{20,})'", raw)
        if quoted:
            return quoted[-1].strip()
        # Try: longest alphanumeric/url-safe segment (typical JWT secret)
        segments = re.findall(r"[A-Za-z0-9_-]{20,}", raw)
        if segments:
            return max(segments, key=len)
    return raw if raw else "your-secret-key-change-this"


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
        # Use environment variable or provided host (default to remote database)
        db_host = os.getenv("DB_HOST", host or "db.abhinavpaudel.com")
        
        self.db_base_config = {
            "host": db_host,
            "user": os.getenv("DB_USER", user),
            "password": os.getenv("DB_PASSWORD", password),
        }
        
        # Add port if specified
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
        
        # Try connection
        # Note: If MySQL 8.0+ authentication fails, the user may need to:
        # 1. Upgrade mysql-connector-python to a version that supports allow_public_key_retrieval
        # 2. Or change MySQL user authentication method to mysql_native_password
        try:
            return mysql.connector.connect(**config)
        except Exception as e:
            # Check if it's an authentication error that might need allow_public_key_retrieval
            error_str = str(e).lower()
            if "access denied" in error_str or ("authentication" in error_str and "caching_sha2_password" in error_str):
                # Try with allow_public_key_retrieval if connector supports it
                try:
                    import inspect
                    sig = inspect.signature(mysql.connector.connect)
                    if "allow_public_key_retrieval" in sig.parameters:
                        config_with_key = config.copy()
                        config_with_key["allow_public_key_retrieval"] = True
                        return mysql.connector.connect(**config_with_key)
                except (AttributeError, TypeError, Exception):
                    # Parameter not supported or other issue
                    # Raise original error with helpful message
                    raise ConnectionError(
                        f"Database connection failed: {str(e)}\n"
                        f"If using MySQL 8.0+, you may need to:\n"
                        f"1. Upgrade mysql-connector-python: pip install --upgrade mysql-connector-python\n"
                        f"2. Or change MySQL user auth method to mysql_native_password"
                    ) from e
            # Raise original error for other issues
            raise
    
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
        if role not in ("teacher", "admin", "student", "superadmin", "superuser"):
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
        secret_key = _get_jwt_secret()
        # Normalize role format for consistency (superadmin -> super-admin)
        normalized_role = "super-admin" if role == "superadmin" else role
        # Use Unix timestamps (seconds since epoch) as required by dashboard
        now = datetime.utcnow()
        payload = {
            "user_id": user_id,  # Keep snake_case for Python compatibility
            "userId": user_id,    # Also include camelCase for React compatibility
            "username": username,
            "role": normalized_role,
            "iat": int(now.timestamp()),  # Issued at (Unix timestamp in seconds)
            "exp": int((now + timedelta(hours=24)).timestamp())  # Expiration (Unix timestamp in seconds)
        }
        return jwt.encode(payload, secret_key, algorithm="HS256")
    
    def validate_token(self, token, device_id):
        """
        Validate JWT token and device ID
        Checks both DashboardTokens table and Devices table
        
        Returns: dict with user info or None
        """
        try:
            secret_key = _get_jwt_secret()
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
        if new_mode not in ("cached", "study", "restricted", "free"):
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

    def log_dashboard_open(self, user_id, role, action="dashboard_open"):
        """Log dashboard open event by user (who opened dashboard, when). DB: DashboardLogs."""
        try:
            device_info = self.get_device_info()
            conn = self._get_conn()
            cursor = conn.cursor()
            r = (role or "").lower()
            if r == "superuser":
                role_enum = "superuser"
            elif r in ("superadmin", "super-admin"):
                role_enum = "superadmin"
            elif r == "admin":
                role_enum = "admin"
            elif r == "teacher":
                role_enum = "teacher"
            else:
                role_enum = "teacher"
            # Use NOW() in DB so date/time is in server timezone; still pass for compatibility
            cursor.execute("""
                INSERT INTO DashboardLogs (user_id, role, action, endpoint, ip_address, device_id, created_at)
                VALUES (%s, %s, %s, NULL, %s, %s, NOW())
            """, (user_id, role_enum, action, device_info.get("ip_address"), device_info.get("device_id")))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error logging dashboard open: {e}")

    def session_start_or_touch(self, user_id, device_id):
        """Start a browser session or update last_activity_at (for ML session usage logging)."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM Sessions WHERE user_id=%s AND device_id=%s AND is_active=1 ORDER BY id DESC LIMIT 1",
                (user_id, device_id),
            )
            row = cursor.fetchone()
            now = datetime.now()
            exp = now + timedelta(hours=24)
            if row:
                cursor.execute(
                    "UPDATE Sessions SET last_activity_at=%s, expires_at=%s WHERE id=%s",
                    (now, exp, row[0]),
                )
            else:
                cursor.execute(
                    """INSERT INTO Sessions (user_id, device_id, token, created_at, expires_at, last_activity_at, is_active)
                       VALUES (%s, %s, %s, %s, %s, %s, 1)""",
                    (user_id, device_id, device_id or str(uuid.uuid4()), now, exp, now),
                )
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error session_start_or_touch: {e}")

    def session_touch(self, user_id, device_id):
        """Update last_activity_at for current session (call periodically or on activity)."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM Sessions WHERE user_id=%s AND device_id=%s AND is_active=1 ORDER BY id DESC LIMIT 1",
                (user_id, device_id),
            )
            row = cursor.fetchone()
            if row:
                cursor.execute(
                    "UPDATE Sessions SET last_activity_at=%s WHERE id=%s",
                    (datetime.now(), row[0]),
                )
                conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error session_touch: {e}")

    def session_end(self, user_id, device_id):
        """Mark current session as ended (on logout/close)."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Sessions SET is_active=0 WHERE user_id=%s AND device_id=%s AND is_active=1",
                (user_id, device_id),
            )
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error session_end: {e}")

    @staticmethod
    def get_cache_base_dir():
        """Base directory for offline cache files (teachers/admins save here)."""
        import os
        if os.name == "nt":
            base = os.environ.get("APPDATA", os.path.expanduser("~"))
        else:
            base = os.path.join(os.path.expanduser("~"), ".config")
        path = os.path.join(base, "EduBrowser", "cache")
        try:
            os.makedirs(path, exist_ok=True)
        except Exception:
            path = os.path.join(os.path.expanduser("~"), "EduBrowser_cache")
            os.makedirs(path, exist_ok=True)
        return path

    def get_cached_site_path(self, url):
        """Return relative file path for a URL in CachedSites, or None. Used in cached mode."""
        if not url or not url.strip():
            return None
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT file_path FROM CachedSites WHERE url=%s AND is_active=1 LIMIT 1",
                (url.strip()[:2048],),
            )
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            return row[0] if row else None
        except Exception as e:
            print(f"Error get_cached_site_path: {e}")
            return None

    def get_cached_sites_list(self):
        """Return list of {url, title, file_path} for all active cached sites."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT url, title, file_path FROM CachedSites WHERE is_active=1 ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return [{"url": r[0], "title": r[1] or r[0], "file_path": r[2]} for r in rows]
        except Exception as e:
            print(f"Error get_cached_sites_list: {e}")
            return []

    def add_cached_site(self, url, title, file_path, added_by):
        """Add a cached site (teachers/admins). file_path is relative to cache base dir."""
        try:
            if not url or not file_path or not added_by:
                return False
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO CachedSites (url, title, file_path, added_by, is_active)
                   VALUES (%s, %s, %s, %s, 1)""",
                (url[:2048], (title or "")[:512], file_path[:1024], added_by),
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error add_cached_site: {e}")
            return False

    def add_browsing_history(self, user_id, url, page_title=None, device_id=None):
        """Append one visit to BrowsingHistory for the user (for own history and teacher view)."""
        try:
            if not url or not url.strip():
                return
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO BrowsingHistory (user_id, url, page_title, visited_at, device_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, url[:2048], (page_title or "")[:512], datetime.now(), device_id))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            # Table might not exist yet
            print(f"Error adding browsing history: {e}")

    # --- Bookmark methods (Database backed) ---

    def add_bookmark_to_db(self, user_id, url, title=None):
        """Add a bookmark to the database for a specific user."""
        try:
            if not url or not url.strip():
                return False
            conn = self._get_conn()
            cursor = conn.cursor()
            # Update if exists, else insert
            cursor.execute("SELECT id FROM Bookmarks WHERE user_id = %s AND url = %s", (user_id, url))
            existing = cursor.fetchone()
            if existing:
                cursor.execute("""
                    UPDATE Bookmarks SET title = %s, added_at = %s 
                    WHERE id = %s
                """, (title or url, datetime.now(), existing[0]))
            else:
                cursor.execute("""
                    INSERT INTO Bookmarks (user_id, url, title, added_at)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, url[:2048], (title or url)[:512], datetime.now()))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding bookmark to DB: {e}")
            return False

    def get_bookmarks_from_db(self, user_id):
        """Fetch all bookmarks for a specific user from the database."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT url, title, added_at FROM Bookmarks 
                WHERE user_id = %s ORDER BY added_at DESC
            """, (user_id,))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return [{"url": r[0], "title": r[1], "added_at": r[2].isoformat() if r[2] else ""} for r in rows]
        except Exception as e:
            print(f"Error fetching bookmarks from DB: {e}")
            return []

    def remove_bookmark_from_db(self, user_id, url):
        """Remove a bookmark by URL for a specific user."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Bookmarks WHERE user_id = %s AND url = %s", (user_id, url))
            deleted = cursor.rowcount > 0
            conn.commit()
            cursor.close()
            conn.close()
            return deleted
        except Exception as e:
            print(f"Error removing bookmark from DB: {e}")
            return False

    def get_student_bookmarks_from_api(self, student_id_or_user_id, username, role):
        """Fetch a specific student's bookmarks (for teachers/admins monitoring)."""
        try:
            base_url = (os.getenv("API_BASE_URL") or "").rstrip("/")
            if not base_url:
                return []
            token = self.generate_token(username, role, 0) # user_id 0 as placeholder, PHP uses token for auth anyway
            if isinstance(token, bytes):
                token = token.decode("utf-8")
            import urllib.request
            req = urllib.request.Request(
                f"{base_url}/api/students/{student_id_or_user_id}/bookmarks",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                import json
                data = json.loads(resp.read().decode())
            if isinstance(data, dict) and data.get("success") and isinstance(data.get("data"), list):
                return data["data"]
            return []
        except Exception as e:
            print(f"Error fetching student bookmarks from API: {e}")
            return []

    # --- End Bookmark methods ---

    def get_browsing_history(self, user_id, username=None, role=None, limit=200):
        """Fetch current user's browsing history from API (personal only). Returns list of {url, pageTitle, visitedAt}."""
        try:
            import os
            if not username or not role:
                try:
                    conn = self._get_conn()
                    cursor = conn.cursor()
                    cursor.execute("SELECT username, role FROM Users WHERE id = %s", (user_id,))
                    row = cursor.fetchone()
                    cursor.close()
                    conn.close()
                    if row:
                        username = username or row[0]
                        role = role or row[1]
                except Exception:
                    pass
            base_url = (os.getenv("API_BASE_URL") or "").rstrip("/")
            if not base_url:
                return []
            token = self.generate_token(username or "", role or "student", user_id)
            if isinstance(token, bytes):
                token = token.decode("utf-8")
            import urllib.request
            req = urllib.request.Request(
                f"{base_url}/api/history?limit={min(max(limit, 1), 500)}",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                import json
                data = json.loads(resp.read().decode())
            if isinstance(data, dict) and data.get("success") and isinstance(data.get("data"), list):
                return data["data"]
            return []
        except Exception as e:
            print(f"Error fetching browsing history: {e}")
            return []

    def get_user_profile(self, user_id):
        """Get current user's profile (username, gmail) from DB. For in-app profile edit only."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT username, gmail FROM Users WHERE id = %s", (user_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row:
                return {"username": row[0] or "", "gmail": row[1] or ""}
            return {"username": "", "gmail": ""}
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return {"username": "", "gmail": ""}

    def update_user_profile(self, user_id, username=None, gmail=None):
        """Update current user's profile (username, gmail). Returns True on success."""
        if not user_id:
            return False
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            if username is not None and gmail is not None:
                cursor.execute(
                    "UPDATE Users SET username = %s, gmail = %s WHERE id = %s",
                    (str(username).strip()[:100], (gmail or "").strip()[:255], user_id),
                )
            elif username is not None:
                cursor.execute("UPDATE Users SET username = %s WHERE id = %s", (str(username).strip()[:100], user_id))
            elif gmail is not None:
                cursor.execute("UPDATE Users SET gmail = %s WHERE id = %s", (str(gmail or "").strip()[:255], user_id))
            else:
                cursor.close()
                conn.close()
                return True
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False
    
    @property
    def db_config(self):
        """Legacy property for backward compatibility"""
        config = self.db_base_config.copy()
        config["database"] = self.database
        return config
