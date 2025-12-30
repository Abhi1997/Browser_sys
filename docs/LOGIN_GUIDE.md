# 🔐 Login Guide

How to login to the Secure Academic Browser application.

## 🚀 Quick Start

1. **Start the application:**
   ```powershell
   # With Docker MySQL
   $env:DB_HOST="localhost"; $env:DB_PORT="3307"; python main.py
   
   # Or use helper script
   .\run_with_docker.ps1
   ```

2. **Login window will appear**

3. **Enter your credentials** (see below)

4. **Click "Login"**

## 👥 Available Login Credentials

### 📚 Students

| Username | Password | Mode |
|----------|----------|------|
| `student1` | `student123` | Exam |
| `student2` | `student123` | Study |
| `student3` | `student123` | Restricted |
| `student4` | `student123` | Free |
| `student5` | `student123` | Exam |
| `student6` | `student123` | Study |
| `student7` | `student123` | Restricted |
| `student8` | `student123` | Free |
| `student9` | `student123` | Exam |
| `student10` | `student123` | Study |

**Note:** All students use the same password: `student123`

### 👨‍🏫 Teachers

| Username | Password |
|----------|----------|
| `teacher1` | `teacher123` |
| `teacher2` | `teacher123` |
| `teacher3` | `teacher123` |

**Note:** All teachers use the same password: `teacher123`

### 👑 Admins

| Username | Password |
|----------|----------|
| `admin1` | `admin123` |

## 🎯 Recommended Test Accounts

### For Testing Dashboard Features:
- **Admin:** `admin1` / `admin123` - Full access to all features
- **Teacher:** `teacher1` / `teacher123` - Access to teacher dashboard

### For Testing Browser Modes:
- **Student (Exam Mode):** `student1` / `student123`
- **Student (Study Mode):** `student2` / `student123`
- **Student (Restricted Mode):** `student3` / `student123`
- **Student (Free Mode):** `student4` / `student123`

## 📋 Login Steps

1. **Run the application**
   - Execute `python main.py` or use `.\run_with_docker.ps1`

2. **Login window appears**
   - Enter your username
   - Enter your password
   - Click "Login" button

3. **After successful login:**
   - Browser window opens
   - Your assigned mode is displayed
   - Navigation bar shows your role

## 🔑 Feature Access by Role

### Student
- ✅ Browser access with mode restrictions
- ✅ View assigned mode
- ❌ No dashboard access
- ❌ Cannot change settings

### Teacher
- ✅ Browser access
- ✅ **Dashboard access** (click Dashboard button)
- ✅ View student activity
- ✅ Change student modes
- ✅ View violations
- ✅ Manage whitelist (limited)

### Admin
- ✅ Browser access
- ✅ **Full dashboard access**
- ✅ View all users and students
- ✅ Change any student mode
- ✅ View all violations
- ✅ Manage whitelist/blacklist
- ✅ View all activity logs
- ✅ User management

## 🖥️ Accessing the Dashboard

After logging in as **Teacher** or **Admin**:

1. Click the **"Dashboard"** button in the browser interface
2. Dashboard opens in a new window at `http://localhost:3000`
3. You'll see:
   - Real-time statistics
   - User tables
   - Activity logs
   - Violations
   - Charts and graphs

## ❌ Troubleshooting

### "Invalid username or password"
- ✅ Check username spelling (case-sensitive)
- ✅ Check password spelling (case-sensitive)
- ✅ Make sure you ran `populate_sample_data.py` to create users
- ✅ Verify database connection

### "Database connection error"
- ✅ Make sure Docker services are running: `docker-compose ps`
- ✅ If using Docker MySQL, set: `$env:DB_PORT="3307"`
- ✅ Check MySQL is healthy: `docker-compose ps` should show `(healthy)`

### "Dashboard not accessible"
- ✅ Only Teachers and Admins can access dashboard
- ✅ Students cannot access dashboard
- ✅ Make sure dashboard service is running: `docker-compose ps`

### Can't see login window
- ✅ Make sure PyQt6 is installed: `pip install PyQt6`
- ✅ Check for error messages in terminal
- ✅ Try running: `python main.py`

## 📝 Creating New Users

To create additional users, you can:

1. **Use the register function in code:**
   ```python
   from authentication import Authentication
   
   auth = Authentication()
   auth.register_user("newuser", "password123", role="student")
   ```

2. **Or add to database directly:**
   ```sql
   INSERT INTO Users (username, password_hash, role, is_active)
   VALUES ('newuser', SHA2('password123', 256), 'student', 1);
   ```

3. **Re-run populate script** (will skip existing users)

## ✅ Quick Reference

**Most Common Logins:**

| Purpose | Username | Password |
|---------|----------|----------|
| Admin Dashboard | `admin1` | `admin123` |
| Teacher Dashboard | `teacher1` | `teacher123` |
| Test Student | `student1` | `student123` |

---

**Happy browsing!** 🎉

