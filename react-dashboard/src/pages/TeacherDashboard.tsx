import React from 'react';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { ClassStatsCards } from '@/components/teacher/ClassStatsCards';
import { ActivityTimelineChart } from '@/components/charts/ActivityTimelineChart';
import { StatCard } from '@/components/shared/StatCard';
import { StudentTable } from '@/components/admin/StudentTable';
import { ViolationsTable } from '@/components/admin/ViolationsTable';
import { Users, TrendingUp, AlertTriangle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { useStudents, useViolations, useActivity } from '@/hooks/useDashboardData';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';

export default function TeacherDashboard() {
  const { data: students, isLoading: studentsLoading } = useStudents();
  const { data: violations } = useViolations(undefined, 20);
  const { data: activity } = useActivity(undefined, 50);

  const totalStudents = students?.length || 0;
  const activeStudents = students?.filter((s: any) => s.isActive).length || 0;
  const recentViolations = violations?.length || 0;
  const recentActivity = activity?.length || 0;

  return (
    <DashboardLayout title="Teacher Dashboard">
      {/* Teacher badge */}
      <div className="mb-6">
        <Badge variant="outline" className="bg-success/20 text-success border-success/30">
          Teacher Access
        </Badge>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {studentsLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))
        ) : (
          <>
            <StatCard
              title="Total Students"
              value={totalStudents}
              icon={Users}
              iconColor="text-primary"
              delay={0}
            />
            <StatCard
              title="Active Students"
              value={activeStudents}
              icon={Users}
              iconColor="text-success"
              delay={100}
            />
            <StatCard
              title="Recent Activity"
              value={recentActivity}
              icon={TrendingUp}
              iconColor="text-accent"
              delay={200}
            />
            <StatCard
              title="Violations"
              value={recentViolations}
              icon={AlertTriangle}
              iconColor="text-warning"
              delay={300}
            />
          </>
        )}
      </div>

      {/* Class Stats */}
      <div className="mb-8">
        <ClassStatsCards />
      </div>

      {/* Tabs for student management */}
      <Tabs defaultValue="students" className="space-y-6">
        <TabsList className="glass-card p-1">
          <TabsTrigger value="students" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
            Students
          </TabsTrigger>
          <TabsTrigger value="violations" className="data-[state=active]:bg-warning data-[state=active]:text-warning-foreground">
            Violations
          </TabsTrigger>
          <TabsTrigger value="activity" className="data-[state=active]:bg-accent data-[state=active]:text-accent-foreground">
            Activity
          </TabsTrigger>
        </TabsList>

        <TabsContent value="students" className="animate-fade-in">
          <StudentTable />
        </TabsContent>

        <TabsContent value="violations" className="animate-fade-in">
          <ViolationsTable />
        </TabsContent>

        <TabsContent value="activity" className="animate-fade-in">
          <ActivityTimelineChart />
        </TabsContent>
      </Tabs>
    </DashboardLayout>
  );
}
