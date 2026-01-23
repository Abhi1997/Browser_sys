/**
 * Example: How to pass authentication data to the dashboard (JavaScript/Node.js)
 * 
 * This shows how your app should construct the dashboard URL
 * with the required token and deviceId parameters.
 */

const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');

// Configuration
// For production, use: https://api.abhinavpaudel.com
// For local development, use: http://localhost:8080
const DASHBOARD_BASE_URL = 'https://api.abhinavpaudel.com';
const SECRET_KEY = 'your-secret-key-here'; // Must match your backend's secret key (from .env JWT_SECRET)

/**
 * Generate a JWT token with user information
 * @param {number|string} userId - User ID
 * @param {string} username - Username
 * @param {string} role - User role: 'super-admin', 'admin', 'teacher', or 'student'
 * @param {string|null} adminId - Optional admin ID
 * @param {number} expiresHours - Token expiration in hours (default: 24)
 * @returns {string} JWT token
 */
function generateJWTToken(userId, username, role, adminId = null, expiresHours = 24) {
  const now = Math.floor(Date.now() / 1000);
  const payload = {
    userId: userId,  // Can also use 'user_id' (snake_case)
    username: username,
    role: role,
    adminId: adminId,
    iat: now,  // Issued at
    exp: now + (expiresHours * 60 * 60)  // Expiration
  };
  
  return jwt.sign(payload, SECRET_KEY, { algorithm: 'HS256' });
}

/**
 * Get or create device ID
 * In a real app, you'd store this persistently (e.g., in localStorage, database, etc.)
 */
function getOrCreateDeviceId() {
  // For this example, we'll generate a new UUID each time
  // In production, you should store and reuse the same device ID
  return uuidv4();
}

/**
 * Construct the dashboard URL with authentication parameters
 * @param {string} dashboardType - 'superadmin', 'admin', or 'teacher'
 * @param {number|string} userId - User ID
 * @param {string} username - Username
 * @param {string} role - User role
 * @param {string|null} adminId - Optional admin ID
 * @returns {string} Complete dashboard URL
 */
function constructDashboardUrl(dashboardType = 'admin', userId, username, role, adminId = null) {
  // Generate token
  const token = generateJWTToken(userId, username, role, adminId);
  
  // Get or create device ID
  const deviceId = getOrCreateDeviceId();
  
  // Construct URL
  const baseUrl = `${DASHBOARD_BASE_URL}/dashboard-${dashboardType}`;
  const params = new URLSearchParams({
    token: token,
    deviceId: deviceId
  });
  
  return `${baseUrl}?${params.toString()}`;
}

// Example usage
if (require.main === module) {
  // Example 1: Admin user
  const adminUrl = constructDashboardUrl(
    'admin',
    123,
    'john_doe',
    'admin',
    'admin_001'
  );
  console.log('Admin Dashboard URL:');
  console.log(adminUrl);
  console.log();
  
  // Example 2: Super Admin user
  const superadminUrl = constructDashboardUrl(
    'superadmin',
    1,
    'super_admin',
    'super-admin'
  );
  console.log('Super Admin Dashboard URL:');
  console.log(superadminUrl);
  console.log();
  
  // Example 3: Teacher user
  const teacherUrl = constructDashboardUrl(
    'teacher',
    456,
    'jane_smith',
    'teacher',
    'admin_001'
  );
  console.log('Teacher Dashboard URL:');
  console.log(teacherUrl);
  console.log();
  
  // In a browser, you would use it like this:
  // window.location.href = adminUrl;
  // or
  // window.open(adminUrl, '_blank');
}

module.exports = {
  generateJWTToken,
  getOrCreateDeviceId,
  constructDashboardUrl
};
