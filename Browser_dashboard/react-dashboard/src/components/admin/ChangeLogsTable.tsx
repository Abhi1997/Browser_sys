import React from 'react';
import { Clock, User, ArrowRight } from 'lucide-react';
import { useChangeLogs } from '@/hooks/useDashboardData';
import { Skeleton } from '@/components/ui/skeleton';
import type { ChangeLog } from '@/lib/types';

export function ChangeLogsTable() {
  const { data: logs, isLoading, error } = useChangeLogs(100);

  if (error) {
    return (
      <div className="rounded-lg border bg-card p-6">
        <p className="text-sm text-destructive">Failed to load change logs from database.</p>
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

  const list = (logs ?? []) as ChangeLog[];

  return (
    <div className="rounded-lg border bg-card overflow-hidden">
      <div className="p-4 border-b bg-muted/30">
        <h3 className="font-semibold text-foreground flex items-center gap-2">
          <Clock className="h-4 w-4" />
          Change logs (mode changes)
        </h3>
        <p className="text-xs text-muted-foreground mt-1">
          Who changed student mode and when. Data from database.
        </p>
      </div>
      <div className="overflow-x-auto">
        {list.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground text-sm">
            No change logs yet.
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/20">
                <th className="text-left p-3 font-medium">Time</th>
                <th className="text-left p-3 font-medium">Student ID</th>
                <th className="text-left p-3 font-medium">Change</th>
                <th className="text-left p-3 font-medium">Changed by</th>
              </tr>
            </thead>
            <tbody>
              {list.map((log) => (
                <tr key={log.id} className="border-b last:border-0 hover:bg-muted/20">
                  <td className="p-3 text-muted-foreground">
                    {log.changedAt ? new Date(log.changedAt).toLocaleString() : '—'}
                  </td>
                  <td className="p-3 font-medium">{log.studentId ?? '—'}</td>
                  <td className="p-3 flex items-center gap-1">
                    <span className="text-muted-foreground">{log.oldMode ?? '—'}</span>
                    <ArrowRight className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">{log.newMode ?? '—'}</span>
                  </td>
                  <td className="p-3 flex items-center gap-1">
                    <User className="h-4 w-4 text-muted-foreground" />
                    {log.changedByName ?? log.changedBy ?? '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
