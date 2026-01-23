"""
Backend API Server for Dashboard

This server connects to your Hostinger MySQL database and provides
REST API endpoints for the dashboard.

Run with: python backend/app.py
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
from functools import wraps
import hashlib

load_dotenv()

app = Flask(__name__)
CORS(app, origins=[
    'http://localhost:3000',
    'http://localhost:8080',
    'https://api.abhinavpaudel.com'
])

# Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-super-secret-jwt-key-change-this-in-production')
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'srv1882.hstgr.io'),
    'user': os.getenv('DB_USER', 'u976383844_abhi097'),
    'password': os.getenv('DB_PASSWORD', '!nN0v@tion113'),
    'database': os.getenv('DB_NAME', 'u976383844_dces'),
    'port': int(os.getenv('DB_PORT', 3306))
}

def get_db_connection():
    """Get database connection"""
    return mysql.connector.connect(**DB_CONFIG)

def verify_jwt_token(token):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Remove 'Bearer '
            except:
                pass
        
        if not token:
            return jsonify({
                "success": False,
                "error": "Missing authentication token"
            }), 401
        
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({
                "success": False,
                "error": "Invalid or expired token"
            }), 401
        
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated_function

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/auth/login', methods=['POST'])
def login():
    """Login endpoint - verify admin credentials and return JWT token"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    device_id = data.get('deviceId')
    
    if not username or not password:
        return jsonify({
            "success": False,
            "error": "Username and password required"
        }), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Query user from database
        # Based on actual schema: Users table has password_hash, gmail, created_at, last_login
        cursor.execute("""
            SELECT id, username, password_hash, role, gmail, is_active, 
                   created_at, last_login
            FROM Users 
            WHERE username = %s
        """, (username,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({
                "success": False,
                "error": "Invalid username or password"
            }), 401
        
        # Verify password - Users table uses password_hash column
        # Admin password_hash in DB: 5c06eb3d5a05a19f49476d694ca81a36344660e9d5b98e3d6a6630f31c2422e7
        stored_password_hash = user.get('password_hash', '')
        password_valid = False
        
        # Method 1: SHA256 hash comparison (standard - matches admin123! hash)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if stored_password_hash == password_hash:
            password_valid = True
        # Method 2: Plain text comparison (fallback for unhashed passwords)
        elif stored_password_hash == password:
            password_valid = True
        
        if not password_valid:
            return jsonify({
                "success": False,
                "error": "Invalid username or password"
            }), 401
        
        if not user.get('is_active', True):
            return jsonify({
                "success": False,
                "error": "Account is inactive"
            }), 401
        
        # Generate JWT token
        now = datetime.now()
        payload = {
            'userId': user['id'],
            'user_id': user['id'],
            'username': user['username'],
            'role': 'super-admin' if user['role'] == 'superadmin' else user['role'],
            'adminId': user.get('adminId'),
            'iat': int(now.timestamp()),
            'exp': int((now + timedelta(hours=24)).timestamp())
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        
        # Update last login
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Users 
                SET last_login = NOW() 
                WHERE id = %s
            """, (user['id'],))
            conn.commit()
            cursor.close()
            conn.close()
        except:
            pass  # Don't fail if update fails
        
        # Format user data - match actual schema
        user_data = {
            "id": str(user['id']),
            "username": user['username'],
            "email": user.get('gmail') or '',  # Users table has gmail, not email
            "role": payload['role'],
            "adminId": None,  # Users table doesn't have adminId column
            "isActive": bool(user.get('is_active', True)),
            "createdAt": str(user.get('created_at') or datetime.now().isoformat()),
            "lastLogin": str(user.get('last_login') or '') if user.get('last_login') else None
        }
        
        return jsonify({
            "success": True,
            "data": {
                "token": token,
                "user": user_data
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Login failed: {str(e)}"
        }), 500

@app.route('/api/auth/verify-token', methods=['POST'])
@require_auth
def verify_token():
    """Verify JWT token and return user information"""
    data = request.json
    token = data.get('token')
    device_id = data.get('deviceId')
    
    payload = request.current_user
    user_id = payload.get('userId') or payload.get('user_id')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, username, gmail, role, is_active, 
                   created_at, last_login
            FROM Users 
            WHERE id = %s
        """, (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404
        
        user_data = {
            "id": str(user['id']),
            "username": user['username'],
            "email": user.get('gmail') or '',  # Users table has gmail column
            "role": 'super-admin' if user['role'] == 'superadmin' else user['role'],
            "adminId": None,  # Users table doesn't have adminId
            "isActive": bool(user.get('is_active', True)),
            "createdAt": str(user.get('created_at') or ''),
            "lastLogin": str(user.get('last_login') or '') if user.get('last_login') else None
        }
        
        return jsonify({
            "success": True,
            "data": {
                "valid": True,
                "user": user_data
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== STATISTICS ENDPOINTS ====================

@app.route('/api/stats', methods=['GET'])
@require_auth
def get_stats():
    """Get system statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Total users
        cursor.execute("SELECT COUNT(*) as total FROM Users")
        total_users = cursor.fetchone()['total']
        
        # Active users
        cursor.execute("SELECT COUNT(*) as active FROM Users WHERE is_active = 1")
        active_users = cursor.fetchone()['active']
        
        # Role distribution
        cursor.execute("""
            SELECT role, COUNT(*) as count 
            FROM Users 
            GROUP BY role
        """)
        roles_data = cursor.fetchall()
        role_distribution = {row['role']: row['count'] for row in roles_data}
        
        # Whitelist size
        try:
            cursor.execute("SELECT COUNT(*) as count FROM WhitelistDomains WHERE is_active = 1")
            whitelist_size = cursor.fetchone()['count']
        except:
            whitelist_size = 0
        
        # Blacklist size
        try:
            cursor.execute("SELECT COUNT(*) as count FROM BlacklistDomains WHERE is_active = 1")
            blacklist_size = cursor.fetchone()['count']
        except:
            blacklist_size = 0
        
        # Recent logins (last 24 hours) - use Users.last_login
        try:
            cursor.execute("""
                SELECT COUNT(*) as count FROM Users 
                WHERE last_login >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            """)
            recent_logins = cursor.fetchone()['count']
        except:
            recent_logins = 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                "totalUsers": total_users,
                "activeUsers": active_users,
                "activeSessions": 0,
                "roleDistribution": {
                    "admin": role_distribution.get('admin', 0),
                    "teacher": role_distribution.get('teacher', 0),
                    "student": role_distribution.get('student', 0)
                },
                "whitelistSize": whitelist_size,
                "blacklistSize": blacklist_size,
                "recentLogins": recent_logins,
                "recentChanges": 0
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== USER ENDPOINTS ====================

@app.route('/api/users', methods=['GET'])
@require_auth
def get_users():
    """Get all users"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, username, gmail, role, is_active, 
                   created_at, last_login
            FROM Users 
            ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": users
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/users', methods=['POST'])
@require_auth
def create_user():
    """Create a new user"""
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Hash password if provided
        password = data.get('password', '')
        if password:
            password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute("""
            INSERT INTO Users (username, password_hash, gmail, role, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (
            data.get('username'),
            password,  # password_hash column
            data.get('email') or data.get('gmail'),  # gmail column
            data.get('role', 'student'),
            data.get('isActive', True)  # is_active column
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT * FROM Users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": user,
            "message": "User created successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/users/<int:user_id>', methods=['PATCH'])
@require_auth
def update_user(user_id):
    """Update a user"""
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        updates = []
        values = []
        
        if 'username' in data:
            updates.append("username = %s")
            values.append(data['username'])
        if 'email' in data or 'gmail' in data:
            updates.append("gmail = %s")
            values.append(data.get('email') or data.get('gmail'))
        if 'role' in data:
            updates.append("role = %s")
            values.append(data['role'])
        if 'isActive' in data:
            updates.append("is_active = %s")
            values.append(data['isActive'])
        
        if not updates:
            return jsonify({
                "success": False,
                "error": "No fields to update"
            }), 400
        
        values.append(user_id)
        query = f"UPDATE Users SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(query, values)
        conn.commit()
        
        cursor.execute("SELECT * FROM Users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": user
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@require_auth
def delete_user(user_id):
    """Delete a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Users WHERE id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "User deleted successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/users/<int:user_id>/toggle-status', methods=['PATCH'])
@require_auth
def toggle_user_status(user_id):
    """Toggle user active/inactive status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get current status
        cursor.execute("SELECT is_active FROM Users WHERE id = %s", (user_id,))
        current = cursor.fetchone()
        if not current:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404
        
        new_status = not current['is_active']
        cursor.execute("UPDATE Users SET is_active = %s WHERE id = %s", (new_status, user_id))
        conn.commit()
        
        cursor.execute("SELECT * FROM Users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": user
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== STUDENT ENDPOINTS ====================

@app.route('/api/students', methods=['GET'])
@require_auth
def get_students():
    """Get all students"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Query Students table - actual schema
        try:
            cursor.execute("""
                SELECT s.id, s.student_id, s.user_id, s.gmail, s.assigned_mode as mode, 
                       s.is_active, s.created_at, u.username
                FROM Students s
                LEFT JOIN Users u ON s.user_id = u.id
                ORDER BY s.created_at DESC
            """)
        except Exception as e:
            # If Students table doesn't exist, try Users with student role
            cursor.execute("""
                SELECT id, id as student_id, username, gmail as email, is_active, 
                       'restricted' as mode, created_at
                FROM Users 
                WHERE role = 'student'
                ORDER BY created_at DESC
            """)
        
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": students
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/students/<student_id>/mode', methods=['POST'])
@require_auth
def set_student_mode(student_id):
    """Set student mode"""
    data = request.json
    mode = data.get('mode')
    changed_by = data.get('changedBy')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Update student mode - Students table has assigned_mode column
        try:
            cursor.execute("""
                UPDATE Students 
                SET assigned_mode = %s
                WHERE student_id = %s OR id = %s
            """, (mode, student_id, student_id))
            
            # Also log to ModeHistory
            try:
                cursor.execute("""
                    SELECT assigned_mode FROM Students 
                    WHERE student_id = %s OR id = %s
                """, (student_id, student_id))
                old_mode_result = cursor.fetchone()
                old_mode = old_mode_result['assigned_mode'] if old_mode_result else None
                
                cursor.execute("""
                    INSERT INTO ModeHistory (student_id, old_mode, new_mode, changed_by, changed_at)
                    VALUES (%s, %s, %s, %s, NOW())
                """, (student_id, old_mode, mode, changed_by))
            except:
                pass  # Don't fail if ModeHistory insert fails
        except:
            # If mode column doesn't exist, skip
            pass
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {"id": student_id, "mode": mode}
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== ACTIVITY ENDPOINTS ====================

@app.route('/api/activity', methods=['GET'])
@require_auth
def get_activity():
    """Get activity logs"""
    student_id = request.args.get('studentId')
    limit = int(request.args.get('limit', 100))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Query ActivityLogs - actual schema columns
        query = """
            SELECT id, student_id as studentId, user_id, url, visit_start as visitStart, 
                   visit_duration as duration, created_at as createdAt, domain, mode
            FROM ActivityLogs
        """
        params = []
        
        if student_id:
            query += " WHERE studentId = %s"
            params.append(student_id)
        
        query += " ORDER BY visitStart DESC, createdAt DESC LIMIT %s"
        params.append(limit)
        
        try:
            cursor.execute(query, params)
        except:
            # If table doesn't exist, return empty
            cursor.close()
            conn.close()
            return jsonify({
                "success": True,
                "data": []
            })
        
        activities = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": activities
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/violations', methods=['GET'])
@require_auth
def get_violations():
    """Get violation logs"""
    student_id = request.args.get('studentId')
    limit = int(request.args.get('limit', 100))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Query Violations - actual schema columns
        query = """
            SELECT id, student_id as studentId, user_id, attempted_url as url, 
                   violation_type, description as reason, created_at as timestamp, 
                   created_at as createdAt, severity, current_mode
            FROM Violations
        """
        params = []
        
        if student_id:
            query += " WHERE studentId = %s"
            params.append(student_id)
        
        query += " ORDER BY timestamp DESC, createdAt DESC LIMIT %s"
        params.append(limit)
        
        try:
            cursor.execute(query, params)
        except:
            cursor.close()
            conn.close()
            return jsonify({
                "success": True,
                "data": []
            })
        
        violations = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": violations
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== WHITELIST ENDPOINTS ====================

@app.route('/api/whitelist', methods=['GET'])
@require_auth
def get_whitelist():
    """Get whitelist entries"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT id, domain as url, description, added_by as addedBy, 
                       created_at as addedAt, is_active as isActive
                FROM WhitelistDomains
                ORDER BY created_at DESC
            """)
        except:
            cursor.close()
            conn.close()
            return jsonify({
                "success": True,
                "data": []
            })
        
        entries = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": entries
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/whitelist', methods=['POST'])
@require_auth
def add_to_whitelist():
    """Add URL to whitelist"""
    data = request.json
    user_id = request.current_user.get('userId') or request.current_user.get('user_id')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Extract domain from URL if full URL provided
        url = data.get('url', '')
        domain = url.replace('https://', '').replace('http://', '').split('/')[0].split('?')[0]
        
        cursor.execute("""
            INSERT INTO WhitelistDomains (domain, mode, description, added_by, created_at, is_active)
            VALUES (%s, %s, %s, %s, NOW(), 1)
        """, (
            domain,
            data.get('mode', 'free'),  # WhitelistDomains requires mode
            data.get('description'),
            user_id
        ))
        
        entry_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT * FROM WhitelistDomains WHERE id = %s", (entry_id,))
        entry = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": entry
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/whitelist/<int:entry_id>', methods=['PATCH'])
@require_auth
def update_whitelist(entry_id):
    """Update whitelist entry"""
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        updates = []
        values = []
        if 'url' in data or 'domain' in data:
            domain = (data.get('url') or data.get('domain', '')).replace('https://', '').replace('http://', '').split('/')[0].split('?')[0]
            updates.append("domain = %s")
            values.append(domain)
        if 'description' in data:
            updates.append("description = %s")
            values.append(data['description'])
        if 'mode' in data:
            updates.append("mode = %s")
            values.append(data['mode'])
        if 'isActive' in data:
            updates.append("is_active = %s")
            values.append(data['isActive'])
        
        if updates:
            values.append(entry_id)
            cursor.execute(f"UPDATE WhitelistDomains SET {', '.join(updates)} WHERE id = %s", values)
            conn.commit()
        
        cursor.execute("SELECT * FROM WhitelistDomains WHERE id = %s", (entry_id,))
        entry = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": entry
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/whitelist/<int:entry_id>', methods=['DELETE'])
@require_auth
def remove_from_whitelist(entry_id):
    """Remove from whitelist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM WhitelistDomains WHERE id = %s", (entry_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Entry removed from whitelist"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== BLACKLIST ENDPOINTS ====================

@app.route('/api/blacklist', methods=['GET'])
@require_auth
def get_blacklist():
    """Get blacklist entries"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT id, domain as url, reason, added_by as addedBy, 
                       created_at as addedAt, is_active as isActive, mode
                FROM BlacklistDomains
                ORDER BY created_at DESC
            """)
        except:
            cursor.close()
            conn.close()
            return jsonify({
                "success": True,
                "data": []
            })
        
        entries = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": entries
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/blacklist', methods=['POST'])
@require_auth
def add_to_blacklist():
    """Add URL to blacklist"""
    data = request.json
    user_id = request.current_user.get('userId') or request.current_user.get('user_id')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Extract domain from URL if full URL provided
        url = data.get('url', '')
        domain = url.replace('https://', '').replace('http://', '').split('/')[0].split('?')[0]
        
        cursor.execute("""
            INSERT INTO BlacklistDomains (domain, mode, reason, added_by, created_at, is_active)
            VALUES (%s, %s, %s, %s, NOW(), 1)
        """, (
            domain,
            data.get('mode', 'free'),  # BlacklistDomains requires mode
            data.get('reason'),
            user_id
        ))
        
        entry_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT * FROM BlacklistDomains WHERE id = %s", (entry_id,))
        entry = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": entry
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/blacklist/<int:entry_id>', methods=['PATCH'])
@require_auth
def update_blacklist(entry_id):
    """Update blacklist entry"""
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        updates = []
        values = []
        if 'url' in data or 'domain' in data:
            domain = (data.get('url') or data.get('domain', '')).replace('https://', '').replace('http://', '').split('/')[0].split('?')[0]
            updates.append("domain = %s")
            values.append(domain)
        if 'reason' in data:
            updates.append("reason = %s")
            values.append(data['reason'])
        if 'mode' in data:
            updates.append("mode = %s")
            values.append(data['mode'])
        if 'isActive' in data:
            updates.append("is_active = %s")
            values.append(data['isActive'])
        
        if updates:
            values.append(entry_id)
            cursor.execute(f"UPDATE BlacklistDomains SET {', '.join(updates)} WHERE id = %s", values)
            conn.commit()
        
        cursor.execute("SELECT * FROM BlacklistDomains WHERE id = %s", (entry_id,))
        entry = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": entry
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/blacklist/<int:entry_id>', methods=['DELETE'])
@require_auth
def remove_from_blacklist(entry_id):
    """Remove from blacklist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM BlacklistDomains WHERE id = %s", (entry_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Entry removed from blacklist"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Backend API is running"})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"Starting backend server on port {port}...")
    print(f"Database: {DB_CONFIG['database']}@{DB_CONFIG['host']}")
    app.run(host='0.0.0.0', port=port, debug=True)
