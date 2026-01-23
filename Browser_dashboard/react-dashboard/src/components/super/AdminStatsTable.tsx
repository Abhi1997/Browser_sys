import React, { useMemo } from 'react';
import { Building2, Users, Activity, Eye } from 'lucide-react';
import { DataTable } from '@/components/shared/DataTable';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { useAuth } from '@/contexts/AuthContext';
import { AdminStats } from '@/lib/types';
import { useUsers, useStudents } from '@/hooks/useDashboardData';
import { Skeleton } from '@/components/ui/skeleton';

export function AdminStatsTable() {
  const { setSelectedAdminId } = useAuth();
  const { data: users, isLoading: usersLoading } = useUsers();
  const { data: students } = useStudents();

  const adminStats = useMemo(() => {
    if (!users) return [];

    // Group by admin (for now, we'll create a single "institution" from all admins)
    const adminUsers = users.filter((u: any) => u.role === 'admin' || u.role === 'super-admin');
    const teacherUsers = users.filter((u: any) => u.role === 'teacher');
    const studentUsers = users.filter((u: any) => u.role === 'student');
    const activeUsers = users.filter((u: any) => u.isActive);

    if (adminUsers.length === 0) return [];

    // For now, create a single admin stat entry representing the system
    return [{
      id: 'system',
      adminId: 'system',
      adminName: 'System Overview',
      totalUsers: users.length,
      activeUsers: activeUsers.length,
      teachers: teacherUsers.length,
      students: studentUsers.length,
      activeSessions: 0, // Not tracked yet
    }];
  }, [users, students]);

  if (usersLoading) {
    return (
      <div className="glass-card p-6">
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  const columns = [
    {
      key: 'adminName',
      header: 'Institution',
      render: (item: AdminStats) => (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
            <Building2 className="h-5 w-5 text-primary" />
          </div>
          <div>
            <p className="font-medium text-foreground">{item.adminName}</p>
            <p className="text-xs text-muted-foreground">ID: {item.adminId}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'totalUsers',
      header: 'Total Users',
      render: (item: AdminStats) => (
        <div className="flex items-center gap-2">
          <Users className="h-4 w-4 text-muted-foreground" />
          <span className="font-medium">{item.totalUsers}</span>
        </div>
      ),
    },
    {
      key: 'activity',
      header: 'Activity Rate',
      render: (item: AdminStats) => {
        const rate = Math.round((item.activeUsers / item.totalUsers) * 100);
        return (
          <div className="w-32 space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">Active</span>
              <span className="font-medium">{rate}%</span>
            </div>
            <Progress value={rate} className="h-1.5" />
          </div>
        );
      },
    },
    {
      key: 'breakdown',
      header: 'User Breakdown',
      render: (item: AdminStats) => (
        <div className="flex gap-2">
          <Badge variant="outline" className="bg-success/10 text-success border-success/30">
            {item.teachers} Teachers
          </Badge>
          <Badge variant="outline" className="bg-accent/10 text-accent border-accent/30">
            {item.students} Students
          </Badge>
        </div>
      ),
    },
    {
      key: 'activeSessions',
      header: 'Sessions',
      render: (item: AdminStats) => (
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-success" />
          <span className="font-medium text-success">{item.activeSessions}</span>
        </div>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (item: AdminStats) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setSelectedAdminId(item.adminId)}
          className="gap-2"
        >
          <Eye className="h-4 w-4" />
          View
        </Button>
      ),
    },
  ];

  return (
    <div className="glass-card p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-foreground">Institution Overview</h3>
        <p className="text-sm text-muted-foreground">All registered admin subsystems</p>
      </div>
      <DataTable
        data={adminStats}
        columns={columns}
      />
    </div>
  );
}
