import { JWTPayload, UserRole, User } from './types';

export type { UserRole };

const DEVICE_ID_KEY = 'edu_browser_device_id';
const TOKEN_KEY = 'edu_browser_token';

export function getDeviceId(): string | null {
  return localStorage.getItem(DEVICE_ID_KEY);
}

export function setDeviceId(deviceId: string): void {
  localStorage.setItem(DEVICE_ID_KEY, deviceId);
}

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearAuth(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export function parseJWT(token: string): JWTPayload | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    
    const payload = JSON.parse(atob(parts[1]));
    return payload as JWTPayload;
  } catch {
    return null;
  }
}

export function isTokenExpired(token: string): boolean {
  const payload = parseJWT(token);
  if (!payload) return true;
  
  const now = Math.floor(Date.now() / 1000);
  return payload.exp < now;
}

export function extractUserFromToken(token: string): User | null {
  const payload = parseJWT(token);
  if (!payload) return null;
  
  return {
    id: payload.userId,
    username: payload.username,
    role: payload.role,
    adminId: payload.adminId,
    email: '', // Not in token for security
    isActive: true,
    createdAt: new Date().toISOString(),
  };
}

export function getQueryParams(): { user?: string; token?: string; deviceId?: string; role?: UserRole } {
  // Support both hash and regular query params for PyQt6 compatibility
  const searchParams = new URLSearchParams(
    window.location.hash.includes('?') 
      ? window.location.hash.split('?')[1]
      : window.location.search
  );
  
  return {
    user: searchParams.get('user') || undefined,
    token: searchParams.get('token') || undefined,
    deviceId: searchParams.get('deviceId') || undefined,
    role: (searchParams.get('role') as UserRole) || undefined,
  };
}

export function hasRole(userRole: UserRole, allowedRoles: UserRole[]): boolean {
  return allowedRoles.includes(userRole);
}

export function canAccessRoute(userRole: UserRole, route: string): boolean {
  const routeRoles: Record<string, UserRole[]> = {
    '/dashboard/super-admin': ['super-admin'],
    '/dashboard/admin': ['admin'],
    '/dashboard/teacher': ['teacher'],
  };
  
  const allowedRoles = routeRoles[route];
  if (!allowedRoles) return false;
  
  return allowedRoles.includes(userRole);
}

export function getRoleDashboardPath(role: UserRole): string {
  switch (role) {
    case 'super-admin':
      return '/dashboard/super-admin';
    case 'admin':
      return '/dashboard/admin';
    case 'teacher':
      return '/dashboard/teacher';
    case 'student':
      return '/unauthorized';
    default:
      return '/unauthorized';
  }
}

export function getRoleColor(role: UserRole): string {
  switch (role) {
    case 'super-admin':
      return 'hsl(262, 83%, 58%)';
    case 'admin':
      return 'hsl(217, 91%, 60%)';
    case 'teacher':
      return 'hsl(142, 71%, 45%)';
    default:
      return 'hsl(215, 20%, 55%)';
  }
}

export function getRoleBadgeClass(role: UserRole): string {
  switch (role) {
    case 'super-admin':
      return 'bg-accent/20 text-accent border-accent/30';
    case 'admin':
      return 'bg-primary/20 text-primary border-primary/30';
    case 'teacher':
      return 'bg-success/20 text-success border-success/30';
    default:
      return 'bg-muted text-muted-foreground border-muted';
  }
}

export function formatRole(role: UserRole): string {
  return role
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
