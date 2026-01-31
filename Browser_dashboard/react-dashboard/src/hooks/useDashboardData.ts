import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  getStatsOverview, 
  getUsers, 
  getStudents, 
  getActivity, 
  getViolations,
  getWhitelist,
  getBlacklist,
  getCachedSites,
  deleteCachedSite,
  getChangeLogs,
  getDashboardLogs,
  getHistory,
  getStudentHistory,
  getWarningTriggers,
  getSessions,
  getAdmins,
  getTeachers,
  setStudentMode,
  assignStudentToTeacher,
  createAdmin,
  toggleUserStatus,
  createUser,
  deleteUser,
  addToWhitelist,
  removeFromWhitelist,
  updateWhitelistEntry,
  addToBlacklist,
  removeFromBlacklist,
  updateBlacklistEntry,
} from '@/lib/api';
import { toast } from '@/hooks/use-toast';

// Stats query
export function useStats() {
  return useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const response = await getStatsOverview();
      if (!response.success) {
        // Return default stats instead of throwing to prevent UI crashes
        console.warn('Failed to fetch stats:', response.error);
        return {
          totalUsers: 0,
          totalStudents: 0,
          activeUsers: 0,
          activeSessions: 0,
          usersByRole: {
            admin: 0,
            teacher: 0,
            student: 0,
          },
          whitelistSize: 0,
          blacklistSize: 0,
          recentLogins: 0,
          recentChanges: 0,
        };
      }
      return response.data!;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
    retry: 2, // Retry failed requests twice
  });
}

// Users query
export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await getUsers();
      if (!response.success) {
        console.warn('Failed to fetch users:', response.error);
        return []; // Return empty array instead of throwing
      }
      return response.data!;
    },
    refetchInterval: 30000,
    retry: 2,
  });
}

// Students query
export function useStudents() {
  return useQuery({
    queryKey: ['students'],
    queryFn: async () => {
      const response = await getStudents();
      if (!response.success) {
        console.warn('Failed to fetch students:', response.error);
        return []; // Return empty array instead of throwing
      }
      return response.data!;
    },
    refetchInterval: 30000,
    retry: 2,
  });
}

// Activity query
export function useActivity(studentId?: string, limit: number = 100) {
  return useQuery({
    queryKey: ['activity', studentId, limit],
    queryFn: async () => {
      const response = await getActivity(studentId, limit);
      if (!response.success) {
        console.warn('Failed to fetch activity:', response.error);
        return []; // Return empty array instead of throwing
      }
      return response.data!;
    },
    refetchInterval: 10000, // Refetch every 10 seconds for activity
    retry: 2,
  });
}

// Violations query
export function useViolations(studentId?: string, limit: number = 100) {
  return useQuery({
    queryKey: ['violations', studentId, limit],
    queryFn: async () => {
      const response = await getViolations(studentId, limit);
      if (!response.success) {
        console.warn('Failed to fetch violations:', response.error);
        return []; // Return empty array instead of throwing
      }
      return response.data!;
    },
    refetchInterval: 30000,
    retry: 2,
  });
}

// Change logs query (mode history for admin audit)
export function useChangeLogs(limit: number = 100) {
  return useQuery({
    queryKey: ['changeLogs', limit],
    queryFn: async () => {
      const response = await getChangeLogs(limit);
      if (!response.success) {
        console.warn('Failed to fetch change logs:', response.error);
        return [];
      }
      return response.data!;
    },
    refetchInterval: 30000,
    retry: 2,
  });
}

// Dashboard logs query (who opened dashboard when - admin only)
export function useDashboardLogs(limit: number = 100) {
  return useQuery({
    queryKey: ['dashboardLogs', limit],
    queryFn: async () => {
      const response = await getDashboardLogs(limit);
      if (!response.success) {
        console.warn('Failed to fetch dashboard logs:', response.error);
        return [];
      }
      return response.data!;
    },
    refetchInterval: 30000,
    retry: 2,
  });
}

// Own browsing history (for My History page)
export function useHistory(limit: number = 100) {
  return useQuery({
    queryKey: ['history', limit],
    queryFn: async () => {
      const response = await getHistory(limit);
      if (!response.success) {
        console.warn('Failed to fetch history:', response.error);
        return [];
      }
      return response.data!;
    },
    refetchInterval: 60000,
    retry: 2,
  });
}

// Student browsing history (for teachers viewing a student's tab)
export function useStudentHistory(studentId: string | undefined, limit: number = 100) {
  return useQuery({
    queryKey: ['studentHistory', studentId, limit],
    queryFn: async () => {
      if (!studentId) return [];
      const response = await getStudentHistory(studentId, limit);
      if (!response.success) {
        console.warn('Failed to fetch student history:', response.error);
        return [];
      }
      return response.data!;
    },
    enabled: !!studentId,
    refetchInterval: 60000,
    retry: 2,
  });
}

// Warning triggers (violations + escalation - teacher/admin)
export function useWarningTriggers(limit: number = 100, studentId?: string) {
  return useQuery({
    queryKey: ['warningTriggers', limit, studentId],
    queryFn: async () => {
      const response = await getWarningTriggers(limit, studentId);
      if (!response.success) {
        console.warn('Failed to fetch warning triggers:', response.error);
        return [];
      }
      return response.data!;
    },
    refetchInterval: 30000,
    retry: 2,
  });
}

// Cached sites (teachers/admins: list and delete; add via Qt app "Cache this page")
export function useCachedSites() {
  return useQuery({
    queryKey: ['cachedSites'],
    queryFn: async () => {
      const response = await getCachedSites();
      if (!response.success) {
        console.warn('Failed to fetch cached sites:', response.error);
        return [];
      }
      return response.data!;
    },
    refetchInterval: 30000,
    retry: 2,
  });
}

export function useDeleteCachedSite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteCachedSite(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cachedSites'] });
      toast({ title: 'Cached site removed' });
    },
    onError: (err: Error) => {
      toast({ title: 'Failed to remove cached site', description: err.message, variant: 'destructive' });
    },
  });
}

// Session usage (browser usage per user/session - admin, for ML)
export function useSessions(limit: number = 100) {
  return useQuery({
    queryKey: ['sessions', limit],
    queryFn: async () => {
      const response = await getSessions(limit);
      if (!response.success) {
        console.warn('Failed to fetch sessions:', response.error);
        return [];
      }
      return response.data!;
    },
    refetchInterval: 60000,
    retry: 2,
  });
}

// Admins list query (for super-admin)
export function useAdmins() {
  return useQuery({
    queryKey: ['admins'],
    queryFn: async () => {
      const response = await getAdmins();
      if (!response.success) {
        console.warn('Failed to fetch admins:', response.error);
        return [];
      }
      return response.data!;
    },
    refetchInterval: 30000,
    retry: 2,
  });
}

// Teachers list (for admin to assign students)
export function useTeachers() {
  return useQuery({
    queryKey: ['teachers'],
    queryFn: async () => {
      const response = await getTeachers();
      if (!response.success) {
        console.warn('Failed to fetch teachers:', response.error);
        return [];
      }
      return response.data!;
    },
    refetchInterval: 30000,
    retry: 2,
  });
}

// Assign student to teacher (admin only)
export function useAssignStudentToTeacher() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ studentId, teacherId }: { studentId: string; teacherId: string | null }) =>
      assignStudentToTeacher(studentId, teacherId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['students'] });
      toast({ title: 'Student assigned to teacher' });
    },
    onError: (err: Error) => {
      toast({ title: 'Failed to assign student', description: err.message, variant: 'destructive' });
    },
  });
}

// Create admin (superadmin only)
export function useCreateAdmin() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { username: string; password: string; email: string }) => createAdmin(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admins'] });
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast({ title: 'Admin created successfully' });
    },
    onError: (err: Error) => {
      toast({ title: 'Failed to create admin', description: err.message, variant: 'destructive' });
    },
  });
}

// Mutations
export function useUpdateStudentMode() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ studentId, mode, changedBy }: { studentId: string; mode: string; changedBy: number }) => {
      const response = await setStudentMode(studentId, mode, changedBy);
      if (!response.success) {
        throw new Error(response.error || 'Failed to update student mode');
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['students'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
      queryClient.invalidateQueries({ queryKey: ['changeLogs'] });
      toast({
        title: 'Mode updated',
        description: 'Student mode has been updated successfully.',
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Update failed',
        description: error.message,
        variant: 'destructive',
      });
    },
  });
}

export function useToggleUserStatus() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (userId: string) => {
      const response = await toggleUserStatus(userId);
      if (!response.success) {
        throw new Error(response.error || 'Failed to toggle user status');
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
      toast({
        title: 'Status updated',
        description: 'User status has been updated successfully.',
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Update failed',
        description: error.message,
        variant: 'destructive',
      });
    },
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (user: Partial<any>) => {
      const response = await createUser(user);
      if (!response.success) {
        throw new Error(response.error || 'Failed to create user');
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
      toast({
        title: 'User created',
        description: 'User has been created successfully.',
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Creation failed',
        description: error.message,
        variant: 'destructive',
      });
    },
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (userId: string) => {
      const response = await deleteUser(userId);
      if (!response.success) {
        throw new Error(response.error || 'Failed to delete user');
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
      toast({
        title: 'User deleted',
        description: 'User has been deleted successfully.',
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Deletion failed',
        description: error.message,
        variant: 'destructive',
      });
    },
  });
}

// Whitelist queries and mutations
export function useWhitelist() {
  return useQuery({
    queryKey: ['whitelist'],
    queryFn: async () => {
      const response = await getWhitelist();
      if (!response.success) {
        console.warn('Failed to fetch whitelist:', response.error);
        return []; // Return empty array instead of throwing
      }
      return response.data!;
    },
    refetchInterval: 30000,
    retry: 2,
  });
}

export function useAddToWhitelist() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (entry: Partial<any>) => {
      const response = await addToWhitelist(entry);
      if (!response.success) {
        throw new Error(response.error || 'Failed to add to whitelist');
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['whitelist'] });
      toast({
        title: 'Entry added',
        description: 'URL added to whitelist successfully.',
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Add failed',
        description: error.message,
        variant: 'destructive',
      });
    },
  });
}

export function useRemoveFromWhitelist() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await removeFromWhitelist(id);
      if (!response.success) {
        throw new Error(response.error || 'Failed to remove from whitelist');
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['whitelist'] });
      toast({
        title: 'Entry removed',
        description: 'URL removed from whitelist successfully.',
        variant: 'destructive',
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Remove failed',
        description: error.message,
        variant: 'destructive',
      });
    },
  });
}

export function useUpdateWhitelistEntry() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, updates }: { id: string; updates: Partial<any> }) => {
      const response = await updateWhitelistEntry(id, updates);
      if (!response.success) {
        throw new Error(response.error || 'Failed to update whitelist entry');
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['whitelist'] });
      toast({
        title: 'Entry updated',
        description: 'Whitelist entry has been updated successfully.',
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Update failed',
        description: error.message,
        variant: 'destructive',
      });
    },
  });
}

// Blacklist queries and mutations
export function useBlacklist() {
  return useQuery({
    queryKey: ['blacklist'],
    queryFn: async () => {
      const response = await getBlacklist();
      if (!response.success) {
        console.warn('Failed to fetch blacklist:', response.error);
        return []; // Return empty array instead of throwing
      }
      return response.data!;
    },
    refetchInterval: 30000,
    retry: 2,
  });
}

export function useAddToBlacklist() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (entry: Partial<any>) => {
      const response = await addToBlacklist(entry);
      if (!response.success) {
        throw new Error(response.error || 'Failed to add to blacklist');
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['blacklist'] });
      toast({
        title: 'Entry added',
        description: 'URL added to blacklist successfully.',
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Add failed',
        description: error.message,
        variant: 'destructive',
      });
    },
  });
}

export function useRemoveFromBlacklist() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await removeFromBlacklist(id);
      if (!response.success) {
        throw new Error(response.error || 'Failed to remove from blacklist');
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['blacklist'] });
      toast({
        title: 'Entry removed',
        description: 'URL removed from blacklist successfully.',
        variant: 'destructive',
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Remove failed',
        description: error.message,
        variant: 'destructive',
      });
    },
  });
}

export function useUpdateBlacklistEntry() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, updates }: { id: string; updates: Partial<any> }) => {
      const response = await updateBlacklistEntry(id, updates);
      if (!response.success) {
        throw new Error(response.error || 'Failed to update blacklist entry');
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['blacklist'] });
      toast({
        title: 'Entry updated',
        description: 'Blacklist entry has been updated successfully.',
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Update failed',
        description: error.message,
        variant: 'destructive',
      });
    },
  });
}

