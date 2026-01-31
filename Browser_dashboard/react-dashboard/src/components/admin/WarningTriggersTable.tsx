import React from 'react';
import { AlertTriangle, User, Clock } from 'lucide-react';
import { useWarningTriggers } from '@/hooks/useDashboardData';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';

export function WarningTriggersTable() {
  const { data: triggers, isLoading, error } = useWarningTriggers(100);

  if (error) {
    return (
      <div className="rounded-lg border bg-card p-6">
        <p className="text-sm text-destructive">Failed to load warning triggers.</p>
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

  const list = (triggers ?? []) as any[];

  return (
    <div className="rounded-lg border bg-card overflow-hidden">
      <div className="p-4 border-b bg-muted/30">
        <h3 className="font-semibold text-foreground flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-warning" />
          Violations & warning triggers
        </h3>
        <p className="text-xs text-muted-foreground mt-1">
          First violation, repeated violation, and escalation. Data from database.
        </p>
      </div>
      <div className="overflow-x-auto">
        {list.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground text-sm">
            No warning triggers yet.
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/20">
                <th className="text-left p-3 font-medium">Time</th>
                <th className="text-left p-3 font-medium">Student</th>
                <th className="text-left p-3 font-medium">Type</th>
                <th className="text-left p-3 font-medium">Count</th>
                <th className="text-left p-3 font-medium">Escalated to</th>
                <th className="text-left p-3 font-medium">Resolved</th>
              </tr>
            </thead>
            <tbody>
              {list.map((w) => (
                <tr key={w.id} className="border-b last:border-0 hover:bg-muted/20">
                  <td className="p-3 text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      {w.createdAt ? new Date(w.createdAt).toLocaleString() : '—'}
                    </span>
                  </td>
                  <td className="p-3 font-medium flex items-center gap-1">
                    <User className="h-4 w-4 text-muted-foreground" />
                    {w.username ?? w.studentId ?? '—'}
                  </td>
                  <td className="p-3">
                    <Badge variant={w.warningType === 'critical_violation' ? 'destructive' : 'secondary'}>
                      {w.warningType ?? '—'}
                    </Badge>
                  </td>
                  <td className="p-3">{w.violationCount ?? '—'}</td>
                  <td className="p-3">{w.escalatedTo ?? '—'}</td>
                  <td className="p-3">{w.resolved ? 'Yes' : 'No'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
