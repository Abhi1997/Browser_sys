import React from 'react';
import { Users, Activity, Shield, Ban, CheckCircle, Clock } from 'lucide-react';
import { StatCard } from '@/components/shared/StatCard';
import { mockStatsOverview } from '@/lib/mock-data';

interface GlobalStatsCardsProps {
  stats?: typeof mockStatsOverview;
}

export function GlobalStatsCards({ stats = mockStatsOverview }: GlobalStatsCardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      <StatCard
        title="Total Users"
        value={stats.totalUsers}
        change={{ value: 12, type: 'increase' }}
        icon={Users}
        iconColor="text-primary"
        delay={0}
      />
      <StatCard
        title="Active Users"
        value={stats.activeUsers}
        change={{ value: 5, type: 'increase' }}
        icon={Activity}
        iconColor="text-success"
        delay={100}
      />
      <StatCard
        title="Active Sessions"
        value={stats.activeSessions}
        change={{ value: 8, type: 'increase' }}
        icon={Clock}
        iconColor="text-accent"
        delay={200}
      />
      <StatCard
        title="Admins"
        value={stats.usersByRole.admin}
        icon={Shield}
        iconColor="text-warning"
        delay={300}
      />
      <StatCard
        title="Whitelisted"
        value={stats.whitelistSize}
        change={{ value: 3, type: 'increase' }}
        icon={CheckCircle}
        iconColor="text-success"
        delay={400}
      />
      <StatCard
        title="Blacklisted"
        value={stats.blacklistSize}
        change={{ value: 2, type: 'decrease' }}
        icon={Ban}
        iconColor="text-destructive"
        delay={500}
      />
    </div>
  );
}
