import React from 'react';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { DashboardStatsCards } from '@/components/shared/DashboardStatsCards';
import { StudentDetailCard } from '@/components/admin/StudentDetailCard';
import { Badge } from '@/components/ui/badge';
import { useStudents } from '@/hooks/useDashboardData';
import { Skeleton } from '@/components/ui/skeleton';

export default function TeacherDashboard() {
  const { data: students, isLoading: studentsLoading } = useStudents();

  return (
    <DashboardLayout title="Teacher Dashboard">
      <div className="mb-6">
        <Badge variant="outline" className="bg-success/20 text-success border-success/30">
          Teacher Access
        </Badge>
      </div>

      {/* Stats: Total Students, Total Whitelist, Total Blacklist */}
      <div className="mb-8">
        <DashboardStatsCards />
      </div>

      {/* Per-student cards: mode (changeable), violations, history (site access with timestamp) */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-foreground">Students</h2>
        <p className="text-sm text-muted-foreground mb-4">
          Per-student: set mode (changeable), violations, and history (site access with timestamp). Data from database.
        </p>
        {studentsLoading ? (
          <Skeleton className="h-64 w-full" />
        ) : !students?.length ? (
          <div className="rounded-lg border bg-card p-8 text-center text-muted-foreground">
            No students found
          </div>
        ) : (
          <div className="space-y-4">
            {(students as any[]).map((s) => (
              <StudentDetailCard key={s.id ?? s.student_id ?? s.user_id} student={s} />
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
