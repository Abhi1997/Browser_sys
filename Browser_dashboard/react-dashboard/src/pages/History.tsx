import React from 'react';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { useHistory } from '@/hooks/useDashboardData';
import { Skeleton } from '@/components/ui/skeleton';
import { Clock, ExternalLink } from 'lucide-react';

export default function History() {
  const { data: history, isLoading, error } = useHistory(200);

  return (
    <DashboardLayout title="My Browsing History">
      <p className="text-sm text-muted-foreground mb-6">
        Your personal browsing history. Only you can see this list.
      </p>
      {error && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-sm text-destructive">
          Failed to load history.
        </div>
      )}
      {isLoading ? (
        <Skeleton className="h-96 w-full" />
      ) : !history?.length ? (
        <div className="rounded-lg border bg-card p-8 text-center text-muted-foreground">
          No browsing history yet. Pages you visit in the browser will appear here.
        </div>
      ) : (
        <div className="rounded-lg border bg-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/20">
                  <th className="text-left p-3 font-medium">Time</th>
                  <th className="text-left p-3 font-medium">Page</th>
                  <th className="text-left p-3 font-medium">URL</th>
                </tr>
              </thead>
              <tbody>
                {(history as any[]).map((h: any) => (
                  <tr key={h.id} className="border-b last:border-0 hover:bg-muted/20">
                    <td className="p-3 text-muted-foreground whitespace-nowrap">
                      <span className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        {h.visitedAt ? new Date(h.visitedAt).toLocaleString() : '—'}
                      </span>
                    </td>
                    <td className="p-3 font-medium max-w-[200px] truncate" title={h.pageTitle || h.url}>
                      {h.pageTitle || '(no title)'}
                    </td>
                    <td className="p-3 text-muted-foreground max-w-[300px] truncate" title={h.url}>
                      <a href={h.url} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">
                        {h.url}
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
