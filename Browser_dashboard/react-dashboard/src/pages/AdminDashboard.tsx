import React from 'react';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { StatCard } from '@/components/shared/StatCard';
import { LoginActivityChart } from '@/components/charts/LoginActivityChart';
import { RoleDistributionChart } from '@/components/charts/RoleDistributionChart';
import { UserTable } from '@/components/admin/UserTable';
import { StudentTable } from '@/components/admin/StudentTable';
import { ViolationsTable } from '@/components/admin/ViolationsTable';
import { ListTable } from '@/components/admin/ListTable';
import { ExportButton } from '@/components/admin/ExportButton';
import { Users, Activity, CheckCircle, Ban, Clock, TrendingUp, AlertTriangle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useStats, useStudents, useViolations } from '@/hooks/useDashboardData';
import { Skeleton } from '@/components/ui/skeleton';

export default function AdminDashboard() {
  const { data: stats, isLoading: statsLoading, error: statsError } = useStats();
  const { data: students } = useStudents();
  const { data: violations } = useViolations(undefined, 10);

  const recentViolations = violations?.length || 0;
  const activeStudents = students?.filter((s: any) => s.isActive).length || 0;

  if (statsError) {
    return (
      <DashboardLayout title="Admin Dashboard">
        <div className="p-6 text-center">
          <AlertTriangle className="h-12 w-12 text-destructive mx-auto mb-4" />
          <p className="text-destructive">Failed to load dashboard data</p>
          <p className="text-sm text-muted-foreground mt-2">{statsError.message}</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Admin Dashboard">
      {/* Admin badge */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Badge variant="outline" className="bg-primary/20 text-primary border-primary/30">
            Full Access
          </Badge>
        </div>
        <ExportButton />
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-8">
        {statsLoading ? (
          Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))
        ) : (
          <>
            <StatCard
              title="Total Users"
              value={stats?.totalUsers || 0}
              icon={Users}
              iconColor="text-primary"
              delay={0}
            />
            <StatCard
              title="Active Users"
              value={stats?.activeUsers || 0}
              icon={Activity}
              iconColor="text-success"
              delay={100}
            />
            <StatCard
              title="Active Students"
              value={activeStudents}
              icon={Users}
              iconColor="text-accent"
              delay={200}
            />
            <StatCard
              title="Recent Violations"
              value={recentViolations}
              icon={AlertTriangle}
              iconColor="text-warning"
              delay={300}
            />
            <StatCard
              title="Students (Exam)"
              value={students?.filter((s: any) => s.assignedMode === 'exam').length || 0}
              icon={CheckCircle}
              iconColor="text-destructive"
              delay={400}
            />
            <StatCard
              title="Students (Free)"
              value={students?.filter((s: any) => s.assignedMode === 'free').length || 0}
              icon={CheckCircle}
              iconColor="text-success"
              delay={500}
            />
          </>
        )}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <LoginActivityChart />
        <RoleDistributionChart />
      </div>

      {/* Tabs for management */}
      <Tabs defaultValue="users" className="space-y-6">
        <TabsList className="glass-card p-1">
          <TabsTrigger value="users" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
            Users
          </TabsTrigger>
          <TabsTrigger value="students" className="data-[state=active]:bg-accent data-[state=active]:text-accent-foreground">
            Students
          </TabsTrigger>
          <TabsTrigger value="whitelist" className="data-[state=active]:bg-success data-[state=active]:text-success-foreground">
            Whitelist
          </TabsTrigger>
          <TabsTrigger value="blacklist" className="data-[state=active]:bg-destructive data-[state=active]:text-destructive-foreground">
            Blacklist
          </TabsTrigger>
          <TabsTrigger value="violations" className="data-[state=active]:bg-warning data-[state=active]:text-warning-foreground">
            Violations
          </TabsTrigger>
        </TabsList>

        <TabsContent value="users" className="animate-fade-in">
          <UserTable />
        </TabsContent>

        <TabsContent value="students" className="animate-fade-in">
          <StudentTable />
        </TabsContent>

        <TabsContent value="whitelist" className="animate-fade-in">
          <ListTable type="whitelist" />
        </TabsContent>

        <TabsContent value="blacklist" className="animate-fade-in">
          <ListTable type="blacklist" />
        </TabsContent>

        <TabsContent value="violations" className="animate-fade-in">
          <ViolationsTable />
        </TabsContent>
      </Tabs>
    </DashboardLayout>
  );
}
