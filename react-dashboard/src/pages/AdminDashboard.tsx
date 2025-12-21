import React from 'react';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { StatCard } from '@/components/shared/StatCard';
import { LoginActivityChart } from '@/components/charts/LoginActivityChart';
import { RoleDistributionChart } from '@/components/charts/RoleDistributionChart';
import { UserTable } from '@/components/admin/UserTable';
import { ListTable } from '@/components/admin/ListTable';
import { ExportButton } from '@/components/admin/ExportButton';
import { Users, Activity, CheckCircle, Ban, Clock, TrendingUp } from 'lucide-react';
import { mockStatsOverview } from '@/lib/mock-data';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function AdminDashboard() {
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
        <StatCard
          title="Total Users"
          value={mockStatsOverview.totalUsers}
          change={{ value: 12, type: 'increase' }}
          icon={Users}
          iconColor="text-primary"
          delay={0}
        />
        <StatCard
          title="Active Users"
          value={mockStatsOverview.activeUsers}
          change={{ value: 5, type: 'increase' }}
          icon={Activity}
          iconColor="text-success"
          delay={100}
        />
        <StatCard
          title="Active Sessions"
          value={mockStatsOverview.activeSessions}
          change={{ value: 8, type: 'increase' }}
          icon={Clock}
          iconColor="text-accent"
          delay={200}
        />
        <StatCard
          title="Recent Logins"
          value={mockStatsOverview.recentLogins}
          icon={TrendingUp}
          iconColor="text-warning"
          delay={300}
        />
        <StatCard
          title="Whitelisted"
          value={mockStatsOverview.whitelistSize}
          change={{ value: 3, type: 'increase' }}
          icon={CheckCircle}
          iconColor="text-success"
          delay={400}
        />
        <StatCard
          title="Blacklisted"
          value={mockStatsOverview.blacklistSize}
          change={{ value: 2, type: 'decrease' }}
          icon={Ban}
          iconColor="text-destructive"
          delay={500}
        />
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
          <TabsTrigger value="whitelist" className="data-[state=active]:bg-success data-[state=active]:text-success-foreground">
            Whitelist
          </TabsTrigger>
          <TabsTrigger value="blacklist" className="data-[state=active]:bg-destructive data-[state=active]:text-destructive-foreground">
            Blacklist
          </TabsTrigger>
        </TabsList>

        <TabsContent value="users" className="animate-fade-in">
          <UserTable />
        </TabsContent>

        <TabsContent value="whitelist" className="animate-fade-in">
          <ListTable type="whitelist" />
        </TabsContent>

        <TabsContent value="blacklist" className="animate-fade-in">
          <ListTable type="blacklist" />
        </TabsContent>
      </Tabs>
    </DashboardLayout>
  );
}
