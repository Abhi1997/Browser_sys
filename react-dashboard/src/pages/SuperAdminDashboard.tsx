import React from 'react';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { GlobalStatsCards } from '@/components/super/GlobalStatsCards';
import { AdminStatsTable } from '@/components/super/AdminStatsTable';
import { LoginActivityChart } from '@/components/charts/LoginActivityChart';
import { RoleDistributionChart } from '@/components/charts/RoleDistributionChart';
import { AdminComparisonChart } from '@/components/charts/AdminComparisonChart';
import { UserTable } from '@/components/admin/UserTable';
import { ListTable } from '@/components/admin/ListTable';
import { useAuth } from '@/contexts/AuthContext';
import { Badge } from '@/components/ui/badge';
import { Eye, AlertTriangle } from 'lucide-react';
import { mockAdminStats } from '@/lib/mock-data';

export default function SuperAdminDashboard() {
  const { selectedAdminId } = useAuth();
  const selectedAdmin = selectedAdminId 
    ? mockAdminStats.find(a => a.adminId === selectedAdminId)
    : null;

  return (
    <DashboardLayout title="Super Admin Dashboard">
      {/* Read-only banner */}
      <div className="mb-6 p-4 rounded-xl bg-accent/10 border border-accent/30 flex items-center gap-3">
        <Eye className="h-5 w-5 text-accent" />
        <div className="flex-1">
          <p className="font-medium text-accent">Read-Only Mode</p>
          <p className="text-sm text-muted-foreground">
            You can view all data across institutions but cannot modify any records.
          </p>
        </div>
        <Badge variant="outline" className="bg-accent/20 text-accent border-accent/30">
          Super Admin
        </Badge>
      </div>

      {selectedAdmin ? (
        // Admin-specific view
        <>
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-foreground">{selectedAdmin.adminName}</h2>
            <p className="text-muted-foreground">Viewing institution data (read-only)</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="stat-card">
              <p className="text-sm text-muted-foreground mb-1">Total Users</p>
              <p className="text-3xl font-bold">{selectedAdmin.totalUsers}</p>
            </div>
            <div className="stat-card">
              <p className="text-sm text-muted-foreground mb-1">Active Users</p>
              <p className="text-3xl font-bold text-success">{selectedAdmin.activeUsers}</p>
            </div>
            <div className="stat-card">
              <p className="text-sm text-muted-foreground mb-1">Teachers</p>
              <p className="text-3xl font-bold text-primary">{selectedAdmin.teachers}</p>
            </div>
            <div className="stat-card">
              <p className="text-sm text-muted-foreground mb-1">Students</p>
              <p className="text-3xl font-bold text-accent">{selectedAdmin.students}</p>
            </div>
          </div>

          <div className="space-y-6">
            <UserTable readOnly />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ListTable type="whitelist" readOnly />
              <ListTable type="blacklist" readOnly />
            </div>
          </div>
        </>
      ) : (
        // Global overview
        <>
          <GlobalStatsCards />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
            <LoginActivityChart />
            <RoleDistributionChart />
          </div>

          <div className="mt-8">
            <AdminComparisonChart />
          </div>

          <div className="mt-8">
            <AdminStatsTable />
          </div>
        </>
      )}
    </DashboardLayout>
  );
}
