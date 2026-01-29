import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  getStatsOverview, 
  getUsers, 
  getStudents, 
  getActivity, 
  getViolations,
  getWhitelist,
  getBlacklist,
  getChangeLogs,
  getAdmins,
  setStudentMode,
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

