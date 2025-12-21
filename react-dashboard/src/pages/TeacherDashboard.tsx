import React from 'react';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { ClassStatsCards } from '@/components/teacher/ClassStatsCards';
import { ActivityTimelineChart } from '@/components/charts/ActivityTimelineChart';
import { StatCard } from '@/components/shared/StatCard';
import { Users, BookOpen, TrendingUp, Clock } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { mockClassMetrics } from '@/lib/mock-data';

export default function TeacherDashboard() {
  const totalStudents = mockClassMetrics.reduce((sum, c) => sum + c.studentCount, 0);
  const avgActivity = Math.round(
    mockClassMetrics.reduce((sum, c) => sum + c.averageActivity, 0) / mockClassMetrics.length
  );
  const totalLessons = mockClassMetrics.reduce((sum, c) => sum + c.completedLessons, 0);
  const totalPlanned = mockClassMetrics.reduce((sum, c) => sum + c.totalLessons, 0);

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
        <StatCard
          title="Total Students"
          value={totalStudents}
          icon={Users}
          iconColor="text-primary"
          delay={0}
        />
        <StatCard
          title="Classes"
          value={mockClassMetrics.length}
          icon={BookOpen}
          iconColor="text-success"
          delay={100}
        />
        <StatCard
          title="Avg. Activity"
          value={`${avgActivity}%`}
          change={{ value: 5, type: 'increase' }}
          icon={TrendingUp}
          iconColor="text-accent"
          delay={200}
        />
        <StatCard
          title="Lessons Done"
          value={`${totalLessons}/${totalPlanned}`}
          icon={Clock}
          iconColor="text-warning"
          delay={300}
        />
      </div>

      {/* Class Cards */}
      <div className="mb-8">
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-foreground">Your Classes</h2>
          <p className="text-sm text-muted-foreground">Class performance and metrics</p>
        </div>
        <ClassStatsCards />
      </div>

      {/* Activity Chart */}
      <ActivityTimelineChart />
    </DashboardLayout>
  );
}
