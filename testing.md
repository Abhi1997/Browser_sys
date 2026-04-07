# EduBrowser — Comprehensive Testing Guide (FYP)

**Project:** Secure Academic Browser (EduBrowser)  
**Platform:** PyQt6 Desktop Application + React Dashboard + PHP REST API  
**Database:** MySQL 8 (Hostinger)  
**Date:** April 2026

---

## Table of Contents

1. [Test Environment Setup](#1-test-environment-setup)
2. [Unit Testing](#2-unit-testing)
3. [Integration Testing](#3-integration-testing)
4. [Functional Testing (Feature-by-Feature)](#4-functional-testing)
5. [Role-Based Access Control Testing](#5-role-based-access-control-testing)
6. [API Endpoint Testing](#6-api-endpoint-testing)
7. [Security Testing](#7-security-testing)
8. [UI/UX Testing](#8-uiux-testing)
9. [Performance Testing](#9-performance-testing)
10. [Compatibility Testing](#10-compatibility-testing)
11. [Regression Testing](#11-regression-testing)
12. [User Acceptance Testing (UAT)](#12-user-acceptance-testing-uat)
13. [Test Summary Report Template](#13-test-summary-report-template)

---

## 1. Test Environment Setup

### 1.1 Prerequisites

| Component | Requirement |
|---|---|
| Python | 3.9+ with PyQt6, PyJWT, mysql-connector-python |
| Node.js | 18+ with npm |
| MySQL | 8.x (Hostinger or local) |
| Browser | Chrome/Firefox for dashboard manual testing |
| OS | macOS (primary), Windows/Linux (cross-platform) |

### 1.2 Setting Up Local Testing

```bash
# 1. Start the React dashboard dev server
cd Browser_dashboard/react-dashboard
npm install
npm run dev          # → http://localhost:8080

# 2. (Optional) Start the Python Flask backend
cd Browser_dashboard/react-dashboard/backend
python app.py        # → http://localhost:5000

# 3. Run individual test scripts
cd qtapp
python tests/test_teacher_dashboard.py
python tests/test_admin_dashboard.py
python tests/test_superadmin_dashboard.py
python tests/test_superuser_dashboard.py
python tests/test_dashboard_window.py      # Interactive login
python tests/test_management_window.py     # Management panel
```

### 1.3 Test User Credentials

| Username | Password | Role | Purpose |
|---|---|---|---|
| `admin` | `admin123!` | superuser | Full system access |
| `superadmin1` | `superadmin123!` | superadmin | Read-only oversight |
| `admintest` | `admintest123!` | admin | Group management |
| `abhinavteacher1` | `abhinavteacher123!` | teacher | Student management |
| `userstudent` | `userstudent123!` | student | End user browsing |

---

## 2. Unit Testing

### 2.1 Authentication Module (`qtapp/authentication.py`)

| # | Test Case | Steps | Expected Result | Status |
|---|---|---|---|---|
| U-01 | Valid password login | Call `authenticate_user("admin", "admin123!", device_id)` | Returns `{success: True, token: ..., user: {role: "superuser"}}` | |
| U-02 | Invalid password | Call `authenticate_user("admin", "wrongpass", device_id)` | Returns `{success: False, error: "Invalid credentials"}` | |
| U-03 | Non-existent user | Call `authenticate_user("nobody", "pass", device_id)` | Returns `{success: False}` | |
| U-04 | Inactive user login | Deactivate a user, then try login | Returns `{success: False}` or `None` | |
| U-05 | JWT token generation | Call `generate_token("admin", "superuser", 1)` | Returns valid JWT string with `userId`, `role`, `exp`, `iat` | |
| U-06 | JWT token validation | Generate token, then call `validate_token(token, device_id)` | Returns user dict with `id`, `username`, `role` | |
| U-07 | Expired token rejection | Create token with past `exp`, validate it | Returns `None` | |
| U-08 | Gmail OAuth login | Call `validate_gmail_user("valid@gmail.com")` | Returns `(role, user_id)` tuple | |
| U-09 | Teacher approval gate | Login as unapproved teacher | Returns `None` (blocked) | |
| U-10 | Device registration | Call `register_device(user_id, device_info)` | Returns `True`, device stored in DB | |

### 2.2 Mode Enforcement (`qtapp/mode_enforcement.py`)

| # | Test Case | Steps | Expected Result | Status |
|---|---|---|---|---|
| U-11 | Cached mode: block HTTP | Student in cached mode visits `https://google.com` | URL intercepted and blocked | |
| U-12 | Cached mode: allow file:// | Student loads cached `file:///.../*.mhtml` | Page loads successfully | |
| U-13 | Study mode: whitelisted URL | Visit a whitelisted domain | Page loads normally | |
| U-14 | Study mode: non-whitelisted | Visit a non-whitelisted domain | Blocked with violation dialog | |
| U-15 | Restricted mode: blacklisted | Visit a blacklisted domain | Blocked with violation logged | |
| U-16 | Free mode: all allowed | Visit any URL | Page loads (with monitoring) | |
| U-17 | Free mode: Safe Browsing | Visit a known malicious URL | Blocked by Google Safe Browsing check | |
| U-18 | Mode change reflects | Admin changes student from restricted→free | Student's next session uses free mode | |

### 2.3 Student Profile Management

| # | Test Case | Steps | Expected Result | Status |
|---|---|---|---|---|
| U-19 | Student profile creation | Register student user | Entry created in both `Users` and `Students` tables | |
| U-20 | Mode assignment | Call `set_student_mode(student_id, "study", admin_id)` | `Students.assigned_mode` updated, `ModeHistory` entry added | |
| U-21 | Get student mode | Call `get_student_mode(user_id)` | Returns current mode string | |

---

## 3. Integration Testing

### 3.1 Authentication → Dashboard Flow

| # | Test Case | Steps | Expected Result | Status |
|---|---|---|---|---|
| I-01 | Login → Dashboard URL | Login via `authenticate_user`, check `_build_dashboard_url()` | URL contains valid JWT token and correct role path | |
| I-02 | PyQt → React handoff | Run `test_teacher_dashboard.py` | QWebEngineView loads React dashboard at localhost:8080 with auth | |
| I-03 | Token verification roundtrip | Generate token in Python, verify via PHP API `/api/auth/verify-token` | PHP decodes and validates the same JWT | |
| I-04 | Session persistence | Login, close app, reopen within 4 hours | Session restored from QSettings, no re-login needed | |
| I-05 | Session expiry | Login, wait 4+ hours (or mock time) | Session expired, cookies cleared, login required | |

### 3.2 Dashboard → API → Database Flow

| # | Test Case | Steps | Expected Result | Status |
|---|---|---|---|---|
| I-06 | Stats fetch | Open admin dashboard, observe stats cards | Numbers match actual DB counts (`SELECT COUNT(*)`) | |
| I-07 | Student list fetch | Open teacher dashboard, check student list | Only students assigned to that teacher appear | |
| I-08 | Mode change via dashboard | Change student mode in dashboard → check DB | `Students.assigned_mode` updated, `ModeHistory` logged | |
| I-09 | Whitelist CRUD | Add → Edit → Delete whitelist entry from dashboard | Changes reflected in `WhitelistDomains` table | |
| I-10 | Blacklist CRUD | Add → Edit → Delete blacklist entry from dashboard | Changes reflected in `BlacklistDomains` table | |

### 3.3 Browser → Database Logging

| # | Test Case | Steps | Expected Result | Status |
|---|---|---|---|---|
| I-11 | Activity logging | Student visits a URL | Entry in `ActivityLogs` with URL, domain, mode, timestamps | |
| I-12 | Violation logging | Student visits blocked URL | Entry in `Violations` with attempted URL, reason, severity | |
| I-13 | Browsing history | Any user visits URL | Entry in `BrowsingHistory` with user_id, URL, title | |
| I-14 | Session logging | User opens app | Entry in `Sessions`, `last_activity_at` updated every 2 min | |
| I-15 | Dashboard open logging | Open dashboard | Entry in `DashboardLogs` with user_id, role, action | |

---

## 4. Functional Testing (Feature-by-Feature)

### 4.1 Browser Application (PyQt6)

| # | Feature | Test Steps | Expected Result | Status |
|---|---|---|---|---|
| F-01 | Tab management | Open new tab, switch tabs, close tab | Tabs open/close correctly, focus switches | |
| F-02 | Address bar | Type URL, press Enter | Page navigates to URL | |
| F-03 | Navigation buttons | Click Back, Forward, Reload, Home | Navigation works as expected | |
| F-04 | Zoom control | Zoom in (Ctrl+Plus), zoom out (Ctrl+Minus) | Page zooms 50%-200% | |
| F-05 | Network indicator | Disconnect WiFi, reconnect | Status bar shows online/offline | |
| F-06 | Loading progress | Navigate to a page | Progress bar shown during load | |
| F-07 | Mode indicator (student) | Login as student | Mode toolbar shows icon, name, description, color | |
| F-08 | Cache page button | Login as teacher, click "Cache this page" | Page saved as MHTML, registered in `CachedSites` | |
| F-09 | Dashboard button | Click "Dashboard" | Dashboard window opens with correct role view | |
| F-10 | Management button | Login as admin, click "Management Panel" | Management window opens | |

### 4.2 Login Window

| # | Feature | Test Steps | Expected Result | Status |
|---|---|---|---|---|
| F-11 | Password login | Enter valid credentials, click Login | App opens with correct role | |
| F-12 | Gmail OAuth login | Click Gmail login, authenticate | App opens if user exists in DB | |
| F-13 | Registration | Click Register, fill form | New user created in DB | |
| F-14 | Forgot password | Click "Forgot Password", enter email | Reset email sent (if SMTP configured) | |
| F-15 | Error display | Enter wrong password | Error message shown in dialog | |
| F-16 | Session remember | Login, close, reopen within 4h | Auto-login without prompt | |
| F-17 | Session expire | Wait 4+ hours | Must re-login, cookies cleared | |

### 4.3 Dashboard (React)

| # | Feature | Test Steps | Expected Result | Status |
|---|---|---|---|---|
| F-18 | Stats cards | Open dashboard | Correct counts for students, whitelist, blacklist | |
| F-19 | Stats card click | Click "Total Students" card | Tab switches to Students tab | |
| F-20 | Student detail card | Expand student card | Shows mode, violations log, browsing history | |
| F-21 | Change student mode | Select different mode in dropdown | API called, mode updated, toast shown | |
| F-22 | Whitelist management | Add/edit/delete whitelist entry | CRUD operations succeed with feedback | |
| F-23 | Blacklist management | Add/edit/delete blacklist entry | CRUD operations succeed with feedback | |
| F-24 | User management | Create/edit/delete user (admin) | User appears/updates/disappears in list | |
| F-25 | Change logs | Open Change Logs tab | Shows mode change history with timestamps | |
| F-26 | Dashboard logs | Open Dashboard Logs tab | Shows who opened dashboard and when | |
| F-27 | Warning triggers | Open Warning Triggers tab | Shows violations with escalation info | |
| F-28 | Session usage | Open Session Usage tab | Shows session data with timestamps | |
| F-29 | Cached sites | Open Cached Sites tab | Lists cached pages, can delete | |
| F-30 | Export database | Click Export button (admin) | SQL file downloads | |
| F-31 | Theme toggle | Switch light/dark mode in Settings | UI theme changes correctly | |
| F-32 | My profile page | Click user menu → My Profile | Shows user info | |
| F-33 | My history page | Click user menu → My History | Shows personal browsing history | |

### 4.4 Caching System (Offline Mode)

| # | Feature | Test Steps | Expected Result | Status |
|---|---|---|---|---|
| F-34 | Cache a page | Teacher clicks "Cache this page" on any URL | MHTML file saved, entry in CachedSites DB | |
| F-35 | Load cached page | Student in cached mode, clicks Home | First cached page loads via file:// | |
| F-36 | Block network in cached | Student in cached mode, types URL | Network request intercepted and blocked | |
| F-37 | Delete cached site | Admin deletes cached site from dashboard | Entry removed from DB, file optionally cleaned up | |

---

## 5. Role-Based Access Control Testing

### 5.1 Data Isolation Matrix

Test that each role sees ONLY its permitted data:

| API Endpoint | Student | Teacher | Admin | Superadmin | Superuser |
|---|---|---|---|---|---|
| `GET /api/students` | ❌ No access | ✅ Own assigned only | ✅ Own group only | ✅ All (read) | ✅ All (read+write) |
| `GET /api/stats` | ❌ | ✅ Own student count | ✅ Own group count | ✅ All counts | ✅ All counts |
| `GET /api/activity` | ❌ | ✅ Own students' | ✅ Own group's | ✅ All | ✅ All |
| `GET /api/violations` | ❌ | ✅ Own students' | ✅ Own group's | ✅ All | ✅ All |
| `GET /api/warning-triggers` | ❌ | ✅ Own students' | ✅ Own group's | ✅ All | ✅ All |
| `POST /api/users` (create) | ❌ | ❌ | ✅ | ❌ (admin only) | ✅ |
| `PATCH /api/users/:id` | ❌ | ❌ | ✅ Own group | ❌ | ✅ |
| `DELETE /api/users/:id` | ❌ | ❌ | ✅ Own group | ❌ | ✅ |
| `POST /api/students/:id/mode` | ❌ | ✅ Own students | ✅ Own group | ❌ (read-only) | ✅ |

### 5.2 Specific RBAC Test Cases

| # | Test Case | Steps | Expected | Status |
|---|---|---|---|---|
| R-01 | Teacher isolation | Login as teacher A, list students | Only teacher A's assigned students shown | |
| R-02 | Teacher cannot see other's | Teacher A should NOT see teacher B's students | Student list empty or filtered | |
| R-03 | Admin isolation | Login as admin A, list students | Only admin A's group students shown | |
| R-04 | Admin cannot see other admin | Admin A should NOT see admin B's data | No cross-group data leakage | |
| R-05 | Superadmin read-only | Superadmin tries to edit a user | 403 Forbidden returned | |
| R-06 | Superadmin admin creation | Superadmin creates new admin | Admin created successfully | |
| R-07 | Superuser full access | Superuser edits any user | Succeeds regardless of group | |
| R-08 | Student no dashboard | Student opens dashboard URL | Access denied or empty view | |
| R-09 | Admin switcher (super) | Superadmin selects different admin | Dashboard data switches to that admin's scope | |
| R-10 | Teacher assign student | Admin assigns student to teacher | Student appears in teacher's dashboard | |

---

## 6. API Endpoint Testing

Use Postman or curl. See `docs/POSTMAN_GUIDE.md` for collection setup.

### 6.1 Authentication Endpoints

| # | Method | Endpoint | Test | Expected | Status |
|---|---|---|---|---|---|
| A-01 | `POST` | `/auth/login` | Valid credentials | 200 + JWT token | |
| A-02 | `POST` | `/auth/login` | Wrong password | 401 + error message | |
| A-03 | `POST` | `/api/auth/verify-token` | Valid token | 200 + user object | |
| A-04 | `POST` | `/api/auth/verify-token` | Expired token | 401 | |
| A-05 | `POST` | `/api/auth/forgot-password` | Valid email | 200 + message | |
| A-06 | `POST` | `/api/auth/reset-password` | Valid reset token | 200 + success | |
| A-07 | `POST` | `/api/auth/dashboard-log-open` | With auth header | 200 + logged | |

### 6.2 CRUD Endpoints

| # | Method | Endpoint | Test | Expected | Status |
|---|---|---|---|---|---|
| A-08 | `GET` | `/api/stats` | With auth header | 200 + stats object | |
| A-09 | `GET` | `/api/users` | As admin | 200 + user array | |
| A-10 | `POST` | `/api/users` | Create user payload | 200 + created user | |
| A-11 | `PATCH` | `/api/users/:id` | Update username | 200 + updated user | |
| A-12 | `DELETE` | `/api/users/:id` | Delete user | 200 + success | |
| A-13 | `PATCH` | `/api/users/:id/toggle-status` | Toggle active | 200 + toggled user | |
| A-14 | `GET` | `/api/students` | As teacher | 200 + filtered students | |
| A-15 | `POST` | `/api/students/:id/mode` | Change mode | 200 + updated mode | |
| A-16 | `POST` | `/api/students/:id/assign-teacher` | Assign teacher | 200 + success | |
| A-17 | `GET` | `/api/whitelist` | With auth | 200 + entries | |
| A-18 | `POST` | `/api/whitelist` | Add domain | 200 + created entry | |
| A-19 | `PATCH` | `/api/whitelist/:id` | Edit entry | 200 + updated entry | |
| A-20 | `DELETE` | `/api/whitelist/:id` | Remove entry | 200 + success | |
| A-21 | `GET` | `/api/blacklist` | With auth | 200 + entries | |
| A-22 | `POST` | `/api/blacklist` | Add domain | 200 + created entry | |
| A-23 | `DELETE` | `/api/blacklist/:id` | Remove entry | 200 + success | |
| A-24 | `GET` | `/api/activity` | As teacher | 200 + filtered activity | |
| A-25 | `GET` | `/api/violations` | As admin | 200 + violations array | |
| A-26 | `GET` | `/api/warning-triggers` | As teacher | 200 + filtered warnings | |
| A-27 | `GET` | `/api/history` | With auth | 200 + personal history | |
| A-28 | `GET` | `/api/students/:id/history` | As teacher | 200 + student history | |
| A-29 | `GET` | `/api/change-logs` | As admin | 200 + mode changes | |
| A-30 | `GET` | `/api/dashboard-logs` | As admin | 200 + dashboard logs | |
| A-31 | `GET` | `/api/sessions` | As admin | 200 + session data | |
| A-32 | `GET` | `/api/cached-sites` | With auth | 200 + cached sites | |
| A-33 | `DELETE` | `/api/cached-sites/:id` | Delete site | 200 + success | |
| A-34 | `GET` | `/api/teachers` | As admin | 200 + teacher list | |
| A-35 | `GET` | `/api/admins` | As superuser | 200 + admin list | |
| A-36 | `POST` | `/export/db` | As admin | 200 + SQL blob | |
| A-37 | `GET` | `/health` | No auth needed | 200 + status:ok | |
| A-38 | `GET` | `/api/bookmarks` | With auth | 200 + user bookmarks | |

### 6.3 Error Handling

| # | Test Case | Steps | Expected | Status |
|---|---|---|---|---|
| A-39 | No auth header | Call any protected endpoint without token | 401 Unauthorized | |
| A-40 | Invalid token | Call with garbage JWT | 401 Invalid token | |
| A-41 | Not found route | `GET /api/nonexistent` | 404 Not found | |
| A-42 | Invalid JSON body | `POST /api/users` with malformed JSON | 400 or 500 with error message | |

---

## 7. Security Testing

| # | Test Case | Steps | Expected | Status |
|---|---|---|---|---|
| S-01 | SQL injection (login) | Username: `' OR 1=1 --` | Login fails, no data leaked | |
| S-02 | SQL injection (API) | `GET /api/users?admin_id=' OR 1=1` | Error or empty response, no bypass | |
| S-03 | XSS in username | Create user with `<script>alert(1)</script>` name | Script not executed in dashboard | |
| S-04 | JWT tampering | Modify JWT payload, keep old signature | 401 Invalid token | |
| S-05 | Expired token | Use token after `exp` time | 401 Expired | |
| S-06 | Cross-role escalation | Teacher's token calls admin-only endpoint | 403 Forbidden | |
| S-07 | Password in response | Login response body | Password hash NOT in response | |
| S-08 | Brute force login | Try 100 rapid login attempts | Server handles gracefully (no crash) | |
| S-09 | CORS headers | OPTIONS preflight request | Correct CORS headers returned | |
| S-10 | Device fingerprint | Login from different device | New device registered in Devices table | |

---

## 8. UI/UX Testing

### 8.1 Dashboard UI

| # | Test Case | Steps | Expected | Status |
|---|---|---|---|---|
| UI-01 | Light mode default | Open dashboard first time | Light theme applied | |
| UI-02 | Dark mode toggle | Switch to dark mode in Settings | All components render in dark theme | |
| UI-03 | Responsive layout | Resize browser to mobile width (< 768px) | Layout stacks vertically, no overflow | |
| UI-04 | Loading skeletons | Open dashboard with slow network | Skeleton placeholders shown while loading | |
| UI-05 | Empty states | Login as teacher with no students | "No students found" message instead of blank | |
| UI-06 | Toast notifications | Perform any CRUD action | Success/error toast appears and auto-dismisses | |
| UI-07 | Confirmation dialogs | Delete a user | Confirmation dialog shown before deletion | |
| UI-08 | Tab navigation | Click through all dashboard tabs | Each tab loads its content correctly | |
| UI-09 | User menu | Click avatar in header | Dropdown with Profile, History, Sign Out | |
| UI-10 | Admin switcher | Login as superadmin, use admin switcher | Dashboard data changes to selected admin's scope | |

### 8.2 Browser UI

| # | Test Case | Steps | Expected | Status |
|---|---|---|---|---|
| UI-11 | Mode toolbar colors | Login as student in each mode | Correct color (violet/blue/amber/green) | |
| UI-12 | Warning dialog | Student visits blocked URL | Security-themed warning dialog, not generic | |
| UI-13 | Tab titles | Open multiple tabs | Each tab shows page title | |
| UI-14 | Debug log button | Click "Debug log" in dashboard window | Console messages shown in dialog | |

---

## 9. Performance Testing

| # | Test Case | Steps | Expected | Status |
|---|---|---|---|---|
| P-01 | Dashboard load time | Open dashboard, measure load | < 3 seconds on broadband | |
| P-02 | Student list (N=100) | Admin with 100 students opens dashboard | List renders within 2 seconds | |
| P-03 | API response time | Call `/api/students` from Postman | Response < 500ms | |
| P-04 | Database queries | Check slow query log | No queries > 1 second | |
| P-05 | Memory usage | Run Qt app for 1 hour with browsing | RAM usage stays below 500MB | |
| P-06 | Connection pooling | Rapid API calls (10/second for 30s) | No "too many connections" errors | |
| P-07 | Concurrent dashboard | Open 5 dashboards simultaneously | All function correctly | |

---

## 10. Compatibility Testing

| # | Test Case | Platform | Expected | Status |
|---|---|---|---|---|
| C-01 | macOS (primary) | macOS 12+ | App runs, all features work | |
| C-02 | Windows | Windows 10/11 | App runs, all features work | |
| C-03 | Linux | Ubuntu 22.04 | App runs, all features work | |
| C-04 | Python version | Python 3.9, 3.10, 3.11, 3.12, 3.13 | No version-specific errors | |
| C-05 | Dashboard on Chrome | Latest Chrome | All features render correctly | |
| C-06 | Dashboard on Firefox | Latest Firefox | All features render correctly | |
| C-07 | Dashboard on Safari | Latest Safari | All features render correctly | |

---

## 11. Regression Testing

After any code change, verify these critical paths still work:

| # | Critical Path | Quick Check | Status |
|---|---|---|---|
| RG-01 | Login → Dashboard | Run `test_admin_dashboard.py` | |
| RG-02 | Teacher sees only own students | Run `test_teacher_dashboard.py`, verify student count | |
| RG-03 | Mode enforcement | Login as student, visit blocked URL | |
| RG-04 | API auth | `curl -H "Authorization: Bearer <token>" https://api.abhinavpaudel.com/api/stats` | |
| RG-05 | Dashboard builds | `cd react-dashboard && npm run build` (no errors) | |
| RG-06 | Session 4-hour expiry | Check `gmail_oauth.py` timestamp logic | |

---

## 12. User Acceptance Testing (UAT)

### 12.1 Scenario-Based Tests

These simulate real-world usage for the FYP demo:

#### Scenario 1: Teacher's Daily Workflow
1. Teacher logs in with username/password
2. Dashboard opens showing **only their assigned students**
3. Teacher views student violations — sees only their students' violations
4. Teacher changes a student's mode from "restricted" → "study"
5. Teacher caches a study webpage for offline use
6. Teacher views student browsing history
7. **Pass criteria:** All data is teacher-scoped, mode change reflects immediately

#### Scenario 2: Admin Sets Up a Class
1. Admin logs in
2. Creates 2 teacher accounts from dashboard
3. Creates 5 student accounts
4. Assigns 3 students to teacher A, 2 to teacher B
5. Adds whitelist domains (e.g., `khan.academy.org`, `wikipedia.org`)
6. Adds blacklist domains (e.g., `facebook.com`, `tiktok.com`)
7. Sets students to "study" mode
8. **Pass criteria:** Teachers see only their assigned students; whitelist/blacklist enforced

#### Scenario 3: Student Exam Mode
1. Admin sets student to "cached" mode
2. Teacher caches exam pages beforehand
3. Student logs in — sees cached mode indicator
4. Student can view cached pages only
5. Student tries typing a URL — **blocked** (network intercepted)
6. Violation logged automatically
7. **Pass criteria:** Complete network isolation, only cached content accessible

#### Scenario 4: Superadmin Oversight
1. Superadmin logs in
2. Sees global statistics across all admins
3. Uses admin switcher to view specific admin's group data
4. Attempts to edit a user — **blocked** (read-only)
5. Creates a new admin account
6. **Pass criteria:** Full visibility, creation works, modification blocked

#### Scenario 5: Superuser Full Control
1. Superuser logs in
2. Sees all data across all groups
3. Can modify any user, whitelist, blacklist
4. Can create users of any role
5. Can delete any user
6. **Pass criteria:** No restrictions, full CRUD on everything

#### Scenario 6: Session & Security
1. User logs in, note the time
2. Close the application
3. Reopen within 4 hours — auto-login works
4. Wait 4+ hours — must re-login
5. After re-login, site cookies (YouTube, Google) are cleared
6. **Pass criteria:** Session persistence and expiry work correctly

### 12.2 UAT Sign-Off Checklist

| Category | Verified By | Date | Signature |
|---|---|---|---|
| Authentication & Login | | | |
| Role-Based Access Control | | | |
| Browsing Mode Enforcement | | | |
| Dashboard Data Accuracy | | | |
| CRUD Operations (Users, Whitelist, Blacklist) | | | |
| Activity & Violation Logging | | | |
| Caching / Offline Mode | | | |
| Session Management | | | |
| Export & Reporting | | | |

---

## 13. Test Summary Report Template

Use this template for the final FYP test report:

```
============================================================
TEST SUMMARY REPORT
Project: Secure Academic Browser (EduBrowser)
Date: ___________
Tester: ___________
============================================================

ENVIRONMENT
-----------
OS: macOS _____ / Windows _____ / Linux _____
Python: _____
Node.js: _____
Database: MySQL 8.x (Hostinger)
API: https://api.abhinavpaudel.com
Dashboard: https://abhinavpaudel.com

RESULTS SUMMARY
---------------
Total Test Cases:    _____
Passed:              _____
Failed:              _____
Blocked:             _____
Not Executed:        _____
Pass Rate:           _____% 

CATEGORY BREAKDOWN
------------------
Unit Tests:          _____ / 21 passed
Integration Tests:   _____ / 15 passed
Functional Tests:    _____ / 37 passed
RBAC Tests:          _____ / 10 passed
API Tests:           _____ / 42 passed
Security Tests:      _____ / 10 passed
UI/UX Tests:         _____ / 14 passed
Performance Tests:   _____ / 7  passed
Compatibility Tests: _____ / 7  passed
Regression Tests:    _____ / 6  passed
UAT Scenarios:       _____ / 6  passed

DEFECTS FOUND
-------------
Critical: _____
High:     _____
Medium:   _____
Low:      _____

KNOWN ISSUES
------------
1. ___________
2. ___________

CONCLUSION
----------
[Overall assessment and recommendation for submission]

SIGN-OFF
--------
Tester:    _____________  Date: __________
Supervisor: ____________  Date: __________
============================================================
```

---

## Quick Reference: Running All Tests

```bash
# From qtapp/ directory

# Automated role-specific tests (requires npm run dev at localhost:8080)
python tests/test_teacher_dashboard.py
python tests/test_admin_dashboard.py
python tests/test_superadmin_dashboard.py
python tests/test_superuser_dashboard.py

# Interactive login test
python tests/test_dashboard_window.py

# Management window test
python tests/test_management_window.py

# API health check
curl https://api.abhinavpaudel.com/health

# Dashboard build check
cd ../Browser_dashboard/react-dashboard && npm run build
```
