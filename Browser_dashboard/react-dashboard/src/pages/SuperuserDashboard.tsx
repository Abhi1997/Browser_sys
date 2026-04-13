import React, { useMemo, useState } from 'react';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { DashboardStatsCards } from '@/components/shared/DashboardStatsCards';
import { AdminSwitcher } from '@/components/super/AdminSwitcher';
import { UserTable } from '@/components/admin/UserTable';
import { StudentDetailCard } from '@/components/admin/StudentDetailCard';
import { ListTable } from '@/components/admin/ListTable';
import { CachedSitesTable } from '@/components/admin/CachedSitesTable';
import { DashboardLogsTable } from '@/components/admin/DashboardLogsTable';
import { ExportButton } from '@/components/admin/ExportButton';
import { TopVisitedChart } from '@/components/charts/TopVisitedChart';
import { RecentLoginsCard } from '@/components/charts/RecentLoginsCard';
import { useAuth } from '@/contexts/AuthContext';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Crown, Building2, Users, GraduationCap, Plus, Shield } from 'lucide-react';
import { useAdmins, useUsers, useStudents, useStats, useCreateAdmin } from '@/hooks/useDashboardData';
import { createUser } from '@/lib/api';
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from '@/hooks/use-toast';

export default function SuperuserDashboard() {
  const [activeTab, setActiveTab] = React.useState("users");
  const { selectedAdminId } = useAuth();
  const { data: admins, isLoading: adminsLoading } = useAdmins();
  const { data: users } = useUsers();
  const { data: students, isLoading: studentsLoading } = useStudents();
  const { data: stats } = useStats();
  const createAdmin = useCreateAdmin();

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newUsername, setNewUsername] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newRole, setNewRole] = useState('admin');

  const selectedAdmin = useMemo(() => {
    if (!selectedAdminId || selectedAdminId === 'system') return null;
    return (admins ?? []).find((a: any) => String(a.id) === selectedAdminId);
  }, [selectedAdminId, admins]);

  const teachers = useMemo(() => {
    const list = users ?? [];
    return list.filter((u: any) => u.role === 'teacher');
  }, [users]);

  const studentCount = useMemo(() => {
    if (students && Array.isArray(students)) return students.length;
    return stats?.totalStudents ?? stats?.usersByRole?.student ?? 0;
  }, [students, stats]);

  const handleCreateUser = async () => {
    if (!newUsername || !newPassword) return;
    try {
      const response = await createUser({
        username: newUsername,
        email: newEmail,
        password: newPassword,
        role: newRole as any,
      });
      if (response.success) {
        toast({ title: `${newRole} created successfully` });
        setIsCreateDialogOpen(false);
        setNewUsername('');
        setNewEmail('');
        setNewPassword('');
        setNewRole('admin');
      } else {
        toast({ title: 'Failed to create user', description: response.error, variant: 'destructive' });
      }
    } catch (err) {
      toast({ title: 'Failed to create user', variant: 'destructive' });
    }
  };

  return (
    <DashboardLayout title="Superuser Dashboard">
      <div className="mb-6 p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Crown className="h-5 w-5 text-amber-500 shrink-0" />
          <div>
            <p className="font-medium text-amber-600">Superuser Mode - Full Access</p>
            <p className="text-sm text-muted-foreground">
              You have full access to view and modify all data across all admins. Use with caution.
            </p>
          </div>
        </div>
        <Badge variant="outline" className="bg-amber-500/20 text-amber-600 border-amber-500/30 shrink-0">
          <Shield className="h-3 w-3 mr-1" />
          Superuser
        </Badge>
      </div>

      {/* Admin switcher - list of admins from database */}
      <div className="mb-6">
        <AdminSwitcher />
      </div>

      {/* Stats */}
      <div className="mb-8">
        <DashboardStatsCards onTabChange={setActiveTab} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <TopVisitedChart />
        <RecentLoginsCard />
      </div>

      {/* Tabs for all data management */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="glass-card p-1 flex flex-wrap gap-1">
          <TabsTrigger value="users" className="data-[state=active]:bg-amber-600 data-[state=active]:text-white">
            All Users
          </TabsTrigger>
          <TabsTrigger value="admins" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
            Admins
          </TabsTrigger>
          <TabsTrigger value="students" className="data-[state=active]:bg-accent data-[state=active]:text-accent-foreground">
            All Students
          </TabsTrigger>
          <TabsTrigger value="whitelist" className="data-[state=active]:bg-success data-[state=active]:text-success-foreground">
            Whitelist
          </TabsTrigger>
          <TabsTrigger value="blacklist" className="data-[state=active]:bg-destructive data-[state=active]:text-destructive-foreground">
            Blacklist
          </TabsTrigger>
          <TabsTrigger value="cached-sites" className="data-[state=active]:bg-amber-600 data-[state=active]:text-white">
            Cached sites
          </TabsTrigger>
          <TabsTrigger value="dashboard-logs" className="data-[state=active]:bg-muted data-[state=active]:text-foreground">
            Dashboard logs
          </TabsTrigger>
        </TabsList>

        <TabsContent value="users" className="animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">All Users</h2>
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button size="sm" className="gap-1 bg-amber-600 hover:bg-amber-700">
                  <Plus className="h-4 w-4" />
                  Create User
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create New User</DialogTitle>
                  <DialogDescription>
                    As a superuser, you can create any user type including other superusers.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="role">Role *</Label>
                    <Select value={newRole} onValueChange={setNewRole}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="superuser">Superuser</SelectItem>
                        <SelectItem value="superadmin">Super Admin</SelectItem>
                        <SelectItem value="admin">Admin</SelectItem>
                        <SelectItem value="teacher">Teacher</SelectItem>
                        <SelectItem value="student">Student</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="username">Username *</Label>
                    <Input
                      id="username"
                      value={newUsername}
                      onChange={(e) => setNewUsername(e.target.value)}
                      placeholder="username"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={newEmail}
                      onChange={(e) => setNewEmail(e.target.value)}
                      placeholder="user@example.com"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password">Password *</Label>
                    <Input
                      id="password"
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="Secure password"
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button
                    onClick={handleCreateUser}
                    disabled={!newUsername || !newPassword}
                    className="bg-amber-600 hover:bg-amber-700"
                  >
                    Create User
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
          <UserTable />
        </TabsContent>

        <TabsContent value="admins" className="animate-fade-in">
          {adminsLoading ? (
            <Skeleton className="h-48 w-full" />
          ) : (
            <div className="rounded-lg border bg-card overflow-hidden">
              <div className="p-4 border-b bg-muted/30 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Building2 className="h-4 w-4" />
                  <h3 className="font-semibold">Admins ({admins?.length ?? 0})</h3>
                </div>
                <ExportButton />
              </div>
              {!admins?.length ? (
                <div className="p-8 text-center text-muted-foreground text-sm">No admins found</div>
              ) : (
                <ul className="divide-y">
                  {(admins as any[]).map((a: any) => (
                    <li key={a.id} className="p-4 flex items-center justify-between hover:bg-muted/20">
                      <div>
                        <p className="font-medium">{a.username}</p>
                        <p className="text-xs text-muted-foreground">{a.email ?? a.gmail ?? '—'}</p>
                      </div>
                      <Badge variant="outline">{a.isActive || a.is_active ? 'Active' : 'Inactive'}</Badge>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </TabsContent>

        <TabsContent value="students" className="animate-fade-in space-y-4">
          <p className="text-sm text-muted-foreground">
            All students across all admins. Full edit access.
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
    </DashboardLayout>
  );
}
