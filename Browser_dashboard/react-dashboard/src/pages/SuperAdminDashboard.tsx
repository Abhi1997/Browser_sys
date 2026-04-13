import React, { useMemo, useState } from 'react';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { DashboardStatsCards } from '@/components/shared/DashboardStatsCards';
import { AdminSwitcher } from '@/components/super/AdminSwitcher';
import { UserTable } from '@/components/admin/UserTable';
import { ListTable } from '@/components/admin/ListTable';
import { TopVisitedChart } from '@/components/charts/TopVisitedChart';
import { RecentLoginsCard } from '@/components/charts/RecentLoginsCard';
import { SystemLogsTree } from '@/components/admin/SystemLogsTree';
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
import { Eye, Building2, Users, GraduationCap, Plus, AlertTriangle } from 'lucide-react';
import { useAdmins, useUsers, useStudents, useStats, useCreateAdmin } from '@/hooks/useDashboardData';
import { Skeleton } from '@/components/ui/skeleton';

export default function SuperAdminDashboard() {
  const { selectedAdminId } = useAuth();
  const { data: admins, isLoading: adminsLoading } = useAdmins();
  const { data: users } = useUsers();
  const { data: students } = useStudents();
  const { data: stats } = useStats();
  const createAdmin = useCreateAdmin();
  
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newAdminUsername, setNewAdminUsername] = useState('');
  const [newAdminEmail, setNewAdminEmail] = useState('');
  const [newAdminPassword, setNewAdminPassword] = useState('');
  
  const handleCreateAdmin = () => {
    if (!newAdminUsername || !newAdminPassword) return;
    createAdmin.mutate({
      username: newAdminUsername,
      email: newAdminEmail,
      password: newAdminPassword,
    }, {
      onSuccess: () => {
        setIsCreateDialogOpen(false);
        setNewAdminUsername('');
        setNewAdminEmail('');
        setNewAdminPassword('');
      },
    });
  };

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

  return (
    <DashboardLayout title="Super Admin Dashboard">
      <div className="mb-6 p-4 rounded-xl bg-accent/10 border border-accent/30 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Eye className="h-5 w-5 text-accent shrink-0" />
          <div>
            <p className="font-medium text-accent">Monitor multiple admins (Read-Only)</p>
            <p className="text-sm text-muted-foreground">
              Each admin has an isolated group (admin → teachers → students). You can only view data and create new admins.
            </p>
          </div>
        </div>
        <Badge variant="outline" className="bg-accent/20 text-accent border-accent/30 shrink-0">
          Super Admin
        </Badge>
      </div>
      
      {/* Read-only warning */}
      <div className="mb-6 p-3 rounded-lg bg-warning/10 border border-warning/30 flex items-center gap-2">
        <AlertTriangle className="h-4 w-4 text-warning shrink-0" />
        <p className="text-sm text-warning">
          Super admins can only <strong>view</strong> data and <strong>create new admins</strong>. To modify users, whitelist, or blacklist, log in as an admin.
        </p>
      </div>

      {/* Admin switcher - list of admins from database */}
      <div className="mb-6">
        <AdminSwitcher />
      </div>

      {/* Stats: Total Students, Whitelist, Blacklist */}
      <div className="mb-8">
        <DashboardStatsCards />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <TopVisitedChart />
        <RecentLoginsCard />
      </div>
      
      <div className="mb-8">
        <SystemLogsTree />
      </div>

      {selectedAdminId && selectedAdminId !== 'system' && selectedAdmin ? (
        <>
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-foreground flex items-center gap-2">
              <Building2 className="h-6 w-6 text-primary" />
              {selectedAdmin.username}
            </h2>
            <p className="text-muted-foreground">Admin group (teachers & students). Data from database.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold flex items-center gap-2 mb-2">
                <GraduationCap className="h-4 w-4" />
                Teachers in this group
              </h3>
              <p className="text-2xl font-bold text-primary">{teachers.length}</p>
              <p className="text-xs text-muted-foreground">
                (When admin_id is in DB, list will filter by admin)
              </p>
            </div>
            <div className="rounded-lg border bg-card p-4">
              <h3 className="font-semibold flex items-center gap-2 mb-2">
                <Users className="h-4 w-4" />
                Students in this group
              </h3>
              <p className="text-2xl font-bold text-accent">{studentCount}</p>
              <p className="text-xs text-muted-foreground">
                (When admin_id is in DB, list will filter by admin)
              </p>
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
        <>
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-foreground">System overview</h2>
            <p className="text-muted-foreground">All admins and system-wide data. Select an admin above to view their isolated group.</p>
          </div>
          {adminsLoading ? (
            <Skeleton className="h-48 w-full" />
          ) : (
            <div className="rounded-lg border bg-card overflow-hidden mb-8">
              <div className="p-4 border-b bg-muted/30 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Building2 className="h-4 w-4" />
                  <h3 className="font-semibold">Admins ({admins?.length ?? 0})</h3>
                </div>
                <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                  <DialogTrigger asChild>
                    <Button size="sm" className="gap-1">
                      <Plus className="h-4 w-4" />
                      Create Admin
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Create New Admin</DialogTitle>
                      <DialogDescription>
                        Create a new admin with their own isolated group. They will be able to create teachers and students under them.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <div className="space-y-2">
                        <Label htmlFor="username">Username *</Label>
                        <Input
                          id="username"
                          value={newAdminUsername}
                          onChange={(e) => setNewAdminUsername(e.target.value)}
                          placeholder="admin_schoolname"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="email">Email</Label>
                        <Input
                          id="email"
                          type="email"
                          value={newAdminEmail}
                          onChange={(e) => setNewAdminEmail(e.target.value)}
                          placeholder="admin@school.com"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="password">Password *</Label>
                        <Input
                          id="password"
                          type="password"
                          value={newAdminPassword}
                          onChange={(e) => setNewAdminPassword(e.target.value)}
                          placeholder="Secure password"
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button
                        onClick={handleCreateAdmin}
                        disabled={!newAdminUsername || !newAdminPassword || createAdmin.isPending}
                      >
                        {createAdmin.isPending ? 'Creating...' : 'Create Admin'}
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
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
                      <Badge variant="outline">{a.isActive ? 'Active' : 'Inactive'}</Badge>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
          <div className="space-y-6">
            <UserTable readOnly />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ListTable type="whitelist" readOnly />
              <ListTable type="blacklist" readOnly />
            </div>
          </div>
        </>
      )}
    </DashboardLayout>
  );
}
