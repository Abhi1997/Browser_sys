# EduBrowser - Complete Feature List

**Version:** Production-Ready  
**Platform:** PyQt6 Desktop Application + React Dashboard + PHP API  
**Target:** Educational institutions, schools, training centers

---

## 🎯 Core Features

### 1. **Multi-Mode Browsing System**
Four distinct browsing modes with automatic enforcement:

- **Cached Mode (Offline Only)** 📁
  - Students can only view pre-cached websites (no network access)
  - Teachers/admins cache pages using "Cache this page" button
  - Network requests (http/https) are completely blocked via URL interceptor
  - Cached files stored as MHTML in local cache directory
  - Manage cached sites from dashboard (list/delete)

- **Study Mode** 📚
  - Whitelist-based: only approved educational sites
  - Blacklist enforcement for blocked domains
  - Designed for focused academic work

- **Restricted Mode** ⚠️
  - Limited browsing with strict content filtering
  - Whitelist + blacklist enforcement
  - Suitable for controlled environments

- **Free Mode** 🌐
  - Unrestricted browsing with monitoring
  - Google Safe Browsing API integration for malicious site detection
  - Whitelist/blacklist still enforced
  - All activity logged for audit

---

## 👥 User Roles & Permissions (Hierarchical Data Isolation)

### **Role Hierarchy**
```
Superuser (ultimate superuser - full access to everything)
     ↓
Super Admin (oversight only - read all, create admins)
     ↓
   Admin (full authority for their isolated group)
     ↓
   Teacher (manages assigned students)
     ↓
   Student (end user)
```

### **Superusers**
- **Ultimate superuser** - can view AND modify everything
- Full access across all admin groups
- Can create any user type (superusers, superadmins, admins, teachers, students)
- Can modify any user, whitelist, blacklist, cached site
- Can delete any user
- No data isolation restrictions
- Dedicated Superuser Dashboard with all tabs and full edit access
- Use for system maintenance and debugging

### **Students**
- Assigned to ONE teacher by admin
- Belong to ONE admin's group
- Assigned browsing mode (cannot change)
- Mode visible at application launch (loading screen + window title)
- Time-window restricted browsing (optional)
- All browsing activity logged
- View own browsing history
- Can only see whitelists/blacklists from their admin's group

### **Teachers**
- Belong to ONE admin
- Can only view students assigned to them
- Change student modes from dashboard
- View student violations and browsing history
- Add/remove whitelist and blacklist entries (for their admin's group)
- Cache pages for offline student access
- View warning triggers for their students
- Cannot see other teachers' students

### **Admins**
- Full operational authority for their own isolated group
- Create and manage teachers (teachers belong to this admin)
- Create students and assign them to teachers
- View all students and teachers in their group
- Manage whitelist/blacklist (isolated per admin)
- Change logs and audit trails (for their group)
- Session usage for ML/reporting (for their group)
- Export database (their group's data)
- Cached sites management (for their group)
- **Cannot see other admins' data** (complete isolation)

### **Super Admins**
- **Read-only oversight** of all admins
- Can view all admins and their groups
- **Cannot modify** any data (users, whitelist, blacklist, etc.)
- **Can ONLY create new admins** (each admin gets isolated data)
- View global statistics across all admins
- Admin switcher to view different admin groups
- System-wide monitoring without interference

---

## 🔐 Authentication & Security

### **Login System**
- Username/password authentication
- Device registration and tracking
- JWT token-based sessions
- Device fingerprinting (IP, MAC address)
- Last login tracking
- Active/inactive user status

### **Password Management**
- Forgot password flow with email reset links
- Password reset tokens with expiration
- Secure password hashing
- Email delivery via SMTP (configurable)

### **Session Management**
- Browser session tracking (start/activity/end)
- Session activity logged every 2 minutes
- Session touch on navigation
- Auto-logout on window close
- Dashboard JWT tokens separate from browser tokens

### **Device Security**
- Device ID generation and registration
- Device-level access control
- Last seen timestamp per device
- Multi-device support per user

---

## 📊 Dashboard (React Web App)

### **Admin Dashboard**
- **Overview:** Total students, whitelist/blacklist size, active sessions
- **Students Tab:** Per-student cards with mode, violations, history
- **Teachers Tab:** List of teachers in group
- **Users Tab:** Create, edit, delete, toggle status
- **Whitelist Tab:** Add/edit/delete allowed domains per mode
- **Blacklist Tab:** Add/edit/delete blocked domains per mode
- **Cached Sites Tab:** List and delete cached offline pages
- **Dashboard Logs Tab:** Who opened dashboard and when
- **Change Logs Tab:** Mode change history (who changed what, when)
- **Warning Triggers Tab:** First violations, repeated violations, escalations
- **Session Usage Tab:** Browser session data for ML/reporting
- **Export:** Database export to SQL file

### **Teacher Dashboard**
- Stats overview (students, whitelist, blacklist)
- Warning triggers table
- Cached sites management
- Per-student cards (mode, violations, history)
- Change student modes
- View student browsing history

### **Student Dashboard**
- Profile view
- Own browsing history ("My History" page)
- View assigned mode (read-only)

### **Dashboard Features**
- Real-time data refresh (30-60 second intervals)
- Responsive design
- Dark/light mode support
- Toast notifications for actions
- Confirmation dialogs for destructive actions
- Search and filter capabilities
- Pagination for large datasets

---

## 🌐 Browser Features (PyQt6 Desktop App)

### **Core Browser**
- Tabbed browsing (multiple tabs)
- Address bar with URL validation
- Back, forward, reload, home buttons
- Zoom control (50%-200%)
- Network status indicator
- Loading progress bar
- Page title display in tabs

### **Mode Enforcement**
- Real-time URL checking before page load
- Security-themed warning dialogs for blocked URLs
- Mode indicator toolbar (students only)
- Mode info: icon, name, description, color-coded
- Automatic violation logging

### **Caching System (Teachers/Admins)**
- "Cache this page" toolbar button
- Save current page as MHTML
- Automatic filename generation (MD5 hash)
- Database registration with 2.5s delay (async save handling)
- Cache directory: `EduBrowser/cache/`
- Success/failure notifications

### **Offline Mode (Cached)**
- OfflineOnlyInterceptor blocks all http/https requests
- Load cached pages from local files using `file://` URLs
- Home button shows first cached site
- No network access whatsoever

### **Activity Tracking**
- Page load start/finish timestamps
- Visit duration calculation
- Browsing history per user (all roles)
- Activity logs per student (mode, URL, duration)
- Session activity touch every 2 minutes

### **Violation System**
- URL blocked violations
- Time window violations
- Repeated violation tracking (5+ in 24 hours)
- First violation triggers
- Severity levels
- Automatic warning escalation

---

## 🕐 Time Window Management

- **Per-student time restrictions**
- Define allowed browsing times by day of week
- Start and end time enforcement
- Outside window = automatic violation
- Logged in `TimeWindows` table
- Enforced in all modes

---

## 📈 Monitoring & Reporting

### **Browsing History**
- Per-user history (URL, page title, timestamp, device)
- "My History" page for all users
- Teacher view of student history
- Searchable and filterable

### **Activity Logs**
- Student visit logs (URL, domain, mode, duration)
- Visit start/end timestamps
- Mode at time of visit
- Used for audit and compliance

### **Violations**
- Blocked URL attempts
- Time window violations
- Current mode at violation
- Severity classification
- Dashboard display for teachers/admins

### **Warning Triggers**
- First violation alerts
- Repeated violation alerts (5+ in 24 hours)
- Escalation tracking
- Teacher/admin action logging

### **Session Usage (ML-Ready)**
- Session start timestamp
- Last activity timestamp (updated every 2 min + on navigate)
- Session end timestamp
- Active/inactive status
- Device and user association
- Queryable for machine learning and automation

### **Dashboard Logs**
- Track who opened the dashboard
- Role, action, IP address, timestamp
- Admin-only view
- Audit trail for compliance

### **Change Logs**
- Mode change history (old mode → new mode)
- Changed by (teacher/admin ID and name)
- Timestamp
- Displayed in dashboard

### **Teacher/Admin Actions**
- Log all teacher actions (e.g., mode changes from dashboard)
- Log all admin actions
- Separate tables for accountability

---

## 🛡️ Content Filtering

### **Whitelist System**
- Per-mode domain whitelists
- Add/edit/delete from dashboard
- Domain pattern matching
- Active/inactive status
- Added by tracking

### **Blacklist System**
- Per-mode domain blacklists
- Reason for blocking
- Add/edit/delete from dashboard
- Domain pattern matching
- Active/inactive status

### **Google Safe Browsing Integration**
- Free mode URL safety checks
- Malicious site detection
- Phishing protection
- API key configuration in `.env`
- Automatic violation logging for unsafe URLs

---

## 🔧 Technical Features

### **Database**
- MySQL 8 / utf8mb4
- Single database schema (Hostinger shared hosting compatible)
- 20+ tables for comprehensive data tracking
- Foreign key constraints
- Indexes for performance
- Migration scripts for schema updates

### **API (PHP)**
- RESTful API at `api.abhinavpaudel.com`
- JWT authentication
- CORS enabled
- JSON responses
- Error handling with detailed messages
- Debug endpoint for troubleshooting
- Path aliases for host compatibility

### **Dashboard (React)**
- Hosted at `abhinavpaudel.com`
- React + TypeScript + Vite
- TanStack Query for data fetching
- Shadcn/ui components
- Tailwind CSS styling
- React Router for navigation
- Auth context for user state

### **Desktop App (PyQt6)**
- Python 3.9+
- PyQt6 WebEngine for browser
- Cross-platform (Windows, macOS, Linux)
- Local cache storage
- Environment variable configuration
- Automatic session management

---

## 📦 Configuration & Deployment

### **Environment Variables**
- Database credentials (host, port, user, password, name)
- Dashboard URL
- API base URL
- JWT secret (must match PHP API)
- Google Safe Browsing API key
- Optional: Gmail OAuth credentials

### **Deployment**
- PHP API on Hostinger
- React dashboard static build
- Qt app as standalone executable or Python script
- Database on Hostinger MySQL
- HTTPS for production

### **Documentation**
- Production checklist
- Database tables usage guide
- JWT secret matching guide
- Hostinger API logs guide
- Forgot password flow documentation
- Setup guides for browser, dashboard, Python app

---

## 🎨 User Experience

### **Visual Indicators**
- Mode-specific colors (violet, blue, amber, green)
- Mode icons (📁, 📚, ⚠️, 🌐)
- Loading screens with mode display
- Window title shows current mode
- Status bar messages
- Network status indicator

### **Notifications**
- Success/error toast messages
- Security-themed warning dialogs
- Confirmation dialogs for destructive actions
- Cache success/failure messages
- Violation warnings

### **Dashboard UX**
- Tabbed interface for organization
- Per-student detail cards
- Collapsible sections
- Real-time data updates
- Skeleton loaders for loading states
- Empty states with helpful messages
- Responsive design for mobile/tablet

---

## 🚀 Production-Ready Features

### **Error Handling**
- PHP exception catching with JSON 500 responses
- React error boundaries
- Qt exception handling
- Graceful fallbacks for missing data
- User-friendly error messages

### **Performance**
- Query result caching
- Indexed database queries
- Lazy loading in dashboard
- Efficient URL checking
- Minimal network requests

### **Security Hardening**
- JWT token expiration
- Device-based access control
- SQL injection prevention (prepared statements)
- XSS protection
- CSRF protection
- Password reset token expiration
- Optional: Rate limiting for debug endpoint

### **Logging & Debugging**
- PHP error logs
- Dashboard console capture
- Debug log button in Qt app
- API debug endpoint
- Detailed violation reasons

### **Maintenance**
- Database migration scripts
- Sample data population
- Admin user creation scripts
- Test user generation
- Database export functionality

---

## 📋 Summary Statistics

- **4 Browsing Modes:** Cached, Study, Restricted, Free
- **4 User Roles:** Student, Teacher, Admin, Super Admin
- **20+ Database Tables:** Comprehensive data tracking
- **30+ API Endpoints:** Full CRUD operations
- **10+ Dashboard Tabs/Sections:** Complete management interface
- **Real-time Monitoring:** Session tracking, violations, activity
- **ML-Ready Data:** Session usage, browsing patterns, violations
- **Production Deployed:** Hostinger PHP API + React dashboard + Qt app

---

## 🎯 Use Cases

1. **Educational Institutions:** Control student browsing during classes
2. **Exam Mode:** Offline-only cached content for secure testing
3. **Library/Lab Computers:** Restricted browsing for public access
4. **Training Centers:** Monitored free browsing with safety checks
5. **Parental Control:** Time-windowed access for students
6. **Compliance:** Full audit trail for regulatory requirements
7. **Research:** ML-ready session data for behavior analysis

---

## 🔮 Market-Ready Status

✅ **Complete feature set**  
✅ **Production-deployed API and dashboard**  
✅ **Comprehensive documentation**  
✅ **Security hardened**  
✅ **Performance optimized**  
✅ **Error handling**  
✅ **Audit trails**  
✅ **ML-ready data**  
✅ **Multi-role support**  
✅ **Offline capability**  

**Ready for deployment in educational institutions and training centers.**
