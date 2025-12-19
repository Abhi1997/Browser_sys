export type UserRole = 'super-admin' | 'admin' | 'teacher' | 'student';

export interface User {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  adminId?: string; // Which admin this user belongs to
  isActive: boolean;
  createdAt: string;
  lastLogin?: string;
}

export interface AuthToken {
  token: string;
  user: User;
  deviceId: string;
  expiresAt: number;
}

export interface JWTPayload {
  userId: string;
  username: string;
  role: UserRole;
  deviceId: string;
  adminId?: string;
  exp: number;
  iat: number;
}

export interface WhitelistEntry {
  id: string;
  url: string;
  description?: string;
  addedBy: string;
  addedAt: string;
  isActive: boolean;
}

export interface BlacklistEntry {
  id: string;
  url: string;
  reason?: string;
  addedBy: string;
  addedAt: string;
  isActive: boolean;
}

export interface StatsOverview {
  totalUsers: number;
  activeUsers: number;
  activeSessions: number;
  usersByRole: {
    admin: number;
    teacher: number;
    student: number;
  };
  whitelistSize: number;
  blacklistSize: number;
  recentLogins: number;
  recentChanges: number;
}

export interface AdminStats {
  id: string;
  adminId: string;
  adminName: string;
  totalUsers: number;
  activeUsers: number;
  teachers: number;
  students: number;
  whitelistSize: number;
  blacklistSize: number;
  activeSessions: number;
}

export interface LoginActivity {
  date: string;
  logins: number;
  uniqueUsers: number;
}

export interface Notification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  actionable: boolean;
  actionUrl?: string;
}

export interface ClassMetrics {
  classId: string;
  className: string;
  studentCount: number;
  averageActivity: number;
  completedLessons: number;
  totalLessons: number;
}

export interface ActivityData {
  timestamp: string;
  activeStudents: number;
  pageViews: number;
  interactions: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
