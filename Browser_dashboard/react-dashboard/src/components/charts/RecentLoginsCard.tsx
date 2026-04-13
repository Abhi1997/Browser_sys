import React from 'react';
import { useSystemLogs } from '@/hooks/useDashboardData';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LogIn, RefreshCcw, User } from 'lucide-react';
import { Button } from '@/components/ui/button';

const ROLE_COLORS: Record<string, string> = {
  superuser: 'bg-red-500/20 text-red-700 border-red-500/30',
  superadmin: 'bg-purple-500/20 text-purple-700 border-purple-500/30',
  'super-admin': 'bg-purple-500/20 text-purple-700 border-purple-500/30',
  admin: 'bg-blue-500/20 text-blue-700 border-blue-500/30',
  teacher: 'bg-emerald-500/20 text-emerald-700 border-emerald-500/30',
  student: 'bg-amber-500/20 text-amber-700 border-amber-500/30',
};

function timeAgo(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return 'just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.floor(diffHr / 24);
  if (diffDay < 7) return `${diffDay}d ago`;
  return date.toLocaleDateString();
}

export function RecentLoginsCard() {
  const { data: logs, isLoading, refetch, isFetching } = useSystemLogs(5, 'student');

  const recentLogins = React.useMemo(() => {
    if (!logs || !Array.isArray(logs)) return [];
    return logs.slice(0, 5);
  }, [logs]);

  return (
    <Card className="glass-card shadow-sm h-full flex flex-col">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle className="flex items-center gap-2 text-lg font-bold">
            <LogIn className="h-5 w-5 text-primary" />
            Recent Student Logins
          </CardTitle>
          <CardDescription>Last 5 browser logins by students</CardDescription>
        </div>
        <Button 
          variant="outline" 
          size="icon" 
          className="h-8 w-8" 
          onClick={() => refetch()}
          disabled={isFetching}
        >
          <RefreshCcw className={`h-4 w-4 ${isFetching ? 'animate-spin' : ''}`} />
        </Button>
      </CardHeader>
      <CardContent className="flex-1 pt-2">
        {isLoading ? (
          <div className="h-full flex items-center justify-center min-h-[200px]">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : !recentLogins || recentLogins.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-muted-foreground min-h-[200px]">
            <LogIn className="h-12 w-12 mb-3 opacity-20" />
            <p>No login activity yet</p>
          </div>
        ) : (
          <ul className="space-y-3">
            {recentLogins.map((log: any, idx: number) => (
              <li
                key={log.id || idx}
                className="flex items-center gap-3 rounded-lg border bg-card p-3 transition-colors hover:bg-muted/50"
              >
                <div className="h-9 w-9 rounded-lg bg-secondary flex items-center justify-center shrink-0">
                  <User className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground truncate">
                    {log.username || `User #${log.userId}`}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {log.createdAt ? timeAgo(log.createdAt) : ''}
                    {log.ipAddress ? ` · ${log.ipAddress}` : ''}
                  </p>
                </div>
                <Badge
                  variant="outline"
                  className={`shrink-0 text-[10px] ${ROLE_COLORS[log.role?.toLowerCase()] ?? ''}`}
                >
                  {log.role ?? '—'}
                </Badge>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
