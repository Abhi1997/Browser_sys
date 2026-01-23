"""
Test script to verify backend login works with admin credentials

Usage:
    python backend/test_login.py
"""

import requests
import json

BACKEND_URL = "http://localhost:5000"

def test_login():
    """Test admin login"""
    print("=" * 60)
    print("Testing Backend Login")
    print("=" * 60)
    print()
    
    # Test login
    login_data = {
        "username": "admin",
        "password": "admin123!",
        "deviceId": "test-device-123"
    }
    
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Username: {login_data['username']}")
    print(f"Password: {'*' * len(login_data['password'])}")
    print()
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data['data']['token']
                user = data['data']['user']
                
                print("✅ Login successful!")
                print()
                print("Token (first 50 chars):")
                print(f"  {token[:50]}...")
                print()
                print("User Information:")
                print(f"  ID: {user['id']}")
                print(f"  Username: {user['username']}")
                print(f"  Role: {user['role']}")
                print(f"  Email: {user.get('email', 'N/A')}")
                print()
                print("You can now use this token in the dashboard!")
                print()
                print(f"Dashboard URL:")
                print(f"  http://localhost:3000/dashboard-{user['role'].replace('super-admin', 'superadmin')}?token={token}&deviceId={login_data['deviceId']}")
            else:
                print("❌ Login failed:")
                print(f"  {data.get('error', 'Unknown error')}")
        else:
            print("❌ Login failed:")
            try:
                error_data = response.json()
                print(f"  {error_data.get('error', 'Unknown error')}")
            except:
                print(f"  HTTP {response.status_code}: {response.text}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server!")
        print()
        print("Make sure the backend is running:")
        print("  cd backend")
        print("  python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    test_login()
