import React, { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { useAuth } from '@/contexts/AuthContext';
import { formatRole, getRoleBadgeClass } from '@/lib/auth';
import { updateUser } from '@/lib/api';
import { useStats, useStudents, useUsers, useAdmins } from '@/hooks/useDashboardData';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { User, Mail, Shield, Calendar, Clock, GraduationCap, Building2, Users } from 'lucide-react';
import { toast } from '@/hooks/use-toast';
import { Skeleton } from '@/components/ui/skeleton';

export default function Profile() {
  const { user, role, refreshUser } = useAuth();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [saving, setSaving] = useState(false);

  const { data: stats } = useStats();
  const { data: students } = useStudents();
  const { data: users } = useUsers();
  const { data: admins } = useAdmins();

  useEffect(() => {
    if (user) {
      setUsername(user.username ?? '');
      setEmail(user.email ?? '');
    }
  }, [user]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user?.id) return;
    setSaving(true);
    try {
      const response = await updateUser(user.id, { username: username.trim(), email: email.trim() });
      if (response.success) {
        await refreshUser?.();
        toast({ title: 'Profile updated', description: 'Your personal info has been saved.' });
      } else {
        toast({ title: 'Update failed', description: response.error ?? 'Could not save.', variant: 'destructive' });
      }
    } catch (err) {
      toast({ title: 'Update failed', description: (err as Error).message, variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  };

  if (!user) {
    return (
      <DashboardLayout title="My profile">
        <Skeleton className="h-64 w-full" />
      </DashboardLayout>
    );
  }

  const teacherCount = (users ?? []).filter((u: any) => u.role === 'teacher').length;
  const studentCount = stats?.totalStudents ?? (students ?? []).length;
  const adminCount = (admins ?? []).length;

  return (
    <DashboardLayout title="My profile">
      <div className="max-w-2xl space-y-8">
        {/* Personal info – editable (same for all roles) */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Personal information
            </CardTitle>
            <CardDescription>Edit your username and email. Changes apply across the dashboard.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSave} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="profile-username">Username</Label>
                <Input
                  id="profile-username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Username"
                  autoComplete="username"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="profile-email">Email</Label>
                <Input
                  id="profile-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Email"
                  autoComplete="email"
                />
              </div>
              <div className="flex items-center gap-4 pt-2">
                <Button type="submit" disabled={saving}>
                  {saving ? 'Saving…' : 'Save changes'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Read-only: role, last login, member since */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Account
            </CardTitle>
            <CardDescription>Role and account details (read-only).</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Role</span>
              <Badge variant="outline" className={role ? getRoleBadgeClass(role) : ''}>
                {role ? formatRole(role) : 'Unknown'}
              </Badge>
            </div>
            <Separator />
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Member since
              </span>
              <span className="text-foreground">
                {user.createdAt ? new Date(user.createdAt).toLocaleDateString() : '—'}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Last login
              </span>
              <span className="text-foreground">
                {user.lastLogin ? new Date(user.lastLogin).toLocaleString() : '—'}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Role-specific section */}
        {role === 'teacher' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GraduationCap className="h-5 w-5" />
                Teacher overview
              </CardTitle>
              <CardDescription>Summary for your teaching account.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Students in system</span>
                <span className="font-medium text-foreground">{studentCount}</span>
              </div>
              <p className="text-xs text-muted-foreground">
                Use the Teacher dashboard to view and manage students, activity, and violations.
              </p>
            </CardContent>
          </Card>
        )}

        {role === 'admin' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5" />
                Admin overview
              </CardTitle>
              <CardDescription>Summary for your admin account.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Teachers</span>
                <span className="font-medium text-foreground">{teacherCount}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Students</span>
                <span className="font-medium text-foreground">{studentCount}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Whitelist entries</span>
                <span className="font-medium text-foreground">{stats?.whitelistSize ?? 0}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Blacklist entries</span>
                <span className="font-medium text-foreground">{stats?.blacklistSize ?? 0}</span>
              </div>
              <p className="text-xs text-muted-foreground">
                Use the Admin dashboard to manage users, students, whitelist, blacklist, and change logs.
              </p>
            </CardContent>
          </Card>
        )}

        {role === 'super-admin' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Super admin overview
              </CardTitle>
              <CardDescription>System-wide summary for your super admin account.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Admins</span>
                <span className="font-medium text-foreground">{adminCount}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Teachers</span>
                <span className="font-medium text-foreground">{teacherCount}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Students</span>
                <span className="font-medium text-foreground">{studentCount}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Whitelist</span>
                <span className="font-medium text-foreground">{stats?.whitelistSize ?? 0}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Blacklist</span>
                <span className="font-medium text-foreground">{stats?.blacklistSize ?? 0}</span>
              </div>
              <p className="text-xs text-muted-foreground">
                Use the Super Admin dashboard to monitor all admins and system-wide data.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
