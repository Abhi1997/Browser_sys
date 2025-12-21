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
CORS(app)

# Initialize database connection
auth = Authentication(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "Innovation"),
    database=os.getenv("DB_NAME", "edubrowser")
)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/auth/verify-token', methods=['POST'])
def verify_token():
    """Verify JWT token"""
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
        conn = mysql.connector.connect(**auth.db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role, created_at, last_login, is_active FROM Users ORDER BY id ASC")
        users = []
        for user in cursor.fetchall():
            users.append({
                "id": user[0],
                "username": user[1],
                "role": user[2],
                "createdAt": user[3].isoformat() if user[3] else None,
                "lastLogin": user[4].isoformat() if user[4] else None,
                "isActive": bool(user[5])
            })
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": users}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    try:
        import mysql.connector
        conn = mysql.connector.connect(**auth.db_config)
        cursor = conn.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) FROM Users")
        total_users = cursor.fetchone()[0]
        
        # Users by role
        cursor.execute("SELECT role, COUNT(*) as count FROM Users GROUP BY role")
        role_counts = {}
        for role, count in cursor.fetchall():
            role_counts[role] = count
        
        # Active users
        cursor.execute("SELECT COUNT(*) FROM Users WHERE is_active=1")
        active_users = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                "totalUsers": total_users,
                "activeUsers": active_users,
                "roleDistribution": role_counts
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
