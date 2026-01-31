import { 
  ApiResponse, 
  User, 
  StatsOverview, 
  AdminStats, 
  WhitelistEntry, 
  BlacklistEntry,
  LoginActivity,
  Notification,
  ClassMetrics,
  ActivityData
} from './types';
import { getStoredToken, getDeviceId } from './auth';

// API Base URL - defaults to local development
// Can be overridden with VITE_API_URL environment variable
// For production, set VITE_API_URL=https://api.abhinavpaudel.com in .env file
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const token = getStoredToken();
  const deviceId = getDeviceId();

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...(deviceId && { 'X-Device-ID': deviceId }),
    ...options.headers,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    // Handle non-JSON responses
    const contentType = response.headers.get('content-type');
    let data;
    
    if (contentType && contentType.includes('application/json')) {
      try {
        data = await response.json();
      } catch (jsonError) {
        // If JSON parsing fails, return error
        return {
          success: false,
          error: `Invalid JSON response from server: ${response.status} ${response.statusText}`,
        };
      }
    } else {
      // For non-JSON responses (like blob), return the response
      if (!response.ok) {
        return {
          success: false,
          error: `Request failed: ${response.status} ${response.statusText}`,
        };
      }
      // For successful non-JSON responses, return the response object
      return {
        success: true,
        data: response as any,
      };
    }

    if (!response.ok) {
      // Prefer server's message (e.g. PHP exception) for debugging 500s
      const serverMessage = data.message || data.error;
      const errorText = serverMessage || `Request failed: ${response.status} ${response.statusText}`;
      return {
        success: false,
        error: errorText,
      };
    }

    return {
      success: true,
      data: data.data || data,
      message: data.message,
    };
  } catch (error) {
    // Handle network errors more gracefully
    if (error instanceof TypeError && error.message.includes('fetch')) {
      // Don't show error for localhost in development - backend might not be set up yet
      const isLocalhost = API_BASE_URL.includes('localhost') || API_BASE_URL.includes('127.0.0.1');
      if (isLocalhost) {
        // Return success with empty data instead of error for localhost
        // This allows the dashboard to work without a backend
        return {
          success: true,
          data: null as any,
        };
      }
      return {
        success: false,
        error: `Cannot connect to API at ${API_BASE_URL}. Please ensure the backend server is running.`,
      };
    }
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Network error',
    };
  }
}

// Auth endpoints
export async function verifyToken(): Promise<ApiResponse<{ valid: boolean; user: User }>> {
  const token = getStoredToken();
  const deviceId = getDeviceId();
  
  if (!token || !deviceId) {
    return { success: false, error: 'Missing token or deviceId' };
  }
  
  return apiRequest('/api/auth/verify-token', {
    method: 'POST',
    body: JSON.stringify({ token, deviceId }),
  });
}

export async function login(
  username: string,
  password: string,
  deviceId: string
): Promise<ApiResponse<{ token: string; user: User }>> {
  return apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password, deviceId }),
  });
}

/** Forgot password: send reset link to registered email. No auth required. */
export async function forgotPassword(email: string): Promise<ApiResponse<{ message?: string }>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      return { success: false, error: (data as { error?: string }).error || 'Request failed' };
    }
    return { success: true, data: data as { message?: string }, message: (data as { message?: string }).message };
  } catch (e) {
    return { success: false, error: e instanceof Error ? e.message : 'Network error' };
  }
}

/** Reset password with token from email link. No auth required. */
export async function resetPassword(token: string, newPassword: string): Promise<ApiResponse<{ message?: string }>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, newPassword }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      return { success: false, error: (data as { error?: string }).error || 'Request failed' };
    }
    return { success: true, data: data as { message?: string }, message: (data as { message?: string }).message };
  } catch (e) {
    return { success: false, error: e instanceof Error ? e.message : 'Network error' };
  }
}

// Stats endpoints
export async function getStatsOverview(): Promise<ApiResponse<StatsOverview>> {
  const response = await apiRequest('/api/stats');
  if (response.success && response.data) {
    const data = response.data as any;
    return {
      success: true,
      data: {
        totalUsers: data.totalUsers || 0,
        totalStudents: data.totalStudents ?? data.roleDistribution?.student ?? 0,
        activeUsers: data.activeUsers ?? 0,
        activeSessions: data.activeSessions ?? 0,
        usersByRole: {
          admin: data.roleDistribution?.admin || 0,
          teacher: data.roleDistribution?.teacher || 0,
          student: data.roleDistribution?.student || 0,
        },
        whitelistSize: data.whitelistSize || 0,
        blacklistSize: data.blacklistSize || 0,
        recentLogins: data.recentLogins ?? 0,
        recentChanges: data.recentChanges ?? 0,
      },
    };
  }
  return response as ApiResponse<StatsOverview>;
}

export async function getChangeLogs(limit: number = 100): Promise<ApiResponse<import('./types').ChangeLog[]>> {
  return apiRequest(`/api/change-logs?limit=${limit}`);
}

export async function getDashboardLogs(limit: number = 100): Promise<ApiResponse<any[]>> {
  return apiRequest(`/api/dashboard-logs?limit=${limit}`);
}

export async function getHistory(limit: number = 100): Promise<ApiResponse<any[]>> {
  return apiRequest(`/api/history?limit=${limit}`);
}

export async function getStudentHistory(studentId: string, limit: number = 100): Promise<ApiResponse<any[]>> {
  return apiRequest(`/api/students/${encodeURIComponent(studentId)}/history?limit=${limit}`);
}

export async function getWarningTriggers(limit: number = 100, studentId?: string): Promise<ApiResponse<any[]>> {
  const q = studentId ? `?limit=${limit}&studentId=${encodeURIComponent(studentId)}` : `?limit=${limit}`;
  return apiRequest(`/api/warning-triggers${q}`);
}

export async function getSessions(limit: number = 100): Promise<ApiResponse<any[]>> {
  return apiRequest(`/api/sessions?limit=${limit}`);
}

export async function getAdmins(): Promise<ApiResponse<User[]>> {
  const response = await apiRequest('/api/admins');
  if (response.success && response.data) {
    const users = (response.data as any[]).map((u: any) => ({
      id: String(u.id),
      username: u.username,
      email: u.gmail || u.email || '',
      role: u.role === 'superadmin' ? 'super-admin' : u.role,
      isActive: u.isActive ?? u.is_active,
      createdAt: u.createdAt || u.created_at,
      lastLogin: u.lastLogin || u.last_login,
    }));
    return { success: true, data: users };
  }
  return response as ApiResponse<User[]>;
}

export async function getAdminStats(adminId: string): Promise<ApiResponse<AdminStats>> {
  return apiRequest(`/stats/admin/${adminId}`);
}

export async function getLoginActivity(days: number = 7): Promise<ApiResponse<LoginActivity[]>> {
  return apiRequest(`/stats/login-activity?days=${days}`);
}

export async function getAllAdminStats(): Promise<ApiResponse<AdminStats[]>> {
  return apiRequest('/stats/admins');
}

// User endpoints
export async function getUsers(adminId?: string): Promise<ApiResponse<User[]>> {
  const response = await apiRequest('/api/users');
  if (response.success && response.data) {
    // Transform API response to match User interface
    const users = (response.data as any[]).map((u: any) => ({
      id: String(u.id),
      username: u.username,
      email: u.gmail || u.email || '',
      role: u.role === 'superadmin' ? 'super-admin' : u.role,
      isActive: u.isActive,
      createdAt: u.createdAt || u.created_at,
      lastLogin: u.lastLogin || u.last_login,
    }));
    return { success: true, data: users };
  }
  return response as ApiResponse<User[]>;
}

export async function createUser(user: Partial<User>): Promise<ApiResponse<User>> {
  return apiRequest('/api/users', {
    method: 'POST',
    body: JSON.stringify(user),
  });
}

export async function updateUser(id: string, updates: Partial<User>): Promise<ApiResponse<User>> {
  return apiRequest(`/api/users/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}

export async function deleteUser(id: string): Promise<ApiResponse<void>> {
  return apiRequest(`/api/users/${id}`, {
    method: 'DELETE',
  });
}

export async function toggleUserStatus(id: string): Promise<ApiResponse<User>> {
  return apiRequest(`/api/users/${id}/toggle-status`, {
    method: 'PATCH',
  });
}

// Whitelist endpoints
export async function getWhitelist(adminId?: string): Promise<ApiResponse<WhitelistEntry[]>> {
  return apiRequest('/api/whitelist');
}

export async function addToWhitelist(entry: Partial<WhitelistEntry>): Promise<ApiResponse<WhitelistEntry>> {
  return apiRequest('/api/whitelist', {
    method: 'POST',
    body: JSON.stringify(entry),
  });
}

export async function updateWhitelistEntry(id: string, updates: Partial<WhitelistEntry>): Promise<ApiResponse<WhitelistEntry>> {
  return apiRequest(`/api/whitelist/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}

export async function removeFromWhitelist(id: string): Promise<ApiResponse<void>> {
  return apiRequest(`/api/whitelist/${id}`, {
    method: 'DELETE',
  });
}

// Blacklist endpoints
export async function getBlacklist(adminId?: string): Promise<ApiResponse<BlacklistEntry[]>> {
  return apiRequest('/api/blacklist');
}

export async function addToBlacklist(entry: Partial<BlacklistEntry>): Promise<ApiResponse<BlacklistEntry>> {
  return apiRequest('/api/blacklist', {
    method: 'POST',
    body: JSON.stringify(entry),
  });
}

export async function updateBlacklistEntry(id: string, updates: Partial<BlacklistEntry>): Promise<ApiResponse<BlacklistEntry>> {
  return apiRequest(`/api/blacklist/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}

export async function removeFromBlacklist(id: string): Promise<ApiResponse<void>> {
  return apiRequest(`/api/blacklist/${id}`, {
    method: 'DELETE',
  });
}

// Export endpoint
export async function exportDatabase(): Promise<ApiResponse<Blob>> {
  const token = getStoredToken();
  const deviceId = getDeviceId();

  try {
    const response = await fetch(`${API_BASE_URL}/export/db`, {
      method: 'POST',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
        ...(deviceId && { 'X-Device-ID': deviceId }),
      },
    });

    if (!response.ok) {
      // Try to parse error as JSON, but handle non-JSON responses
      let errorMessage = 'Export failed';
      try {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json();
          errorMessage = data.error || data.message || `Export failed: ${response.status} ${response.statusText}`;
        } else {
          errorMessage = `Export failed: ${response.status} ${response.statusText}`;
        }
      } catch {
        errorMessage = `Export failed: ${response.status} ${response.statusText}`;
      }
      return {
        success: false,
        error: errorMessage,
      };
    }

    const blob = await response.blob();
    return {
      success: true,
      data: blob,
    };
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      return {
        success: false,
        error: `Cannot connect to API at ${API_BASE_URL}. Please ensure the backend server is running.`,
      };
    }
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Export failed',
    };
  }
}

// Notifications endpoint
export async function getNotifications(): Promise<ApiResponse<Notification[]>> {
  return apiRequest('/notifications');
}

export async function markNotificationRead(id: string): Promise<ApiResponse<void>> {
  return apiRequest(`/notifications/${id}/read`, {
    method: 'PATCH',
  });
}

// Student endpoints
export async function getStudents(): Promise<ApiResponse<any[]>> {
  return apiRequest('/api/students');
}

export async function setStudentMode(studentId: string, mode: string, changedBy: number): Promise<ApiResponse<any>> {
  return apiRequest(`/api/students/${studentId}/mode`, {
    method: 'POST',
    body: JSON.stringify({ mode, changedBy }),
  });
}

// Teachers list (for admin to assign students to teachers)
export async function getTeachers(): Promise<ApiResponse<any[]>> {
  return apiRequest('/api/teachers');
}

// Assign student to teacher (admin only)
export async function assignStudentToTeacher(studentId: string, teacherId: string | null): Promise<ApiResponse<any>> {
  return apiRequest(`/api/students/${studentId}/assign-teacher`, {
    method: 'POST',
    body: JSON.stringify({ teacherId }),
  });
}

// Create admin (superadmin only)
export async function createAdmin(data: { username: string; password: string; email: string }): Promise<ApiResponse<any>> {
  return apiRequest('/api/users', {
    method: 'POST',
    body: JSON.stringify({ ...data, role: 'admin' }),
  });
}

// Activity endpoints
export async function getActivity(studentId?: string, limit: number = 100): Promise<ApiResponse<any[]>> {
  const query = studentId ? `?studentId=${studentId}&limit=${limit}` : `?limit=${limit}`;
  return apiRequest(`/api/activity${query}`);
}

export async function getViolations(studentId?: string, limit: number = 100): Promise<ApiResponse<any[]>> {
  const query = studentId ? `?studentId=${studentId}&limit=${limit}` : `?limit=${limit}`;
  return apiRequest(`/api/violations${query}`);
}

// Cached sites (teachers/admins: list and delete; add is from Qt app "Cache this page")
export async function getCachedSites(): Promise<ApiResponse<any[]>> {
  return apiRequest('/api/cached-sites');
}

export async function deleteCachedSite(id: string): Promise<ApiResponse<void>> {
  return apiRequest(`/api/cached-sites/${id}`, { method: 'DELETE' });
}

// Teacher endpoints
export async function getClassMetrics(): Promise<ApiResponse<ClassMetrics[]>> {
  // Transform students data to class metrics
  const studentsResponse = await getStudents();
  const activityResponse = await getActivity(undefined, 1000); // Get more activity for calculation
  
  if (studentsResponse.success && studentsResponse.data) {
    const students = studentsResponse.data as any[];
    const activities = activityResponse.success && activityResponse.data ? activityResponse.data as any[] : [];
    
    // Calculate average activity based on recent activity (last 7 days)
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    
    const recentActivities = activities.filter((a: any) => {
      const activityDate = new Date(a.visitStart || a.createdAt);
      return activityDate >= sevenDaysAgo;
    });
    
    // Calculate activity percentage: (active students / total students) * 100
    const activeStudentIds = new Set(recentActivities.map((a: any) => a.studentId));
    const activeStudentsCount = activeStudentIds.size;
    const totalStudents = students.length;
    const averageActivity = totalStudents > 0 
      ? Math.round((activeStudentsCount / totalStudents) * 100)
      : 0;
    
    // Group by mode or create default class
    const metrics: ClassMetrics[] = [
      {
        classId: 'all',
        className: 'All Students',
        studentCount: students.length,
        averageActivity: averageActivity,
        completedLessons: 0, // Not tracked in current schema
        totalLessons: 0, // Not tracked in current schema
      },
    ];
    return { success: true, data: metrics };
  }
  return { success: false, error: 'Failed to fetch class metrics' };
}

export async function getClassActivity(classId: string, hours: number = 24): Promise<ApiResponse<ActivityData[]>> {
  const response = await getActivity(undefined, 100);
  if (response.success && response.data) {
    // Transform activity logs to ActivityData format
    const activities = (response.data as any[]).map((a: any) => ({
      timestamp: a.visitStart || a.createdAt,
      activeStudents: 1,
      pageViews: 1,
      interactions: 0,
    }));
    return { success: true, data: activities };
  }
  return response as ApiResponse<ActivityData[]>;
}
