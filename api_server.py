"""
API Server for EduBrowser
Provides REST API endpoints for authentication and dashboard operations
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from authentication import Authentication
from datetime import datetime
import os

app = Flask(__name__)

# Configure CORS with explicit settings
CORS(app, 
     resources={r"/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization", "X-Device-ID"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True)

# Initialize database connection with single database
auth = Authentication(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "Innovation"),
    database=os.getenv("DB_NAME", os.getenv("DATABASE", "edubrowser"))
)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/auth/login', methods=['POST'])
def login():
    """Login endpoint for web dashboard"""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    device_id = data.get('deviceId')
    
    if not username or not password or not device_id:
        return jsonify({"success": False, "error": "Missing credentials"}), 400
    
    try:
        result = auth.authenticate_user(username, password, device_id)
        if result and result.get('success'):
            user_data = result.get('user', {})
            return jsonify({
                "success": True,
                "data": {
                    "token": result.get('token'),
                    "user": {
                        "id": str(user_data.get('id')),
                        "username": user_data.get('username'),
                        "role": user_data.get('role'),
                        "email": user_data.get('gmail', ''),
                        "isActive": user_data.get('is_active', True)
                    }
                }
            }), 200
        else:
            return jsonify({"success": False, "error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/auth/verify', methods=['OPTIONS', 'GET', 'POST'])
def verify():
    """Verify token endpoint (alias for compatibility)"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Device-ID')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        return response, 200
    elif request.method == 'GET':
        # Handle GET requests (fallback - should use POST)
        # Try to get token from query params or header
        token = request.args.get('token') or (request.headers.get('Authorization', '').replace('Bearer ', '') if request.headers.get('Authorization') else None)
        device_id = request.args.get('deviceId') or request.headers.get('X-Device-ID')
        
        if not token or not device_id:
            return jsonify({
                "success": False, 
                "error": "Missing token or deviceId. Use POST /api/auth/verify-token instead."
            }), 400
        
        # Manually call validate_token logic (since verify_token() expects JSON body)
        try:
            user_data = auth.validate_token(token, device_id)
            if user_data:
                return jsonify({
                    "success": True,
                    "data": {
                        "user": {
                            "id": str(user_data['id']),
                            "username": user_data['username'],
                            "role": user_data['role'],
                            "email": "",
                            "isActive": user_data['is_active']
                        }
                    }
                }), 200
            else:
                return jsonify({"success": False, "error": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    else:
        # POST request
        return verify_token()

@app.route('/api/auth/verify-token', methods=['OPTIONS', 'POST'])
def verify_token():
    """Verify JWT token"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Device-ID')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response, 200
    
    data = request.get_json() or {}
    token = data.get('token')
    device_id = data.get('deviceId')
    
    if not token or not device_id:
        return jsonify({"success": False, "error": "Missing token or deviceId"}), 400
    
    try:
        user_data = auth.validate_token(token, device_id)
        if user_data:
            return jsonify({
                "success": True,
                "data": {
                    "user": {
                        "id": str(user_data['id']),
                        "username": user_data['username'],
                        "role": user_data['role'],
                        "email": "",
                        "isActive": user_data['is_active']
                    }
                }
            }), 200
        else:
            return jsonify({"success": False, "error": "Invalid token"}), 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    try:
        import mysql.connector
        conn = auth._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, gmail, role, created_at, last_login, is_active, 
                   teacher_approval_status 
            FROM Users ORDER BY id ASC
        """)
        users = []
        for user in cursor.fetchall():
            users.append({
                "id": user[0],
                "username": user[1],
                "gmail": user[2],
                "role": user[3],
                "createdAt": user[4].isoformat() if user[4] else None,
                "lastLogin": user[5].isoformat() if user[5] else None,
                "isActive": bool(user[6]),
                "teacherApprovalStatus": user[7]
            })
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": users}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/students', methods=['GET'])
def get_students():
    """Get all students with their modes"""
    try:
        import mysql.connector
        conn = auth._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT student_id, user_id, gmail, assigned_mode, violation_count, 
                   created_at, updated_at, is_active
            FROM Students ORDER BY student_id ASC
        """)
        students = []
        for student in cursor.fetchall():
            students.append({
                "studentId": student[0],
                "userId": student[1],
                "gmail": student[2],
                "assignedMode": student[3],
                "violationCount": student[4],
                "createdAt": student[5].isoformat() if student[5] else None,
                "updatedAt": student[6].isoformat() if student[6] else None,
                "isActive": bool(student[7])
            })
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": students}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/students/<student_id>/mode', methods=['POST'])
def set_student_mode(student_id):
    """Set student mode (admin/teacher only)"""
    try:
        data = request.get_json() or {}
        new_mode = data.get('mode')
        changed_by = data.get('changedBy')  # User ID
        
        if not new_mode or not changed_by:
            return jsonify({"success": False, "error": "Missing mode or changedBy"}), 400
        
        if auth.set_student_mode(student_id, new_mode, changed_by):
            return jsonify({"success": True, "message": "Mode updated"}), 200
        else:
            return jsonify({"success": False, "error": "Failed to update mode"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/activity', methods=['GET'])
def get_activity():
    """Get activity logs (filtered by role)"""
    try:
        import mysql.connector
        student_id = request.args.get('studentId')
        limit = int(request.args.get('limit', 100))
        
        conn = auth._get_conn()
        cursor = conn.cursor()
        
        if student_id:
            cursor.execute("""
                SELECT id, student_id, url, domain, mode, visit_duration, 
                       visit_start, visit_end, is_allowed, created_at
                FROM ActivityLogs 
                WHERE student_id=%s 
                ORDER BY visit_start DESC 
                LIMIT %s
            """, (student_id, limit))
        else:
            cursor.execute("""
                SELECT id, student_id, url, domain, mode, visit_duration, 
                       visit_start, visit_end, is_allowed, created_at
                FROM ActivityLogs 
                ORDER BY visit_start DESC 
                LIMIT %s
            """, (limit,))
        
        activities = []
        for activity in cursor.fetchall():
            activities.append({
                "id": activity[0],
                "studentId": activity[1],
                "url": activity[2],
                "domain": activity[3],
                "mode": activity[4],
                "visitDuration": activity[5],
                "visitStart": activity[6].isoformat() if activity[6] else None,
                "visitEnd": activity[7].isoformat() if activity[7] else None,
                "isAllowed": bool(activity[8]),
                "createdAt": activity[9].isoformat() if activity[9] else None
            })
        
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": activities}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/violations', methods=['GET'])
def get_violations():
    """Get violation logs"""
    try:
        import mysql.connector
        student_id = request.args.get('studentId')
        limit = int(request.args.get('limit', 100))
        
        conn = auth._get_conn()
        cursor = conn.cursor()
        
        if student_id:
            cursor.execute("""
                SELECT id, student_id, violation_type, description, attempted_url,
                       current_mode, severity, created_at
                FROM Violations 
                WHERE student_id=%s 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (student_id, limit))
        else:
            cursor.execute("""
                SELECT id, student_id, violation_type, description, attempted_url,
                       current_mode, severity, created_at
                FROM Violations 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (limit,))
        
        violations = []
        for violation in cursor.fetchall():
            violations.append({
                "id": violation[0],
                "studentId": violation[1],
                "violationType": violation[2],
                "description": violation[3],
                "attemptedUrl": violation[4],
                "currentMode": violation[5],
                "severity": violation[6],
                "createdAt": violation[7].isoformat() if violation[7] else None
            })
        
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": violations}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/users/<user_id>/toggle-status', methods=['PATCH'])
def toggle_user_status(user_id):
    """Toggle user active status"""
    try:
        import mysql.connector
        conn = auth._get_conn()
        cursor = conn.cursor()
        
        # Get current status
        cursor.execute("SELECT is_active FROM Users WHERE id=%s", (user_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        new_status = 0 if result[0] else 1
        
        # Update status
        cursor.execute("UPDATE Users SET is_active=%s WHERE id=%s", (new_status, user_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "data": {"id": user_id, "isActive": bool(new_status)}}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        import mysql.connector
        data = request.get_json() or {}
        
        username = data.get('username')
        password = data.get('password')
        email = data.get('email') or data.get('gmail')
        role = data.get('role', 'student')
        
        if not username or not password:
            return jsonify({"success": False, "error": "Username and password are required"}), 400
        
        if role not in ['admin', 'teacher', 'student']:
            return jsonify({"success": False, "error": "Invalid role"}), 400
        
        conn = auth._get_conn()
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT id FROM Users WHERE username=%s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": "Username already exists"}), 400
        
        # Hash password
        password_hash = sha256(password.encode()).hexdigest()
        
        # Create user
        teacher_approval = "APPROVED" if role == 'teacher' else None
        cursor.execute("""
            INSERT INTO Users (username, gmail, password_hash, role, is_active, teacher_approval_status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (username, email, password_hash, role, 1, teacher_approval, datetime.now()))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                "id": str(user_id),
                "username": username,
                "email": email,
                "role": role,
                "isActive": True
            }
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    try:
        import mysql.connector
        conn = auth._get_conn()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM Users WHERE id=%s", (user_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": "User not found"}), 404
        
        # Delete user (cascade will handle related records)
        cursor.execute("DELETE FROM Users WHERE id=%s", (user_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/whitelist', methods=['GET'])
def get_whitelist():
    """Get all whitelist entries"""
    try:
        import mysql.connector
        conn = auth._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, domain, mode, description, added_by, created_at, is_active
            FROM WhitelistDomains ORDER BY created_at DESC
        """)
        entries = []
        for entry in cursor.fetchall():
            entries.append({
                "id": str(entry[0]),
                "url": entry[1],  # Using 'url' for consistency with frontend
                "domain": entry[1],
                "mode": entry[2],
                "description": entry[3],
                "addedBy": str(entry[4]) if entry[4] else None,
                "addedAt": entry[5].isoformat() if entry[5] else None,
                "isActive": bool(entry[6])
            })
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": entries}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/whitelist', methods=['POST'])
def add_to_whitelist():
    """Add entry to whitelist"""
    try:
        import mysql.connector
        data = request.get_json() or {}
        domain = data.get('domain') or data.get('url')
        mode = data.get('mode', 'free')
        description = data.get('description', '')
        added_by = data.get('addedBy') or 1  # Default to admin user
        
        if not domain:
            return jsonify({"success": False, "error": "Domain is required"}), 400
        
        conn = auth._get_conn()
        cursor = conn.cursor()
        
        # Check if entry already exists
        cursor.execute("SELECT id FROM WhitelistDomains WHERE domain=%s AND mode=%s", (domain, mode))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": "Entry already exists"}), 400
        
        # Insert new entry
        cursor.execute("""
            INSERT INTO WhitelistDomains (domain, mode, description, added_by, is_active, created_at)
            VALUES (%s, %s, %s, %s, 1, %s)
        """, (domain, mode, description, added_by, datetime.now()))
        
        entry_id = cursor.lastrowid
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                "id": str(entry_id),
                "url": domain,
                "domain": domain,
                "mode": mode,
                "description": description,
                "addedBy": str(added_by),
                "addedAt": datetime.now().isoformat(),
                "isActive": True
            }
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/whitelist/<entry_id>', methods=['PATCH'])
def update_whitelist_entry(entry_id):
    """Update whitelist entry"""
    try:
        import mysql.connector
        data = request.get_json() or {}
        
        conn = auth._get_conn()
        cursor = conn.cursor()
        
        # Build update query dynamically
        updates = []
        params = []
        
        if 'isActive' in data:
            updates.append("is_active=%s")
            params.append(1 if data['isActive'] else 0)
        
        if 'description' in data:
            updates.append("description=%s")
            params.append(data['description'])
        
        if updates:
            params.append(entry_id)
            cursor.execute(f"UPDATE WhitelistDomains SET {', '.join(updates)} WHERE id=%s", params)
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "message": "Entry updated"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/whitelist/<entry_id>', methods=['DELETE'])
def remove_from_whitelist(entry_id):
    """Remove entry from whitelist"""
    try:
        import mysql.connector
        conn = auth._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM WhitelistDomains WHERE id=%s", (entry_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "message": "Entry removed"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/blacklist', methods=['GET'])
def get_blacklist():
    """Get all blacklist entries"""
    try:
        import mysql.connector
        conn = auth._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, domain, mode, reason, added_by, created_at, is_active
            FROM BlacklistDomains ORDER BY created_at DESC
        """)
        entries = []
        for entry in cursor.fetchall():
            entries.append({
                "id": str(entry[0]),
                "url": entry[1],  # Using 'url' for consistency with frontend
                "domain": entry[1],
                "mode": entry[2],
                "reason": entry[3],
                "addedBy": str(entry[4]) if entry[4] else None,
                "addedAt": entry[5].isoformat() if entry[5] else None,
                "isActive": bool(entry[6])
            })
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": entries}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/blacklist', methods=['POST'])
def add_to_blacklist():
    """Add entry to blacklist"""
    try:
        import mysql.connector
        data = request.get_json() or {}
        domain = data.get('domain') or data.get('url')
        mode = data.get('mode', 'exam')
        reason = data.get('reason', '')
        added_by = data.get('addedBy') or 1  # Default to admin user
        
        if not domain:
            return jsonify({"success": False, "error": "Domain is required"}), 400
        
        conn = auth._get_conn()
        cursor = conn.cursor()
        
        # Check if entry already exists
        cursor.execute("SELECT id FROM BlacklistDomains WHERE domain=%s AND mode=%s", (domain, mode))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": "Entry already exists"}), 400
        
        # Insert new entry
        cursor.execute("""
            INSERT INTO BlacklistDomains (domain, mode, reason, added_by, is_active, created_at)
            VALUES (%s, %s, %s, %s, 1, %s)
        """, (domain, mode, reason, added_by, datetime.now()))
        
        entry_id = cursor.lastrowid
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                "id": str(entry_id),
                "url": domain,
                "domain": domain,
                "mode": mode,
                "reason": reason,
                "addedBy": str(added_by),
                "addedAt": datetime.now().isoformat(),
                "isActive": True
            }
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/blacklist/<entry_id>', methods=['PATCH'])
def update_blacklist_entry(entry_id):
    """Update blacklist entry"""
    try:
        import mysql.connector
        data = request.get_json() or {}
        
        conn = auth._get_conn()
        cursor = conn.cursor()
        
        # Build update query dynamically
        updates = []
        params = []
        
        if 'isActive' in data:
            updates.append("is_active=%s")
            params.append(1 if data['isActive'] else 0)
        
        if 'reason' in data:
            updates.append("reason=%s")
            params.append(data['reason'])
        
        if updates:
            params.append(entry_id)
            cursor.execute(f"UPDATE BlacklistDomains SET {', '.join(updates)} WHERE id=%s", params)
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "message": "Entry updated"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/blacklist/<entry_id>', methods=['DELETE'])
def remove_from_blacklist(entry_id):
    """Remove entry from blacklist"""
    try:
        import mysql.connector
        conn = auth._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM BlacklistDomains WHERE id=%s", (entry_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "message": "Entry removed"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    try:
        import mysql.connector
        
        # Get database connection
        conn = auth._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM Users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT role, COUNT(*) as count FROM Users GROUP BY role")
        role_counts = {}
        for role, count in cursor.fetchall():
            role_counts[role] = count
        
        cursor.execute("SELECT COUNT(*) FROM Users WHERE is_active=1")
        active_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Students WHERE is_active=1")
        active_students = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT assigned_mode, COUNT(*) as count 
            FROM Students 
            WHERE is_active=1 
            GROUP BY assigned_mode
        """)
        mode_distribution = {}
        for mode, count in cursor.fetchall():
            mode_distribution[mode] = count
        
        cursor.execute("""
            SELECT COUNT(*) FROM Violations 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        """)
        recent_violations = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Whitelist WHERE is_active=1")
        whitelist_size = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Blacklist WHERE is_active=1")
        blacklist_size = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM Users 
            WHERE last_login >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        """)
        recent_logins = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                "totalUsers": total_users,
                "activeUsers": active_users,
                "activeStudents": active_students,
                "roleDistribution": role_counts,
                "modeDistribution": mode_distribution,
                "recentViolations": recent_violations,
                "whitelistSize": whitelist_size,
                "blacklistSize": blacklist_size,
                "recentLogins": recent_logins
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
