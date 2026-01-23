"""
Backend API Server for Dashboard
REST API endpoints for dashboard data access
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import authentication module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from authentication import Authentication
import jwt
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# CORS configuration
CORS(app, origins=[
    "http://localhost:3000",
    "http://localhost:8080",
    "https://api.abhinavpaudel.com",
    "https://abhinavpaudel.com"
])

# Initialize authentication
auth = Authentication(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "edubrowser")
)

# JWT Secret
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-this")


def verify_token(f):
    """Decorator to verify JWT token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        device_id = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({
                    "success": False,
                    "error": "Invalid authorization header format"
                }), 401
        
        # Get device ID from header
        device_id = request.headers.get('X-Device-ID')
        
        # Also check request body for token/deviceId (for POST requests)
        if not token and request.is_json:
            data = request.get_json()
            token = data.get('token') if data else None
            device_id = data.get('deviceId') if data and not device_id else device_id
        
        if not token:
            return jsonify({
                "success": False,
                "error": "Token is missing"
            }), 401
        
        try:
            # Decode and verify token
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            
            # Extract user info
            user_id = decoded.get('userId') or decoded.get('user_id')
            username = decoded.get('username')
            role = decoded.get('role')
            
            # Store in request context
            request.current_user = {
                'id': user_id,
                'username': username,
                'role': role
            }
            
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                "success": False,
                "error": "Token has expired"
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "success": False,
                "error": "Invalid token"
            }), 401
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Token verification failed: {str(e)}"
            }), 401
    
    return decorated_function


def format_datetime(dt):
    """Format datetime to ISO format"""
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    if isinstance(dt, datetime):
        return dt.isoformat() + 'Z'
    return str(dt)


# ==================== Authentication Endpoints ====================

@app.route('/api/auth/verify-token', methods=['POST'])
def verify_token_endpoint():
    """Verify JWT token and return user information"""
    try:
        data = request.get_json()
        token = data.get('token') if data else None
        device_id = data.get('deviceId') if data else None
        
        if not token:
            return jsonify({
                "success": False,
                "error": "Token is required"
            }), 400
        
        try:
            # Decode token
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            user_id = decoded.get('userId') or decoded.get('user_id')
            
            # Get user from database
            conn = auth._get_conn()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT id, username, gmail, role, is_active, created_at, last_login
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
            
            # Format user data
            user_data = {
                "id": str(user['id']),
                "username": user['username'],
                "email": user.get('gmail') or user.get('email', ''),
                "role": user['role'],
                "isActive": bool(user['is_active']),
                "createdAt": format_datetime(user.get('created_at')),
                "lastLogin": format_datetime(user.get('last_login'))
            }
            
            return jsonify({
                "success": True,
                "data": {
                    "valid": True,
                    "user": user_data
                }
            })
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                "success": False,
                "error": "Token has expired"
            }), 401
        except jwt.InvalidTokenError as e:
            return jsonify({
                "success": False,
                "error": f"Invalid token: {str(e)}"
            }), 401
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500


# ==================== Statistics Endpoints ====================

@app.route('/api/stats', methods=['GET'])
@verify_token
def get_stats():
    """Get overall system statistics"""
    try:
        conn = auth._get_conn()
        cursor = conn.cursor(dictionary=True)
        
        stats = {}
        
        # Total users
        cursor.execute("SELECT COUNT(*) as count FROM Users")
        stats['totalUsers'] = cursor.fetchone()['count']
        
        # Active users
        cursor.execute("SELECT COUNT(*) as count FROM Users WHERE is_active = 1")
        stats['activeUsers'] = cursor.fetchone()['count']
        
        # Active sessions (approximate - count active tokens)
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as count 
            FROM Sessions 
            WHERE is_active = 1 AND expires_at > NOW()
        """)
        stats['activeSessions'] = cursor.fetchone()['count']
        
        # Role distribution
        cursor.execute("""
            SELECT role, COUNT(*) as count 
            FROM Users 
            GROUP BY role
        """)
        role_dist = {}
        for row in cursor.fetchall():
            role_dist[row['role']] = row['count']
        stats['roleDistribution'] = role_dist
        
        # Whitelist size
        cursor.execute("SELECT COUNT(*) as count FROM WhitelistDomains WHERE is_active = 1")
        stats['whitelistSize'] = cursor.fetchone()['count']
        
        # Blacklist size
        cursor.execute("SELECT COUNT(*) as count FROM BlacklistDomains WHERE is_active = 1")
        stats['blacklistSize'] = cursor.fetchone()['count']
        
        # Recent logins (last 24 hours)
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM Users 
            WHERE last_login >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        """)
        stats['recentLogins'] = cursor.fetchone()['count']
        
        # Recent changes (last 24 hours) - from AdminActions and TeacherActions
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM (
                SELECT id FROM AdminActions WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
                UNION ALL
                SELECT id FROM TeacherActions WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ) as recent_actions
        """)
        stats['recentChanges'] = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": stats
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to fetch statistics: {str(e)}"
        }), 500


# ==================== User Management Endpoints ====================

@app.route('/api/users', methods=['GET'])
@verify_token
def get_users():
    """Get list of all users"""
    try:
        conn = auth._get_conn()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, username, gmail, role, is_active, created_at, last_login
            FROM Users
            ORDER BY created_at DESC
        """)
        
        users = []
        for row in cursor.fetchall():
            users.append({
                "id": row['id'],
                "username": row['username'],
                "email": row.get('gmail') or '',
                "gmail": row.get('gmail') or '',
                "role": row['role'],
                "isActive": bool(row['is_active']),
                "createdAt": format_datetime(row.get('created_at')),
                "created_at": format_datetime(row.get('created_at')),
                "lastLogin": format_datetime(row.get('last_login')),
                "last_login": format_datetime(row.get('last_login'))
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": users
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to fetch users: {str(e)}"
        }), 500


@app.route('/api/users', methods=['POST'])
@verify_token
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        username = data.get('username')
        email = data.get('email') or data.get('gmail')
        role = data.get('role', 'student')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                "success": False,
                "error": "Username and password are required"
            }), 400
        
        # Hash password
        from hashlib import sha256
        password_hash = sha256(password.encode()).hexdigest()
        
        conn = auth._get_conn()
        cursor = conn.cursor(dictionary=True)
        
        # Check if user exists
        cursor.execute("SELECT id FROM Users WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "error": "Username already exists"
            }), 400
        
        # Insert user
        cursor.execute("""
            INSERT INTO Users (username, password_hash, gmail, role, is_active, created_at)
            VALUES (%s, %s, %s, %s, 1, NOW())
        """, (username, password_hash, email, role))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        # Get created user
        cursor.execute("""
            SELECT id, username, gmail, role, is_active, created_at
            FROM Users
            WHERE id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                "id": user['id'],
                "username": user['username'],
                "email": user.get('gmail') or '',
                "role": user['role'],
                "isActive": bool(user['is_active']),
                "createdAt": format_datetime(user.get('created_at'))
            },
            "message": "User created successfully"
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to create user: {str(e)}"
        }), 500


@app.route('/api/users/<int:user_id>', methods=['PATCH'])
@verify_token
def update_user(user_id):
    """Update a user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        conn = auth._get_conn()
        cursor = conn.cursor(dictionary=True)
        
        # Build update query dynamically
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
        
        if 'isActive' in data or 'is_active' in data:
            updates.append("is_active = %s")
            values.append(data.get('isActive') or data.get('is_active'))
        
        if not updates:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "error": "No fields to update"
            }), 400
        
        values.append(user_id)
        
        query = f"UPDATE Users SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(query, tuple(values))
        conn.commit()
        
        # Get updated user
        cursor.execute("""
            SELECT id, username, gmail, role, is_active, created_at
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
        
        return jsonify({
            "success": True,
            "data": {
                "id": user['id'],
                "username": user['username'],
                "email": user.get('gmail') or '',
                "role": user['role'],
                "isActive": bool(user['is_active'])
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to update user: {str(e)}"
        }), 500


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@verify_token
def delete_user(user_id):
    """Delete a user (soft delete - set is_active = 0)"""
    try:
        conn = auth._get_conn()
        cursor = conn.cursor()
        
        # Soft delete
        cursor.execute("UPDATE Users SET is_active = 0 WHERE id = %s", (user_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "User deleted successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to delete user: {str(e)}"
        }), 500


@app.route('/api/users/<int:user_id>/toggle-status', methods=['PATCH'])
@verify_token
def toggle_user_status(user_id):
    """Toggle user active/inactive status"""
    try:
        conn = auth._get_conn()
        cursor = conn.cursor(dictionary=True)
        
        # Get current status
        cursor.execute("SELECT is_active FROM Users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404
        
        # Toggle status
        new_status = 0 if user['is_active'] else 1
        cursor.execute("UPDATE Users SET is_active = %s WHERE id = %s", (new_status, user_id))
        conn.commit()
        
        # Get updated user
        cursor.execute("SELECT id, username, is_active FROM Users WHERE id = %s", (user_id,))
        updated_user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                "id": updated_user['id'],
                "username": updated_user['username'],
                "isActive": bool(updated_user['is_active'])
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to toggle user status: {str(e)}"
        }), 500


# ==================== Student Endpoints ====================

@app.route('/api/students', methods=['GET'])
@verify_token
def get_students():
    """Get list of all students"""
    try:
        conn = auth._get_conn()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT s.id, s.student_id, s.user_id, s.gmail, s.assigned_mode, 
                   s.violation_count, s.is_active, s.created_at,
                   u.username
            FROM Students s
            LEFT JOIN Users u ON s.user_id = u.id
            ORDER BY s.created_at DESC
        """)
        
        students = []
        for row in cursor.fetchall():
            students.append({
                "id": row['id'],
                "studentId": row['student_id'],
                "name": row.get('username') or row.get('student_id'),
                "email": row.get('gmail') or '',
                "isActive": bool(row['is_active']),
                "mode": row.get('assigned_mode') or 'restricted',
                "createdAt": format_datetime(row.get('created_at'))
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": students
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to fetch students: {str(e)}"
        }), 500


@app.route('/api/students/<student_id>/mode', methods=['POST'])
@verify_token
def change_student_mode(student_id):
    """Change student mode"""
    try:
        data = request.get_json()
        mode = data.get('mode') if data else None
        changed_by = data.get('changedBy') if data else request.current_user['id']
        
        if not mode:
            return jsonify({
                "success": False,
                "error": "Mode is required"
            }), 400
        
        valid_modes = ['exam', 'study', 'restricted', 'free']
        if mode not in valid_modes:
            return jsonify({
                "success": False,
                "error": f"Invalid mode. Must be one of: {', '.join(valid_modes)}"
            }), 400
        
        conn = auth._get_conn()
        cursor = conn.cursor(dictionary=True)
        
        # Get current mode
        cursor.execute("SELECT assigned_mode FROM Students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "error": "Student not found"
            }), 404
        
        old_mode = student['assigned_mode']
        
        # Update mode
        cursor.execute("""
            UPDATE Students 
            SET assigned_mode = %s 
            WHERE student_id = %s
        """, (mode, student_id))
        conn.commit()
        
        # Log mode change
        cursor.execute("""
            INSERT INTO ModeHistory (student_id, old_mode, new_mode, changed_by, changed_at)
            VALUES (%s, %s, %s, %s, NOW())
        """, (student_id, old_mode, mode, changed_by))
        conn.commit()
        
        # Get updated student
        cursor.execute("""
            SELECT id, student_id, assigned_mode
            FROM Students
            WHERE student_id = %s
        """, (student_id,))
        
        updated_student = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                "id": updated_student['id'],
                "studentId": updated_student['student_id'],
                "mode": updated_student['assigned_mode']
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to change student mode: {str(e)}"
        }), 500


# ==================== Activity Endpoints ====================

@app.route('/api/activity', methods=['GET'])
@verify_token
def get_activity():
    """Get activity logs"""
    try:
        student_id = request.args.get('studentId')
        limit = int(request.args.get('limit', 100))
        
        conn = auth._get_conn()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT id, student_id, user_id, url, domain, mode, 
                   visit_duration, visit_start, is_allowed, created_at
            FROM ActivityLogs
        """
        
        params = []
        if student_id:
            query += " WHERE student_id = %s"
            params.append(student_id)
        
        query += " ORDER BY visit_start DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, tuple(params))
        
        activities = []
        for row in cursor.fetchall():
            activities.append({
                "id": row['id'],
                "studentId": row.get('student_id'),
                "url": row.get('url') or '',
                "visitStart": format_datetime(row.get('visit_start')),
                "createdAt": format_datetime(row.get('created_at')),
                "duration": row.get('visit_duration') or 0
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": activities
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to fetch activity: {str(e)}"
        }), 500


@app.route('/api/violations', methods=['GET'])
@verify_token
def get_violations():
    """Get violation logs"""
    try:
        student_id = request.args.get('studentId')
        limit = int(request.args.get('limit', 100))
        
        conn = auth._get_conn()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT id, student_id, user_id, violation_type, description, 
                   severity, created_at
            FROM Violations
        """
        
        params = []
        if student_id:
            query += " WHERE student_id = %s"
            params.append(student_id)
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, tuple(params))
        
        violations = []
        for row in cursor.fetchall():
            violations.append({
                "id": row['id'],
                "studentId": row.get('student_id'),
                "url": row.get('description', ''),  # Using description as URL placeholder
                "reason": row.get('violation_type') or 'Violation',
                "timestamp": format_datetime(row.get('created_at')),
                "createdAt": format_datetime(row.get('created_at'))
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": violations
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to fetch violations: {str(e)}"
        }), 500


# ==================== Whitelist Endpoints ====================

@app.route('/api/whitelist', methods=['GET'])
@verify_token
def get_whitelist():
    """Get all whitelist entries"""
    try:
        conn = auth._get_conn()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, domain, mode, description, added_by, created_at, is_active
            FROM WhitelistDomains
            ORDER BY created_at DESC
        """)
        
        whitelist = []
        for row in cursor.fetchall():
            whitelist.append({
                "id": str(row['id']),
                "url": row.get('domain') or '',
                "description": row.get('description') or '',
                "addedBy": str(row.get('added_by') or ''),
                "addedAt": format_datetime(row.get('created_at')),
                "isActive": bool(row['is_active'])
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": whitelist
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to fetch whitelist: {str(e)}"
        }), 500


@app.route('/api/whitelist', methods=['POST'])
@verify_token
def add_whitelist():
    """Add URL to whitelist"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        url = data.get('url') or data.get('domain')
        description = data.get('description', '')
        added_by = data.get('addedBy') or request.current_user['id']
        mode = data.get('mode', 'free')
        
        if not url:
            return jsonify({
                "success": False,
                "error": "URL/domain is required"
            }), 400
        
        conn = auth._get_conn()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            INSERT INTO WhitelistDomains (domain, mode, description, added_by, created_at, is_active)
            VALUES (%s, %s, %s, %s, NOW(), 1)
        """, (url, mode, description, added_by))
        
        entry_id = cursor.lastrowid
        conn.commit()
        
        # Get created entry
        cursor.execute("""
            SELECT id, domain, mode, description, added_by, created_at, is_active
            FROM WhitelistDomains
            WHERE id = %s
        """, (entry_id,))
        
        entry = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                "id": str(entry['id']),
                "url": entry['domain'],
                "description": entry.get('description') or '',
                "addedBy": str(entry.get('added_by') or ''),
                "addedAt": format_datetime(entry.get('created_at')),
                "isActive": bool(entry['is_active'])
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to add whitelist entry: {str(e)}"
        }), 500


@app.route('/api/whitelist/<int:entry_id>', methods=['PATCH'])
@verify_token
def update_whitelist(entry_id):
    """Update whitelist entry"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        conn = auth._get_conn()
        cursor = conn.cursor(dictionary=True)
        
        updates = []
        values = []
        
        if 'url' in data or 'domain' in data:
            updates.append("domain = %s")
            values.append(data.get('url') or data.get('domain'))
        
        if 'description' in data:
            updates.append("description = %s")
            values.append(data['description'])
        
        if 'isActive' in data or 'is_active' in data:
            updates.append("is_active = %s")
            values.append(data.get('isActive') or data.get('is_active'))
        
        if not updates:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "error": "No fields to update"
            }), 400
        
        values.append(entry_id)
        
        query = f"UPDATE WhitelistDomains SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(query, tuple(values))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Whitelist entry updated successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to update whitelist entry: {str(e)}"
        }), 500


@app.route('/api/whitelist/<int:entry_id>', methods=['DELETE'])
@verify_token
def delete_whitelist(entry_id):
    """Remove from whitelist (soft delete)"""
    try:
        conn = auth._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE WhitelistDomains SET is_active = 0 WHERE id = %s", (entry_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "error": "Whitelist entry not found"
            }), 404
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Whitelist entry deleted successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to delete whitelist entry: {str(e)}"
        }), 500


# ==================== Blacklist Endpoints ====================

@app.route('/api/blacklist', methods=['GET'])
@verify_token
def get_blacklist():
    """Get all blacklist entries"""
    try:
        conn = auth._get_conn()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, domain, mode, reason, added_by, created_at, is_active
            FROM BlacklistDomains
            ORDER BY created_at DESC
        """)
        
        blacklist = []
        for row in cursor.fetchall():
            blacklist.append({
                "id": str(row['id']),
                "url": row.get('domain') or '',
                "reason": row.get('reason') or '',
                "addedBy": str(row.get('added_by') or ''),
                "addedAt": format_datetime(row.get('created_at')),
                "isActive": bool(row['is_active'])
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": blacklist
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to fetch blacklist: {str(e)}"
        }), 500


@app.route('/api/blacklist', methods=['POST'])
@verify_token
def add_blacklist():
    """Add URL to blacklist"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        url = data.get('url') or data.get('domain')
        reason = data.get('reason', '')
        added_by = data.get('addedBy') or request.current_user['id']
        mode = data.get('mode', 'restricted')
        
        if not url:
            return jsonify({
                "success": False,
                "error": "URL/domain is required"
            }), 400
        
        conn = auth._get_conn()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            INSERT INTO BlacklistDomains (domain, mode, reason, added_by, created_at, is_active)
            VALUES (%s, %s, %s, %s, NOW(), 1)
        """, (url, mode, reason, added_by))
        
        entry_id = cursor.lastrowid
        conn.commit()
        
        # Get created entry
        cursor.execute("""
            SELECT id, domain, mode, reason, added_by, created_at, is_active
            FROM BlacklistDomains
            WHERE id = %s
        """, (entry_id,))
        
        entry = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                "id": str(entry['id']),
                "url": entry['domain'],
                "reason": entry.get('reason') or '',
                "addedBy": str(entry.get('added_by') or ''),
                "addedAt": format_datetime(entry.get('created_at')),
                "isActive": bool(entry['is_active'])
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to add blacklist entry: {str(e)}"
        }), 500


@app.route('/api/blacklist/<int:entry_id>', methods=['PATCH'])
@verify_token
def update_blacklist(entry_id):
    """Update blacklist entry"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        conn = auth._get_conn()
        cursor = conn.cursor(dictionary=True)
        
        updates = []
        values = []
        
        if 'url' in data or 'domain' in data:
            updates.append("domain = %s")
            values.append(data.get('url') or data.get('domain'))
        
        if 'reason' in data:
            updates.append("reason = %s")
            values.append(data['reason'])
        
        if 'isActive' in data or 'is_active' in data:
            updates.append("is_active = %s")
            values.append(data.get('isActive') or data.get('is_active'))
        
        if not updates:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "error": "No fields to update"
            }), 400
        
        values.append(entry_id)
        
        query = f"UPDATE BlacklistDomains SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(query, tuple(values))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Blacklist entry updated successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to update blacklist entry: {str(e)}"
        }), 500


@app.route('/api/blacklist/<int:entry_id>', methods=['DELETE'])
@verify_token
def delete_blacklist(entry_id):
    """Remove from blacklist (soft delete)"""
    try:
        conn = auth._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE BlacklistDomains SET is_active = 0 WHERE id = %s", (entry_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "error": "Blacklist entry not found"
            }), 404
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Blacklist entry deleted successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to delete blacklist entry: {str(e)}"
        }), 500


# ==================== Export Endpoint ====================

@app.route('/export/db', methods=['POST'])
@verify_token
def export_database():
    """Export database as file"""
    try:
        # This is a placeholder - implement actual database export
        # For now, return a simple response
        return jsonify({
            "success": False,
            "error": "Database export not yet implemented"
        }), 501
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to export database: {str(e)}"
        }), 500


# ==================== Health Check ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Dashboard API"
    })


if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting API server on port {port}")
    print(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
