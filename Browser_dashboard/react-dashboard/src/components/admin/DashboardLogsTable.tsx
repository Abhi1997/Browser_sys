import React from 'react';
import { Clock, User, Monitor } from 'lucide-react';
import { useDashboardLogs } from '@/hooks/useDashboardData';
import { Skeleton } from '@/components/ui/skeleton';

export function DashboardLogsTable() {
  const { data: logs, isLoading, error } = useDashboardLogs(100);

  if (error) {
    return (
      <div className="rounded-lg border bg-card p-6">
        <p className="text-sm text-destructive">Failed to load dashboard logs.</p>
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

  const list = (logs ?? []) as any[];

  return (
    <div className="rounded-lg border bg-card overflow-hidden">
      <div className="p-4 border-b bg-muted/30">
        <h3 className="font-semibold text-foreground flex items-center gap-2">
          <Monitor className="h-4 w-4" />
          Dashboard open logs
        </h3>
        <p className="text-xs text-muted-foreground mt-1">
          Who opened the dashboard and when. Data from database.
        </p>
      </div>
      <div className="overflow-x-auto">
        {list.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground text-sm">
            No dashboard logs yet.
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/20">
                <th className="text-left p-3 font-medium">Time</th>
                <th className="text-left p-3 font-medium">User</th>
                <th className="text-left p-3 font-medium">Role</th>
                <th className="text-left p-3 font-medium">Action</th>
                <th className="text-left p-3 font-medium">IP</th>
              </tr>
            </thead>
            <tbody>
              {list.map((log) => (
                <tr key={log.id} className="border-b last:border-0 hover:bg-muted/20">
                  <td className="p-3 text-muted-foreground">
                    {log.createdAt ? new Date(log.createdAt).toLocaleString() : '—'}
                  </td>
                  <td className="p-3 font-medium flex items-center gap-1">
                    <User className="h-4 w-4 text-muted-foreground" />
                    {log.username ?? log.userId ?? '—'}
                  </td>
                  <td className="p-3">{log.role ?? '—'}</td>
                  <td className="p-3">{log.action ?? '—'}</td>
                  <td className="p-3 text-muted-foreground">{log.ipAddress ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
