import React from 'react';
import { Users, Activity, Shield, Ban, CheckCircle, Clock } from 'lucide-react';
import { StatCard } from '@/components/shared/StatCard';
import { useStats } from '@/hooks/useDashboardData';
import { Skeleton } from '@/components/ui/skeleton';

export function GlobalStatsCards() {
  const { data: stats, isLoading } = useStats();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
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
        title="Active Sessions"
        value={stats?.activeSessions || 0}
        icon={Clock}
        iconColor="text-accent"
        delay={200}
      />
      <StatCard
        title="Admins"
        value={stats?.usersByRole?.admin || 0}
        icon={Shield}
        iconColor="text-warning"
        delay={300}
      />
      <StatCard
        title="Whitelisted"
        value={stats?.whitelistSize || 0}
        icon={CheckCircle}
        iconColor="text-success"
        delay={400}
      />
      <StatCard
        title="Blacklisted"
        value={stats?.blacklistSize || 0}
        icon={Ban}
        iconColor="text-destructive"
        delay={500}
      />
    </div>
  );
}
