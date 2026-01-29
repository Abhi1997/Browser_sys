import React from 'react';
import { Users, ShieldCheck, ShieldAlert } from 'lucide-react';
import { StatCard } from '@/components/shared/StatCard';
import { useStats } from '@/hooks/useDashboardData';
import { Skeleton } from '@/components/ui/skeleton';

/**
 * Dashboard stats: Total Students, Total Whitelist, Total Blacklist only.
 * Data from database via API.
 */
export function DashboardStatsCards() {
  const { data: stats, isLoading, error } = useStats();

  if (error) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="col-span-full p-4 rounded-lg bg-destructive/10 text-destructive text-sm">
          Failed to load stats from database.
        </div>
      </div>
    );
  }

  if (isLoading || !stats) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    );
  }

  const totalStudents = stats.totalStudents ?? stats.usersByRole?.student ?? 0;
  const totalWhitelist = stats.whitelistSize ?? 0;
  const totalBlacklist = stats.blacklistSize ?? 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <StatCard
        title="Total Students"
        value={totalStudents}
        icon={Users}
        iconColor="text-primary"
        delay={0}
      />
      <StatCard
        title="Total Whitelist"
        value={totalWhitelist}
        icon={ShieldCheck}
        iconColor="text-success"
        delay={100}
      />
      <StatCard
        title="Total Blacklist"
        value={totalBlacklist}
        icon={ShieldAlert}
        iconColor="text-destructive"
        delay={200}
      />
    </div>
  );
}
