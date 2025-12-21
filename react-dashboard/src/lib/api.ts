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

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000';

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
  return apiRequest('/auth/verify');
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
  return apiRequest('/stats/overview');
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
  const query = adminId ? `?adminId=${adminId}` : '';
  return apiRequest(`/users${query}`);
}

export async function createUser(user: Partial<User>): Promise<ApiResponse<User>> {
  return apiRequest('/users', {
    method: 'POST',
    body: JSON.stringify(user),
  });
}

export async function updateUser(id: string, updates: Partial<User>): Promise<ApiResponse<User>> {
  return apiRequest(`/users/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}

export async function toggleUserStatus(id: string): Promise<ApiResponse<User>> {
  return apiRequest(`/users/${id}/toggle-status`, {
    method: 'PATCH',
  });
}

// Whitelist endpoints
export async function getWhitelist(adminId?: string): Promise<ApiResponse<WhitelistEntry[]>> {
  const query = adminId ? `?adminId=${adminId}` : '';
  return apiRequest(`/whitelist${query}`);
}

export async function addToWhitelist(entry: Partial<WhitelistEntry>): Promise<ApiResponse<WhitelistEntry>> {
  return apiRequest('/whitelist', {
    method: 'POST',
    body: JSON.stringify(entry),
  });
}

export async function updateWhitelistEntry(id: string, updates: Partial<WhitelistEntry>): Promise<ApiResponse<WhitelistEntry>> {
  return apiRequest(`/whitelist/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}

export async function removeFromWhitelist(id: string): Promise<ApiResponse<void>> {
  return apiRequest(`/whitelist/${id}`, {
    method: 'DELETE',
  });
}

// Blacklist endpoints
export async function getBlacklist(adminId?: string): Promise<ApiResponse<BlacklistEntry[]>> {
  const query = adminId ? `?adminId=${adminId}` : '';
  return apiRequest(`/blacklist${query}`);
}

export async function addToBlacklist(entry: Partial<BlacklistEntry>): Promise<ApiResponse<BlacklistEntry>> {
  return apiRequest('/blacklist', {
    method: 'POST',
    body: JSON.stringify(entry),
  });
}

export async function updateBlacklistEntry(id: string, updates: Partial<BlacklistEntry>): Promise<ApiResponse<BlacklistEntry>> {
  return apiRequest(`/blacklist/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}

export async function removeFromBlacklist(id: string): Promise<ApiResponse<void>> {
  return apiRequest(`/blacklist/${id}`, {
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

// Teacher endpoints
export async function getClassMetrics(): Promise<ApiResponse<ClassMetrics[]>> {
  return apiRequest('/teacher/classes');
}

export async function getClassActivity(classId: string, hours: number = 24): Promise<ApiResponse<ActivityData[]>> {
  return apiRequest(`/teacher/classes/${classId}/activity?hours=${hours}`);
}
