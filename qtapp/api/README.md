# Dashboard API Server

REST API server for the EduBrowser Dashboard.

## Setup

### 1. Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root (parent directory) with:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=u976383844_abhi097
DB_PASSWORD=!nN0v@tion113
DB_NAME=u976383844_dces

# JWT Secret (MUST MATCH BROWSER APP!)
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production

# API Configuration
API_PORT=5000
FLASK_DEBUG=False
```

### 3. Run the Server

```bash
# From the api directory
python app.py

# Or from project root
python api/app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/verify-token` - Verify JWT token

### Statistics
- `GET /api/stats` - Get system statistics

### Users
- `GET /api/users` - Get all users
- `POST /api/users` - Create user
- `PATCH /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user
- `PATCH /api/users/:id/toggle-status` - Toggle user status

### Students
- `GET /api/students` - Get all students
- `POST /api/students/:studentId/mode` - Change student mode

### Activity
- `GET /api/activity?studentId=<id>&limit=100` - Get activity logs
- `GET /api/violations?studentId=<id>&limit=100` - Get violations

### Whitelist
- `GET /api/whitelist` - Get all whitelist entries
- `POST /api/whitelist` - Add to whitelist
- `PATCH /api/whitelist/:id` - Update whitelist entry
- `DELETE /api/whitelist/:id` - Remove from whitelist

### Blacklist
- `GET /api/blacklist` - Get all blacklist entries
- `POST /api/blacklist` - Add to blacklist
- `PATCH /api/blacklist/:id` - Update blacklist entry
- `DELETE /api/blacklist/:id` - Remove from blacklist

### Health Check
- `GET /health` - Health check endpoint

## Authentication

All endpoints (except `/health`) require JWT authentication:

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
X-Device-ID: <device_id>
```

## Testing

Test the API with curl:

```bash
# Health check
curl http://localhost:5000/health

# Verify token
curl -X POST http://localhost:5000/api/auth/verify-token \
  -H "Content-Type: application/json" \
  -d '{"token": "your-jwt-token", "deviceId": "device-id"}'

# Get stats (requires authentication)
curl http://localhost:5000/api/stats \
  -H "Authorization: Bearer your-jwt-token" \
  -H "X-Device-ID: device-id"
```

## Production Deployment

For production:

1. Use a production WSGI server (gunicorn, uwsgi)
2. Set `FLASK_DEBUG=False`
3. Use environment variables for configuration
4. Enable HTTPS
5. Set up proper logging
6. Configure firewall rules

Example with gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Troubleshooting

### Database Connection Issues
- Verify database credentials in `.env`
- Check database is accessible from server
- Ensure MySQL user has proper permissions

### JWT Token Issues
- Verify `JWT_SECRET` matches browser app
- Check token expiration
- Ensure token format is correct

### CORS Issues
- Add your dashboard domain to CORS origins in `app.py`
- Check browser console for CORS errors

## Notes

- The API uses the same `authentication.py` module as the browser app
- Database connection is shared with browser app configuration
- All endpoints return JSON with `success` and `data`/`error` fields
- Soft deletes are used (setting `is_active = 0`)
