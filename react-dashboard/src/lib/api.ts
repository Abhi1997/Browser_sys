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

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        error: data.error || data.message || 'Request failed',
      };
    }

    return {
      success: true,
      data: data.data || data,
      message: data.message,
    };
  } catch (error) {
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

// Stats endpoints
export async function getStatsOverview(): Promise<ApiResponse<StatsOverview>> {
  const response = await apiRequest('/api/stats');
  if (response.success && response.data) {
    // Transform API response to match StatsOverview interface
    const data = response.data as any;
    return {
      success: true,
      data: {
        totalUsers: data.totalUsers || 0,
        activeUsers: data.activeUsers || 0,
        activeSessions: 0, // Not tracked yet
        usersByRole: {
          admin: data.roleDistribution?.admin || 0,
          teacher: data.roleDistribution?.teacher || 0,
          student: data.roleDistribution?.student || 0,
        },
        whitelistSize: data.whitelistSize || 0,
        blacklistSize: data.blacklistSize || 0,
        recentLogins: data.recentLogins || 0,
        recentChanges: 0, // Not tracked yet
      },
    };
  }
  return response as ApiResponse<StatsOverview>;
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
      const data = await response.json();
      return {
        success: false,
        error: data.error || 'Export failed',
      };
    }

    const blob = await response.blob();
    return {
      success: true,
      data: blob,
    };
  } catch (error) {
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

// Activity endpoints
export async function getActivity(studentId?: string, limit: number = 100): Promise<ApiResponse<any[]>> {
  const query = studentId ? `?studentId=${studentId}&limit=${limit}` : `?limit=${limit}`;
  return apiRequest(`/api/activity${query}`);
}

export async function getViolations(studentId?: string, limit: number = 100): Promise<ApiResponse<any[]>> {
  const query = studentId ? `?studentId=${studentId}&limit=${limit}` : `?limit=${limit}`;
  return apiRequest(`/api/violations${query}`);
}

// Teacher endpoints
export async function getClassMetrics(): Promise<ApiResponse<ClassMetrics[]>> {
  // Transform students data to class metrics
  const studentsResponse = await getStudents();
  if (studentsResponse.success && studentsResponse.data) {
    const students = studentsResponse.data as any[];
    // Group by mode or create default class
    const metrics: ClassMetrics[] = [
      {
        classId: 'all',
        className: 'All Students',
        studentCount: students.length,
        averageActivity: 75, // TODO: Calculate from activity logs
        completedLessons: 0,
        totalLessons: 0,
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
