# Node/Express Backend Server

This document describes the backend API structure that should be implemented in a separate `server/` directory.

## Directory Structure

```
server/
├── src/
│   ├── server.ts           # Express app entry point
│   ├── routes/
│   │   ├── auth.ts         # POST /auth/login, GET /auth/verify
│   │   ├── stats.ts        # GET /stats/overview, /stats/admin/:id, /stats/admins
│   │   ├── users.ts        # GET/POST/PATCH /users
│   │   ├── whitelist.ts    # GET/POST/PATCH/DELETE /whitelist
│   │   ├── blacklist.ts    # GET/POST/PATCH/DELETE /blacklist
│   │   └── export.ts       # POST /export/db
│   ├── middleware/
│   │   ├── verifyJWT.ts    # JWT token verification
│   │   ├── checkDevice.ts  # Device ID validation
│   │   ├── checkRole.ts    # RBAC enforcement
│   │   └── auditLogger.ts  # Audit logging for sensitive ops
│   └── db/
│       ├── connection.ts   # MySQL connection pool
│       └── queries.ts      # Database queries
├── .env.example
├── package.json
└── tsconfig.json
```

## API Endpoints

### Authentication
- `POST /auth/login` - Returns JWT with role, username, deviceId
- `GET /auth/verify` - Validates current token

### Stats (RBAC protected)
- `GET /stats/overview` - Global stats (scoped by role)
- `GET /stats/admin/:adminId` - Admin-specific stats (super-admin read-only)
- `GET /stats/admins` - All admin stats (super-admin only)
- `GET /stats/login-activity` - Login activity data

### Users (Admin only, Super-admin read-only)
- `GET /users` - List users
- `POST /users` - Create user (admin only)
- `PATCH /users/:id` - Update user (admin only)
- `PATCH /users/:id/toggle-status` - Toggle user status

### Whitelist/Blacklist (Admin only, Super-admin read-only)
- `GET /whitelist`, `GET /blacklist` - List entries
- `POST /whitelist`, `POST /blacklist` - Add entry (admin only)
- `PATCH /:id` - Update entry (admin only)
- `DELETE /:id` - Remove entry (admin only)

### Export (Admin only)
- `POST /export/db` - Generate database snapshot

## Environment Variables (.env)

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=edu_browser

# JWT
JWT_SECRET=your-256-bit-secret
JWT_EXPIRES_IN=8h

# Server
PORT=4000
NODE_ENV=development
```

## JWT Payload Structure

```typescript
{
  userId: string;
  username: string;
  role: 'super-admin' | 'admin' | 'teacher' | 'student';
  deviceId: string;
  adminId?: string; // For scoped access
  exp: number;
  iat: number;
}
```

## Security Implementation

### Middleware Chain
1. `verifyJWT` - Validates JWT signature and expiration
2. `checkDevice` - Compares request deviceId with token deviceId
3. `checkRole` - Enforces RBAC per route

### Role Permissions
- **super-admin**: Read-only across all admins, can switch context
- **admin**: Full CRUD within their domain
- **teacher**: Read class data, limited actions
- **student**: No dashboard access

## MySQL Schema Reference

```sql
-- Existing tables (assumed)
CREATE TABLE Users (
  id VARCHAR(36) PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(255),
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('super-admin', 'admin', 'teacher', 'student'),
  admin_id VARCHAR(36),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP
);

CREATE TABLE Whitelist (
  id VARCHAR(36) PRIMARY KEY,
  url VARCHAR(500) NOT NULL,
  description TEXT,
  added_by VARCHAR(36),
  admin_id VARCHAR(36),
  is_active BOOLEAN DEFAULT TRUE,
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Blacklist (
  id VARCHAR(36) PRIMARY KEY,
  url VARCHAR(500) NOT NULL,
  reason TEXT,
  added_by VARCHAR(36),
  admin_id VARCHAR(36),
  is_active BOOLEAN DEFAULT TRUE,
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add audit_logs table
CREATE TABLE AuditLogs (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36),
  action VARCHAR(100),
  resource VARCHAR(100),
  details JSON,
  ip_address VARCHAR(45),
  device_id VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## PyQt6 Integration

The React app uses HashRouter for compatibility:

```python
# Python example
from PyQt6.QtWebEngineWidgets import QWebEngineView

def open_dashboard(role, username, token, device_id):
    url = f"file:///path/to/dist/index.html#/dashboard/{role}?user={username}&token={token}&deviceId={device_id}"
    # Or for dev server:
    # url = f"http://localhost:5173/#/dashboard/{role}?user={username}&token={token}&deviceId={device_id}"
    
    web_view = QWebEngineView()
    web_view.load(QUrl(url))
```

## Development Setup

```bash
# Install dependencies
cd server
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm test
```

## HTTPS Configuration (Production)

For production with self-signed certificates:

```typescript
import https from 'https';
import fs from 'fs';

const options = {
  key: fs.readFileSync('path/to/key.pem'),
  cert: fs.readFileSync('path/to/cert.pem')
};

https.createServer(options, app).listen(4000);
```
