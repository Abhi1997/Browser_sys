import { 
  StatsOverview, 
  AdminStats, 
  User, 
  WhitelistEntry, 
  BlacklistEntry,
  LoginActivity,
  Notification,
  ClassMetrics,
  ActivityData
} from './types';

// Mock data for demo purposes when API is not available
export const mockStatsOverview: StatsOverview = {
  totalUsers: 1247,
  activeUsers: 892,
  activeSessions: 156,
  usersByRole: {
    admin: 12,
    teacher: 85,
    student: 1150,
  },
  whitelistSize: 342,
  blacklistSize: 89,
  recentLogins: 234,
  recentChanges: 45,
};

export const mockAdminStats: AdminStats[] = [
  {
    id: 'admin-1',
    adminId: 'admin-1',
    adminName: 'Central High School',
    totalUsers: 450,
    activeUsers: 380,
    teachers: 28,
    students: 420,
    whitelistSize: 120,
    blacklistSize: 32,
    activeSessions: 45,
  },
  {
    id: 'admin-2',
    adminId: 'admin-2',
    adminName: 'West Academy',
    totalUsers: 320,
    activeUsers: 275,
    teachers: 22,
    students: 296,
    whitelistSize: 95,
    blacklistSize: 18,
    activeSessions: 38,
  },
  {
    id: 'admin-3',
    adminId: 'admin-3',
    adminName: 'East Technical',
    totalUsers: 280,
    activeUsers: 210,
    teachers: 18,
    students: 260,
    whitelistSize: 78,
    blacklistSize: 24,
    activeSessions: 32,
  },
  {
    id: 'admin-4',
    adminId: 'admin-4',
    adminName: 'North Prep',
    totalUsers: 197,
    activeUsers: 145,
    teachers: 17,
    students: 174,
    whitelistSize: 49,
    blacklistSize: 15,
    activeSessions: 28,
  },
];

export const mockUsers: User[] = [
  { id: '1', username: 'jsmith', email: 'jsmith@school.edu', role: 'teacher', isActive: true, createdAt: '2024-01-15', lastLogin: '2024-12-09' },
  { id: '2', username: 'mjohnson', email: 'mjohnson@school.edu', role: 'teacher', isActive: true, createdAt: '2024-02-20', lastLogin: '2024-12-10' },
  { id: '3', username: 'swilliams', email: 'swilliams@school.edu', role: 'student', isActive: true, createdAt: '2024-03-10', lastLogin: '2024-12-09' },
  { id: '4', username: 'tbrown', email: 'tbrown@school.edu', role: 'student', isActive: false, createdAt: '2024-01-05', lastLogin: '2024-11-15' },
  { id: '5', username: 'ldavis', email: 'ldavis@school.edu', role: 'student', isActive: true, createdAt: '2024-04-01', lastLogin: '2024-12-10' },
  { id: '6', username: 'kmiller', email: 'kmiller@school.edu', role: 'teacher', isActive: true, createdAt: '2024-02-28', lastLogin: '2024-12-08' },
  { id: '7', username: 'rwilson', email: 'rwilson@school.edu', role: 'student', isActive: true, createdAt: '2024-05-15', lastLogin: '2024-12-10' },
  { id: '8', username: 'amoore', email: 'amoore@school.edu', role: 'student', isActive: true, createdAt: '2024-03-22', lastLogin: '2024-12-09' },
];

export const mockWhitelist: WhitelistEntry[] = [
  { id: '1', url: 'wikipedia.org', description: 'Educational resource', addedBy: 'admin', addedAt: '2024-01-10', isActive: true },
  { id: '2', url: 'khanacademy.org', description: 'Learning platform', addedBy: 'admin', addedAt: '2024-01-12', isActive: true },
  { id: '3', url: 'coursera.org', description: 'Online courses', addedBy: 'admin', addedAt: '2024-01-15', isActive: true },
  { id: '4', url: 'wolframalpha.com', description: 'Math computation', addedBy: 'admin', addedAt: '2024-02-01', isActive: true },
  { id: '5', url: 'quizlet.com', description: 'Study tools', addedBy: 'admin', addedAt: '2024-02-10', isActive: true },
];

export const mockBlacklist: BlacklistEntry[] = [
  { id: '1', url: 'facebook.com', reason: 'Social media distraction', addedBy: 'admin', addedAt: '2024-01-05', isActive: true },
  { id: '2', url: 'twitter.com', reason: 'Social media distraction', addedBy: 'admin', addedAt: '2024-01-05', isActive: true },
  { id: '3', url: 'tiktok.com', reason: 'Social media distraction', addedBy: 'admin', addedAt: '2024-01-05', isActive: true },
  { id: '4', url: 'twitch.tv', reason: 'Entertainment streaming', addedBy: 'admin', addedAt: '2024-01-08', isActive: true },
];

export const mockLoginActivity: LoginActivity[] = [
  { date: '2024-12-04', logins: 145, uniqueUsers: 120 },
  { date: '2024-12-05', logins: 189, uniqueUsers: 152 },
  { date: '2024-12-06', logins: 234, uniqueUsers: 198 },
  { date: '2024-12-07', logins: 67, uniqueUsers: 54 },
  { date: '2024-12-08', logins: 45, uniqueUsers: 38 },
  { date: '2024-12-09', logins: 267, uniqueUsers: 215 },
  { date: '2024-12-10', logins: 312, uniqueUsers: 248 },
];

export const mockNotifications: Notification[] = [
  { id: '1', type: 'warning', title: 'High Traffic Alert', message: 'System experiencing higher than normal load', timestamp: '2024-12-10T09:30:00Z', read: false, actionable: true },
  { id: '2', type: 'info', title: 'New Users Added', message: '15 new student accounts created today', timestamp: '2024-12-10T08:00:00Z', read: false, actionable: false },
  { id: '3', type: 'success', title: 'Backup Complete', message: 'Daily database backup completed successfully', timestamp: '2024-12-10T03:00:00Z', read: true, actionable: false },
  { id: '4', type: 'error', title: 'Failed Login Attempts', message: '5 failed login attempts for user jsmith', timestamp: '2024-12-09T16:45:00Z', read: false, actionable: true },
];

export const mockClassMetrics: ClassMetrics[] = [
  { classId: 'class-1', className: 'Mathematics 101', studentCount: 32, averageActivity: 78, completedLessons: 12, totalLessons: 18 },
  { classId: 'class-2', className: 'Physics Advanced', studentCount: 24, averageActivity: 85, completedLessons: 8, totalLessons: 15 },
  { classId: 'class-3', className: 'English Literature', studentCount: 28, averageActivity: 72, completedLessons: 14, totalLessons: 20 },
];

export const mockActivityData: ActivityData[] = Array.from({ length: 24 }, (_, i) => ({
  timestamp: new Date(Date.now() - (23 - i) * 3600000).toISOString(),
  activeStudents: Math.floor(Math.random() * 50) + 10,
  pageViews: Math.floor(Math.random() * 200) + 50,
  interactions: Math.floor(Math.random() * 100) + 20,
}));
