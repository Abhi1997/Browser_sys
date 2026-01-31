import React from 'react';
import { Clock, User, Monitor } from 'lucide-react';
import { useSessions } from '@/hooks/useDashboardData';
import { Skeleton } from '@/components/ui/skeleton';

export function SessionUsageTable() {
  const { data: sessions, isLoading, error } = useSessions(100);

  if (error) {
    return (
      <div className="rounded-lg border bg-card p-6">
        <p className="text-sm text-destructive">Failed to load session usage.</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="rounded-lg border bg-card p-6">
        <Skeleton className="h-8 w-48 mb-4" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  const list = (sessions ?? []) as any[];

  return (
    <div className="rounded-lg border bg-card overflow-hidden">
      <div className="p-4 border-b bg-muted/30">
        <h3 className="font-semibold text-foreground flex items-center gap-2">
          <Monitor className="h-4 w-4" />
          Browser session usage (for ML)
        </h3>
        <p className="text-xs text-muted-foreground mt-1">
          Session start and last activity per user. Timestamps for automation/ML.
        </p>
      </div>
      <div className="overflow-x-auto">
        {list.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground text-sm">
            No session data yet.
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/20">
                <th className="text-left p-3 font-medium">User</th>
                <th className="text-left p-3 font-medium">Session start</th>
                <th className="text-left p-3 font-medium">Last activity</th>
                <th className="text-left p-3 font-medium">Active</th>
              </tr>
            </thead>
            <tbody>
              {list.map((s) => (
                <tr key={s.id} className="border-b last:border-0 hover:bg-muted/20">
                  <td className="p-3 font-medium flex items-center gap-1">
                    <User className="h-4 w-4 text-muted-foreground" />
                    {s.username ?? s.userId ?? '—'}
                  </td>
                  <td className="p-3 text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      {s.sessionStart ? new Date(s.sessionStart).toLocaleString() : '—'}
                    </span>
                  </td>
                  <td className="p-3 text-muted-foreground">
                    {s.lastActivityAt ? new Date(s.lastActivityAt).toLocaleString() : '—'}
                  </td>
                  <td className="p-3">{s.isActive ? 'Yes' : 'No'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
