import React from 'react';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { DashboardStatsCards } from '@/components/shared/DashboardStatsCards';
import { UserTable } from '@/components/admin/UserTable';
import { StudentDetailCard } from '@/components/admin/StudentDetailCard';
import { ListTable } from '@/components/admin/ListTable';
import { ExportButton } from '@/components/admin/ExportButton';
import { ChangeLogsTable } from '@/components/admin/ChangeLogsTable';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useStudents, useUsers } from '@/hooks/useDashboardData';
import { Skeleton } from '@/components/ui/skeleton';
import { GraduationCap } from 'lucide-react';

export default function AdminDashboard() {
  const { data: students, isLoading: studentsLoading } = useStudents();
  const { data: users } = useUsers();
  const teachers = (users ?? []).filter((u: any) => u.role === 'teacher' || u.role === 'teacher');

  return (
    <DashboardLayout title="Admin Dashboard">
      <div className="mb-6 flex items-center justify-between">
        <Badge variant="outline" className="bg-primary/20 text-primary border-primary/30">
          Full Access
        </Badge>
        <ExportButton />
      </div>

      {/* Stats: Total Students, Total Whitelist, Total Blacklist only */}
      <div className="mb-8">
        <DashboardStatsCards />
      </div>

      {/* Tabs: Users, Students (per-student cards), Teachers, Whitelist, Blacklist, Change logs */}
      <Tabs defaultValue="students" className="space-y-6">
        <TabsList className="glass-card p-1 flex flex-wrap gap-1">
          <TabsTrigger value="students" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
            Students
          </TabsTrigger>
          <TabsTrigger value="teachers" className="data-[state=active]:bg-accent data-[state=active]:text-accent-foreground">
            Teachers
          </TabsTrigger>
          <TabsTrigger value="users" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
            Users
          </TabsTrigger>
          <TabsTrigger value="whitelist" className="data-[state=active]:bg-success data-[state=active]:text-success-foreground">
            Whitelist
          </TabsTrigger>
          <TabsTrigger value="blacklist" className="data-[state=active]:bg-destructive data-[state=active]:text-destructive-foreground">
            Blacklist
          </TabsTrigger>
          <TabsTrigger value="logs" className="data-[state=active]:bg-muted data-[state=active]:text-foreground">
            Change logs
          </TabsTrigger>
        </TabsList>

        <TabsContent value="students" className="animate-fade-in space-y-4">
          <p className="text-sm text-muted-foreground">
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
        </TabsContent>

        <TabsContent value="teachers" className="animate-fade-in">
          <p className="text-sm text-muted-foreground mb-4">
            Teachers in your group. Data from database.
          </p>
          <div className="rounded-lg border bg-card overflow-hidden">
            <div className="p-4 border-b bg-muted/30 flex items-center gap-2">
              <GraduationCap className="h-4 w-4" />
              <h3 className="font-semibold">Teachers</h3>
            </div>
            {!teachers.length ? (
              <div className="p-8 text-center text-muted-foreground text-sm">No teachers found</div>
            ) : (
              <ul className="divide-y">
                {teachers.map((t: any) => (
                  <li key={t.id} className="p-4 flex items-center justify-between hover:bg-muted/20">
                    <div>
                      <p className="font-medium">{t.username}</p>
                      <p className="text-xs text-muted-foreground">{t.email ?? t.gmail ?? '—'}</p>
                    </div>
                    <Badge variant="outline">{t.isActive ? 'Active' : 'Inactive'}</Badge>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </TabsContent>

        <TabsContent value="users" className="animate-fade-in">
          <UserTable />
        </TabsContent>

        <TabsContent value="whitelist" className="animate-fade-in">
          <ListTable type="whitelist" />
        </TabsContent>

        <TabsContent value="blacklist" className="animate-fade-in">
          <ListTable type="blacklist" />
        </TabsContent>

        <TabsContent value="logs" className="animate-fade-in">
          <ChangeLogsTable />
        </TabsContent>
      </Tabs>
    </DashboardLayout>
  );
}
