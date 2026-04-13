import React from 'react';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { DashboardStatsCards } from '@/components/shared/DashboardStatsCards';

import { StudentDetailCard } from '@/components/admin/StudentDetailCard';
import { ListTable } from '@/components/admin/ListTable';
import { ExportButton } from '@/components/admin/ExportButton';
import { DashboardLogsTable } from '@/components/admin/DashboardLogsTable';
import { CachedSitesTable } from '@/components/admin/CachedSitesTable';
import { TopVisitedChart } from '@/components/charts/TopVisitedChart';
import { RecentLoginsCard } from '@/components/charts/RecentLoginsCard';
import { SystemLogsTree } from '@/components/admin/SystemLogsTree';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useStudents, useUsers } from '@/hooks/useDashboardData';
import { Skeleton } from '@/components/ui/skeleton';
import { GraduationCap, UserPlus } from 'lucide-react';
import { AddUserModal } from '@/components/admin/AddUserModal';
import { Button } from '@/components/ui/button';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = React.useState("students");
  const [isAddUserOpen, setIsAddUserOpen] = React.useState(false);
  const { data: students, isLoading: studentsLoading } = useStudents();
  const { data: users } = useUsers();
  const teachers = (users ?? []).filter((u: any) => u.role === 'teacher' || u.role === 'teacher');

  return (
    <DashboardLayout title="Admin Dashboard">
      <div className="mb-6 flex items-center justify-between">
        <Badge variant="outline" className="bg-primary/20 text-primary border-primary/30">
          Full Access
        </Badge>
        <div className="flex items-center gap-4">
          <Button onClick={() => setIsAddUserOpen(true)} className="gap-2">
            <UserPlus className="h-4 w-4" />
            Add User
          </Button>
          <ExportButton />
        </div>
      </div>

      {/* Stats: Total Students, Total Whitelist, Total Blacklist only */}
      <div className="mb-8">
        <DashboardStatsCards onTabChange={setActiveTab} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <TopVisitedChart />
        <RecentLoginsCard />
      </div>
      
      <div className="mb-8">
        <SystemLogsTree />
      </div>

      {/* Tabs: Users, Students (per-student cards), Teachers, Whitelist, Blacklist, Change logs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="glass-card p-1 flex flex-wrap gap-1">
          <TabsTrigger value="students" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
            Students
          </TabsTrigger>
          <TabsTrigger value="teachers" className="data-[state=active]:bg-accent data-[state=active]:text-accent-foreground">
            Teachers
          </TabsTrigger>
          <TabsTrigger value="whitelist" className="data-[state=active]:bg-success data-[state=active]:text-success-foreground">
            Whitelist
          </TabsTrigger>
          <TabsTrigger value="blacklist" className="data-[state=active]:bg-destructive data-[state=active]:text-destructive-foreground">
            Blacklist
          </TabsTrigger>
          <TabsTrigger value="cached-sites" className="data-[state=active]:bg-violet-600 data-[state=active]:text-white">
            Cached sites
          </TabsTrigger>
          <TabsTrigger value="dashboard-logs" className="data-[state=active]:bg-muted data-[state=active]:text-foreground">
            Dashboard logs
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

        <TabsContent value="whitelist" className="animate-fade-in">
          <ListTable type="whitelist" />
        </TabsContent>

        <TabsContent value="blacklist" className="animate-fade-in">
          <ListTable type="blacklist" />
        </TabsContent>

        <TabsContent value="cached-sites" className="animate-fade-in">
          <CachedSitesTable />
        </TabsContent>

        <TabsContent value="dashboard-logs" className="animate-fade-in">
          <DashboardLogsTable />
        </TabsContent>
      </Tabs>
      <AddUserModal isOpen={isAddUserOpen} onClose={() => setIsAddUserOpen(false)} />
    </DashboardLayout>
  );
}
